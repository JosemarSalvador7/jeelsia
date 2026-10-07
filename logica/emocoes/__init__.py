"""Módulo de deteção de emoções e respostas empáticas."""

from .emocoes import (
    detectar_emocao,
    deve_priorizar_empatia,
    responder_com_empatia,
)

__all__ = [
    "detectar_emocao",
    "deve_priorizar_empatia",
    "responder_com_empatia",
]
