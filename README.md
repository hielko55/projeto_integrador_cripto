# Projeto Integrador Extensionista — Criptoativos declarados à Receita Federal

Painel analítico em **Python (pandas + Plotly + Streamlit)** construído sobre a planilha de dados abertos da Receita Federal (`criptoativos_dados_abertos_20260826.xls`, IN RFB nº 1.888/2019). Dados **públicos e agregados**: não exigem autorização.

Disciplinas: Técnicas de Visualização de Dados e Business Intelligence.

> ⚠️ **Antes de tudo:** o projeto só é extensionista com uma **organização parceira real**. Preencha `src/config.py` (nome, público, decisão apoiada) e registre cada contato em `docs/registro_interacoes.md`. Roteiro de conversa: `docs/perguntas_para_organizacao.md`.

## Como rodar
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.pipeline            # lê data/raw, valida, calcula KPIs e grava data/processed/
streamlit run app/dashboard.py    # abre o painel no navegador
pytest -q                         # 13 testes automatizados
```

## Fluxo de dados
```
data/raw/*.xls ──extract──▶ data/interim/*_bruto.csv ──clean──▶ data/processed/base_*.csv
                                                       ├─kpis──▶ data/processed/kpi_*.csv
                                                       ├─quality▶ data/processed/qualidade_*.csv
                                                       └─insights▶ docs/achados_gerados.md
data/processed ──────────────────────────────────────────────▶ app/dashboard.py (Streamlit)
```
O painel lê **somente** `data/processed/`. Para atualizar a base: substitua a planilha em `data/raw/`, ajuste `ARQUIVO_FONTE` em `src/config.py` e rode o pipeline.

## Estrutura
```
├── data/raw | interim | processed   dados originais, brutos por relatório, bases limpas e KPIs
├── src/
│   ├── config.py      organização parceira, premissas (stablecoins), limiares, paleta
│   ├── extract.py     lê as 4 abas da planilha
│   ├── clean.py       tipos, datas, colunas derivadas, grupos de ativos
│   ├── quality.py     13 validações, quebras de série, operações atípicas
│   ├── kpis.py        os 8 indicadores
│   ├── insights.py    achados calculados (Data Storytelling)
│   ├── charts.py      gráficos Plotly (paleta acessível)
│   └── pipeline.py    orquestra tudo: python -m src.pipeline
├── app/dashboard.py   painel Streamlit (6 abas)
├── notebooks/         01_exploracao_e_kpis.ipynb
├── tests/             testes com pytest
├── docs/              dicionário, KPIs, visualizações, storytelling, relatório (esqueleto),
│                      roteiro da apresentação, registro de interações, checklist
└── evidencias/        prints, e-mails, atas e aceite da organização parceira
```

## Abas do painel (ordem da narrativa)
1. **Panorama** — volume, crescimento, peso das stablecoins
2. **Canais e perfil** — exchanges no Brasil × exterior × P2P; PF × PJ; declarantes únicos
3. **Mercado por ativo** — composição, ranking, concentração (Top-5/HHI), ticket médio
4. **Gênero** — participação feminina em operações e em valor
5. **Qualidade dos dados** — validações, quebras na série, cobertura do Relatório 4
6. **Conclusões** — achados e modelo de recomendações

## Mapa das entregas do edital
| Entrega | Onde está |
|---|---|
| Relatório técnico | `docs/relatorio_tecnico_esqueleto.md` |
| Dashboard | `app/dashboard.py` |
| Código-fonte | `src/`, `notebooks/`, `tests/` |
| Apresentação oral | `docs/roteiro_apresentacao.md` |
| Caráter extensionista | `docs/registro_interacoes.md` + `evidencias/` |

Status detalhado: `docs/checklist_entregas.md`.

## Limitações da fonte (resumo)
Dados nacionais e agregados (sem estado/município); valores revisáveis pela Receita; nome do ativo é campo livre; Relatório 4 cobre só compra e venda dos principais ativos (≈ 93% do total do Relatório 1); série de CPF/CNPJ únicos tem quebras bruscas. Detalhes em `docs/dicionario_dados.md`.
