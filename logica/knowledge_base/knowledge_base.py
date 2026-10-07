import random
import sqlite3
from functools import lru_cache
from rapidfuzz import fuzz
from random import shuffle, randint
import re
import os
from typing import List, Dict, Any


class KnowledgeBase:
    def __init__(self, db_path="cerebro.db") -> None:
        # Remove ficheiros WAL/SHM antigos antes de abrir a ligação
        for suffix in ("-wal", "-shm"):
            caminho = f"{db_path}{suffix}"
            if os.path.exists(caminho):
                os.remove(caminho)

        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = DELETE")
        self.conn.commit()
        self.cursor = self.conn.cursor()  # Move para antes de criar tabelas
        self.criar_tabelas()
        self._criar_tabelas_perfil()
        self.carregar_dados_em_memoria()

    def _criar_tabelas_perfil(self) -> None:
        """Garante as tabelas de perfil/histórico do utilizador no mesmo DB.

        O DDL vive em ``logica.perfil``; aqui apenas asseguramos que a
        base de dados nasce com a tabela ``perfil_utilizador`` (dados do
        utilizador para gerar melhores respostas) e ``historico_conversas``.
        """
        from logica.perfil.perfil import DDL_PERFIL

        self.conn.executescript(DDL_PERFIL)
        # linha de perfil padrão (utilizador local)
        self.conn.execute(
            "INSERT OR IGNORE INTO perfil_utilizador (id) VALUES (1)"
        )
        self.conn.commit()

    def criar_tabelas(self) -> None:
        cursor = self.conn.cursor()

        # Tabela de factos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS factos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topico TEXT NOT NULL,
                facto TEXT,
                fonte TEXT,
                categoria TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(topico, facto)
            )
        """)

        # Tabela de conhecimentos
        cursor.execute("""
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
            )
        """)

        # Tabela de conselhos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conselhos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problema TEXT NOT NULL,
                conselho TEXT NOT NULL,
                categoria TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(problema, conselho)
            )
        """)

        # Tabela de habilidades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habilidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                exemplo_uso TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(nome)
            )
        """)

        # Tabela de histórias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                autor TEXT,
                categoria TEXT,
                origem TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(titulo, conteudo)
            )
        """)

        # Criar índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_factos_topico ON factos(topico)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_conhecimentos_pergunta ON conhecimentos(pergunta)"
        )

        self.conn.commit()

    def _normalizar_texto(self, texto: str) -> str:
        """Remove pontuação e normaliza texto para busca"""
        return re.sub(r"[!?.,;:]", "", texto.lower().strip())

    def _normalizar_texto2(self, texto: str) -> str:
        """Remove pontuação e normaliza texto para busca"""
        return re.sub(r"[!.,;:]", "", texto.lower().strip())

    def carregar_dados_em_memoria(self) -> None:
        """Carrega todos os dados em memória para busca rápida"""
        self.factos = self._carregar_todos("factos")
        self.conhecimentos = self._carregar_todos("conhecimentos")
        self.conselhos = self._carregar_todos("conselhos")
        self.historias = self._carregar_todos("historias")
        self.habilidades = self._carregar_todos("habilidades")

        print(
            f"Base de conhecimento carregada: {len(self.factos)} factos, "
            f"{len(self.conhecimentos)} conhecimentos, "
            f"{len(self.conselhos)} conselhos, "
            f"{len(self.historias)} histórias"
        )

        # Normalizar textos e embaralhar listas
        for fato in self.factos:
            fato["topico"] = self._normalizar_texto(fato["topico"])

        for conhecimento in self.conhecimentos:
            conhecimento["pergunta"] = self._normalizar_texto2(conhecimento["pergunta"])

        for conselho in self.conselhos:
            conselho["problema"] = self._normalizar_texto(conselho["problema"])

        for historia in self.historias:
            historia["titulo"] = self._normalizar_texto(historia["titulo"])

        for habilidade in self.habilidades:
            habilidade["nome"] = self._normalizar_texto(habilidade["nome"])

        # Ordenar e embaralhar
        self.factos.sort(key=lambda x: x["topico"])
        self.conhecimentos.sort(key=lambda x: x["pergunta"])
        self.conselhos.sort(key=lambda x: x["problema"])
        self.historias.sort(key=lambda x: x["titulo"])
        self.habilidades.sort(key=lambda x: x["nome"])

        shuffle(self.factos)
        shuffle(self.conhecimentos)
        shuffle(self.conselhos)
        shuffle(self.historias)
        shuffle(self.habilidades)

    def _carregar_todos(self, tabela: str) -> List[Dict[str, Any]]:
        """Carrega todos os registros de uma tabela"""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {tabela}")
        colunas = [desc[0] for desc in cursor.description]
        return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]

    @lru_cache(maxsize=1024)
    def pesquisar_factos_qradio(
        self, consulta: str, limite: int = 1, threshold: int = 100
    ) -> List[Dict[str, Any]]:
        """Busca simples e direta nos fatos usando QRatio"""
        if not consulta or not consulta.strip():
            return []

        consulta = self._normalizar_texto(consulta)
        resultados = []

        for fato in self.factos:
            similaridade = fuzz.QRatio(consulta, fato["topico"])

            if similaridade >= threshold:
                resultados.append(
                    {
                        "id": fato["id"],
                        "topico": fato["topico"],
                        "facto": fato["facto"],
                        "fonte": fato["fonte"],
                        "similaridade": similaridade,
                    }
                )

        if not resultados:
            return []

        resultados.sort(key=lambda x: x["similaridade"], reverse=True)
        return resultados[:limite]

    def pesquisar_factos_token_sort_ratio(
        self, consulta: str, limite: int = 1, threshold: int = 100
    ) -> List[Dict[str, Any]]:
        """Busca nos fatos usando token_sort_ratio"""
        if not consulta or not consulta.strip():
            return []

        consulta = self._normalizar_texto(consulta)
        resultados = []

        for fato in self.factos:
            similaridade = fuzz.token_sort_ratio(consulta, fato["topico"])

            if similaridade >= threshold:
                resultados.append(
                    {
                        "id": fato["id"],
                        "topico": fato["topico"],
                        "facto": fato["facto"],
                        "fonte": fato["fonte"],
                        "similaridade": similaridade,
                    }
                )

        if not resultados:
            return []

        resultados.sort(key=lambda x: x["similaridade"], reverse=True)
        return resultados[:limite]

    def pesquisar_conhecimento_qradio(
        self, pergunta: str, limite: int = 1, threshold: int = 85
    ) -> List[Dict[str, Any]]:
        """Busca nas perguntas/respostas usando QRatio"""
        if not pergunta or not pergunta.strip():
            return []

        pergunta = self._normalizar_texto(pergunta)
        resultados = []

        for conhecimento in self.conhecimentos:
            similaridade = fuzz.QRatio(pergunta, conhecimento["pergunta"])

            if similaridade >= threshold:
                resultados.append(
                    {
                        "id": conhecimento["id"],
                        "pergunta": conhecimento["pergunta"],
                        "resposta": conhecimento["resposta"],
                        "fonte": conhecimento["fonte"],
                        "similaridade": similaridade,
                    }
                )

        if not resultados:
            return []

        resultados.sort(key=lambda x: x["similaridade"], reverse=True)
        return resultados[:limite]

    def pesquisar_conhecimento_token_sort_ratio(
        self, pergunta: str, limite: int = 1, threshold: int = 100
    ) -> List[Dict[str, Any]]:
        """Busca nas perguntas/respostas usando token_sort_ratio"""
        if not pergunta or not pergunta.strip():
            return []

        pergunta = self._normalizar_texto(pergunta)
        resultados = []

        for conhecimento in self.conhecimentos:
            similaridade = fuzz.token_sort_ratio(pergunta, conhecimento["pergunta"])

            if similaridade >= threshold:
                resultados.append(
                    {
                        "id": conhecimento["id"],
                        "pergunta": conhecimento["pergunta"],
                        "resposta": conhecimento["resposta"],
                        "fonte": conhecimento["fonte"],
                        "similaridade": similaridade,
                    }
                )

        if not resultados:
            return []

        resultados.sort(key=lambda x: x["similaridade"], reverse=True)
        return resultados[:limite]

    @lru_cache(maxsize=512)
    def pesquisar_conselhos(
        self, problema: str, limite: int = 1, threshold: int = 85
    ) -> List[Dict[str, Any]]:
        """Busca nos conselhos usando WRatio"""
        if not problema or not problema.strip():
            return [
                {
                    "id": conselho["id"],
                    "problema": conselho["problema"],
                    "conselho": conselho["conselho"],
                    "categoria": conselho["categoria"],
                    "similaridade": 100,
                }
                for conselho in self.conselhos[:limite]
            ]

        problema = problema.lower().strip()
        resultados = []

        for conselho in self.conselhos:
            if problema in conselho["problema"]:
                similaridade = 100
            else:
                similaridade = fuzz.WRatio(problema, conselho["problema"])

            if similaridade >= threshold:
                resultados.append(
                    {
                        "id": conselho["id"],
                        "problema": conselho["problema"],
                        "conselho": conselho["conselho"],
                        "categoria": conselho["categoria"],
                        "similaridade": similaridade,
                    }
                )

        resultados.sort(key=lambda x: x["similaridade"], reverse=True)
        return resultados[:limite]

    def pesquisar_conselhos_qradio(
        self, problema: str, limite: int = 1, threshold: int = 85
    ) -> List[Dict[str, Any]]:
        """Busca nos conselhos usando QRatio"""
        if not problema or not problema.strip():
            return [
                {
                    "id": conselho["id"],
                    "problema": conselho["problema"],
                    "conselho": conselho["conselho"],
                    "categoria": conselho["categoria"],
                    "similaridade": 100,
                }
                for conselho in self.conselhos[:limite]
            ]

        problema = problema.lower().strip()
        resultados = []

        for conselho in self.conselhos:
            if problema in conselho["problema"]:
                similaridade = 100
            else:
                similaridade = fuzz.QRatio(problema, conselho["problema"])

            if similaridade >= threshold:
                resultados.append(
                    {
                        "id": conselho["id"],
                        "problema": conselho["problema"],
                        "conselho": conselho["conselho"],
                        "categoria": conselho["categoria"],
                        "similaridade": similaridade,
                    }
                )

        resultados.sort(key=lambda x: x["similaridade"], reverse=True)
        return resultados[:limite]

    @lru_cache(maxsize=512)
    def pesquisar_historias(
        self, titulo: str, limite: int = 1, threshold: int = 85
    ) -> List[Dict[str, Any]]:
        """Busca nas histórias"""
        if not titulo or not titulo.strip():
            return []

        titulo = titulo.lower().strip()
        resultados = []

        for historia in self.historias:
            if titulo in historia["titulo"]:
                similaridade = 100
            else:
                similaridade = fuzz.QRatio(titulo, historia["titulo"])

            if similaridade >= threshold:
                resultados.append(
                    {
                        "id": historia["id"],
                        "titulo": historia["titulo"],
                        "conteudo": historia["conteudo"],
                        "autor": historia["autor"],
                        "origem": historia["origem"],
                        "similaridade": similaridade,
                    }
                )

        resultados.sort(key=lambda x: x["similaridade"], reverse=True)
        return resultados[:limite]

    def listar_topicos_conhecimentos(self) -> List[str]:
        """Lista todos os tópicos e perguntas disponíveis"""
        self.cursor.execute("SELECT topico FROM factos")
        topicos = self.cursor.fetchall()
        lista_topico: List[str] = [item[0].lower() for item in topicos if item]

        self.cursor.execute("SELECT pergunta FROM conhecimentos")
        perguntas = self.cursor.fetchall()
        lista_pergunta: List[str] = [item[0].lower() for item in perguntas if item]

        return lista_topico + lista_pergunta

    def listar_habilidades(self) -> List[Dict[str, str]]:
        """Retorna lista com todas habilidades e suas descrições"""
        habilidades_lista: List[Dict[str, str]] = []
        for habilidade in self.habilidades:
            habilidades_lista.append(
                {
                    "nome": habilidade["nome"],
                    "descricao": habilidade["descricao"],
                    "exemplo_uso": habilidade["exemplo_uso"],
                }
            )
        return habilidades_lista

    def randon_fact(self, n=0):
        return f"{self.factos[n]['topico']} : {self.factos[n]['facto']}"

    def randon_knowledge(self, n=0):
        return f"{self.conhecimentos[n]['pergunta']} R: {self.conhecimentos[n]['resposta']}"

    def curiosidade(self):
        randf = randint(0, len(self.factos) - 1)
        randc = randint(0, len(self.conhecimentos) - 1)
        return random.choices([self.randon_fact(randf), self.randon_knowledge(randc)])[
            0
        ]


if __name__ == "__main__":
    print("Sistema de Busca de Conhecimento")
    kb = KnowledgeBase()

    print(kb.curiosidade())
