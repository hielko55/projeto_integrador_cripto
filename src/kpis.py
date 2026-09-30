"""Cálculo dos indicadores-chave (KPIs).

Cada função devolve um DataFrame pronto para gráfico/tabela. A justificativa de
cada KPI para a decisão da organização está em `docs/kpis.md`.

Unidades: Relatório 1 em R$ milhões (mi) ou bilhões (bi); Relatório 4 em R$.
"""
from __future__ import annotations

import pandas as pd

from . import config


# ------------------------------------------------------------ KPI 1 — volume
def kpi_volume(r1: pd.DataFrame) -> pd.DataFrame:
    """Volume mensal, acumulado de 12 meses e variação anual (YoY)."""
    df = r1[["mes", "total_geral"]].copy().sort_values("mes")
    df["volume_bi"] = df["total_geral"] / 1_000
    df["acum_12m_bi"] = df["volume_bi"].rolling(12).sum()
    df["yoy_mensal"] = df["volume_bi"].pct_change(12)
    df["yoy_acum_12m"] = df["acum_12m_bi"].pct_change(12)
    return df.drop(columns="total_geral").reset_index(drop=True)


# ------------------------------------------------------------ KPI 2 — canais
def kpi_canais(r1: pd.DataFrame) -> pd.DataFrame:
    """Participação de cada canal no total: exchange BR × exchange exterior × sem exchange."""
    df = r1[["mes", "exchange_br", "ext_subtotal", "sem_subtotal", "total_geral"]].copy()
    df = df.rename(columns={
        "exchange_br": "Exchanges no Brasil",
        "ext_subtotal": "Exchanges no exterior",
        "sem_subtotal": "Sem exchange (P2P)",
    })
    canais = ["Exchanges no Brasil", "Exchanges no exterior", "Sem exchange (P2P)"]
    longo = df.melt(id_vars=["mes", "total_geral"], value_vars=canais,
                    var_name="canal", value_name="valor_rs_mi")
    longo["participacao"] = longo["valor_rs_mi"] / longo["total_geral"]
    return longo.drop(columns="total_geral").sort_values(["mes", "canal"]).reset_index(drop=True)


# ------------------------------------------------------------ KPI 3 — PF × PJ
def kpi_pf_pj(r1: pd.DataFrame) -> pd.DataFrame:
    """PF × PJ entre quem declara por conta própria (exclui exchanges no Brasil, sempre PJ)."""
    df = r1[["mes", "pf_declarante_rs_mi", "pj_declarante_rs_mi",
             "base_autodeclarada_rs_mi", "share_pf_autodeclarada"]].copy()
    df["share_pj_autodeclarada"] = 1 - df["share_pf_autodeclarada"]
    return df


# --------------------------------------------------- KPI 4 — declarantes únicos
def kpi_declarantes(r2: pd.DataFrame) -> pd.DataFrame:
    df = r2.sort_values("mes").copy()
    df["cpf_yoy"] = df["cpf_unicos"].pct_change(12)
    df["cnpj_yoy"] = df["cnpj_unicos"].pct_change(12)
    df["cpf_media_6m"] = df["cpf_unicos"].rolling(6).median()
    df["cnpj_media_6m"] = df["cnpj_unicos"].rolling(6).median()
    return df.reset_index(drop=True)


# ------------------------------------------------------------- KPI 5 — gênero
def kpi_genero(r3: pd.DataFrame) -> pd.DataFrame:
    return r3[["mes", "ops_fem_pct", "valor_fem_pct", "gap_fem_pp", "ticket_relativo_fem"]].copy()


