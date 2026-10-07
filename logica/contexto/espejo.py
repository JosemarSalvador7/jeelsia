"""Espelhamento empático ao estilo ELIZA — a camada psicológica da conversa.

A estrutura da Jeelsia (intenções, base de conhecimento, perfil SQLite,
fio condutor) diz *o que* responder; este módulo acrescenta o modo
*como* da ELIZA: devolver ao utilizador as suas próprias palavras em
perguntas abertas, que é o recurso que fazia a ELIZA parecer "ouvir".

Diferenças conscientes em relação à ELIZA original:
- O espelho só entra quando há conteúdo para espelhar (verbo + complemento
  com >= 3 palavras); caso contrário a Jeelsia mantém as suas perguntas
  progressivas, que são mais úteis;
- As reflexões usam ``REFLECTIONS`` já existente (eu->você, meu->seu...)
  mas aplicadas ao *conteúdo* extraído da mensagem, não à resposta da IA;
- Nada aqui gera respostas fixas: todas as funções devolvem peças que
  ``main.responder()`` combina com empatia/perguntas do fio.

Funções públicas:
- ``extrair_conteudo_espelhavel``: núcleo declarativo da frase ("que o
  trabalho está a pesar-te");
- ``gerar_espejo``: pergunta aberta espelhada, contextualizada pelo perfil
  (profissão/nome/gostos) quando disponível;
- ``aplicar_espejo``: funde o espelho com uma resposta já gerada, sem
  duplicar perguntas.
"""

from __future__ import annotations

import random
import re

from logica.utils.texto import normalizar_texto

from .contexto import REFLECTIONS, STOPWORDS

# ----------------------------------------------------------------------
# 1. Extração do conteúdo espelhável
# ----------------------------------------------------------------------

# Verbos de estado/ação que anunciam conteúdo pessoal. A ELIZA clássica
# operava sobre "I am X" / "I feel X"; em português: "estou X",
# "sinto-me X", "quero X", "preciso X", "acho que X"...
VERBOS_CONTEUDO = [
    r"sinto[- ]?me", r"sentir[- ]?me", r"sinto\s+que", r"estou", r"tou", r"fiquei",
    r"estava", r"tenho", r"quero", r"queria", r"desejo",
    r"preciso", r"precisava", r"acho\s+que", r"penso\s+que", r"acredito\s+que",
    r"espero\s+que", r"gosto\s+de", r"adoro", r"odeio", r"nao\s+suporto",
    r"venho", r"andei", r"andai",
]

_RE_VERBO = re.compile(
    r"\b(?:" + "|".join(VERBOS_CONTEUDO) + r")\s+(?P<comp>[^.!?]+)",
    re.IGNORECASE,
)

# Estruturas "X esta a Y" (ex.: "o trabalho está a pesar") que o verbo
# auxiliar isolado não captura porque o complemento começa antes dele.
_RE_ESTA_A = re.compile(
    r"\b(?P<suj>[\w'-]+(?:\s+[\w'-]+){0,3}?)\s+"
    r"(?:esta|estao|andes|anda|andam|vem|veem)\s+a\s+(?P<inf>[\w'-]+)",
    re.IGNORECASE,
)

# Palavras que nunca devem iniciar um conteúdo espelhado (artigos,
# pronomes soltos, advérbios vazios).
_INICIO_INVALIDO = set(STOPWORDS) | {
    "muito", "mesmo", "ainda", "já", "ja", "também", "tambem", "só", "so",
    "porque", "poque", "quando", "como", "assim", "desta", "disso", "depois",
}


def _refletir_palavra(palavra: str) -> str:
    """Aplica REFLECTIONS a uma palavra, preservando maiúsculas iniciais."""
    chave = re.sub(r"[^\w'-]", "", palavra).lower()
    if chave in REFLECTIONS:
        refletida = REFLECTIONS[chave]
        if palavra[0].isupper():
            refletida = refletida.capitalize()
        return palavra.replace(chave, refletida) if chave != palavra.lower() else refletida
    return palavra


def _refletir_texto(texto: str) -> str:
    """Reflete todos os pronomes/verbos de 1.ª pessoa num trecho."""
    tokens = texto.split(" ")
    return " ".join(_refletir_palavra(t) for t in tokens)


def _preparar(mensagem: str) -> str:
    """Normalização própria do espelho.

    ``normalizar_texto`` remove todos os sinais de pontuação, incluindo o
    hífen dos mesoclíticos ("pesar-me" -> "pesarme"), o que quebrava os
    padrões de reflexão. Aqui preservamos hífens e apóstrofos e mantemos
    as vogais acentuadas (as regex usam [\\w], que já cobre acentos).
    """
    if not mensagem:
        return ""
    texto = re.sub(r"[^A-Za-zÀ-ÿ0-9\s'-]", "", mensagem)
    texto = re.sub(r"\s{2,}", " ", texto)
    return texto.lower().strip()


