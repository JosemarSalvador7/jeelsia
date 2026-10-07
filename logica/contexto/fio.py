"""Fio condutor da conversa — desenvolve o diálogo sem perder o contexto.

Este módulo dá à assistente a capacidade de *conduzir* a conversa:
em vez de tratar cada mensagem como um comando isolado, ela mantém uma
"linha de conversa" (``fio_condutor``) que sobrevive entre turnos e é
usada para:

- retomar automaticamente o desabafo/assunto pendente quando o
  utilizador responde de forma vaga ("pois", "ah", "depois falo");
- desenvolver o tema com perguntas progressivas (open → específico),
  em vez de repetir sempre a mesma pergunta genérica;
- reconhecer respostas curtas afirmativas/negativas direcionadas à
  última pergunta feita pela IA (elipse conversacional);
- decidir quando *soltar* o fio (mudança clara de tópico ou despedida).

Tudo opera sobre o dicionário ``estado`` criado por
``logica.contexto.criar_estado`` — funções puras, sem efeitos globais.
"""

import random
import re

from logica.utils.texto import normalizar_texto

# Importação tardia dentro de funções para evitar ciclo: espejo importa
# contexto.contexto (REFLECTIONS), e este módulo é consumido por main.


def _gerar_espejo_seguro(*args, **kwargs):
    """Wrapper tolerante a falhas para o espelho ELIZA."""
    try:
        from .espejo import gerar_espejo as _ge
        return _ge(*args, **kwargs)
    except Exception:
        return None

# ----------------------------------------------------------------------
# Vocabulário de continuidade conversacional
# ----------------------------------------------------------------------

# Palavras que sozinhas não abrem novo tópico — sinalizam que o
# utilizador continua no fio anterior ("pois", "entendi", "hmm"...).
CONTINUADORES = {
    "pois", "poise", "sim", "s", "claro", "ok", "okei", "okay", "hm",
    "hmm", "hum", "ah", "aha", "aham", "entendi", "certo", "tá", "ta",
    "está", "esta", "boa", "fixe", "exato", "exatamente", "compreendi",
    "percebi", "interessante", "realmente", "mesmo", "lindo", "obg",
}

# Concordância seguida de pouco mais ("pois é", "é isso", "ao invés disso")
EXPRESSES_CONTINUIDADE = [
    "pois é", "poi e", "isso mesmo", "é isso", "e isso", "exatamente isso",
    "pode crer", "nem me fale", "nem me contes", "vc nem imagina",
    "tu nem imaginas", "é verdade", "mesmo assim", "ainda assim",
]

# Sinais de que o desabafo chegou ao fim (encerrar o fio emocional)
ENCERRAMENTOS = [
    "chega", "por hoje chega", "para por aqui", "não quero falar",
    "ja falei demais", "já falei demais", "melhor assim", "passou",
    "superei", "esquece isso", "esqueça isso", "deixa pra lá",
    "deixa pra lado", "vou embora", "falar depois", "depois falamos",
]

# Perguntas progressivas por emoção dominante — desenvolvem o tema em
# camadas (sentimento → causa → impacto → apoio), sem repetir nível.
PERGUNTAS_PROGRESSIVAS = {
    "tristeza": [
        "Queres contar-me o que aconteceu?",
        "Há quanto tempo te sentes assim?",
        "Foi algo específico que desencadeou isso, ou foi acumulando?",
        "O que costuma ajudar-te nestes momentos?",
        "Preferes desabafar mais ou que pensemos juntos num próximo passo?",
    ],
    "raiva": [
        "O que exatamente te deixou tão irritado?",
        "Já tinhas avisado a pessoa/situado, ou rebentou de repente?",
        "Como achas que queres resolver — falando ou agindo?",
        "O que te ajudaria a baixar a pressão agora?",
    ],
    "medo": [
        "O que mais te preocupa nessa situação?",
        "Já viveste algo parecido antes?",
        "Se tudo corresse bem, como seria o desfecho ideal?",
        "Queres que pensemos num plano pequeno para começar?",
    ],
    "alegria": [
        "Conta-me melhor — qual foi a melhor parte?",
        "Vais comemorar de alguma forma?",
        "Quem soubeste primeiro? Partilhaste com alguém?",
        "Que outro objetivo te apetece alcançar agora que estás inspirado?",
    ],
}

# Transições suaves para retomar o fio após uma mensagem vaga
RETOMADAS = [
    "Continuando do ponto onde ficámos:",
    "Voltando ao que estavas a contar:",
    "Retomando o teu desabafo:",
    "Ainda sobre aquilo que mencionaste,",
]