# ------------------------------------------------ KPI 6 — mercado por criptoativo
def kpi_ativos(r4: pd.DataFrame, inicio=None, fim=None) -> pd.DataFrame:
    """Ranking de ativos no período: valor, operações, ticket médio e participação."""
    df = r4.copy()
    if inicio is not None:
        df = df[df["mes"] >= pd.Timestamp(inicio)]
    if fim is not None:
        df = df[df["mes"] <= pd.Timestamp(fim)]
    ag = (df.groupby(["criptoativo", "grupo"], as_index=False)
            .agg(valor_total=("valor_total", "sum"), n_operacoes=("n_operacoes", "sum")))
    ag["ticket_medio"] = ag["valor_total"] / ag["n_operacoes"]
    ag["participacao"] = ag["valor_total"] / ag["valor_total"].sum()
    return ag.sort_values("valor_total", ascending=False).reset_index(drop=True)


def kpi_composicao(r4: pd.DataFrame) -> pd.DataFrame:
    """Participação mensal de cada grupo (Bitcoin, Ethereum, Stablecoins, Outros) no valor do R4."""
    g = r4.groupby(["mes", "grupo"], as_index=False)["valor_total"].sum()
    g["participacao"] = g["valor_total"] / g.groupby("mes")["valor_total"].transform("sum")
    return g


def kpi_concentracao(r4: pd.DataFrame) -> pd.DataFrame:
    """Concentração mensal do mercado: participação do Top-5 e índice HHI (0 a 10.000)."""
    def _calc(x: pd.DataFrame) -> pd.Series:
        part = x["valor_total"] / x["valor_total"].sum()
        return pd.Series({
            "top5_participacao": part.nlargest(5).sum(),
            "hhi": float((part ** 2).sum() * 10_000),
            "n_ativos": int(len(x)),
        })
    return r4.groupby("mes").apply(_calc, include_groups=False).reset_index()


def kpi_ticket(r4: pd.DataFrame) -> pd.DataFrame:
    """Ticket médio mensal por grupo (valor total ÷ nº de operações)."""
    g = (r4.groupby(["mes", "grupo"], as_index=False)
           .agg(valor_total=("valor_total", "sum"), n_operacoes=("n_operacoes", "sum")))
    g["ticket_medio"] = g["valor_total"] / g["n_operacoes"]
    return g


# ------------------------------------------------------------ cartões-resumo
def resumo(d: dict[str, pd.DataFrame]) -> dict:
    """Números de manchete (últimos 12 meses vs. 12 anteriores) para os cartões do painel."""
    r1, r2, r3 = d["r1"], d["r2"], d["r3"]
    vol = kpi_volume(r1)
    ult = vol.iloc[-1]
    ult_mes = r1.iloc[-1]
    ano_ant = r1.iloc[-13] if len(r1) >= 13 else r1.iloc[0]
    concentr = kpi_concentracao(d["r4"]).iloc[-1]
    comp = kpi_composicao(d["r4"])
    comp_ult = comp[comp["mes"] == comp["mes"].max()].set_index("grupo")["participacao"]
    return {
        "ultimo_mes": ult_mes["mes"],
        "volume_ultimo_mes_bi": float(ult["volume_bi"]),
        "acum_12m_bi": float(ult["acum_12m_bi"]),
        "yoy_acum_12m": float(ult["yoy_acum_12m"]),
        "share_exchange_br_ult": float(ult_mes["share_exchange_br"]),
        "share_exchange_br_ano_ant": float(ano_ant["share_exchange_br"]),
        "share_sem_exchange_ult": float(ult_mes["share_sem_exchange"]),
        "share_pf_autodeclarada_ult": float(ult_mes["share_pf_autodeclarada"]),
        "cpf_ult": int(r2.iloc[-1]["cpf_unicos"]),
        "cnpj_ult": int(r2.iloc[-1]["cnpj_unicos"]),
        "fem_ops_ult": float(r3.iloc[-1]["ops_fem_pct"]),
        "fem_valor_ult": float(r3.iloc[-1]["valor_fem_pct"]),
        "btc_share_ult": float(comp_ult.get("Bitcoin", 0)),
        "stable_share_ult": float(comp_ult.get("Stablecoins", 0)),
        "top5_ult": float(concentr["top5_participacao"]),
        "hhi_ult": float(concentr["hhi"]),
    }
