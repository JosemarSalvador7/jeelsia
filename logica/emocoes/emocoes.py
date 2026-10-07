"""Deteção de emoções e geração de respostas empáticas.

Este módulo contém funções puras (sem estado) extraídas da classe Jeelsia:
- detectar_emocao: analisa um texto e devolve as pontuações por emoção.
- responder_com_empatia: escolhe uma resposta empática conforme a emoção dominante.
"""

import random
import re

# ----------------------------------------------------------------------
# Negativas — corrigem o caso "hoje o dia não correu bem", em que a
# palavra "bem" dava pontuação de alegria 100% e a assistente respondia
# "Essa alegria é linda!" a alguém claramente triste.
# ----------------------------------------------------------------------
NEGATIVAS = [
    "não", "nao", "nunca", "nem", "sem", "negativo",
    "não correu", "nao correu", "não deu", "nao deu",
    "não foi", "nao foi", "não está", "nao esta",
]

# Expressões idiomáticas negativas (pontuam como tristeza, não alegria)
EXPRESSES_NEGATIVAS = [
    "não correu bem", "nao correu bem",
    "não foi bom", "nao foi bom",
    "dia ruim", "dia mau", "mau dia", "mal o dia", "dia mal",
    "correu mal", "foi mal", "tá difícil", "ta dificil",
    "não estou bem", "nao estou bem", "não me sinto bem",
    "sem sorte", "para baixo", "pra baixo",
]

# Marcadores de primeira pessoa (utilizador a falar de si → empatia tem prioridade)
PRIMEIRA_PESSOA = ["estou", "to ", "tou", "me sinto", "sinto-me", "sentir-me", "estava", "fiquei"]

# Palavras-chave por emoção
PALAVRAS_TRISTEZA = [
    "triste", "chateado", "mal", "deprimido", "desanimado", "frustrado",
    "saudade", "chorar", "sofrendo", "pior", "difícil", "cansado",
    "esgotado", "desiludido", "melancólico", "abatido",
]
PALAVRAS_ALEGRIA = [
    "feliz", "alegre", "bem", "ótimo", "excelente", "maravilhoso", "incrível",
    "animado", "contente", "radiante", "top", "perfeito", "bom", "alegria",
    "sorriso", "felicidade", "realizado",
]
PALAVRAS_RAIVA = [
    "raiva", "bravo", "irritado", "nervoso", "pistola", "furioso",
    "estressado", "ódio", "puto", "injusto", "revoltado", "indignado",
    "aborrecido", "enfurecido",
]
PALAVRAS_MEDO = [
    "medo", "preocupado", "ansioso", "inseguro", "receio", "temeroso",
    "apreensivo", "nervoso", "angustiado", "aflito", "assustado", "com medo",
]
PALAVRAS_SURPRESA = [
    "uau", "nossa", "caramba", "que legal", "incrível", "sensacional",
    "fantástico", "surpresa", "nunca", "impossível", "inacreditável",
    "espantado", "pasmo",
]

