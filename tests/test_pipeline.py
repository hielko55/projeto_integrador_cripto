"""Testes automatizados do pipeline (rode com: pytest -q)."""
import pandas as pd
import pytest

from src import clean, config, extract, insights, kpis, pipeline, quality


@pytest.fixture(scope="module")
def brutos():
    return extract.extrair_tudo()


@pytest.fixture(scope="module")
def d(brutos):
    return clean.limpar_tudo(brutos)


# ------------------------------------------------------------ extração
def test_planilha_existe():
    assert config.ARQUIVO_FONTE.exists()


def test_extracao_formato(brutos):
    assert list(brutos) == ["r1", "r2", "r3", "r4"]
    assert len(brutos["r1"]) == len(brutos["r2"]) == len(brutos["r3"]) == 83
    assert len(brutos["r4"]) > 4000
    assert list(brutos["r4"].columns) == extract.COLUNAS_R4


# -------------------------------------------------------------- limpeza
def test_parse_mes():
    assert clean.parse_mes("Agosto de 2019") == pd.Timestamp("2019-08-01")
    assert clean.parse_mes("março de 2021") == pd.Timestamp("2021-03-01")
    with pytest.raises(ValueError):
        clean.parse_mes("Foo de 2020")


def test_tipos_e_sem_nulos(d):
    for nome, df in d.items():
        assert pd.api.types.is_datetime64_any_dtype(df["mes"]), nome
        assert df.isna().sum().sum() == 0, nome
    assert (d["r1"]["mes"].dt.day == 1).all()


def test_classificacao_ativos():
    assert clean.classificar_ativo("BTC") == "Bitcoin"
    assert clean.classificar_ativo("USDT") == "Stablecoins"
    assert clean.classificar_ativo("SOL") == "Outros ativos"


# ------------------------------------------------------------ qualidade
def test_nenhuma_validacao_falha(d):
    val = quality.validar(d)
    assert not (val["status"] == "FALHA").any(), val[val["status"] == "FALHA"]


def test_quebras_detectadas(d):
    q = quality.detectar_quebras(d["r2"])
    assert not q.empty
    assert set(q["serie"]) <= {"CPF", "CNPJ"}


# ----------------------------------------------------------------- KPIs
def test_participacoes_somam_um(d):
    canais = kpis.kpi_canais(d["r1"]).groupby("mes")["participacao"].sum()
    assert canais.sub(1).abs().max() < 1e-9
    comp = kpis.kpi_composicao(d["r4"]).groupby("mes")["participacao"].sum()
    assert comp.sub(1).abs().max() < 1e-9


def test_volume_yoy(d):
    vol = kpis.kpi_volume(d["r1"])
    assert vol["acum_12m_bi"].isna().sum() == 11  # primeiros 11 meses sem janela completa
    manual = d["r1"]["total_geral"].tail(12).sum() / 1000
    assert vol["acum_12m_bi"].iloc[-1] == pytest.approx(manual)


def test_resumo_chaves(d):
    r = kpis.resumo(d)
    for k in ("acum_12m_bi", "yoy_acum_12m", "stable_share_ult", "hhi_ult"):
        assert k in r
    assert 0 <= r["stable_share_ult"] <= 1


def test_ranking_ordenado(d):
    rank = kpis.kpi_ativos(d["r4"])
    assert rank["valor_total"].is_monotonic_decreasing
    assert rank["participacao"].sum() == pytest.approx(1)


# -------------------------------------------------------------- achados
def test_achados(d):
    achados = insights.gerar_achados(d)
    assert len(achados) == 6
    assert all(a["titulo"] and a["texto"] and a["evidencia"] for a in achados)


# ------------------------------------------------------------- pipeline
def test_pipeline_gera_arquivos():
    pipeline.executar(verbose=False)
    for nome in ("base_criptoativos", "kpi_volume", "qualidade_validacoes", "resumo_kpis"):
        assert any(config.DIR_PROCESSED.glob(f"{nome}.*")), nome
    assert (config.DIR_DOCS / "achados_gerados.md").exists()
    carregados = pipeline.carregar_processados()
    assert set(carregados) == {"r1", "r2", "r3", "r4"}
