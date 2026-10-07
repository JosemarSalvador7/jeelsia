"""Funções de fluidez conversacional (comunicação natural).

Objetivo: transformar respostas "de comando" numa conversa fluida, com:
1. Transições suaves — a resposta começa com uma ponte contextual em vez
   de despejar informação "a seco".
2. Perguntas de seguimento — quando faz sentido, a resposta termina com
   uma pergunta que convida o utilizador a continuar (turn-taking).
3. Variações para palavras curtas ("sim"/"não"/"talvez") dependentes do
   tópico anterior, evitando repetição mecânica.
4. Reconhecimento/feedback imediato para mensagens longas ou elaboradas.
5. Despedidas e resumo final baseados no histórico real da conversa.

Todas as funções são puras em relação ao estado: recebem o ``estado``
(dicionário criado por ``logica.contexto.criar_estado``) como argumento.
"""

import random

from logica.contexto import extrair_topico

# ----------------------------------------------------------------------
# 1. Transições (ponte antes da resposta principal)
# ----------------------------------------------------------------------

TRANSICOES_GERAIS = [
    "Boa pergunta!",
    "Deixa-me pensar...",
    "Claro, vamos a isso!",
    "Gosto desse tema!",
    "Entendi!",
    "Certo!",
]

TRANSICOES_POR_TOPICO = {
    "tristeza": [
        "Compreendo o que sentes.",
        "Sinto muito por isso.",
        "Entendo, e quero ajudar.",
    ],
    "alegria": [
        "Adorei saber disso!",
        "Que notícia boa!",
        "Isso merece celebração!",
    ],
    "curiosidade": [
        "Interessante quereres saber isso!",
        "Ótimo tema para explorar!",
        "Vamos descobrir juntos!",
    ],
    "decisao": [
        "Pensei um pouco sobre isso.",
        "Vou dar-te a minha opinião sincera.",
        "Refleti na tua questão.",
    ],
}

# Encadeamentos que ligam a resposta anterior ao novo turno
CONTINUACOES = [
    "Relativamente a isso,",
    "A propósito do que falávamos,",
    "Retomando o teu ponto,",
    "Sobre o que mencionaste,",
    "Seguindo essa ideia,",
]

# ----------------------------------------------------------------------
# 2. Perguntas de seguimento (mantêm a conversa viva)
# ----------------------------------------------------------------------

PERGUNTAS_SEGUIMENTO_GERAIS = [
    "Faz sentido para ti?",
    "Queres que eu aprofunde algum ponto?",
    "Posso ajudar-te com mais alguma coisa sobre isto?",
    "O que pensas sobre isso?",
    "Como te fez sentir esta resposta?",
    "Há algo mais que gostarias de saber?",
]

PERGUNTAS_SEGUIMENTO_POR_CONTEXTO = {
    "conselho": [
        "Achas que poderias tentar isso esta semana?",
        "Queres que pensemos juntos num plano mais concreto?",
        "Isto parece aplicar-se à tua situação?",
    ],
    "história": [
        "Queres ouvir outra história?",
        "O que achaste do final?",
        "Preferes histórias mais alegres ou mais reflexivas?",
    ],
    # Piadas e elogios são pontos de remate da conversa — não pedem
    # seguimento, sob pena de soar deslocado ("Conheces alguma melhor?"
    # depois de um "obrigado").
    "piada": [],
    "elogio": [],
    "agradecimento": [],
    "conhecimento": [
        "Gostarias de saber mais detalhes sobre este tema?",
        "Queres que relacione isto com outro assunto?",
        "Há algum aspeto específico que te interesse mais?",
    ],
    "emocao": [
        "Queres desabafar um pouco mais?",
        "O que aconteceu para te sentires assim?",
        "Como posso apoiar-te agora?",
    ],
}

# ----------------------------------------------------------------------
# 3. Respostas curtas contextuais (sim / não / talvez)
# ----------------------------------------------------------------------

RESPOSTAS_SIM_COM_TEXTO = [
    "Excelente! Então seguimos em frente com isso. Queres que dê o próximo passo?",
    "Ótimo, fico contente que estejas de acordo! Sobre o que mais gostarias de falar?",
    "Perfeito, estamos na mesma página! Há algo mais em que te possa ajudar?",
    "Boa! Adoro a tua energia. O que exploramos agora?",
    "Fixe! Então avançamos. Tens mais alguma dúvida sobre o assunto?",
]

