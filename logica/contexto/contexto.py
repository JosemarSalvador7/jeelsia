"""Gestão de contexto da conversa e memória de respostas.

Funções extraídas da classe Jeelsia que operam sobre um dicionário de
estado partilhado (``estado``), mantendo o comportamento original:

- extrair_topico: obtém o tópico principal de uma mensagem.
- manter_contexto: atualiza o histórico e deteta continuidade de tópico.
- obter_resposta_unica: evita repetição de respostas recentes.
- aplicar_reflections: inverte pronomes ("eu" -> "você", etc.).

O submódulo ``fio`` acrescenta a capacidade de *conduzir* a conversa:
desenvolver o tema ativo, retomar desabafos pendentes e reconhecer
respostas elípticas ("sim"/"pois") sem perder o contexto entre turnos.
"""

import random

from .fio import (
    atualizar_fio,
    encerrar_fio_se_despedida,
    proxima_pergunta_progressiva,
    responder_elipse,
    retomar_fio,
)

# Palavras comuns removidas na extração de tópicos
STOPWORDS = [
    "o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "da", "do",
    "das", "dos", "para", "com", "por", "em", "na", "no", "que", "se",
    "é", "são", "está", "estão",
]

# Reflexões para inverter pronomes (espelhamento)
REFLECTIONS = {
    "eu": "você",
    "meu": "seu",
    "minha": "sua",
    "me": "te",
    "estou": "está",
    "sinto": "sente",
    "quero": "quer",
    "preciso": "precisa",
    "vou": "vai",
    "posso": "pode",
    "tenho": "tem",
    "estava": "estava",
    "fui": "foi",
    "faz": "faz",
    "sei": "sabe",
    "acho": "acha",
    "penso": "pensa",
    "gosto": "gosta",
    "adoro": "adora",
    "amo": "ama",
    "queria": "queria",
    "precisava": "precisava",
}


def criar_estado() -> dict:
    """Cria o estado inicial de contexto/memória da assistente."""
    return {
        "historico_conversa": [],
        "max_historico": 10,
        "ultimas_respostas": [],
        "max_historico_respostas": 5,
        "ultimo_topico": None,
        # Campos de fluidez conversacional (logica.comunicacao)
        "ultima_pergunta_seguimento": None,
        "turnos": 0,
        # Memória emocional (logica.emocoes): última emoção dominante e
        # últimas frases empáticas usadas por emoção (evita repetição e
        # permite continuidade do desabafo entre turnos).
        "ultima_emocao": None,
        "historico_empaticas": {},
        # Fio condutor da conversa (logica.contexto.fio): mantém a linha
        # de conversa ativa entre turnos para desenvolver o tema sem
        # perder o contexto.
        "fio": {"emocao": None, "nivel": 0,
                "ultima_pergunta": None, "resumo": []},
    }


def extrair_topico(mensagem: str) -> str | None:
    """Extrai tópico principal da mensagem.

    Remove palavras comuns (stopwords) e mantém substantivos principais.
    """
    palavras = mensagem.lower().split()
    topicos = [
        p for p in palavras if p not in STOPWORDS and len(p) > 3
    ]
    return topicos[0] if topicos else None


def manter_contexto(estado: dict, mensagem: str) -> bool:
    """Mantém contexto da conversa, atualizando o histórico em ``estado``.

    Devolve True se a mensagem continua o tópico anterior, False caso contrário.
    """
    historico = estado["historico_conversa"]

    # Se não há histórico, adiciona
    if not historico:
        historico.append(mensagem)
        return False

    # Verifica se a mensagem se relaciona com o último tópico
    topico_atual = extrair_topico(mensagem)
    ultimo_topico = extrair_topico(historico[-1]) if historico else None

    if topico_atual and ultimo_topico and topico_atual == ultimo_topico:
        return True

    # Adiciona ao histórico
    historico.append(mensagem)
    if len(historico) > estado["max_historico"]:
        historico.pop(0)
    return False


def obter_resposta_unica(estado: dict, resposta: str) -> str:
    """Garante que a resposta não seja repetida recentemente.

    A janela de comparação é curta (4): o suficiente para evitar eco
    imediato, sem sufocar a variação natural quando o assistente usa
    mecânicas de fio (elipses/retomadas) que já sorteiam moldes.
    """
    ultimas = estado["ultimas_respostas"]

    if resposta in ultimas:
        # Tenta variação ou resposta alternativa
        variacoes = [
            f"{resposta} E reitero: estou aqui.",
            f"Como dizia: {resposta}",
            f"Retomando — {resposta[0].lower() + resposta[1:]}",
            f"Insisto no que te disse: {resposta}",
        ]
        return random.choice(variacoes)
    else:
        ultimas.append(resposta)
        if len(ultimas) > min(estado["max_historico_respostas"], 4):
            ultimas.pop(0)
        return resposta


def aplicar_reflections(texto: str) -> str:
    """Aplica reflexões para inverter pronomes, preservando capitalização."""
    palavras = texto.split()
    for i, palavra in enumerate(palavras):
        palavra_limpa = palavra.lower().strip(".,!?")
        if palavra_limpa in REFLECTIONS:
            # Preservar capitalização
            if palavra[0].isupper():
                palavras[i] = REFLECTIONS[palavra_limpa].capitalize()
            else:
                palavras[i] = REFLECTIONS[palavra_limpa]
    return " ".join(palavras)
