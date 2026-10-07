"""Conversa multi-assunto — vários fios temáticos em paralelo.

Ser humanos não conversam sobre uma coisa de cada vez: abrem um assunto,
saltam para outro, e mais tarde retomam o primeiro ("ah, voltando ao que
dizias do teu trabalho..."). Este módulo dá isso à Jeelsia:

- ``gerir_topicos``: mantém no ``estado`` uma lista de até 3 tópicos
  abertos (pilha LRU). Cada tópico tem o seu próprio sub-fio
  (emoção, nível de perguntas progressivas, última pergunta, resumo);
- ``detectar_mudanca_topico`` + ``MUDANCA_TOPICO``: reconhece quando o
  utilizador muda deliberadamente de assunto ("mudando de assunto",
  "ah, outra coisa", "voltando ao trabalho") e quando retoma um tópico
  antigo;
- ``transicao_natural``: gera a ponte conversacional entre assuntos,
  em vez de responder como se a conversa começasse do zero.

O ``fio condutor`` clássico (logica.contexto.fio) continua a ser usado
para o tópico ATIVO — aqui apenas se adiciona a capacidade de ter
vários fios guardados e alternar entre eles sem perder contexto.
"""

from __future__ import annotations

import random
import re

from logica.utils.texto import normalizar_texto

# Verbos/estados comuns que nunca abrem um novo tópico (evita falsos
# tópicos como "estou", "muito", "porque" quando não há categoria clara).
_SKIP_TOPICOS = {
    "estou", "está", "esta", "estava", "estão", "são", "ser", "estar",
    "muito", "pouco", "porque", "poque", "quando", "onde", "como",
    "depois", "ontem", "hoje", "amanhã", "amanha", "agora", "ainda",
    "também", "tambem", "mesmo", "minha", "meu", "nossa", "nosso",
    "ele", "ela", "eles", "elas", "nada", "tudo", "coisa", "modo",
    "forma", "vezes", "veze", "dizia", "dizias", "sabes", "sei",
    "zangado", "zangada", "triste", "feliz", "contente", "cansado",
    "cansada", "assim", "desta", "desse", "disso", "muitas", "muitos",
}

# ----------------------------------------------------------------------
# Vocabulário de mudança/retomada de assunto
# ----------------------------------------------------------------------

# Sinais explícitos de que o utilizador quer mudar de tópico
MUDANCA_TOPICO = [
    "mudando de assunto", "mudando de papo", "mudar de assunto",
    "trocar de assunto", "outro assunto", "outra coisa", "a propósito",
    "falando nisso", "isso me lembra", "isso lembra-me", "aliás",
    "entretanto", "deixa eu te contar", "deixa-me contar-te",
    "quero falar de outra coisa", "vamos falar de outra coisa",
    "muda de tema", "mudo de tema", "outro tema", "nova pergunta",
]

# Sinais de retomada de um tópico anterior
RETOMADA_TOPICOS = [
    "voltando ao", "volta ao", "retomando o", "sobre o que eu dizia",
    "aquilo que eu contava", "lembra-te que eu falei", "continuando aquilo",
    "onde estávamos com", "aquele assunto do", "e sobre aquela coisa do",
]

# Pontes naturais usadas pelo assistente ao alternar assuntos
TRANSICOES_MUDANCA = [
    "Boa, mudamos então de assunto.",
    "Claro, saltemos para aí.",
    "Combinado — deixamos esse tema em aberto e seguimos.",
    "Sem problema, novo tema!",
    "Ok, guardo o que dizias e vamos a isto.",
]

TRANSICOES_RETOMADA = [
    "Lembro-me bem — retomando {topico}:",
    "Ah sim, {topico}! Onde tínhamos ficado?",
    "Sobre {topico}, continua...",
    "Claro, {topico} estava pendente — diz lá.",
]