RESPOSTAS_NAO_COM_TEXTO = [
    "Sem problema, respeito totalmente. Preferes abordar outro assunto?",
    "Tudo bem! Fica registado. Queres que sugira uma alternativa?",
    "Compreendo. Se mudares de ideias, estou cá. Enquanto isso, sobre o que conversamos?",
    "Ok, sem pressão. Gostarias de explorar um tema diferente?",
    "Entendido! E se pudesses mudar um detalhe, o que seria?",
]

RESPOSTAS_TALVEZ_COM_TEXTO = [
    "Faz sentido, nem tudo precisa de resposta imediata. Queres que liste prós e contras?",
    "Também acho que vale a pena ponderar. O que te deixa mais em dúvida?",
    "Sem pressa! Às vezes a melhor decisão amadurece devagar. Quer falar sobre os teus receios?",
    "Entendo a indecisão. Se tiveres de escolher hoje, para onde pende a balança?",
]

# ----------------------------------------------------------------------
# 4. Reconhecimento de mensagens longas/elaboradas
# ----------------------------------------------------------------------

RECONHECIMENTOS = [
    "Nossa, escreveste bastante — deixa-me organizar isso contigo.",
    "Vejo que pensaste muito no assunto. Vamos por partes.",
    "Boa reflexão! Deixa-me responder com calma.",
    "Percebi a tua mensagem completa. Aqui vai a minha resposta:",
]

# ----------------------------------------------------------------------
# 5. Despedidas e resumo final
# ----------------------------------------------------------------------

DESPEDIDAS = [
    "Foi mesmo bom conversar contigo! Volta sempre que quiseres. Até já! 👋",
    "Adorei a nossa conversa. Cuida-te bem e até à próxima!",
    "Já vou, mas fica sabendo: estou sempre aqui quando precisares. Até logo!",
    "Que papo bom! Descansa, diverte-te... e volta quando quiseres. Tchau-tchau!",
]


def _topico_recente(estado: dict) -> str | None:
    """Devolve o tópico da última mensagem do utilizador, se existir."""
    historico = estado.get("historico_conversa") or []
    if not historico:
        return None
    return extrair_topico(historico[-1])


def _tem_contexto(estado: dict) -> bool:
    """True se já houve pelo menos uma troca relevante na conversa."""
    return bool(estado.get("historico_conversa"))


def gerar_transicao(estado: dict, emocao: dict | None = None) -> str:
    """Escolhe uma transição/ponte natural para anteceder a resposta.

    - Usa conectivos de continuidade quando há contexto prévio;
    - Usa transições emocionais quando foi detetada uma emoção forte;
    - Caso contrário, usa uma transição geral aleatória.
    """
    # Emoção dominante acima de limiar → transição empática
    if emocao:
        for nome, chave in (
            ("tristeza", "tristeza"),
            ("alegria", "alegria"),
            ("raiva", "tristeza"),
        ):
            if emocao.get(nome, 0) >= 2 and chave in TRANSICOES_POR_TOPICO:
                return random.choice(TRANSICOES_POR_TOPICO[chave])

    if _tem_contexto(estado) and random.random() < 0.35:
        return random.choice(CONTINUACOES)

    return random.choice(TRANSICOES_GERAIS)


# ----------------------------------------------------------------------
# 6. Detete de intenção por similaridade (ordem determinística)
# ----------------------------------------------------------------------

# Ordem em que as intenções são testadas — substitui a iteração sobre
# dicionário (que dependia da ordem de inserção e produzia casamentos
# inesperados). Intenções pessoais/emocionais vêm antes das gerais.
ORDEM_INTENCOES = [
    "saudacao_despedida",
    "agradecimento",
    "elogio",
    "teamo",
    "sad_state_user",
    "good_state_user",
    "cansado",
    "estado",
    "identidade",
    "criador",
    "idade",
    "origem",
    "piada",
    "conselho",
    "historia",
    "data",
    "horas",
]


