"""Deteção de emoções e geração de respostas empáticas.

Este módulo contém funções puras (sem estado) extraídas da classe Jeelsia:
- detectar_emocao: analisa um texto e devolve as pontuações por emoção.
- responder_com_empatia: escolhe uma resposta empática conforme a emoção dominante.
"""

import random

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
        "Percebo que estás a sentir-te triste. Queres conversar sobre isso? Estou aqui para ouvir.",
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


def detectar_emocao(texto: str) -> dict:
    """Detecta emoções no texto do usuário.

    Devolve um dicionário com percentagens por emoção e a chave
    ``dominante`` com a emoção mais forte detetada.
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

    for palavra in PALAVRAS_TRISTEZA:
        if palavra in texto_lower:
            emocao["tristeza"] += 1
    for palavra in PALAVRAS_ALEGRIA:
        if palavra in texto_lower:
            emocao["alegria"] += 1
    for palavra in PALAVRAS_RAIVA:
        if palavra in texto_lower:
            emocao["raiva"] += 1
    for palavra in PALAVRAS_MEDO:
        if palavra in texto_lower:
            emocao["medo"] += 1
    for palavra in PALAVRAS_SURPRESA:
        if palavra in texto_lower:
            emocao["surpresa"] += 1

    # Se nenhuma emoção detectada
    if sum(emocao.values()) == 0:
        emocao["neutro"] = 1

    # Normalizar para percentuais
    total = sum(emocao.values())
    for key in emocao:
        emocao[key] = (emocao[key] / total) * 100 if total > 0 else 0

    # Encontrar emoção dominante
    emocao["dominante"] = max(emocao, key=lambda k: emocao[k])

    return emocao


def responder_com_empatia(emocao: dict, mensagem: str) -> str | None:
    """Gera resposta com base na emoção detectada.

    Só responde com empatia se a emoção dominante for forte (>40%).
    Caso contrário devolve ``None``.
    """
    dominante = emocao["dominante"]

    if emocao[dominante] < 40:
        return None

    respostas = RESPOSTAS_EMPATICAS.get(dominante)
    if respostas:
        return random.choice(respostas)
    return None
