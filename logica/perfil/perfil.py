"""Perfil do utilizador persistido em SQLite — respostas mais personalizadas.

Duas novas tabelas na base de dados (``cerebro.db``):

1. ``perfil_utilizador`` — uma linha por utilizador com nome, preferências
   (gostos/odios/assuntos favoritos), profissão, localização e humor
   atual. É esta informação que permite à Jeelsia dizer
   "Então, {nome}, como correu o trabalho?" em vez de respostas genéricas.

2. ``historico_conversas`` — um registo por turno relevante
   (mensagem, intenção, emoção, tópico). Permite retomar assuntos de
   sessões anteriores ("Da última vez falavas sobre o teu dia difícil...").

O módulo também expõe:

- ``extrair_informacoes``: aprende factos do utilizador a partir das
  mensagens normais da conversa (nome, idade, gosto por X, trabalho,
  localização, estado emocional) — sem comandos especiais;
- ``contexto_pessoal`` / ``personalizar_resposta``: injetam o perfil na
  resposta para gerar comunicação natural e fluida.

Tudo opera sobre a mesma ligação sqlite3 da KnowledgeBase (``kb.conn``),
sem abrir segunda ligação.
"""

from __future__ import annotations

import random
import re
import sqlite3
from datetime import datetime
from typing import Any

# ----------------------------------------------------------------------
# DDL das tabelas de perfil
# ----------------------------------------------------------------------

DDL_PERFIL = """
CREATE TABLE IF NOT EXISTS perfil_utilizador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    idade INTEGER,
    preferencias TEXT,          -- JSON: {"gostos": [], "odios": [], "favoritos": []}
    profissao TEXT,
    localizacao TEXT,
    humor_atual TEXT,
    ultimo_assunto TEXT,
    notas TEXT,                 -- factos soltos aprendidos nas conversas
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS historico_conversas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    perfil_id INTEGER,
    mensagem TEXT NOT NULL,
    intencao TEXT,
    emocao TEXT,
    topico TEXT,
    sessao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(perfil_id) REFERENCES perfil_utilizador(id)
);
CREATE INDEX IF NOT EXISTS idx_historico_perfil ON historico_conversas(perfil_id);
CREATE INDEX IF NOT EXISTS idx_historico_topico ON historico_conversas(topico);
"""


