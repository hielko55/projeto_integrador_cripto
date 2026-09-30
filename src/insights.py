"""Achados calculados a partir dos dados (base do Data Storytelling).

Os textos são montados com os números reais da planilha; se a base for
atualizada, os achados acompanham. Nenhum número é digitado à mão.
"""
from __future__ import annotations

import pandas as pd

from . import config, kpis, quality


def _pct(x: float, casas: int = 1) -> str:
    return f"{x * 100:.{casas}f}%".replace(".", ",")


def _num(x: float, casas: int = 1) -> str:
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _janela(df: pd.DataFrame, n: int, fim: bool = True) -> pd.DataFrame:
    return df.tail(n) if fim else df.head(n)


def gerar_achados(d: dict[str, pd.DataFrame]) -> list[dict]:
    r1, r2, r3, r4 = d["r1"], d["r2"], d["r3"], d["r4"]
    achados: list[dict] = []
    ini, fim = r1["mes"].min(), r1["mes"].max()
    periodo = f"{ini:%m/%Y} a {fim:%m/%Y}"

    # 1 — Crescimento do volume
    vol = kpis.kpi_volume(r1)
    u = vol.iloc[-1]
    pico = vol.loc[vol["volume_bi"].idxmax()]
    achados.append({
        "id": "volume",
        "titulo": "O volume declarado continua em expansão",
        "texto": (
            f"Nos 12 meses até {fim:%m/%Y}, foram declarados R$ {_num(u['acum_12m_bi'])} bilhões "
            f"em operações com criptoativos, {_pct(u['yoy_acum_12m'])} acima dos 12 meses anteriores. "
            f"O maior mês da série foi {pico['mes']:%m/%Y}, com R$ {_num(pico['volume_bi'])} bilhões."
        ),
        "evidencia": "Relatório 1 — total geral mensal",
    })

    # 2 — Stablecoins dominam
    comp = kpis.kpi_composicao(r4)
    ult12 = comp[comp["mes"] > comp["mes"].max() - pd.DateOffset(months=12)]
    prim12 = comp[comp["mes"] < comp["mes"].min() + pd.DateOffset(months=12)]

    def _part(base: pd.DataFrame, grupo: str) -> float:
        tot = base["valor_total"].sum()
        return float(base.loc[base["grupo"] == grupo, "valor_total"].sum() / tot)

    st_ult, st_prim = _part(ult12, "Stablecoins"), _part(prim12, "Stablecoins")
    btc_ult, btc_prim = _part(ult12, "Bitcoin"), _part(prim12, "Bitcoin")
    rank = kpis.kpi_ativos(r4, inicio=comp["mes"].max() - pd.DateOffset(months=11))
    lider = rank.iloc[0]
    achados.append({
        "id": "stablecoins",
        "titulo": "As stablecoins viraram o centro do mercado",
        "texto": (
            f"Nos últimos 12 meses, stablecoins somam {_pct(st_ult)} do valor negociado nos principais ativos "
            f"(eram {_pct(st_prim)} nos 12 primeiros meses da série), enquanto o Bitcoin caiu de "
            f"{_pct(btc_prim)} para {_pct(btc_ult)}. O {lider['criptoativo']} sozinho responde por "
            f"{_pct(lider['participacao'])} do valor."
        ),
        "evidencia": "Relatório 4 — valor por criptoativo (classificação de stablecoins é premissa do projeto)",
    })

    # 3 — Concentração
    conc = kpis.kpi_concentracao(r4).iloc[-1]
    achados.append({
        "id": "concentracao",
        "titulo": "Mercado altamente concentrado em poucos ativos",
        "texto": (
            f"Em {fim:%m/%Y}, os 5 maiores ativos concentram {_pct(conc['top5_participacao'])} do valor "
            f"(HHI de {_num(conc['hhi'], 0)} em 10.000). Acompanhar a diversidade de ativos é tão "
            f"importante quanto acompanhar o volume."
        ),
        "evidencia": "Relatório 4 — participação por ativo no mês",
    })

    # 4 — Canais
    a, b = _janela(r1, 12), r1.iloc[-24:-12]
    br_a = a["exchange_br"].sum() / a["total_geral"].sum()
    br_b = b["exchange_br"].sum() / b["total_geral"].sum()
    p2p_a = a["sem_subtotal"].sum() / a["total_geral"].sum()
    p2p_b = b["sem_subtotal"].sum() / b["total_geral"].sum()
    sentido = "perderam" if br_a < br_b else "ganharam"
    achados.append({
        "id": "canais",
        "titulo": "Exchanges no Brasil seguem à frente, mas o peso dos canais mudou",
        "texto": (
            f"Nos últimos 12 meses, exchanges no Brasil intermediaram {_pct(br_a)} do volume e "
            f"{sentido} participação frente aos 12 meses anteriores ({_pct(br_b)}). "
            f"As operações sem exchange (P2P) passaram de {_pct(p2p_b)} para {_pct(p2p_a)}."
        ),
        "evidencia": "Relatório 1 — canal de intermediação",
    })

    # 5 — Gênero
    g = _janela(r3, 12)
    fem_ops, fem_val = g["ops_fem_pct"].mean(), g["valor_fem_pct"].mean()
    ticket_rel = g["ticket_relativo_fem"].mean()
    achados.append({
        "id": "genero",
        "titulo": "Mulheres participam mais em número de operações do que em valor",
        "texto": (
            f"Nos últimos 12 meses, mulheres responderam em média por {_pct(fem_ops / 100)} das operações "
            f"e {_pct(fem_val / 100)} do valor; o ticket médio feminino equivale a cerca de "
            f"{_pct(ticket_rel, 0)} do masculino."
        ),
        "evidencia": "Relatório 3 — apenas pessoas físicas, por gênero declarado",
    })

    # 6 — Qualidade
    q = quality.detectar_quebras(r2)
    cob = quality.cobertura_r4_sobre_r1(d)
    achados.append({
        "id": "qualidade",
        "titulo": "Os indicadores de declarantes únicos exigem cautela",
        "texto": (
            f"A série de CPF/CNPJ únicos tem {len(q)} quebras bruscas entre meses consecutivos, "
            f"que não parecem refletir mudança real de comportamento. Uma hipótese é o efeito de declarações "
            f"extemporâneas e retificadoras (a Receita avisa que a base é recalculada), mas a planilha não "
            f"permite confirmar. Por isso o painel usa mediana móvel e destaca esses meses. O Relatório 4 cobre em média "
            f"{_pct(cob['cobertura'].mean(), 0)} do total do Relatório 1, pois traz só compra e venda dos principais ativos."
        ),
        "evidencia": "Relatórios 2 e 4 — ver aba Qualidade do painel",
    })

    for x in achados:
        x["periodo"] = periodo
    return achados


def achados_em_markdown(achados: list[dict]) -> str:
    linhas = [
        "# Achados gerados automaticamente",
        "",
        f"_Fonte: {config.FONTE}. Período analisado: {achados[0]['periodo']}._",
        "",
        "> Arquivo gerado por `python -m src.pipeline`. Não edite à mão: reexecute o pipeline.",
        "",
    ]
    for i, a in enumerate(achados, 1):
        linhas += [f"## {i}. {a['titulo']}", "", a["texto"], "", f"*Evidência:* {a['evidencia']}", ""]
    return "\n".join(linhas)
