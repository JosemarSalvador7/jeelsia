"""Funções utilitárias de normalização e análise de similaridade de texto."""

import re

from rapidfuzz import fuzz


def normalizar_texto(texto: str) -> str:
    """Normaliza texto removendo caracteres especiais e espaços duplicados."""
    try:
        texto = re.sub(r"[^\w\s]", "", texto)
        texto = re.sub(r"\s{2,}", " ", texto)
        return texto.lower().strip()
    except Exception:
        return texto.lower().strip() if texto else ""


def analisar_similaridade(
    frase: str, lista: list, threshold: int = 90, token_threshold: int = 90
) -> bool:
    """Analisa similaridade entre uma frase e os itens de uma lista.

    Retorna True se algum item da lista atingir o limite (threshold) de
    similaridade com a frase, usando QRatio ou token_sort_ratio.
    """
    try:
        if not lista:
            return False

        frase = normalizar_texto(frase)
        for linha in lista:
            try:
                if fuzz.QRatio(f"{frase}", f"{linha}") >= threshold:
                    return True
                if fuzz.token_sort_ratio(f"{frase}", f"{linha}") >= token_threshold:
                    return True
            except Exception:
                continue
        return False
    except Exception:
        return False
