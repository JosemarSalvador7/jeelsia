"""Pacote de perfil do utilizador — memória persistente entre sessões.

Exposição pública:

- ``PerfilUtilizador``: CRUD da tabela ``perfil_utilizador`` (nome,
  preferências, estado de humor) e histórico da tabela
  ``historico_conversas``;
- ``extrair_informacoes``: aprende factos do utilizador a partir das
  mensagens ("o meu nome é X", "eu trabalho com Y", "estou triste");
- ``contexto_pessoal`` / ``personalizar_resposta``: usam o perfil para
  gerar respostas mais naturais e personalizadas;
- ``gerir_topicos`` + ``MUDANCA_TOPICO``: permite conversar sobre
  vários assuntos diferentes, alternando entre eles sem perder o fio
  de cada um (como seres humanos fazem).
"""

from .perfil import (
    PerfilUtilizador,
    extrair_informacoes,
    contexto_pessoal,
    personalizar_resposta,
)
from .topicos import (
    MUDANCA_TOPICO,
    TOPICOS_CONVERSACIONAIS,
    detectar_mudanca_topico,
    gerir_topicos,
)

__all__ = [
    "PerfilUtilizador",
    "extrair_informacoes",
    "contexto_pessoal",
    "personalizar_resposta",
    # multi-assunto (conversa natural com vários tópicos em paralelo)
    "MUDANCA_TOPICO",
    "TOPICOS_CONVERSACIONAIS",
    "detectar_mudanca_topico",
    "gerir_topicos",
]