# Reconhecimentos de elipse ("sim" respondendo a uma pergunta da IA)
ELIPSES_AFIRMATIVAS = [
    "Fixe, então seguimos por aí.",
    "Perfeito, entendi.",
    "Boa, fico contente.",
    "Certo, vamos por partes então.",
]
ELIPSES_NEGATIVAS = [
    "Sem problema, respeito totalmente.",
    "Tudo bem, deixamos isso para depois.",
    "Compreendo, sem pressão.",
    "Ok, então sigo por outro caminho contigo.",
]


def _dividir_frases(texto: str) -> list[str]:
    """Divide texto em frases (mantendo pontuação final)."""
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+", texto.strip()) if f.strip()]


def _frase_substantiva(frase: str) -> bool:
    """False para continuadores/elipses — só memora conteúdo real."""
    m = normalizar_texto(frase)
    if m in CONTINUADORES:
        return False
    if any(exp == m for exp in EXPRESSES_CONTINUIDADE):
        return False
    return len(m) > 3


def atualizar_fio(estado: dict, mensagem: str, resposta_ia: str | None,
                  emocao: dict | None = None) -> None:
    """Atualiza o "fio condutor" da conversa após um turno completo.

    Guarda em ``estado['fio']``:
    - ``emocao``: emoção ativa do último desabafo (âncora emocional);
    - ``nivel``: quantas perguntas progressivas já foram feitas;
    - ``ultima_pergunta``: a última pergunta aberta pela IA (permite
      reconhecer respostas elípticas como "sim"/"pois");
    - ``resumo``: últimas frases relevantes do utilizador (memória curta).
    """
    fio = estado.setdefault("fio", {"emocao": None, "nivel": 0,
                                    "ultima_pergunta": None, "resumo": []})

    # Âncora emocional do turno
    if emocao and emocao.get("dominante") not in (None, "neutro"):
        dom = emocao["dominante"]
        if dom != fio.get("emocao"):
            fio["emocao"] = dom
            if dom in PERGUNTAS_PROGRESSIVAS:
                fio["nivel"] = 0
    m = mensagem.lower().strip()
    if any(e in m for e in ENCERRAMENTOS):
        fio["emocao"] = None
        fio["nivel"] = 0

    # Memória curta: as duas últimas frases substantivas do utilizador
    frases = _dividir_frases(mensagem)
    for f in frases[-2:]:
        if _frase_substantiva(f):
            resumo = fio["resumo"]
            if f not in resumo:
                resumo.append(f)
            del resumo[:-4]

    # Última pergunta aberta da IA (base para elipses). Só perguntas
    # feitas ao utilizador alimentam o nível — retomadas que citam o
    # desabafo ("Sobre 'X', ...?") não contam como novo turno de pergunta.
    if resposta_ia and not eh_mensagem_vaga(mensagem):
        questoes = re.findall(r"[^.!?]*\?[^.!?]*", resposta_ia)
        if questoes:
            fio["ultima_pergunta"] = questoes[-1].strip()
            fio["nivel"] = min(fio.get("nivel", 0) + 1, 99)


def _fio_ativo(estado: dict) -> dict | None:
    """Fio utilizável pelas mecânicas de elipse/retomada.

    Antes exigia ``emocao`` válida (âncora emocional); passou também a
    aceitar um fio com pergunta pendente — é o caso de espelhos ELIZA e
    retomadas que ficam à espera de resposta mesmo sem emoção forte.
    Sem isso, "sim" depois de um espelho caía em "não reconheci".
    """
    fio = estado.get("fio")
    if not isinstance(fio, dict):
        return None
    if fio.get("emocao") in PERGUNTAS_PROGRESSIVAS:
        return fio
    if fio.get("ultima_pergunta"):
        return fio
    return None


def _avancar_nivel(fio: dict) -> None:
    """Avança o nível do fio para a pergunta que acabou de ser feita."""
    pool = PERGUNTAS_PROGRESSIVAS[fio["emocao"]]
    fio["nivel"] = (fio.get("nivel", 0) + 1) % len(pool)


def eh_mensagem_vaga(mensagem: str) -> bool:
    """True se a mensagem não traz conteúdo novo (continuador/elipse)."""
    m = normalizar_texto(mensagem)
    if not m:
        return True
    if m in CONTINUADORES:
        return True
    if any(exp in m for exp in EXPRESSES_CONTINUIDADE):
        return True
    # Só stopwords/palavras muito curtas ("a", "e", "mas", "depois")
    palavras = [p for p in m.split() if len(p) > 2]
    return len(palavras) == 0