def extrair_conteudo_espelhavel(mensagem: str) -> str | None:
    """Devolve o núcleo declarativo da mensagem, já refletido ("seu/está").

    Ex.: "o trabalho está a pesar-me" -> "que o trabalho está a pesar-te"
         "estou muito cansada"         -> "que muito cansada ultimamente"

    Regras anti-ruído (a ELIZA espelhava tudo e por isso soava vazia):
    - exige verbo de conteúdo + complemento com >= 3 palavras reais
      (sem stopwords) — frases vagas como "estou assim" não espelham;
    - corta o complemento na primeira vírgula longa ou em 14 palavras.
    """
    m = _preparar(mensagem)
    if not m:
        return None

    # PRIMEIRO a estrutura "X está a Y" (sujeito + perifrástica), porque o
    # verbo auxiliar isolado não captura frases cujo conteúdo começa antes
    # dele ("o trabalho está a pesar"). Depois, verbos de conteúdo.
    aux = _RE_ESTA_A.search(m)
    match = _RE_VERBO.search(m)
    comp: str | None
    prefixo_que = True
    if aux and (not match or aux.start() < match.start()):
        comp = f"{aux.group('suj').strip()} está a {aux.group('inf')}"
        palavras_aux = comp.split()
        # remove artigo inicial do sujeito ("o trabalho..." -> "trabalho...")
        while palavras_aux and palavras_aux[0].lower() in STOPWORDS:
            palavras_aux = palavras_aux[1:]
        comp = " ".join(palavras_aux)
    elif match:
        verbo = m[max(0, match.start()):match.start("comp")].strip()
        comp = match.group("comp").strip()
        # Verbos que já introduzem complemento com conjunção ("acho que X",
        # "gosto de X") não levem "que" extra — o espelho usa o próprio
        # trecho ("que eu acho que...", "de que gostas..." soariam mal;
        # "que pensas que..." é aceitável, mas "que adoras" não).
        if verbo in ("gosto de", "gosta de", "adoro", "odeio",
                     "nao suporto", "não suporto"):
            prefixo_que = False
    else:
        return None

    # Remove pontuação final e clausulas coordenadas muito longas
    comp = comp.split(",")[0] if len(comp.split(",")) <= 2 else ",".join(
        comp.split(",")[:2])
    palavras = comp.split()
    reais = [p for p in palavras
             if re.sub(r"[^\w'-]", "", p).lower() not in _INICIO_INVALIDO
             and len(p) > 2]
    if len(reais) < 2:
        return None

    comp = " ".join(palavras[:14])
    refletido = _refletir_texto(comp)
    # Mesoclíticos em 1.ª pessoa: "pesar-me" -> "pesar-te",
    # "entender-me" -> "entender-te" (ELIZA clássica fazia o mesmo com
    # "myself" -> "yourself").
    refletido = re.sub(r"-me\b", "-te", refletido)
    # "que ..." soa mais natural em perguntas indiretas
    if prefixo_que and not refletido.startswith(
            ("que ", "se ", "como ", "quando ")):
        refletido = f"que {refletido}"
    return refletido


# ----------------------------------------------------------------------
# 2. Perguntas espelhadas (abertas, estilo ELIZA, mas contextualizadas)
# ----------------------------------------------------------------------

_ESPEJO_BASE = [
    "Conta-me mais {c}.",
    "Como assim, {c}?",
    "Há quanto tempo {c}?",
    "E o que {c} significa para ti, concretamente?",
    "Faz sentido — {c}... queres explorar isso comigo?",
]

# Espelhos específicos por categoria emocional (mais precisos que o
# espelho genérico quando já sabemos a emoção dominante).
_ESPEJO_POR_EMOCAO = {
    "tristeza": [
        "Sinto muito por {c}. O que {c} te fez sentir mais?",
        "{c}... e houve algo que tenhas tentado para aliviar isso?",
    ],
    "raiva": [
        "Entendo — {c}. Foi a gota de água ou vinha a acumular?",
        "{c} dá mesmo que raiva. O que gostarias que tivesse acontecido?",
    ],
    "medo": [
        "{c}... o que receias que possa acontecer se nada mudar?",
        "Compreendo o incómodo de {c}. Qual seria o teu cenário seguro?",
    ],
    "alegria": [
        "Adorei saber {c}! Como aconteceu?",
        "{c} merece festa — com quem partilhaste?",
    ],
}

