"""Ponto de entrada: python -m logica.knowledge_base [--db caminho/cerebro.db]"""

import argparse

from . import DB_PADRAO, popular_db


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Popula a base de dados do Jeelsia com dados semente (idempotente)."
    )
    parser.add_argument(
        "--db", default=DB_PADRAO, help="caminho do ficheiro SQLite (default: %(default)s)"
    )
    args = parser.parse_args()
    popular_db(args.db)


if __name__ == "__main__":
    main()