# Categorias temáticas simples para agrupar mensagens afins
TOPICOS_CONVERSACIONAIS = {
    "trabalho": ["trabalho", "emprego", "chefe", "escritório", "escritorio",
                 "sala de aula", "empresa", "colega", "salário", "salario",
                 "estágio", "estagio", "reunião", "reuniao", "projeto"],
    "estudos": ["escola", "estudo", "estudar", "prova", "exame", "faculdade",
                "curso", "turma", "professor", "professora", "nota", "aprender"],
    "saúde": ["saúde", "saude", "doente", "doença", "doenca", "dor", "médico",
              "medico", "hospital", "remédio", "remedio", "cansaço", "cansaco",
              "sono", "dormir", "insónia", "insomnia"],
    "relações": ["namorada", "namorado", "amigo", "amiga", "família", "familia",
                 "mãe", "mae", "pai", "irmão", "irmao", "irmã", "irma",
                 "casamento", "relacionamento", "briga", "discussão", "discussao"],
    "dinheiro": ["dinheiro", "contas", "dívida", "divida", "salário", "salario",
                 "poupar", "economizar", "preço", "preco", "caro", "barato",
                 "renda", "fatura", "falta de dinheiro"],
    "lazer": ["futebol", "música", "musica", "filme", "cinema", "viagem",
              "viajar", "praia", "festa", "jogo", "hobby", "videojogos",
              "desporto", "desporto"],
    "dia-a-dia": ["hoje", "ontem", "amanhã", "amanha", "acordei", "acordar",
                  " trânsito", "transito", "autocarro", "fila", "longo",
                  "não correu bem", "nao correu bem", "meu dia"],
}


def _classificar(mensagem_norm: str) -> str | None:
    """Devolve a categoria temática da mensagem, ou None."""
    melhor, melhor_score = None, 0.0
    for topico, palavras in TOPICOS_CONVERSACIONAIS.items():
        hits = sum(1 for p in palavras if p in mensagem_norm)
        if hits > melhor_score:
            melhor, melhor_score = topico, hits
    return melhor


def _chave_topico(mensagem: str) -> str | None:
    """Chave estável para o tópico da mensagem (categoria ou 2 palavras-chave)."""
    m = normalizar_texto(mensagem)
    cat = _classificar(m)
    if cat:
        return cat
    # fallback: primeira palavra substantiva como assinatura do assunto
    from logica.contexto import extrair_topico

    base = extrair_topico(m)
    if not base or base in _SKIP_TOPICOS:
        return None
    return base


# ----------------------------------------------------------------------
# Gestão da pilha de tópicos abertos
# ----------------------------------------------------------------------

_MAX_TOPICOS = 3


def gerir_topicos(estado: dict, mensagem: str) -> dict:
    """Atualiza a pilha de tópicos do ``estado`` com a mensagem atual.

    Estrutura criada em ``estado['topicos']``::

        {
          "ativo": "trabalho",
          "abertos": {
             "trabalho": {"emocao": ..., "nivel": ..., "ultima_pergunta": ...,
                          "resumo": [...], "turnos": n},
             ...
          },
          "ordem": ["trabalho", "saúde"]   # LRU: mais recente primeiro
        }

    Devolve metadados do movimento detetado::

        {"acao": "novo"|"continua"|"retoma"|"muda",
         "topico": <chave>, "anterior": <chave ou None>}
    """
    topo = estado.setdefault("topicos", {"ativo": None, "abertos": {}, "ordem": []})
    m = normalizar_texto(mensagem)
    nova = _chave_topico(mensagem)

    sinal_mudanca = any(e in m for e in MUDANCA_TOPICO)
    sinal_retoma = any(e in m for e in RETOMADA_TOPICOS)

    resultado = {"acao": "continua", "topico": nova or topo["ativo"],
                 "anterior": topo["ativo"]}

    # --- Retomada explícita de um tópico aberto -----------------------
    if sinal_retoma and topo["abertos"]:
        alvo = None
        for chave in topo["abertos"]:
            if chave and (chave in m or _classificar_por_palavra(m, chave)):
                alvo = chave
                break
        if alvo and alvo != topo["ativo"]:
            anterior = topo["ativo"]
            topo["ativo"] = alvo
            _trazer_para_frente(topo, alvo)
            resultado = {"acao": "retoma", "topico": alvo, "anterior": anterior}
            return resultado

    # --- Sem conteúdo novo (elipse/vaga): mantém tópico ativo ---------
    if nova is None:
        resultado["acao"] = "continua"
        resultado["topico"] = topo["ativo"]
        return resultado

    # --- Mesma categoria do tópico ativo: continuidade -----------------
    if nova == topo["ativo"] and not sinal_mudanca:
        _trazer_para_frente(topo, nova)
        resultado["acao"] = "continua"
        return resultado

    # --- Categoria diferente: pode ser novo assunto ou mudança ----------
    anterior = topo["ativo"]
    if nova in topo["abertos"] and nova != anterior:
        # já estava aberto → é uma MUDANÇA para tópico conhecido
        topo["ativo"] = nova
        _trazer_para_frente(topo, nova)
        resultado = {"acao": "muda", "topico": nova, "anterior": anterior}
        return resultado

    if sinal_mudanca or anterior is None or nova != anterior:
        # abrir (ou substituir) tópico
        topo["abertos"][nova] = topo["abertos"].get(nova) or {
            "emocao": None, "nivel": 0, "ultima_pergunta": None,
            "resumo": [], "turnos": 0,
        }
        topo["ativo"] = nova
        _trazer_para_frente(topo, nova)
        _podar(topo)
        resultado = {"acao": "novo" if not sinal_mudanca else "muda",
                     "topico": nova, "anterior": anterior}
        return resultado

    return resultado


