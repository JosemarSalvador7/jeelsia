"""
Pacote da base de conhecimento do Jeelsia.

Ao importar este pacote, os dados semente são inseridos na base de dados
SQLite (idempotente: INSERT OR IGNORE). Para popular explicitamente, use:

    python -m logica.knowledge_base [--db caminho/cerebro.db]
"""

from __future__ import annotations

import sqlite3
from typing import Any

from .knowledge_base import KnowledgeBase
from .seeds import (
    SEED_CONHECIMENTOS,
    SEED_CONSELHOS,
    SEED_FACTOS,
    SEED_HABILIDADES,
    SEED_HISTORIAS,
    obter_seeds,
)

DB_PADRAO = "./cerebro.db"

# Mapeamento: tabela -> (lista de seeds, colunas a inserir)
_MAPA_INSERCAO: dict[str, tuple[list[dict], list[str]]] = {
    "factos": (SEED_FACTOS, ["topico", "facto", "fonte", "categoria"]),
    "conhecimentos": (SEED_CONHECIMENTOS, ["pergunta", "resposta", "fonte", "categoria"]),
    "conselhos": (SEED_CONSELHOS, ["problema", "conselho", "categoria"]),
    "habilidades": (SEED_HABILIDADES, ["nome", "descricao", "exemplo_uso"]),
    "historias": (SEED_HISTORIAS, ["titulo", "conteudo", "autor", "categoria", "origem"]),
}


def criar_estrutura(conn: sqlite3.Connection) -> None:
    """Garante que todas as tabelas e índices existem (mesmo DDL de KnowledgeBase)."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS factos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topico TEXT NOT NULL,
            facto TEXT,
            fonte TEXT,
            categoria TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(topico, facto)
        );
        CREATE TABLE IF NOT EXISTS conhecimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT NOT NULL,
            resposta TEXT NOT NULL,
            facto_id INTEGER,
            fonte TEXT,
            categoria TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(pergunta, resposta),
            FOREIGN KEY(facto_id) REFERENCES factos(id)
        );
        CREATE TABLE IF NOT EXISTS conselhos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problema TEXT NOT NULL,
            conselho TEXT NOT NULL,
            categoria TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(problema, conselho)
        );
        CREATE TABLE IF NOT EXISTS habilidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            exemplo_uso TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(nome)
        );
        CREATE TABLE IF NOT EXISTS historias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            autor TEXT,
            categoria TEXT,
            origem TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(titulo, conteudo)
        );
        CREATE INDEX IF NOT EXISTS idx_factos_topico ON factos(topico);
        CREATE INDEX IF NOT EXISTS idx_conhecimentos_pergunta ON conhecimentos(pergunta);
        """
    )
    conn.commit()


def popular_db(db_path: str = DB_PADRAO, verbose: bool = True) -> dict[str, int]:
    """Insere todos os dados semente nas tabelas. Idempotente (INSERT OR IGNORE).

    Devolve um resumo {"tabela": nº de linhas newly inseridas}.
    """
    conn = sqlite3.connect(db_path)
    resumo: dict[str, int] = {}
    try:
        criar_estrutura(conn)
        for tabela, (registos, colunas) in _MAPA_INSERCAO.items():
            antes = conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
            sql = (
                f"INSERT OR IGNORE INTO {tabela} ({', '.join(colunas)}) "
                f"VALUES ({', '.join('?' * len(colunas))})"
            )
            for registo in registos:
                valores: list[Any] = [registo.get(coluna) for coluna in colunas]
                conn.execute(sql, valores)
            depois = conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
            resumo[tabela] = depois - antes
        conn.commit()
    finally:
        conn.close()

    if verbose:
        total = sum(resumo.values())
        print(f"Base de dados '{db_path}' populada: {total} novos registos -> {resumo}")
    return resumo


def popular_com_kb(kb: KnowledgeBase) -> dict[str, int]:
    """Variante que usa uma instância KnowledgeBase já aberta (partilha a ligação)."""
    resumo: dict[str, int] = {}
    for tabela, (registos, colunas) in _MAPA_INSERCAO.items():
        antes = kb.cursor.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        sql = (
            f"INSERT OR IGNORE INTO {tabela} ({', '.join(colunas)}) "
            f"VALUES ({', '.join('?' * len(colunas))})"
        )
        for registo in registos:
            kb.cursor.execute(sql, [registo.get(coluna) for coluna in colunas])
        depois = kb.cursor.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        resumo[tabela] = depois - antes
    kb.conn.commit()
    kb.carregar_dados_em_memoria()
    return resumo


# Popular automaticamente ao importar o pacote (silencioso em caso de erro de ambiente)
try:
    popular_db(DB_PADRAO, verbose=False)
except sqlite3.Error:  # pragma: no cover - ambiente sem permissões, por exemplo
    pass

__all__ = [
    "KnowledgeBase",
    "popular_db",
    "popular_com_kb",
    "criar_estrutura",
    "obter_seeds",
    "SEED_FACTOS",
    "SEED_CONHECIMENTOS",
    "SEED_CONSELHOS",
    "SEED_HABILIDADES",
    "SEED_HISTORIAS",
    "DB_PADRAO",
]