# Pergunta-padrão da ELIZA adaptada: quando não há conteúdo mas há
# sentimento vago ("não sei", "talvez"), devolver a dúvida ao utilizador.
_ESPEJO_VAGO = [
    "Parece que ainda estás a pensar nisso. O que te ocorre primeiro quando pensas no assunto?",
    "Está bem — e se tiveres de escolher UMA coisa a dizer sobre isto, qual seria?",
]


def gerar_espejo(mensagem: str, estado: dict | None = None,
                 ctx_perfil: dict | None = None,
                 emocao: dict | None = None) -> str | None:
    """Gera uma pergunta espelhada sobre a mensagem, ou None.

    Combina três fontes, por ordem de qualidade:
    1. Espelho específico da emoção dominante (se houver conteúdo);
    2. Espelho base sobre o conteúdo refletido;
    3. Espelho vago ELIZA-style quando o turno tem marcador de indecisão
       ("não sei", "talvez") mas sem conteúdo claro.

    O perfil (``ctx_perfil``) personaliza: mencionar a profissão conhecida
    transforma "o trabalho" em "o trabalho no marketing", por exemplo.
    """
    conteudo = extrair_conteudo_espelhavel(mensagem)
    dom = (emocao or {}).get("dominante")

    if not conteudo:
        # Frases com cópula sem predicado ("é que loucura") ainda têm
        # núcleo aproveitável — espelho vago estilo ELIZA.
        nucleo = re.search(
            r"(?:\b[eé]que?\s+|\b[eé]\s+|\bque\s+)([\wà-üáéíóúãõâêç'-]{4,})",
            m_preparado := _preparar(mensagem))
        if nucleo and len(m_preparado.split()) <= 6:
            conteudo = nucleo.group(1)

    if conteudo:
        pool = _ESPEJO_POR_EMOCAO.get(dom, []) or _ESPEJO_BASE
        molde = random.choice(list(pool) + _ESPEJO_BASE)
        espejo = molde.format(c=conteudo.rstrip(".?!"))
        # Normaliza pontuação dupla ("...mais.??" → "...mais?")
        espejo = re.sub(r"[.!?]+(\s*\?)", r"\1", espejo.strip())
        if not espejo.endswith("?"):
            espejo += "?"
        return espejo

    # Marcadores de indecisão: a mensagem pode ter pontuação/acentos que
    # _preparar preserva, por isso testamos sobre o texto já preparado.
    m = _preparar(mensagem)
    if any(e in m for e in ("não sei", "nao sei", "talvez", "não faço ideia",
                            "nao faco ideia", "sei lá", "sei la")):
        ponte = random.choice(_ESPEJO_VAGO)
        nome = (ctx_perfil or {}).get("nome")
        if nome and random.random() < 0.4:
            ponte = ponte.replace(".", f", {nome}.", 1)
        return ponte

    return None


def tem_conteudo_espelhavel(mensagem: str) -> bool:
    """True se a mensagem tem conteúdo pessoal aproveitável pelo espelho."""
    return extrair_conteudo_espelhavel(mensagem) is not None


# ----------------------------------------------------------------------
# 3. Fusão do espelho com a resposta já composta
# ----------------------------------------------------------------------

def aplicar_espejo(resposta: str | None, espejo: str | None) -> str | None:
    """Insere o espelho na resposta sem criar dupla de perguntas.

    - Sem resposta: o espelho segue sozinho (turno puramente empático);
    - Resposta termina em "?": substitui a pergunta da IA pela pergunta
      espelhada APENAS quando a pergunta da IA é genérica (pergunta de
      seguimento padrão) — perguntas progressivas específicas do fio têm
      prioridade porque foram desenhadas para o tema;
    - Resposta afirmativa: espelho vai para o fim como convite aberto.
    """
    if not espejo:
        return resposta
    if not resposta:
        return espejo
    corpo = resposta.strip()
    if corpo.endswith("?"):
        # Já há pergunta; só troca se a existente for curta/genérica
        ultima = re.split(r"[.!?]\s+", corpo)[-1]
        generica = len(ultima.split()) <= 7
        if generica:
            anterior = corpo[: corpo.rfind(ultima)].rstrip()
            if anterior:
                return f"{anterior} {espejo}"
            return espejo
        return corpo
    return f"{corpo} {espejo}"


if __name__ == "__main__":  # smoke test manual
    testes = [
        "o trabalho está a pesar-me",
        "estou muito cansada ultimamente",
        "sinto que ninguém me entende",
        "não sei o que fazer",
        "oi",
        "estou assim",
    ]
    for t in testes:
        print(f"{t!r:45} -> {gerar_espejo(t)}")
