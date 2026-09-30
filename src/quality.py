"""Qualidade dos dados: validações de consistência e detecção de quebras nas séries.

O Relatório 2 (CPF/CNPJ únicos) apresenta saltos bruscos que não parecem
mudanças reais de comportamento e sim efeito de declarações/retificações.
Em vez de esconder isso, o projeto mede e mostra (aba "Qualidade" do painel).
"""
from __future__ import annotations

import pandas as pd

from . import config


def _linha(verificacao: str, ok: bool, detalhe: str, gravidade: str = "erro") -> dict:
    return {
        "verificacao": verificacao,
        "status": "OK" if ok else ("FALHA" if gravidade == "erro" else "ATENÇÃO"),
        "detalhe": detalhe,
    }


def validar(d: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Testes de integridade entre e dentro dos relatórios."""
    r1, r2, r3, r4 = d["r1"], d["r2"], d["r3"], d["r4"]
    linhas: list[dict] = []

    # --- Relatório 1: somas internas
    e1 = (r1["ext_pf"] + r1["ext_pj"] - r1["ext_subtotal"]).abs().max()
    e2 = (r1["sem_pf"] + r1["sem_pj"] - r1["sem_subtotal"]).abs().max()
    e3 = (r1["ext_subtotal"] + r1["sem_subtotal"] + r1["exchange_br"] - r1["total_geral"]).abs().max()
    linhas.append(_linha("R1: PF + PJ = subtotal (exterior)", e1 < 0.01, f"erro máx. {e1:.6f} R$ mi"))
    linhas.append(_linha("R1: PF + PJ = subtotal (sem exchange)", e2 < 0.01, f"erro máx. {e2:.6f} R$ mi"))
    linhas.append(_linha("R1: subtotais + exchanges BR = total geral", e3 < 0.01, f"erro máx. {e3:.6f} R$ mi"))

    # --- Relatório 3: percentuais somam 100
    p1 = (r3["ops_fem_pct"] + r3["ops_masc_pct"] - 100).abs().max()
    p2 = (r3["valor_fem_pct"] + r3["valor_masc_pct"] - 100).abs().max()
    linhas.append(_linha("R3: % feminino + masculino = 100 (operações)", p1 < 0.05, f"desvio máx. {p1:.3f} p.p."))
    linhas.append(_linha("R3: % feminino + masculino = 100 (valor)", p2 < 0.05, f"desvio máx. {p2:.3f} p.p."))

    # --- Relatório 4: média = total / operações; sem duplicatas/negativos/nulos
    med = ((r4["valor_total"] / r4["n_operacoes"]) - r4["valor_medio"]).abs().max()
    linhas.append(_linha("R4: valor médio = valor total / nº de operações", med < 0.01, f"erro máx. R$ {med:.6f}"))
    dup = int(r4.duplicated(["criptoativo", "mes"]).sum())
    linhas.append(_linha("R4: sem duplicatas (ativo × mês)", dup == 0, f"{dup} duplicatas"))
    neg = int((r4[["n_operacoes", "valor_total"]] < 0).sum().sum())
    linhas.append(_linha("R4: sem valores negativos", neg == 0, f"{neg} ocorrências"))
    nulos = int(r4.isna().sum().sum())
    linhas.append(_linha("R4: sem valores nulos", nulos == 0, f"{nulos} células vazias"))

    # --- Cobertura temporal
    continuo = bool(r1["mes"].diff().dropna().dt.days.between(28, 31).all())
    linhas.append(_linha("Séries mensais contínuas (sem meses faltando)", continuo,
                         f"{r1['mes'].min():%m/%Y} a {r1['mes'].max():%m/%Y}, {len(r1)} meses"))
    iguais = bool((r1["mes"].values == r2["mes"].values).all() and (r1["mes"].values == r3["mes"].values).all())
    linhas.append(_linha("R1, R2 e R3 cobrem os mesmos meses", iguais, "comparação mês a mês"))

    # --- Cruzamento R4 × R1 (informativo): R4 só traz compra/venda dos principais ativos
    cobertura = cobertura_r4_sobre_r1(d)
    linhas.append(_linha(
        "R4 cobre parte do total do R1 (esperado: < 100%)",
        bool((cobertura["cobertura"] <= 1.0).all()),
        f"cobertura entre {cobertura['cobertura'].min():.0%} e {cobertura['cobertura'].max():.0%} (média {cobertura['cobertura'].mean():.0%})",
        gravidade="aviso",
    ))

    # --- Quebras de série (informativo)
    q = detectar_quebras(d["r2"])
    linhas.append(_linha(
        "R2: quebras bruscas em CPF/CNPJ únicos",
        q.empty,
        f"{len(q)} meses sinalizados (ver aba Qualidade)",
        gravidade="aviso",
    ))
    return pd.DataFrame(linhas)


def cobertura_r4_sobre_r1(d: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Razão entre o valor do R4 (soma dos ativos) e o total geral do R1, por mês."""
    r4_mes = d["r4"].groupby("mes")["valor_total"].sum().div(1_000_000).rename("r4_rs_mi")
    r1_mes = d["r1"].set_index("mes")["total_geral"].rename("r1_rs_mi")
    out = pd.concat([r4_mes, r1_mes], axis=1).dropna()
    out["cobertura"] = out["r4_rs_mi"] / out["r1_rs_mi"]
    return out.reset_index()


def detectar_quebras(r2: pd.DataFrame) -> pd.DataFrame:
    """Sinaliza meses em que CPF ou CNPJ únicos saltam/caem além dos limiares da config."""
    base = r2.sort_values("mes").copy()
    linhas = []
    for col, rotulo in (("cpf_unicos", "CPF"), ("cnpj_unicos", "CNPJ")):
        razao = base[col] / base[col].shift(1)
        achados = base.loc[
            (razao > config.LIMIAR_SALTO_ALTA) | (razao < config.LIMIAR_SALTO_QUEDA)
        ]
        for idx in achados.index:
            linhas.append({
                "mes": base.loc[idx, "mes"],
                "serie": rotulo,
                "valor": base.loc[idx, col],
                "valor_mes_anterior": base.loc[idx - 1, col],
                "razao_sobre_mes_anterior": razao.loc[idx],
                "tipo": "salto" if razao.loc[idx] > 1 else "queda",
            })
    cols = ["mes", "serie", "valor", "valor_mes_anterior", "razao_sobre_mes_anterior", "tipo"]
    return pd.DataFrame(linhas, columns=cols).sort_values(["mes", "serie"]).reset_index(drop=True)


def operacoes_atipicas(r4: pd.DataFrame, top: int = 15) -> pd.DataFrame:
    """Ativo×mês com muitas operações e ticket muito baixo — possível automação (ex.: bots).

    Critério explicável: ticket médio abaixo de 20% da mediana do próprio ativo
    e número de operações acima de 3× a mediana do próprio ativo.
    """
    g = r4.groupby("criptoativo")
    med_ticket = g["valor_medio"].transform("median")
    med_ops = g["n_operacoes"].transform("median")
    sinal = r4[(r4["valor_medio"] < 0.2 * med_ticket) & (r4["n_operacoes"] > 3 * med_ops)].copy()
    sinal["ticket_vs_mediana"] = sinal["valor_medio"] / med_ticket.loc[sinal.index]
    sinal["ops_vs_mediana"] = sinal["n_operacoes"] / med_ops.loc[sinal.index]
    return sinal.sort_values("n_operacoes", ascending=False).head(top).reset_index(drop=True)
