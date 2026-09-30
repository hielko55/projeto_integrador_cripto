"""Pipeline ponta a ponta: planilha da Receita -> bases limpas -> KPIs -> achados.

Uso (a partir da raiz do projeto):
    python -m src.pipeline

Fluxo:
    data/raw/*.xls --extract--> data/interim/*.csv (brutos por relatório)
                   --clean----> data/processed/base_*.csv (tipos corretos)
                   --kpis-----> data/processed/kpi_*.csv
                   --quality--> data/processed/qualidade_*.csv
                   --insights-> docs/achados_gerados.md
"""
from __future__ import annotations

import json

import pandas as pd

from . import clean, config, extract, insights, kpis, quality

NOMES_BASES = {
    "r1": "base_valores_por_canal",
    "r2": "base_declarantes_unicos",
    "r3": "base_genero_pf",
    "r4": "base_criptoativos",
}


def executar(verbose: bool = True) -> dict[str, pd.DataFrame]:
    for pasta in (config.DIR_INTERIM, config.DIR_PROCESSED, config.DIR_DOCS):
        pasta.mkdir(parents=True, exist_ok=True)

    # 1) Extração -------------------------------------------------------
    brutos = extract.extrair_tudo()
    for chave, df in brutos.items():
        df.to_csv(config.DIR_INTERIM / f"{NOMES_BASES[chave]}_bruto.csv", index=False, encoding="utf-8")

    # 2) Limpeza --------------------------------------------------------
    d = clean.limpar_tudo(brutos)
    for chave, df in d.items():
        df.to_csv(config.DIR_PROCESSED / f"{NOMES_BASES[chave]}.csv", index=False, encoding="utf-8")

    # 3) KPIs -----------------------------------------------------------
    saidas = {
        "kpi_volume": kpis.kpi_volume(d["r1"]),
        "kpi_canais": kpis.kpi_canais(d["r1"]),
        "kpi_pf_pj": kpis.kpi_pf_pj(d["r1"]),
        "kpi_declarantes": kpis.kpi_declarantes(d["r2"]),
        "kpi_genero": kpis.kpi_genero(d["r3"]),
        "kpi_ranking_ativos": kpis.kpi_ativos(d["r4"]),
        "kpi_composicao": kpis.kpi_composicao(d["r4"]),
        "kpi_concentracao": kpis.kpi_concentracao(d["r4"]),
        "kpi_ticket": kpis.kpi_ticket(d["r4"]),
    }
    for nome, df in saidas.items():
        df.to_csv(config.DIR_PROCESSED / f"{nome}.csv", index=False, encoding="utf-8")

    resumo = kpis.resumo(d)
    (config.DIR_PROCESSED / "resumo_kpis.json").write_text(
        json.dumps(resumo, default=str, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 4) Qualidade ------------------------------------------------------
    validacoes = quality.validar(d)
    validacoes.to_csv(config.DIR_PROCESSED / "qualidade_validacoes.csv", index=False, encoding="utf-8")
    quality.detectar_quebras(d["r2"]).to_csv(
        config.DIR_PROCESSED / "qualidade_quebras_declarantes.csv", index=False, encoding="utf-8")
    quality.operacoes_atipicas(d["r4"]).to_csv(
        config.DIR_PROCESSED / "qualidade_operacoes_atipicas.csv", index=False, encoding="utf-8")
    quality.cobertura_r4_sobre_r1(d).to_csv(
        config.DIR_PROCESSED / "qualidade_cobertura_r4_r1.csv", index=False, encoding="utf-8")

    # 5) Achados (Data Storytelling) -----------------------------------
    achados = insights.gerar_achados(d)
    (config.DIR_DOCS / "achados_gerados.md").write_text(
        insights.achados_em_markdown(achados), encoding="utf-8")

    if verbose:
        print(f"Fonte:    {config.ARQUIVO_FONTE.name}")
        print(f"Período:  {d['r1']['mes'].min():%m/%Y} a {d['r1']['mes'].max():%m/%Y} ({len(d['r1'])} meses)")
        print(f"Ativos:   {d['r4']['criptoativo'].nunique()} criptoativos, {len(d['r4'])} linhas (R4)")
        print("Validações:")
        print(validacoes.to_string(index=False))
        print(f"\nArquivos gerados em {config.DIR_PROCESSED} e {config.DIR_DOCS / 'achados_gerados.md'}")
    return d


def carregar_processados() -> dict[str, pd.DataFrame]:
    """Lê as bases limpas de data/processed/ (é a única fonte do dashboard)."""
    def _ler(nome: str) -> pd.DataFrame:
        caminho = config.DIR_PROCESSED / f"{nome}.csv"
        if not caminho.exists():
            raise FileNotFoundError(
                f"{caminho.name} não encontrado. Rode `python -m src.pipeline` primeiro."
            )
        return pd.read_csv(caminho, parse_dates=["mes"])

    return {chave: _ler(nome) for chave, nome in NOMES_BASES.items()}


if __name__ == "__main__":
    executar()
