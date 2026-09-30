"""Gráficos (Plotly) com identidade visual única e paleta acessível (Okabe-Ito).

Escolhas de visualização (justificadas em docs/justificativa_visualizacoes.md):
- Séries no tempo  -> linha/área (mostram tendência e ruptura);
- Composição       -> área 100% empilhada (mostra mudança de participação);
- Ranking          -> barras horizontais ordenadas (comparação por categoria);
- Escalas muito diferentes (CPF × CNPJ) -> painéis separados, nunca eixo duplo.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import PALETA as C

COR_GRUPO = {
    "Bitcoin": C["laranja"],
    "Ethereum": C["azul_claro"],
    "Stablecoins": C["verde"],
    "Outros ativos": C["cinza"],
}
COR_CANAL = {
    "Exchanges no Brasil": C["azul"],
    "Exchanges no exterior": C["laranja"],
    "Sem exchange (P2P)": C["vermelho"],
}
_FONTE = "Fonte: Receita Federal — Criptoativos, Dados Abertos (26/08/2026)"


def _base(fig: go.Figure, altura: int = 380, titulo_y: str | None = None, legenda: bool = True) -> go.Figure:
    fig.update_layout(
        height=altura,
        template="simple_white",
        font=dict(family="Arial, sans-serif", size=13, color="#222"),
        margin=dict(l=10, r=10, t=30, b=90),
        hovermode="x unified",
        showlegend=legenda,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        separators=",.",  # vírgula decimal, ponto de milhar (padrão pt-BR)
        annotations=list(fig.layout.annotations) + [dict(
            text=_FONTE, xref="paper", yref="paper", x=0, y=-0.22, showarrow=False,
            font=dict(size=10, color="#666"), xanchor="left")],
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EEE", title_text=titulo_y)
    return fig


# ------------------------------------------------------------------ volume
def fig_volume(vol: pd.DataFrame) -> go.Figure:
    df = vol.copy()
    df["media_12m"] = df["acum_12m_bi"] / 12
    fig = go.Figure()
    fig.add_bar(x=df["mes"], y=df["volume_bi"], name="Volume mensal",
                marker_color=C["azul_claro"], hovertemplate="%{y:,.1f} R$ bi")
    fig.add_scatter(x=df["mes"], y=df["media_12m"], name="Média móvel de 12 meses",
                    line=dict(color=C["azul"], width=3), hovertemplate="%{y:,.1f} R$ bi")
    return _base(fig, titulo_y="R$ bilhões por mês")


# ------------------------------------------------------------------ canais
def fig_canais(canais: pd.DataFrame, participacao: bool = True) -> go.Figure:
    col = "participacao" if participacao else "valor_rs_mi"
    fig = go.Figure()
    for canal, cor in COR_CANAL.items():
        d = canais[canais["canal"] == canal]
        y = d[col] * (100 if participacao else 1 / 1000)
        fig.add_scatter(
            x=d["mes"], y=y, name=canal, stackgroup="um", mode="lines",
            line=dict(width=0.5, color=cor), fillcolor=cor,
            hovertemplate="%{y:.1f}%" if participacao else "R$ %{y:,.1f} bi",
        )
    if participacao:
        fig.update_yaxes(range=[0, 100], ticksuffix="%")
    return _base(fig, titulo_y="% do valor total" if participacao else "R$ bilhões por mês")


def fig_pf_pj(pf_pj: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=pf_pj["mes"], y=pf_pj["share_pf_autodeclarada"] * 100, name="Pessoa física",
                    line=dict(color=C["rosa"], width=3), hovertemplate="%{y:.1f}%")
    fig.add_scatter(x=pf_pj["mes"], y=pf_pj["share_pj_autodeclarada"] * 100, name="Pessoa jurídica",
                    line=dict(color=C["azul"], width=3), hovertemplate="%{y:.1f}%")
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    return _base(fig, titulo_y="% do valor autodeclarado")


# -------------------------------------------------------------- declarantes
def fig_declarantes(decl: pd.DataFrame, quebras: pd.DataFrame | None = None) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
                        subplot_titles=("Pessoas físicas (CPF únicos)", "Pessoas jurídicas (CNPJ únicos)"))
    for linha, (col, med, cor, rotulo) in enumerate(
        [("cpf_unicos", "cpf_media_6m", C["rosa"], "CPF"), ("cnpj_unicos", "cnpj_media_6m", C["azul"], "CNPJ")], start=1
    ):
        fig.add_scatter(x=decl["mes"], y=decl[col], name=f"{rotulo} no mês", mode="lines",
                        line=dict(color=cor, width=1.5), opacity=0.55,
                        hovertemplate="%{y:,.0f}", row=linha, col=1, showlegend=False)
        fig.add_scatter(x=decl["mes"], y=decl[med], name=f"{rotulo} — mediana móvel 6 meses", mode="lines",
                        line=dict(color=cor, width=3), hovertemplate="%{y:,.0f}", row=linha, col=1, showlegend=False)
        if quebras is not None and not quebras.empty:
            q = quebras[quebras["serie"] == rotulo].merge(decl[["mes", col]], on="mes")
            fig.add_scatter(x=q["mes"], y=q[col], mode="markers", name="Quebra sinalizada",
                            marker=dict(symbol="x", size=10, color=C["vermelho"], line=dict(width=2)),
                            hovertemplate="Quebra: %{y:,.0f}", row=linha, col=1, showlegend=(linha == 1))
    fig.update_yaxes(tickformat=",.0f")
    return _base(fig, altura=520)


# ------------------------------------------------------------------ gênero
def fig_genero(gen: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=gen["mes"], y=gen["ops_fem_pct"], name="% das operações",
                    line=dict(color=C["rosa"], width=3), hovertemplate="%{y:.1f}%")
    fig.add_scatter(x=gen["mes"], y=gen["valor_fem_pct"], name="% do valor",
                    line=dict(color=C["azul"], width=3, dash="dash"), hovertemplate="%{y:.1f}%")
    fig.update_yaxes(range=[0, 50], ticksuffix="%")
    return _base(fig, titulo_y="Participação feminina (pessoas físicas)")


# -------------------------------------------------------- ativos / mercado
def fig_ranking(rank: pd.DataFrame, top_n: int = 10) -> go.Figure:
    d = rank.head(top_n).iloc[::-1]
    fig = go.Figure(go.Bar(
        x=d["participacao"] * 100, y=d["criptoativo"], orientation="h",
        marker_color=[COR_GRUPO[g] for g in d["grupo"]],
        text=[f"{p:.1f}%".replace(".", ",") for p in d["participacao"] * 100], textposition="outside",
        customdata=d[["valor_total", "n_operacoes", "ticket_medio"]],
        hovertemplate=("<b>%{y}</b><br>Valor: R$ %{customdata[0]:,.0f}<br>"
                       "Operações: %{customdata[1]:,.0f}<br>Ticket médio: R$ %{customdata[2]:,.2f}<extra></extra>"),
    ))
    fig.update_xaxes(ticksuffix="%", range=[0, max(5, d["participacao"].max() * 100 * 1.18)])
    fig = _base(fig, altura=max(300, 34 * len(d) + 90), legenda=False)
    fig.update_layout(hovermode="closest")
    return fig


def fig_composicao(comp: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for grupo in ["Stablecoins", "Bitcoin", "Ethereum", "Outros ativos"]:
        d = comp[comp["grupo"] == grupo]
        fig.add_scatter(x=d["mes"], y=d["participacao"] * 100, name=grupo, stackgroup="um",
                        mode="lines", line=dict(width=0.5, color=COR_GRUPO[grupo]),
                        fillcolor=COR_GRUPO[grupo], hovertemplate="%{y:.1f}%")
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    return _base(fig, titulo_y="% do valor negociado")


def fig_concentracao(conc: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=conc["mes"], y=conc["top5_participacao"] * 100, name="Participação dos 5 maiores ativos",
                    line=dict(color=C["azul"], width=3), hovertemplate="%{y:.1f}%")
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    return _base(fig, altura=300, titulo_y="Top-5 no valor total", legenda=False)


def fig_ticket(ticket: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for grupo, cor in COR_GRUPO.items():
        d = ticket[ticket["grupo"] == grupo]
        fig.add_scatter(x=d["mes"], y=d["ticket_medio"], name=grupo,
                        line=dict(color=cor, width=2.5), hovertemplate="R$ %{y:,.0f}")
    fig.update_yaxes(type="log")
    return _base(fig, titulo_y="Ticket médio por operação (R$, escala log)")


# --------------------------------------------------------------- qualidade
def fig_cobertura(cob: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=cob["mes"], y=cob["cobertura"] * 100, name="Relatório 4 ÷ Relatório 1",
                    line=dict(color=C["azul"], width=3), hovertemplate="%{y:.1f}%")
    fig.update_yaxes(range=[0, 105], ticksuffix="%")
    return _base(fig, altura=300, titulo_y="Cobertura do Relatório 4", legenda=False)