class PerfilUtilizador:
    """CRUD simples sobre ``perfil_utilizador`` + ``historico_conversas``.

    Usa a ligação já aberta pela KnowledgeBase (``kb.conn``), partilhando
    o mesmo ficheiro ``cerebro.db``.
    """

    def __init__(self, conn: sqlite3.Connection, perfil_id: int = 1) -> None:
        self.conn = conn
        self.perfil_id = perfil_id
        self._criar_tabelas()
        self._garantir_perfil()

    # ---------------- estrutura ----------------
    def _criar_tabelas(self) -> None:
        self.conn.executescript(DDL_PERFIL)
        self.conn.commit()

    def _garantir_perfil(self) -> None:
        row = self.conn.execute(
            "SELECT id FROM perfil_utilizador WHERE id = ?", (self.perfil_id,)
        ).fetchone()
        if row is None:
            self.conn.execute(
                "INSERT INTO perfil_utilizador (id) VALUES (?)", (self.perfil_id,)
            )
            self.conn.commit()

    # ---------------- leitura ----------------
    def obter(self) -> dict[str, Any]:
        """Devolve o perfil como dicionário (preferências já como dict)."""
        cur = self.conn.execute(
            "SELECT * FROM perfil_utilizador WHERE id = ?", (self.perfil_id,)
        )
        colunas = [d[0] for d in cur.description]
        linha = cur.fetchone()
        perfil = dict(zip(colunas, linha)) if linha else {}
        perfil["preferencias"] = self._parse_json(perfil.get("preferencias"))
        return perfil

    @staticmethod
    def _parse_json(valor: str | None) -> dict:
        import json

        if not valor:
            return {"gostos": [], "odios": [], "favoritos": []}
        try:
            dados = json.loads(valor)
            if isinstance(dados, dict):
                dados.setdefault("gostos", [])
                dados.setdefault("odios", [])
                dados.setdefault("favoritos", [])
                return dados
        except (ValueError, TypeError):
            pass
        return {"gostos": [], "odios": [], "favoritos": []}

    # ---------------- escrita ----------------
    def atualizar(self, **campos: Any) -> None:
        """Atualiza colunas do perfil. ``preferencias`` aceita dict ou JSON."""
        if not campos:
            return
        import json

        if "preferencias" in campos and isinstance(campos["preferencias"], dict):
            campos["preferencias"] = json.dumps(
                campos["preferencias"], ensure_ascii=False
            )
        colunas = ", ".join(f"{k} = ?" for k in campos)
        valores = list(campos.values()) + [self.perfil_id]
        self.conn.execute(
            f"UPDATE perfil_utilizador SET {colunas}, "
            f"atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
            valores,
        )
        self.conn.commit()

    def adicionar_preferencia(self, tipo: str, item: str) -> None:
        """Acrescenta um gosto/odio/favorito ao perfil (sem duplicar)."""
        if tipo not in ("gostos", "odios", "favoritos"):
            return
        prefs = self.obter()["preferencias"]
        item = item.strip().lower()
        if item and item not in prefs[tipo]:
            prefs[tipo].append(item)
            self.atualizar(preferencias=prefs)

    def registar_assunto(self, assunto: str) -> None:
        if assunto:
            self.atualizar(ultimo_assunto=assunto[:120])

    def registar_humor(self, emocao: str | None) -> None:
        if emocao and emocao != "neutro":
            self.atualizar(humor_atual=emocao)

    def anexar_nota(self, nota: str) -> None:
        """Guarda um facto solto aprendido sobre o utilizador."""
        nota = nota.strip()
        if not nota:
            return
        atual = self.obter().get("notas") or ""
        if nota.lower() in atual.lower():
            return
        novo = f"{atual}\n{nota}".strip() if atual else nota
        self.atualizar(notas=novo[-1500:])  # limita tamanho

    def registrar_turno(self, mensagem: str, intencao: str | None = None,
                       emocao: str | None = None, topico: str | None = None,
                       sessao: str | None = None) -> None:
        """Insere o turno em ``historico_conversas``."""
        self.conn.execute(
            "INSERT INTO historico_conversas "
            "(perfil_id, mensagem, intencao, emocao, topico, sessao) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (self.perfil_id, mensagem[:500], intencao, emocao, topico, sessao),
        )
        self.conn.commit()

    def ultimos_assuntos(self, limite: int = 5) -> list[str]:
        """Assuntos mais recentes (distintos) do histórico."""
        cur = self.conn.execute(
            "SELECT DISTINCT topico FROM historico_conversas "
            "WHERE perfil_id = ? AND topico IS NOT NULL "
            "ORDER BY id DESC LIMIT ?",
            (self.perfil_id, limite),
        )
        return [r[0] for r in cur.fetchall()]

    def ultima_mensagem_emovente(self, emocao: str) -> str | None:
        cur = self.conn.execute(
            "SELECT mensagem FROM historico_conversas "
            "WHERE perfil_id = ? AND emocao = ? ORDER BY id DESC LIMIT 1",
            (self.perfil_id, emocao),
        )
        row = cur.fetchone()
        return row[0] if row else None

    # ---------------- helpers de conversa ----------------
    def tem_identidade(self) -> bool:
        return bool(self.obter().get("nome"))


# ----------------------------------------------------------------------
# Extração de informação das mensagens (aprendizagem implícita)
# ----------------------------------------------------------------------

# Padrões de autoafirmação — ordem importa (primeiro match ganha por tipo)
_PADROES_NOME = [
    r"\b(?:o meu nome é|o meu nome e|meu nome é|meu nome e|chamo-me|chamo me|"
    r"o meu nome está|podes chamar-me|podes me chamar|meu nome:)\s+([A-ZÀ-Ü][\w'À-ÿ-]{1,29})",
    r"\b(?:eu sou|sou)\s+(?:o|a)?\s*([A-ZÀ-Ü][\w'À-ÿ-]{2,29})\b(?!\s+(?:cansado|triste|feliz|contente|zangado|com|a fazer|em|de fome))",
    r"\b(?:my name is|i am i'm|im)\s+([A-Z][A-Za-z]{1,29})",
]

