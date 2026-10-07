"""Módulo de comunicação: torna as respostas mais naturais e fluidas.

Expondo:
- gerar_transicao: conectivo/ponte para a resposta não começar "a seco".
- gerar_pergunta_seguimento: pergunta contextual no fim da resposta,
  convidando o utilizador a continuar a conversa.
- gerar_resposta_curta: reformulações variadas para "sim"/"não"/"talvez".
- gerar_reconhecimento: feedback imediato ao receber uma mensagem longa.
- gerar_despedida: despedida calorosa quando o utilizador sai.
- finalizar_conversa: encerra com um resumo curto da conversa.
"""

from .fluidez import (
    gerar_transicao,
    gerar_pergunta_seguimento,
    gerar_resposta_curta,
    gerar_reconhecimento,
    gerar_despedida,
    finalizar_conversa,
)

__all__ = [
    "gerar_transicao",
    "gerar_pergunta_seguimento",
    "gerar_resposta_curta",
    "gerar_reconhecimento",
    "gerar_despedida",
    "finalizar_conversa",
]
