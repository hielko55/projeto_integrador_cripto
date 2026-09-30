"""Limpeza: converte tipos, padroniza datas e cria colunas derivadas.

Convenções:
- `mes` vira a data do 1º dia do mês (datetime64), para ordenar e filtrar.
- Valores do Relatório 1 ficam em R$ milhões (como na fonte);
  valores do Relatório 4 ficam em R$ (como na fonte). As colunas derivadas
  deixam a unidade explícita no nome (`_rs_mi`, `_rs`).
"""
from __future__ import annotations

import pandas as pd

from . import config

MESES_PT = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}


def parse_mes(texto: str) -> pd.Timestamp:
    """'Agosto de 2019' -> Timestamp('2019-08-01')."""
    nome, _, ano = str(texto).strip().lower().partition(" de ")
    if nome not in MESES_PT:
        raise ValueError(f"Mês não reconhecido: {texto!r}")
    return pd.Timestamp(year=int(ano), month=MESES_PT[nome], day=1)


def _numerico(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    df = df.copy()
    for c in colunas:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def limpar_r1(bruto: pd.DataFrame) -> pd.DataFrame:
    """Valores por tipo de declaração (R$ milhões) + participações."""
    df = bruto.copy()
    df["mes"] = df["mes"].map(parse_mes)
    df = _numerico(df, [c for c in df.columns if c != "mes"])
    df = df.sort_values("mes").drop_duplicates("mes").reset_index(drop=True)

    # Quem declara: exchanges no Brasil são sempre PJ (nota da fonte) e declaram em nome
    # dos clientes. Por isso, a comparação PF x PJ só faz sentido entre quem declara por
    # conta própria (exchange no exterior ou sem exchange).
    df["pf_declarante_rs_mi"] = df["ext_pf"] + df["sem_pf"]
    df["pj_declarante_rs_mi"] = df["ext_pj"] + df["sem_pj"]
    df["base_autodeclarada_rs_mi"] = df["ext_subtotal"] + df["sem_subtotal"]
    df["share_pf_autodeclarada"] = df["pf_declarante_rs_mi"] / df["base_autodeclarada_rs_mi"]
    # Canal: onde a operação foi intermediada.
    df["share_exchange_br"] = df["exchange_br"] / df["total_geral"]
    df["share_exchange_ext"] = df["ext_subtotal"] / df["total_geral"]
    df["share_sem_exchange"] = df["sem_subtotal"] / df["total_geral"]
    df["total_geral_bi"] = df["total_geral"] / 1_000
    return df


def limpar_r2(bruto: pd.DataFrame) -> pd.DataFrame:
    df = bruto.copy()
    df["mes"] = df["mes"].map(parse_mes)
    df = _numerico(df, ["cpf_unicos", "cnpj_unicos"])
    return df.sort_values("mes").drop_duplicates("mes").reset_index(drop=True)


def limpar_r3(bruto: pd.DataFrame) -> pd.DataFrame:
    df = bruto.copy()
    df["mes"] = df["mes"].map(parse_mes)
    df = _numerico(df, [c for c in df.columns if c != "mes"])
    df = df.sort_values("mes").drop_duplicates("mes").reset_index(drop=True)
    # Diferença em pontos percentuais entre a participação nas operações e no valor.
    df["gap_fem_pp"] = df["ops_fem_pct"] - df["valor_fem_pct"]
    # Ticket relativo: >1 significa ticket feminino maior que o masculino.
    df["ticket_relativo_fem"] = (
        (df["valor_fem_pct"] / df["ops_fem_pct"])
        / (df["valor_masc_pct"] / df["ops_masc_pct"])
    )
    return df


def classificar_ativo(ativo: str) -> str:
    """Grupo analítico do ativo (premissa do projeto — ver config.STABLECOINS)."""
    if ativo == "BTC":
        return "Bitcoin"
    if ativo == "ETH":
        return "Ethereum"
    if ativo in config.STABLECOINS:
        return "Stablecoins"
    return "Outros ativos"


def limpar_r4(bruto: pd.DataFrame) -> pd.DataFrame:
    df = bruto.copy()
    df["mes"] = df["mes"].map(parse_mes)
    df["criptoativo"] = df["criptoativo"].astype(str).str.strip().str.upper()
    df = _numerico(df, ["n_operacoes", "valor_total", "valor_medio"])
    df = df.sort_values(["criptoativo", "mes"]).reset_index(drop=True)
    df["grupo"] = df["criptoativo"].map(classificar_ativo)
    df["valor_total_mi"] = df["valor_total"] / 1_000_000
    return df


def limpar_tudo(brutos: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {
        "r1": limpar_r1(brutos["r1"]),
        "r2": limpar_r2(brutos["r2"]),
        "r3": limpar_r3(brutos["r3"]),
        "r4": limpar_r4(brutos["r4"]),
    }