def detectar_intencoes(mensagem: str, listas: dict) -> list[tuple[str, int]]:
    """Devolve todas as intenções que casam com a mensagem, ordenadas.

    Percorre ``listas`` (o dicionário de padrões de conversa) de forma
    determinística e devolve pares ``(intenção, score_máximo)`` para
    todas as intenções cujo melhor candidato atinja o threshold.
    Ordena por score decrescente — quem decide a prioridade é o caller.
    """
    from logica.utils.texto import normalizar_texto
    from rapidfuzz import fuzz

    frase = normalizar_texto(mensagem)
    encontrados: list[tuple[str, int]] = []

    for nome, entrada in listas.items():
        chaves = entrada[0] if isinstance(entrada, list) and entrada and isinstance(entrada[0], list) else entrada
        melhor = 0
        for k in chaves:
            try:
                s = max(fuzz.QRatio(frase, k), fuzz.token_sort_ratio(frase, k))
            except Exception:
                continue
            if s > melhor:
                melhor = s
        if melhor >= 90:
            encontrados.append((nome, int(melhor)))

    encontrados.sort(key=lambda x: x[1], reverse=True)
    return encontrados


# ----------------------------------------------------------------------
# Intenções conversacionais "pequenas" (turnos sociais curtos)
# ----------------------------------------------------------------------
# Quando nenhuma variação da lista casa com threshold alto, estas
# intenções ainda merecem uma 2ª chance com score moderado — são os
# turnos sociais que faziam a Jeelsia cair em "não aprendi a lidar
# com isso" ("tudo e com voce", "estou bem e você?").
INTENCOES_SOCIAIS = {
    "saudacao", "estado", "good_state_user", "sad_state_user",
    "agradecimento", "elogio", "despedida",
}


def melhor_score_intencao(frase: str, chaves: list) -> tuple[int, str]:
    """Devolve (score máximo, chave mais parecida) para uma lista de padrões."""
    from rapidfuzz import fuzz

    melhor, melhor_chave = 0, ""
    for k in chaves:
        try:
            s = max(fuzz.QRatio(frase, k), fuzz.token_sort_ratio(frase, k))
        except Exception:
            continue
        if s > melhor:
            melhor, melhor_chave = int(s), k
    return melhor, melhor_chave


def casar_social_flexivel(
    comando_lower: str, listas: dict, floor: int = 62
) -> tuple[str, str] | None:
    """Casa mensagens sociais pequenas com score moderado.

    Um humano não responde "não entendi" a "e contigo?" — o mínimo de
    elegância é devolvê-la à intenção social mais próxima. Só entra em
    intenções sociais (nunca em factos/conhecimento, onde um casamento
    parcial produziria respostas erradas).
    """
    from logica.utils.texto import normalizar_texto

    frase = normalizar_texto(comando_lower)
    if not frase or len(frase.split()) > 8:
        return None

    melhor_nome, melhor_s = None, 0
    melhor_respostas: list | None = None
    for nome, entrada in listas.items():
        if nome not in INTENCOES_SOCIAIS:
            continue
        if not isinstance(entrada, list) or not entrada:
            continue
        chaves = entrada[0] if isinstance(entrada[0], list) else entrada
        respostas = entrada[1] if (
            isinstance(entrada[0], list) and len(entrada) > 1
            and isinstance(entrada[1], list)) else None
        if not respostas:
            continue
        s, _ = melhor_score_intencao(frase, chaves)
        if s > melhor_s:
            melhor_nome, melhor_s = nome, s
            melhor_respostas = respostas
    if melhor_nome and melhor_s >= floor:
        return melhor_nome, random.choice(melhor_respostas)
    return None


def responder_a_intencao_esperando_resposta(anterior: str | None) -> bool:
    """Heurística simples: a última resposta da IA terminava em pergunta?"""
    return bool(anterior and anterior.rstrip().endswith("?"))


def gerar_pergunta_seguimento(
    estado: dict, tipo_resposta: str | None = None
) -> str | None:
    """Gera uma pergunta de seguimento adequada ao tipo de resposta dada.

    Devolve ``None`` ocasionalmente para não soar interrogativa demais —
    uma conversa natural também tem respostas que simplesmente terminam.
    """
    if random.random() < 0.25:  # 25% das vezes, sem pergunta
        return None

    tipo = (tipo_resposta or "").lower()
    # Tipos que encerram o turno (piada/elogio/agradecimento) não pedem seguimento
    if tipo in {"piada", "elogio", "agradecimento"}:
        return None

    pool = PERGUNTAS_SEGUIMENTO_POR_CONTEXTO.get(tipo)
    if pool is None:
        pool = PERGUNTAS_SEGUIMENTO_GERAIS
    elif not pool:
        return None

    pergunta = random.choice(pool)

    # Evitar repetir a mesma pergunta duas vezes seguidas
    ultima = estado.get("ultima_pergunta_seguimento")
    if pergunta == ultima:
        pergunta = random.choice(PERGUNTAS_SEGUIMENTO_GERAIS)

    estado["ultima_pergunta_seguimento"] = pergunta
    return pergunta


