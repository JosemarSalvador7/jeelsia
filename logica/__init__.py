from .knowledge_base.knowledge_base import KnowledgeBase
from .msgs.msgs import (
    mensagens_busca,
    prefixos_factuais,
    padroes_conversa,
    sem_resposta,
)
from .utils.texto import normalizar_texto, analisar_similaridade
from .emocoes.emocoes import detectar_emocao, responder_com_empatia
from .contexto.contexto import (
    criar_estado,
    extrair_topico,
    manter_contexto,
    obter_resposta_unica,
    aplicar_reflections,
)
from .comunicacao import (
    gerar_transicao,
    gerar_pergunta_seguimento,
    gerar_resposta_curta,
    gerar_reconhecimento,
    gerar_despedida,
    finalizar_conversa,
)
from .comunicacao.fluidez import compor_resposta
# Perfil do utilizador (tabela no SQLite) + conversa multi-assunto
from .perfil import (
    PerfilUtilizador,
    extrair_informacoes,
    contexto_pessoal,
    personalizar_resposta,
    MUDANCA_TOPICO,
    detectar_mudanca_topico,
    gerir_topicos,
)

__all__ = [
    "KnowledgeBase",
    "mensagens_busca",
    "padroes_conversa",
    "prefixos_factuais",
    "sem_resposta",
    "normalizar_texto",
    "analisar_similaridade",
    "detectar_emocao",
    "responder_com_empatia",
    "criar_estado",
    "extrair_topico",
    "manter_contexto",
    "obter_resposta_unica",
    "aplicar_reflections",
    # comunicação / fluidez
    "gerar_transicao",
    "gerar_pergunta_seguimento",
    "gerar_resposta_curta",
    "gerar_reconhecimento",
    "gerar_despedida",
    "finalizar_conversa",
    "compor_resposta",
    # perfil do utilizador + multi-assunto
    "PerfilUtilizador",
    "extrair_informacoes",
    "contexto_pessoal",
    "personalizar_resposta",
    "MUDANCA_TOPICO",
    "detectar_mudanca_topico",
    "gerir_topicos",
]
