"""Configuração central do projeto.

Tudo que depende da organização parceira ou de decisões do analista fica aqui,
para que o restante do código não precise ser alterado.
"""
from pathlib import Path

# ---------------------------------------------------------------- caminhos
RAIZ = Path(__file__).resolve().parents[1]
DIR_RAW = RAIZ / "data" / "raw"
DIR_INTERIM = RAIZ / "data" / "interim"
DIR_PROCESSED = RAIZ / "data" / "processed"
DIR_DOCS = RAIZ / "docs"

ARQUIVO_FONTE = DIR_RAW / "criptoativos_dados_abertos_20260826.xls"

# ------------------------------------------------ organização parceira
ORGANIZACAO = "Estrutura Contábil (escritório de contabilidade, Brasília-DF)"
SETOR = "Contabilidade / assessoria tributária"
PUBLICO_ALVO = "Clientes do escritório interessados em investir em criptoativos"
DECISAO_APOIADA = (
    "Orientar clientes sobre quais criptoativos vêm ganhando participação de mercado "
    "e qual a tendência geral de movimentação, como apoio à conversa sobre investimento "
    "e conformidade na declaração à Receita Federal"
)

# ------------------------------------------------------------------ fonte
FONTE = (
    "Receita Federal do Brasil — Criptoativos: Relatório de Dados Abertos "
    "(IN RFB nº 1.888/2019), versão de 26/08/2026"
)

# ---------------------------------------------------- abas da planilha
ABA_R1 = "Relatorio1"   # valores por tipo de declaração (R$ milhões)
ABA_R2 = "Relatorio2"   # CPF/CNPJ únicos
ABA_R3 = "Relatório3"   # gênero (PF)
ABA_R4 = "Relatorio4"   # por criptoativo

# ------------------------------------------- premissas do analista (documentar!)
# Classificação própria de stablecoins: o campo "criptoativo" é de preenchimento
# livre na declaração; esta lista é uma PREMISSA DO PROJETO, não da Receita.
STABLECOINS = {
    "USDT", "USDC", "DAI", "BUSD", "TUSD", "USDP", "PAX", "GUSD",
    "BRZ", "BRZX", "BRLT", "CBRL", "BIDR",
}
TOP_N_ATIVOS = 10

# Limiares para sinalizar possíveis quebras/anomalias nas séries (qualidade)
LIMIAR_SALTO_ALTA = 2.0    # mês atual > 2x o anterior
LIMIAR_SALTO_QUEDA = 0.50  # mês atual < 50% do anterior

# ------------------------------------------------ paleta acessível (Okabe-Ito)
PALETA = {
    "azul": "#0072B2",
    "laranja": "#E69F00",
    "verde": "#009E73",
    "vermelho": "#D55E00",
    "rosa": "#CC79A7",
    "azul_claro": "#56B4E9",
    "amarelo": "#F0E442",
    "cinza": "#6B6B6B",
}