def compor_resposta(
    resposta: str,
    estado: dict,
    tipo_resposta: str | None = None,
    adicionar_transicao: bool = True,
    adicionar_seguimento: bool = True,
) -> str:
    """Compõe a resposta final com transição + corpo + pergunta de seguimento.

    Regras de bom senso para não poluir:
    - Não adiciona transição se a resposta já é curta/conversacional
      (pergunta empática ou saudação);
    - Não encadeia mais de um elemento extra por resposta;
    - Nunca transforma despedidas/comandos de saída em perguntas.
    """
    if not resposta:
        return resposta

    texto = resposta.strip()

    # Respostas que já terminam em pergunta não precisam de seguimento
    ja_pergunta = texto.endswith("?")

    # Sem transição nem seguimento para textos muito curtos
    if len(texto.split()) <= 4:
        return texto

    partes = []

    if adicionar_transicao and not ja_pergunta and random.random() < 0.5:
        partes.append(gerar_transicao(estado))

    corpo = texto
    if partes:
        corpo = corpo[0].lower() + corpo[1:] if corpo[0].isupper() else corpo

    resultado = " ".join(partes + [corpo]) if partes else corpo

    if adicionar_seguimento and not ja_pergunta:
        pergunta = gerar_pergunta_seguimento(estado, tipo_resposta)
        if pergunta:
            resultado = f"{resultado} {pergunta}"

    return resultado


def gerar_resposta_curta(mensagem: str, estado: dict) -> str | None:
    """Responde a palavras curtas com variação dependente do contexto.

    Substitui as listas fixas antigas por reformulações que referem o
    tópico anterior, criando a sensação de continuidade conversacional.
    """
    m = mensagem.lower().strip()

    sim = {"sim", "s", "si", "yeah", "yep", "claro", "exato",
           "exatamente", "certeza", "ok", "okei", "blz", "beleza", "boa"}
    nao = {"não", "nao", "n", "nah", "nem", "nops", "nunca", "negativo"}
    talvez = {"talvez", "quem sabe", "pode ser", "vamos ver",
              "não sei", "nao sei", "dúvida", "duvida"}

    topico = _topico_recente(estado)

    if m in sim:
        if topico and random.random() < 0.6:
            return (
                f"Que bom que sim! Então voltamos a '{topico}': "
                f"{random.choice(['queres aprofundar?', 'seguimos?', 'o que mais te interessa nesse tema?'])}"
            )
        return random.choice(RESPOSTAS_SIM_COM_TEXTO)

    if m in nao:
        if topico and random.random() < 0.6:
            return (
                f"Tudo bem, deixamos '{topico}' para depois. "
                f"{random.choice(['Preferes mudar de assunto?', 'Sobre o que mais gostavas de falar?', 'Queres que sugira um tema novo?'])}"
            )
        return random.choice(RESPOSTAS_NAO_COM_TEXTO)

    if m in talvez:
        return random.choice(RESPOSTAS_TALVEZ_COM_TEXTO)

    return None


def gerar_reconhecimento(mensagem: str) -> str | None:
    """Feedback curto para mensagens longas (mostra que a IA 'ouviu')."""
    if len(mensagem.split()) >= 25:
        return random.choice(RECONHECIMENTOS)
    return None


def gerar_despedida(estado: dict | None = None) -> str:
    """Despedida calorosa, com referência ao tempo/tópico da conversa."""
    base = random.choice(DESPEDIDAS)
    if estado:
        n_turnos = len(estado.get("historico_conversa") or [])
        if n_turnos >= 5:
            base = f"Conversámos durante {n_turnos} temas bons! " + base
    return base


def finalizar_conversa(estado: dict) -> str:
    """Encerra com um mini-resumo dos tópicos abordados + despedida."""
    historico = estado.get("historico_conversa") or []
    topicos = []
    for msg in historico[-5:]:
        t = extrair_topico(msg)
        if t and t not in topicos:
            topicos.append(t)

    if topicos:
        resumo = ", ".join(topicos[:-1]) + (
            f" e {topicos[-1]}" if len(topicos) > 1 else ""
        )
        parte_resumo = f"Falámos sobre {resumo}. "
    else:
        parte_resumo = ""

    return parte_resumo + gerar_despedida(estado)
