"""Módulo de gestão de contexto da conversa."""

from .contexto import (
    criar_estado,
    extrair_topico,
    manter_contexto,
    obter_resposta_unica,
    aplicar_reflections,
)
from .fio import (
    atualizar_fio,
    encerrar_fio_se_despedida,
    proxima_pergunta_progressiva,
    responder_elipse,
    retomar_fio,
)
from .espejo import (
    extrair_conteudo_espelhavel,
    gerar_espejo,
    aplicar_espejo,
    tem_conteudo_espelhavel,
)

__all__ = [
    "criar_estado",
    "extrair_topico",
    "manter_contexto",
    "obter_resposta_unica",
    "aplicar_reflections",
    # fio condutor (desenvolver conversa sem perder contexto)
    "atualizar_fio",
    "encerrar_fio_se_despedida",
    "proxima_pergunta_progressiva",
    "responder_elipse",
    "retomar_fio",
    # espelhamento empático ELIZA-style
    "extrair_conteudo_espelhavel",
    "gerar_espejo",
    "aplicar_espejo",
    "tem_conteudo_espelhavel",
]
