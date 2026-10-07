"""Módulo de gestão de contexto da conversa."""

from .contexto import (
    criar_estado,
    extrair_topico,
    manter_contexto,
    obter_resposta_unica,
    aplicar_reflections,
)

__all__ = [
    "criar_estado",
    "extrair_topico",
    "manter_contexto",
    "obter_resposta_unica",
    "aplicar_reflections",
]
