"""Painel analítico — Criptoativos declarados à Receita Federal (IN RFB 1.888/2019).

Executar (a partir da raiz do projeto):
    python -m src.pipeline            # gera data/processed/
    streamlit run app/dashboard.py

O painel lê SOMENTE de data/processed/ e segue a ordem do Data Storytelling:
contexto -> panorama -> canais e perfil -> mercado -> gênero -> qualidade -> conclusões.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import charts, config, insights, kpis, quality  # noqa: E402
from src.pipeline import carregar_processados  # noqa: E402

st.set_page_config(page_title="Criptoativos no Brasil — painel", page_icon="📊", layout="wide")


# ------------------------------------------------------------------ dados
@st.cache_data(show_spinner="Carregando dados...")
def carregar() -> dict[str, pd.DataFrame]:
    return carregar_processados()


def fmt_bi(x: float) -> str:
    return f"R$ {x:,.1f} bi".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(x: float, casas: int = 1) -> str:
    return f"{x * 100:.{casas}f}%".replace(".", ",")


def fmt_int(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".")


try:
    dados = carregar()
except FileNotFoundError as erro:
    st.error(str(erro))
    st.stop()

r1, r2, r3, r4 = dados["r1"], dados["r2"], dados["r3"], dados["r4"]
meses = sorted(r1["mes"].unique())  # datas (numpy datetime64), em ordem

# ---------------------------------------------------------------- filtros
with st.sidebar:
    st.header("Filtros")
    pos_ini, pos_fim = st.select_slider(
        "Período", options=list(range(len(meses))), value=(0, len(meses) - 1),
        format_func=lambda i: pd.Timestamp(meses[i]).strftime("%m/%Y"), key="periodo",
    )
    st.caption("O período vale para todas as abas.")
    st.divider()
    st.markdown(
        f"**Organização parceira**  \n{config.ORGANIZACAO}\n\n"
        f"**Público do painel**  \n{config.PUBLICO_ALVO}\n\n"
        f"**Decisão apoiada**  \n{config.DECISAO_APOIADA}"
    )
    st.divider()
    st.caption(config.FONTE)

ini, fi = pd.Timestamp(meses[pos_ini]), pd.Timestamp(meses[pos_fim])


def recorte(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["mes"] >= ini) & (df["mes"] <= fi)].reset_index(drop=True)


f1, f2, f3, f4 = recorte(r1), recorte(r2), recorte(r3), recorte(r4)
if f1.empty:
    st.warning("Nenhum dado no período selecionado.")
    st.stop()

# ---------------------------------------------------------------- cabeçalho
st.title("Criptoativos no Brasil: quanto, por onde e com quais ativos")
st.caption(
    f"Dados declarados à Receita Federal · {ini:%m/%Y} a {fi:%m/%Y} · "
    "valores em reais · base pública (dados abertos)"
)

tabs = st.tabs([
    "1 · Panorama", "2 · Canais e perfil", "3 · Mercado por ativo",
    "4 · Gênero", "5 · Qualidade dos dados", "6 · Conclusões",
])

# ------------------------------------------------------------ 1 Panorama
with tabs[0]:
    resumo = kpis.resumo(dados)
    _sentido = "cresceu" if resumo["yoy_acum_12m"] >= 0 else "caiu"
    st.subheader(
        f"O volume dos últimos 12 meses {_sentido} {fmt_pct(abs(resumo['yoy_acum_12m']))} "
        f"e {fmt_pct(resumo['stable_share_ult'], 0)} do valor está em stablecoins"
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Volume, últimos 12 meses", fmt_bi(resumo["acum_12m_bi"]),
              f"{resumo['yoy_acum_12m'] * 100:+.1f}".replace(".", ",") + "% vs 12 meses anteriores")
    c2.metric(f"Volume em {resumo['ultimo_mes']:%m/%Y}", fmt_bi(resumo["volume_ultimo_mes_bi"]))
    c3.metric("Stablecoins no valor do mês", fmt_pct(resumo["stable_share_ult"]))
    c4.metric("Bitcoin no valor do mês", fmt_pct(resumo["btc_share_ult"]))
    st.caption("Cartões sempre mostram o dado mais recente da base, independentemente do filtro de período.")

    st.markdown("**Volume mensal declarado (R$ bilhões)**")
    st.plotly_chart(charts.fig_volume(recorte(kpis.kpi_volume(r1))), width="stretch")
    st.caption("Barras: volume do mês. Linha: média móvel de 12 meses, que suaviza a sazonalidade. "
               "Fonte: Relatório 1.")

# --------------------------------------------------------- 2 Canais e perfil
with tabs[1]:
    st.subheader("Por onde passam as operações: exchanges no Brasil, no exterior ou direto (P2P)")
    modo = st.radio("Mostrar", ["Participação (%)", "Valor (R$ bi)"], horizontal=True)
    canais = recorte(kpis.kpi_canais(r1))
    st.plotly_chart(charts.fig_canais(canais, participacao=modo.startswith("Part")), width="stretch")
    st.caption("Canal de intermediação das operações. Fonte: Relatório 1.")

    st.subheader("Quem declara por conta própria: pessoas físicas ou jurídicas?")
    st.plotly_chart(charts.fig_pf_pj(recorte(kpis.kpi_pf_pj(r1))), width="stretch")
    st.info(
        "Exchanges no Brasil são sempre pessoas jurídicas e declaram em nome dos clientes. "
        "Por isso a comparação PF × PJ considera apenas quem declara por conta própria "
        "(exchanges no exterior ou sem exchange)."
    )

    st.subheader("Quantos declarantes únicos?")
    quebras = quality.detectar_quebras(r2)
    quebras_recorte = quebras[(quebras["mes"] >= ini) & (quebras["mes"] <= fi)]
    st.plotly_chart(charts.fig_declarantes(recorte(kpis.kpi_declarantes(r2)), quebras_recorte),
                    width="stretch")
    st.warning(
        "A série tem quebras bruscas (marcadas com ✕) que não parecem mudança real de comportamento. "
        "Leia a tendência pela linha grossa (mediana móvel de 6 meses), não mês a mês."
    )

# ----------------------------------------------------------- 3 Mercado
with tabs[2]:
    _conc = kpis.kpi_concentracao(f4).iloc[-1]
    st.subheader(
        f"Os 5 maiores ativos concentram {fmt_pct(_conc['top5_participacao'], 0)} "
        f"do valor em {f4['mes'].max():%m/%Y}"
    )
    comp = recorte(kpis.kpi_composicao(r4))
    st.plotly_chart(charts.fig_composicao(comp), width="stretch")
    st.caption("Participação de cada grupo no valor negociado dos principais ativos. "
               "A classificação de stablecoins é uma premissa do projeto (ver docs/dicionario_dados.md). "
               "Fonte: Relatório 4.")

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown("**Ranking de ativos no período**")
        top_n = st.slider("Quantos ativos mostrar", 5, 20, config.TOP_N_ATIVOS)
        rank = kpis.kpi_ativos(r4, inicio=ini, fim=fi)
        st.plotly_chart(charts.fig_ranking(rank, top_n), width="stretch")
    with col_b:
        st.markdown("**Concentração (Top-5)**")
        st.plotly_chart(charts.fig_concentracao(recorte(kpis.kpi_concentracao(r4))), width="stretch")
        conc = kpis.kpi_concentracao(f4).iloc[-1]
        st.metric("HHI no último mês do período", fmt_int(conc["hhi"]),
                  help="Índice Herfindahl-Hirschman: soma dos quadrados das participações (0 a 10.000). "
                       "Quanto maior, mais concentrado.")

    st.markdown("**Ticket médio por grupo de ativo**")
    st.plotly_chart(charts.fig_ticket(recorte(kpis.kpi_ticket(r4))), width="stretch")

    with st.expander("Tabela completa do ranking (baixar CSV)"):
        tabela = rank.rename(columns={
            "criptoativo": "Ativo", "grupo": "Grupo", "valor_total": "Valor total (R$)",
            "n_operacoes": "Operações", "ticket_medio": "Ticket médio (R$)", "participacao": "Participação",
        })
        st.dataframe(tabela, width="stretch", hide_index=True)
        st.download_button("Baixar CSV", tabela.to_csv(index=False).encode("utf-8"),
                           file_name="ranking_ativos.csv", mime="text/csv")

# ------------------------------------------------------------ 4 Gênero
with tabs[3]:
    gen = recorte(kpis.kpi_genero(r3))
    ult = gen.iloc[-1]
    st.subheader(
        f"Em {f3['mes'].max():%m/%Y}, mulheres somam {ult['ops_fem_pct']:.0f}% das operações "
        f"e {ult['valor_fem_pct']:.0f}% do valor"
    )
    st.plotly_chart(charts.fig_genero(gen), width="stretch")
    g1, g2, g3 = st.columns(3)
    g1.metric("Mulheres nas operações", f"{ult['ops_fem_pct']:.1f}%".replace(".", ","))
    g2.metric("Mulheres no valor", f"{ult['valor_fem_pct']:.1f}%".replace(".", ","))
    g3.metric("Ticket feminino ÷ masculino", fmt_pct(ult["ticket_relativo_fem"], 0),
              help="Razão entre o valor por operação de mulheres e de homens (100% = igual).")
    st.caption("Somente pessoas físicas, por gênero declarado. Fonte: Relatório 3.")

# ---------------------------------------------------------- 5 Qualidade
with tabs[4]:
    st.subheader("Confiança nos números: o que foi verificado e o que exige cautela")
    val = quality.validar(dados)
    st.dataframe(val, width="stretch", hide_index=True)
    n_ok = int((val["status"] == "OK").sum())
    st.caption(f"{n_ok} de {len(val)} verificações passaram sem ressalvas.")

    st.markdown("**Meses com quebra brusca em CPF/CNPJ únicos**")
    st.dataframe(quality.detectar_quebras(r2).assign(mes=lambda x: x["mes"].dt.strftime("%m/%Y")),
                 width="stretch", hide_index=True)

    st.markdown("**Quanto do total do Relatório 1 o Relatório 4 cobre?**")
    st.plotly_chart(charts.fig_cobertura(quality.cobertura_r4_sobre_r1(dados)), width="stretch")
    st.caption("O Relatório 4 traz só compra e venda dos principais ativos, por isso nunca soma 100%.")

    with st.expander("Ativo × mês com muitas operações e ticket muito baixo (possível automação)"):
        st.dataframe(quality.operacoes_atipicas(r4), width="stretch", hide_index=True)

    st.markdown(
        "**Limitações da fonte:** dados agregados no nível Brasil (sem recorte por estado ou município); "
        "valores podem ser revistos pela Receita (declarações retificadoras e extemporâneas); "
        "o nome do criptoativo é campo livre na declaração; registros com erro evidente foram excluídos pela fonte."
    )

# ------------------------------------------------------------ 6 Conclusões
with tabs[5]:
    st.subheader("O que os dados mostram")
    for i, a in enumerate(insights.gerar_achados(dados), 1):
        st.markdown(f"**{i}. {a['titulo']}**")
        st.write(a["texto"])
        st.caption(f"Evidência: {a['evidencia']}")
    st.divider()
    st.subheader("Recomendações para a organização parceira")
    st.info(
        "Preencha com a organização parceira: para cada achado acima, registre a decisão ou ação "
        "correspondente (veja o modelo em docs/roteiro_storytelling.md). "
        f"Decisão apoiada atualmente configurada: **{config.DECISAO_APOIADA}**."
    )