def _classificar_por_palavra(m: str, chave: str) -> bool:
    """True se a mensagem menciona palavras da categoria ``chave``."""
    palavras = TOPICOS_CONVERSACIONAIS.get(chave, [])
    return any(p in m for p in palavras)


def _trazer_para_frente(topo: dict, chave: str) -> None:
    if chave in topo["ordem"]:
        topo["ordem"].remove(chave)
    topo["ordem"].insert(0, chave)


def _podar(topo: dict) -> None:
    """Mantém no máximo _MAX_TOPICOS abertos (descarta o menos recente)."""
    while len(topo["ordem"]) > _MAX_TOPICOS:
        velho = topo["ordem"].pop()
        topo["abertos"].pop(velho, None)


# ----------------------------------------------------------------------
# Ponte entre o fio global e o sub-fio do tópico ativo
# ----------------------------------------------------------------------

def sincronizar_fio_com_topico(estado: dict, emocao: dict | None) -> None:
    """Copia o sub-fio do tópico ativo para ``estado['fio']``.

    Assim o módulo ``fio`` (perguntas progressivas, elipses, retomadas)
    trabalha sempre sobre a linha do ASSUNTO atual — e quando o
    utilizador voltar a um assunto antigo, o nível de profundidade das
    perguntas continua de onde parou.
    """
    topo = estado.get("topicos")
    if not topo or not topo.get("ativo"):
        return
    sub = topo["abertos"].get(topo["ativo"])
    if sub is None:
        return
    estado["fio"] = {
        "emocao": sub.get("emocao"),
        "nivel": sub.get("nivel", 0),
        "ultima_pergunta": sub.get("ultima_pergunta"),
        "resumo": list(sub.get("resumo", [])),
    }


def persistir_fio_no_topico(estado: dict) -> None:
    """Escreve o ``estado['fio']`` atual de volta ao sub-fio do tópico ativo."""
    topo = estado.get("topicos")
    if not topo or not topo.get("ativo"):
        return
    fio = estado.get("fio") or {}
    sub = topo["abertos"].setdefault(topo["ativo"], {
        "emocao": None, "nivel": 0, "ultima_pergunta": None,
        "resumo": [], "turnos": 0,
    })
    sub["emocao"] = fio.get("emocao")
    sub["nivel"] = fio.get("nivel", 0)
    sub["ultima_pergunta"] = fio.get("ultima_pergunta")
    sub["resumo"] = list(fio.get("resumo", []))
    sub["turnos"] = sub.get("turnos", 0) + 1


def transicao_natural(info_topicos: dict, estado: dict) -> str | None:
    """Frase-ponte quando há mudança/retomada de assunto."""
    acao = info_topicos.get("acao")
    topo_ativo = info_topicos.get("topico")
    if acao == "muda" and topo_ativo:
        retomaveis = [t for t in (estado.get("topicos", {}).get("ordem") or [])[1:]
                      if t]
        guarda = ""
        if retomaveis:
            guarda = f" Quando quiseres, voltamos ao {retomaveis[0]}."
        return random.choice(TRANSICOES_MUDANCA) + guarda
    if acao == "retoma" and topo_ativo:
        ponte = random.choice(TRANSICOES_RETOMADA)
        return ponte.format(topico=topo_ativo)
    if acao == "novo" and topo_ativo and random.random() < 0.35:
        return random.choice([
            "Novo tema, boa!",
            "Vamos a isso!",
            "Interessante — mudemos então para aí.",
        ])
    return None


def detectar_mudanca_topico(mensagem: str) -> bool:
    """True se a mensagem contém sinal explícito de mudança de assunto."""
    m = normalizar_texto(mensagem)
    return any(e in m for e in MUDANCA_TOPICO)


if __name__ == "__main__":  # smoke test manual
    st: dict = {}
    seq = [
        "hoje no trabalho o meu chefe gritou comigo",
        "estou muito zangado com ele",
        "ah, mudando de assunto, vi um filme ontem",
        "mas voltando ao trabalho, ele pediu desculpa",
    ]
    for s in seq:
        info = gerir_topicos(st, s)
        print(s, "->", info, "| ativos:", st["topicos"]["ordem"])