RESPOSTAS_EMPATICAS = {
    "tristeza": [
        "Percebo que estás a sentir-te triste. Queres conversar sobre isso?",
        "Sinto muito que estejas triste. Às vezes partilhar ajuda. O que está a acontecer?",
        "Entendo que estejas a passar por um momento difícil. Podes contar comigo para desabafar.",
        "A tristeza faz parte da vida, mas não precisas de a carregar sozinho. Queres falar sobre o que te preocupa?",
        "Percebo a tua tristeza. Lembra-te que também há dias bons a caminho. Queres conversar?",
        "Ah, sinto muito. Estou aqui para te ouvir, sempre que precisares desabafar.",
    ],
    "alegria": [
        "Que bom ver-te tão feliz! Conta-me o que te deixou assim tão radiante.",
        "A tua alegria é contagiante! O que está a acontecer de tão bom?",
        "Fico muito feliz por ti! Partilha essa energia positiva comigo.",
        "Uau, que energia boa! É tão bom ver alguém tão feliz. Conta-me mais!",
        "Que maravilha! Ver-te assim alegre faz o meu dia melhor também!",
        "Essa alegria é linda! O que te deixou tão radiante hoje?",
    ],
    "raiva": [
        "Entendo que estejas irritado. Respira fundo e, quando quiseres, podes contar-me o que aconteceu.",
        "Às vezes a raiva é justa, mas precisamos de processá-la. Queres desabafar?",
        "Percebo a tua frustração. Vamos respirar juntos e, se quiseres, conversar sobre isso.",
        "É normal sentir raiva às vezes. Estou aqui para ouvir e ajudar se puder.",
        "Entendo que estejas chateado. Quando te sentires pronto, podes contar-me tudo.",
        "A raiva é uma emoção válida. Queres falar sobre o que te deixou assim?",
    ],
    "medo": [
        "Entendo que possas estar com medo ou preocupado. Queres partilhar o que te deixa assim?",
        "O medo é uma emoção natural. Estou aqui para te ouvir e, juntos, podemos pensar sobre isso.",
        "Percebo a tua ansiedade. Respira comigo e, quando estiveres pronto, podes falar sobre isso.",
        "Não precisas de enfrentar os teus medos sozinho. Estou aqui para te apoiar.",
        "Sei que o medo pode ser paralisante. Queres conversar sobre o que te preocupa?",
        "É normal sentir medo. Estou aqui para te ajudar a enfrentá-lo, se quiseres.",
    ],
    "surpresa": [
        "Uau, parece que algo te surpreendeu! Conta-me o que aconteceu!",
        "Percebo a tua surpresa! São esses momentos que tornam a vida interessante.",
        "Que reação incrível! Partilha essa surpresa comigo.",
        "Também fico surpresa quando algo me tira do eixo. Conta-me tudo!",
        "Adoro ver essa surpresa! O que foi que te deixou assim tão espantado?",
        "Essa surpresa é contagiante! Partilha comigo o que aconteceu!",
    ],
    "neutro": None,
}


# Respostas empáticas contextualmente melhores quando o utilizador fala
# de um momento/dia ("hoje o dia não correu bem") em vez de uma emoção
# rotulada explicitamente.
RESPOSTAS_MOMENTO_DIFICIL = [
    "Sinto muito que o dia não tenha corrido como querias. Queres contar-me o que aconteceu?",
    "Às vezes os dias simplesmente não colaboram. Estou aqui — queres desabafar?",
    "Parece que foi um dia pesado. O que foi a parte mais difícil para ti?",
    "Sinto muito. Quer falar sobre isso ou preferes distrair-te com outro assunto?",
]


def _tem_negacao(texto_lower: str) -> bool:
    return any(n in texto_lower for n in NEGATIVAS)


def _fala_de_si(texto_lower: str) -> bool:
    """True quando o utilizador fala dos próprios sentimentos ('estou mal')."""
    palavras = re.split(r"\W+", texto_lower)
    if any(p in PRIMEIRA_PESSOA for p in palavras):
        return True
    return texto_lower.startswith(("to ", "tou ", "estou ", "estava ", "me sinto", "sinto-me"))


def _pontuar(texto_lower: str, palavras: list) -> int:
    """Conta ocorrências com fronteira de palavra (evita 'mal' dentro de 'amanhã")."""
    pontos = 0
    for p in palavras:
        if re.search(rf"(?<!\w){re.escape(p)}(?!\w)", texto_lower):
            pontos += 1
    return pontos


