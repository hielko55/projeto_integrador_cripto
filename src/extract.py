"""Extração: lê as abas da planilha da Receita Federal e devolve DataFrames brutos.

A planilha não é "tidy": cada aba tem texto explicativo no topo, cabeçalhos em
várias linhas e o mês escrito por extenso ("Agosto de 2019"). Aqui só
localizamos as linhas de dados e nomeamos as colunas; a limpeza de tipos e as
validações ficam em `clean.py`.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from . import config

_PADRAO_MES = re.compile(r"^\s*[A-Za-zÀ-ÿ]+ de \d{4}\s*$")

COLUNAS_R1 = [
    "mes",
    "ext_pf", "ext_pj", "ext_subtotal",
    "sem_pf", "sem_pj", "sem_subtotal",
    "exchange_br", "total_geral",
]
COLUNAS_R2 = ["mes", "cpf_unicos", "cnpj_unicos"]
COLUNAS_R3 = ["mes", "ops_fem_pct", "ops_masc_pct", "valor_fem_pct", "valor_masc_pct"]
COLUNAS_R4 = ["criptoativo", "mes", "n_operacoes", "valor_total", "valor_medio"]


def _ler_aba(caminho: Path, aba: str) -> pd.DataFrame:
    return pd.read_excel(caminho, sheet_name=aba, header=None, engine="xlrd")


def _linhas_de_dados(df: pd.DataFrame, coluna_mes: int) -> pd.DataFrame:
    """Mantém só as linhas cuja coluna de mês casa com 'Mês de AAAA'."""
    mascara = df.iloc[:, coluna_mes].astype(str).str.match(_PADRAO_MES)
    return df.loc[mascara].reset_index(drop=True)


def extrair_relatorio1(caminho: Path = config.ARQUIVO_FONTE) -> pd.DataFrame:
    df = _linhas_de_dados(_ler_aba(caminho, config.ABA_R1), 0)
    df = df.iloc[:, : len(COLUNAS_R1)]
    df.columns = COLUNAS_R1
    return df


def extrair_relatorio2(caminho: Path = config.ARQUIVO_FONTE) -> pd.DataFrame:
    df = _linhas_de_dados(_ler_aba(caminho, config.ABA_R2), 0)
    df = df.iloc[:, : len(COLUNAS_R2)]
    df.columns = COLUNAS_R2
    return df


def extrair_relatorio3(caminho: Path = config.ARQUIVO_FONTE) -> pd.DataFrame:
    df = _linhas_de_dados(_ler_aba(caminho, config.ABA_R3), 0)
    df = df.iloc[:, : len(COLUNAS_R3)]
    df.columns = COLUNAS_R3
    return df


def extrair_relatorio4(caminho: Path = config.ARQUIVO_FONTE) -> pd.DataFrame:
    # No Relatório 4 o mês está na 2ª coluna (a 1ª é o criptoativo).
    df = _linhas_de_dados(_ler_aba(caminho, config.ABA_R4), 1)
    df = df.iloc[:, : len(COLUNAS_R4)]
    df.columns = COLUNAS_R4
    return df


def extrair_tudo(caminho: Path = config.ARQUIVO_FONTE) -> dict[str, pd.DataFrame]:
    """Devolve os quatro relatórios brutos, indexados por nome curto."""
    if not Path(caminho).exists():
        raise FileNotFoundError(
            f"Planilha não encontrada em {caminho}. "
            "Coloque o arquivo da Receita em data/raw/."
        )
    return {
        "r1": extrair_relatorio1(caminho),
        "r2": extrair_relatorio2(caminho),
        "r3": extrair_relatorio3(caminho),
        "r4": extrair_relatorio4(caminho),
    }