_PADRAO_IDADE = r"\b(?:tenho|tengo|i am|i'm|im)\s+(\d{1,2})\s*(?:anos?|years?|años?)?\b"
_PADRAO_GOSTO = r"\b(?:eu\s+)?(?:gosto muito de|gosto de|adorei|adoro|amo|curto de|curto|especialmente gosto de)\s+(?:de\s+)?((?:[\wà-üáéíóúãõâêôç'-]+\s?){1,6})"
_PADRAO_ODIO = r"\b(?:eu\s+)?(?:não gosto de|nao gosto de|odeio|detesto|não suporto|nao suporto)\s+((?:[\wà-üáéíóúãõâêôç'-]+\s?){1,6})"
_PADRAO_TRABALHO = r"\b(?:eu\s+)?(?:trabalho (?:como|em|de)|sou\b)\s+(professor|professora|programador|programadora|estudante|médico|medica|medico|enfermeiro|enfermeira|engenheiro|engenheira|cozinheiro|cozinheira|designer|contador|contadora|advogado|advogada|jornalista|motorista|piloto|farmacêutico|farmaceutico|eletricista|mecanico|mecânica|mecanica)\b"
_PADRAO_LOCAL = r"\b(?:moro em|vivo em|sou de|estou em|fica?rei? em)\s+([A-ZÀ-Ü][\w'À-ÿ-]{2,29})"
_PADRAO_ASSUNTO_FAV = r"\b(?:o meu assunto favorito (?:é|e)|assunto favorito:|prefiro falar sobre|gosto de falar sobre)\s+((?:[\wà-üáéíóúãõâêôç'-]+\s?){1,5})"

# Palavras a ignorar quando o "nome" capturado é claramente outra coisa
_INVALIDOS_NOME = {
    "triste", "feliz", "cansado", "zangado", "doente", "ocupado", "aqui",
    "assim", "confuso", "confusa", "preocupado", "preocupada", "animado",
    "animada", "sozinho", "sozinha", "mal", "bem", "ótimo", "otimo",
    "estudante", "programador", "programadora", "professor", "professora",
}

_STOPWORDS_PREF = {"isso", "isto", "nada", "tudo", "muito", "agora", "sempre",
                   "nunca", "eles", "elas", "vocês", "voce", "tu", "nós", "nos"}

# Palavras que nunca abrem um novo tópico (verbos/estados comuns) —
# evitam falsos tópicos como "estou", "muito", "porque".
_SKIP_TOPICOS = {
    "estou", "está", "esta", "estava", "estão", "são", "ser", "estar",
    "muito", "pouco", "porque", "poque", "quando", "onde", "como",
    "depois", "ontem", "hoje", "amanhã", "amanha", "agora", "ainda",
    "também", "tambem", "mesmo", "minha", "meu", "nossa", "nosso",
    "ele", "ela", "eles", "elas", "nada", "tudo", "coisa", "modo",
    "forma", "vezes", "veze", "dizia", "dizias", "sabes", "sei",
}


def _limpar_fragmento(txt: str) -> str:
    txt = re.sub(r"[!?.;,]+$", "", txt.strip())
    palavras = [p for p in txt.split() if p][:4]
    return " ".join(palavras)


def extrair_informacoes(mensagem: str, perfil: PerfilUtilizador) -> list[str]:
    """Lê a mensagem e grava automaticamente factos no perfil.

    Devolve a lista de novos factos aprendidos (para feedback opcional).
    Nunca exige comandos — faz parte da conversa normal.
    """
    aprendidos: list[str] = []
    if not mensagem or not mensagem.strip():
        return aprendidos

    texto = mensagem.strip()

    # NOME
    if not perfil.tem_identidade():
        for padrao in _PADROES_NOME:
            m = re.search(padrao, texto, flags=re.IGNORECASE)
            if m:
                nome = m.group(1).strip().capitalize()
                if nome.lower() in _INVALIDOS_NOME:
                    continue
                perfil.atualizar(nome=nome)
                aprendidos.append(f"nome={nome}")
                break

    # IDADE
    m = re.search(_PADRAO_IDADE, texto, flags=re.IGNORECASE)
    if m and not perfil.obter().get("idade"):
        idade = int(m.group(1))
        if 3 <= idade <= 120:
            perfil.atualizar(idade=idade)
            aprendidos.append(f"idade={idade}")

    # GOSTOS / ÓDIOS
    m = re.search(_PADRAO_GOSTO, texto, flags=re.IGNORECASE)
    if m:
        item = _limpar_fragmento(m.group(1))
        if item and item.lower() not in _STOPWORDS_PREF:
            antes = len(perfil.obter()["preferencias"]["gostos"])
            perfil.adicionar_preferencia("gostos", item)
            if len(perfil.obter()["preferencias"]["gostos"]) > antes:
                aprendidos.append(f"gosta de {item}")
    m = re.search(_PADRAO_ODIO, texto, flags=re.IGNORECASE)
    if m:
        item = _limpar_fragmento(m.group(1))
        if item and item.lower() not in _STOPWORDS_PREF:
            antes = len(perfil.obter()["preferencias"]["odios"])
            perfil.adicionar_preferencia("odios", item)
            if len(perfil.obter()["preferencias"]["odios"]) > antes:
                aprendidos.append(f"não gosta de {item}")

    # PROFISSÃO
    m = re.search(_PADRAO_TRABALHO, texto, flags=re.IGNORECASE)
    if m and not perfil.obter().get("profissao"):
        perfil.atualizar(profissao=m.group(1).lower())
        aprendidos.append(f"profissão={m.group(1).lower()}")

    # LOCALIZAÇÃO
    m = re.search(_PADRAO_LOCAL, texto)
    if m and not perfil.obter().get("localizacao"):
        cidade = m.group(1).strip().capitalize()
        if cidade.lower() not in _INVALIDOS_NOME:
            perfil.atualizar(localizacao=cidade)
            aprendidos.append(f"localização={cidade}")

    # ASSUNTO FAVORITO
    m = re.search(_PADRAO_ASSUNTO_FAV, texto, flags=re.IGNORECASE)
    if m:
        item = _limpar_fragmento(m.group(1))
        if item:
            antes = len(perfil.obter()["preferencias"]["favoritos"])
            perfil.adicionar_preferencia("favoritos", item)
            if len(perfil.obter()["preferencias"]["favoritos"]) > antes:
                aprendidos.append(f"assunto favorito={item}")

    # NOTAS soltas (frases de autoapresentação ricas)
    if re.search(r"\b(?:o meu nome|eu trabalho|estudo em|a minha paixão é|a minha paixao é)\b",
                 texto, flags=re.IGNORECASE):
        perfil.anexar_nota(texto[:140])

    return aprendidos