def detectar_emocao(texto: str) -> dict:
    """Detecta emoções no texto do usuário.

    Devolve um dicionário com percentagens por emoção e a chave
    ``dominante`` com a emoção mais forte detetada.

    Melhorias de fluidez conversacional:
    - Negativas anulam a alegria ("não correu bem" ≠ feliz);
    - Expressões idiomáticas negativas pontuam como tristeza;
    - Palavras com fronteira de palavra (menos falsos positivos).
    """
    emocao = {
        "tristeza": 0,
        "alegria": 0,
        "raiva": 0,
        "medo": 0,
        "surpresa": 0,
        "neutro": 0,
    }

    texto_lower = texto.lower()

    emocao["tristeza"] = _pontuar(texto_lower, PALAVRAS_TRISTEZA)
    emocao["alegria"] = _pontuar(texto_lower, PALAVRAS_ALEGRIA)
    emocao["raiva"] = _pontuar(texto_lower, PALAVRAS_RAIVA)
    emocao["medo"] = _pontuar(texto_lower, PALAVRAS_MEDO)
    emocao["surpresa"] = _pontuar(texto_lower, PALAVRAS_SURPRESA)

    # Expressões idiomáticas negativas → reforço direto de tristeza
    tem_negativa_idiomática = False
    for exp in EXPRESSES_NEGATIVAS:
        if exp in texto_lower:
            tem_negativa_idiomática = True
            break

    # REGRA DE OURO: negação anula a pontuação de alegria.
    # "o dia não correu bem" deixa de ser lido como felicidade.
    if _tem_negacao(texto_lower):
        emocao["alegria"] = 0
        if tem_negativa_idiomática:
            emocao["tristeza"] += 1

    # Se nenhuma emoção detectada
    if sum(emocao.values()) == 0:
        emocao["neutro"] = 1

    # Normalizar para percentuais
    total = sum(emocao.values())
    for key in emocao:
        emocao[key] = (emocao[key] / total) * 100 if total > 0 else 0

    # Encontrar emoção dominante
    emocao["dominante"] = max(emocao, key=lambda k: emocao[k])

    # Metadados úteis para o fluxo de decisão (main/comunicacao)
    emocao["_brutos"] = {k: v for k, v in emocao.items() if k not in ("dominante", "_brutos", "_negado")}
    emocao["_negado"] = _tem_negacao(texto_lower)
    emocao["_primeira_pessoa"] = _fala_de_si(texto_lower)

    return emocao


def deve_priorizar_empatia(emocao: dict, mensagem: str) -> bool:
    """Decide se a empatia deve ter prioridade sobre padrões/intenções.

    Regras para um fluxo natural:
    - Emoção negativa (tristeza/raiva/medo) + utilizador a falar de si
      → SEMPRE empatia primeiro (mesmo que um padrão tipo "estado" ou
      "agradecimento" também coincida — ex.: "estou mal, obrigado pela ajuda");
    - Alegria só ganha prioridade sem negação no texto.
    """
    dominante = emocao.get("dominante", "neutro")
    if dominante == "neutro":
        return False
    if emocao.get(dominante, 0) < 40:
        return False

    if dominante in ("tristeza", "raiva", "medo"):
        return True  # desabafo explícito — nunca deve cair em respostas genéricas

    if dominante == "alegria":
        return not emocao.get("_negado", False)

    return True


def responder_com_empatia(
    emocao: dict, mensagem: str, estado: dict | None = None
) -> str | None:
    """Gera resposta empática com base na emoção dominante.

    Só responde se a emoção for forte (>=40%) e não for neutra.
    Usa memória emocional (``estado['ultima_emocao']``) para:
    - evitar repetir exatamente a mesma frase empática;
    - dar continuidade ao desabafo em vez de recomeçar ("Entendo…").
    """
    dominante = emocao.get("dominante", "neutro")

    if dominante == "neutro" or emocao.get(dominante, 0) < 40:
        return None

    respostas = RESPOSTAS_EMPATICAS.get(dominante)
    if not respostas:
        return None

    # Desabafo sobre o dia/momento sem rótulo emocional explícito
    texto_lower = mensagem.lower()
    if dominante == "tristeza" and not _pontuar(texto_lower, PALAVRAS_TRISTEZA):
        respostas = RESPOSTAS_MOMENTO_DIFICIL

    # Memória emocional: não repetir a última frase nem a anterior
    historico = (estado or {}).get("historico_empaticas", {})
    ja_usadas = set(historico.get(dominante, []))
    candidatas = [r for r in respostas if r not in ja_usadas] or list(respostas)
    escolha = random.choice(candidatas)

    # Continuidade: se a emoção triste se repete entre turnos, emendar
    ultima_emocao = (estado or {}).get("ultima_emocao")
    if (
        estado is not None
        and dominante == "tristeza"
        and ultima_emocao == "tristeza"
        and not escolha.rstrip().endswith("?")
    ):
        continuacoes = [
            "Entendo… e agradeço por continuares a confiar em mim.",
            "Percebo, e estou aqui contigo, sem pressa.",
            "Notei que ainda é um tema pesado — vamos com calma.",
        ]
        escolha = f"{random.choice(continuacoes)} {escolha}"

    if estado is not None:
        hist = estado.setdefault("historico_empaticas", {})
        fila = hist.setdefault(dominante, [])
        fila.append(escolha)
        del fila[:-3]  # guarda as últimas 3 por emoção
        estado["ultima_emocao"] = dominante

    return escolha