def responder_elipse(estado: dict, mensagem: str) -> str | None:
    """Reconhece respostas curtas à última pergunta da IA (elipse).

    Ex.: IA: "...Queres conversar sobre isso?" → Utilizador: "pois".
    Devolve resposta que retoma o fio, ou None se não for elipse.
    """
    fio = _fio_ativo(estado)
    m = normalizar_texto(mensagem)

    afirmativas = {"sim", "s", "si", "yeah", "yep", "pois", "poise", "claro",
                   "exato", "exatamente", "ok", "okei", "blz", "beleza", "boa", "fixe"}
    negativas = {"não", "nao", "n", "nah", "nem", "nops", "nunca", "negativo",
                 "agora nao", "agora não", "ja nao", "já não"}

    if m not in afirmativas and m not in negativas:
        return None

    ultima = (fio or {}).get("ultima_pergunta") or ""
    eh = m in afirmativas

    base = random.choice(ELIPSES_AFIRMATIVAS if eh else ELIPSES_NEGATIVAS)

    if ultima:
        retomada = random.choice(RETOMADAS)
        follow = proxima_pergunta_progressiva(estado)
        if eh:
            _avancar_nivel(fio)
            nova_pend = follow or (fio.get("ultima_pergunta") or "")
            fio["ultima_pergunta"] = nova_pend
            if follow:
                return f"{base} {retomada} {follow}"
            # Sem pool progressivo (fio só com espelho pendente): retomar
            # citando o último trecho memorizado em vez de repetir a
            # pergunta que acabou de ser respondida.
            resumo = fio.get("resumo") or []
            gancho = ""
            if resumo:
                trecho = resumo[-1]
                if len(trecho) > 60:
                    trecho = trecho[:57].rstrip() + "..."
                gancho = f"Sobre \"{trecho}\", "
            convite = random.choice([
                "queres acrescentar mais alguma coisa?",
                "faz sentido parar aqui ou continuamos?",
                "o que mais te vai passando pela cabeça?",
            ])
            return f"{base} {retomada} {gancho}{convite}"
        if not eh:
            return f"{base} Se mudares de ideias, é só dizer."
    if not eh:
        return f"{base} Queres mudar de assunto ou preferes ficar aqui?"
    return None


def proxima_pergunta_progressiva(estado: dict) -> str | None:
    """Devolve a próxima pergunta do fio, avançando um nível."""
    fio = _fio_ativo(estado)
    if not fio or fio.get("emocao") not in PERGUNTAS_PROGRESSIVAS:
        return None
    pool = PERGUNTAS_PROGRESSIVAS[fio["emocao"]]
    nivel = fio.get("nivel", 0) % len(pool)
    # Evita devolver a mesma pergunta que está registada
    pergunta = pool[nivel]
    if pergunta == fio.get("ultima_pergunta"):
        pergunta = pool[(nivel + 1) % len(pool)]
    return pergunta


def retomar_fio(estado: dict, mensagem: str) -> str | None:
    """Desenvolve a conversa a partir do fio quando a mensagem é vaga.

    Combina um reconhecimento curto com a próxima pergunta progressiva,
    citando quando possível a última frase relevante do utilizador.
    Sem pool progressivo ativo (ex.: fio sustentado só por um espelho
    ELIZA), usa o espelho diferido sobre a memória curta — nunca a
    pergunta que está pendente (seria repetição).
    """
    fio = _fio_ativo(estado)
    if not fio or not eh_mensagem_vaga(mensagem):
        return None

    resumo = fio.get("resumo") or []
    gancho = ""
    if resumo:
        trecho = resumo[-1]
        if len(trecho) > 60:
            trecho = trecho[:57].rstrip() + "..."
        gancho = f"Sobre \"{trecho}\", "

    pergunta = proxima_pergunta_progressiva(estado)
    if pergunta:
        ponte = random.choice(RETOMADAS)
        resposta = f"{ponte} {gancho}{pergunta[0].lower() + pergunta[1:]}"
        # O fio avançou: esta pergunta passa a ser a pendente.
        fio["ultima_pergunta"] = pergunta
        _avancar_nivel(fio)
        return resposta

    # Espelho diferido como retomada (ELIZA-escuta sobre a memória curta)
    if resumo:
        espejo = _gerar_espejo_seguro(resumo[-1], estado, None,
                                      {"dominante": fio.get("emocao")})
        if espejo and espejo != fio.get("ultima_pergunta"):
            ponte = random.choice(RETOMADAS)
            fio["ultima_pergunta"] = espejo
            return f"{ponte} {espejo}"

    return None


def encerrar_fio_se_despedida(estado: dict, mensagem: str) -> None:
    """Limpa o fio emocional quando o utilizador encerra o tema."""
    m = normalizar_texto(mensagem)
    if any(e in m for e in ENCERRAMENTOS):
        fio = estado.get("fio")
        if fio:
            fio["emocao"] = None
            fio["nivel"] = 0