# ----------------------------------------------------------------------
# Uso do perfil para gerar melhores respostas
# ----------------------------------------------------------------------

def contexto_pessoal(perfil: PerfilUtilizador) -> dict[str, Any]:
    """Resumo do perfil pronto a injetar no gerador de respostas."""
    dados = perfil.obter()
    prefs = dados.get("preferencias") or {}
    return {
        "nome": dados.get("nome"),
        "idade": dados.get("idade"),
        "profissao": dados.get("profissao"),
        "localizacao": dados.get("localizacao"),
        "humor": dados.get("humor_atual"),
        "gostos": prefs.get("gostos", [])[:3],
        "odios": prefs.get("odios", [])[:3],
        "favoritos": prefs.get("favoritos", [])[:3],
        "ultimo_assunto": dados.get("ultimo_assunto"),
    }


def saudação_com_perfil(ctx: dict, periodo: str) -> str | None:
    """Saudação personalizada se conhecermos o nome/último assunto."""
    nome = ctx.get("nome")
    if not nome:
        return None
    assumpto = ctx.get("ultimo_assunto")
    humor = ctx.get("humor")
    opcoes = [f"Olá, {nome}! Boa {periodo}!"]
    if assumpto:
        opcoes.append(
            f"Bem-vindo de volta, {nome}! Da última vez falávamos sobre \"{assumpto}\" — queres continuar ou mudar de assunto?"
        )
    if humor in ("tristeza", "raiva", "medo"):
        opcoes.append(
            f"Oi, {nome}! Lembro-me que da última vez estavas {humor}. Espero que hoje estejas melhor — como te sentes agora?"
        )
    return random.choice(opcoes)


def personalizar_resposta(resposta: str, ctx: dict, tipo: str | None = None) -> str:
    """Aplica toques de personalidade ao corpo da resposta.

    - Trata o utilizador pelo nome quando a resposta é direta ("tu");
    - Sugere temas ligados aos gostos quando há abertura;
    - Evita recomendar algo que o utilizador declarou odiar.
    """
    if not resposta:
        return resposta
    nome = ctx.get("nome")
    if nome and tipo == "conhecimento" and random.random() < 0.25:
        resposta = resposta.rstrip(".!?") + f", {nome}."
    return resposta


def sugestao_por_gostos(ctx: dict) -> str | None:
    """Pergunta de seguimento baseada nos gostos conhecidos."""
    gostos = ctx.get("gostos") or []
    favoritos = ctx.get("favoritos") or []
    pool = favoritos or gostos
    if not pool:
        return None
    tema = random.choice(pool)
    return random.choice([
        f"Aliás, {tema}: querias falar sobre isso?",
        f"Se quiseres, podemos saltar para {tema} — sei que gostas.",
        f"E o teu interesse por {tema}, como está?",
    ])


if __name__ == "__main__":  # smoke test manual
    con = sqlite3.connect(":memory:")
    p = PerfilUtilizador(con)
    for msg in ["o meu nome é Carlos", "eu gosto de música", "tenho 27 anos",
                "trabalho como programador", "não gosto de chuva"]:
        print(msg, "->", extrair_informacoes(msg, p))
    print(contexto_pessoal(p))
