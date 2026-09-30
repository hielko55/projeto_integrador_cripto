# Dicionário de dados

**Fonte:** Receita Federal do Brasil — *Criptoativos: Relatório de Dados Abertos e Informações Gerais* (planilha `criptoativos_dados_abertos_20260826.xls`), com base na Instrução Normativa RFB nº 1.888/2019.
**Natureza:** dados públicos e agregados (sem CPF/CNPJ identificáveis) — não exigem autorização de uso.
**Período:** 08/2019 a 06/2026 (83 meses). **Abrangência:** Brasil (não há recorte por estado ou município).

A planilha consolida três tipos de declaração: (1) exchanges domiciliadas no Brasil, (2) PF/PJ que usam exchanges no exterior acima de R$ 30 mil por mês e (3) PF/PJ que operam entre si sem exchange acima de R$ 30 mil por mês. Usa a informação mais recente da base da Receita (inclui declarações extemporâneas e retificadoras), portanto **os números podem divergir de versões anteriores**.

## Relatório 1 — Valores por tipo de declaração (`base_valores_por_canal.csv`)
Unidade: **R$ milhões** por mês.

| Coluna | Significado |
|---|---|
| `mes` | 1º dia do mês (data) |
| `ext_pf`, `ext_pj`, `ext_subtotal` | Operações com exchanges no exterior, declaradas por PF, por PJ e subtotal |
| `sem_pf`, `sem_pj`, `sem_subtotal` | Operações sem exchange (P2P), idem |
| `exchange_br` | Operações declaradas por exchanges no Brasil (todas PJ) |
| `total_geral` | Soma dos três canais |
| `pf_declarante_rs_mi`, `pj_declarante_rs_mi` | *Derivada.* PF e PJ entre quem declara por conta própria (exclui `exchange_br`) |
| `base_autodeclarada_rs_mi` | *Derivada.* `ext_subtotal + sem_subtotal` |
| `share_pf_autodeclarada` | *Derivada.* PF ÷ base autodeclarada |
| `share_exchange_br`, `share_exchange_ext`, `share_sem_exchange` | *Derivadas.* Participação de cada canal no total geral |
| `total_geral_bi` | *Derivada.* Total geral em R$ bilhões |

Observações da fonte: registros com erro evidente de preenchimento foram excluídos; nem toda transação precisa informar valor monetário (art. 7º, I, "f", da IN 1.888).

## Relatório 2 — Declarantes únicos (`base_declarantes_unicos.csv`)
| Coluna | Significado |
|---|---|
| `mes` | 1º dia do mês |
| `cpf_unicos` | CPFs distintos com ao menos uma transação no mês (todas as modalidades) |
| `cnpj_unicos` | CNPJs distintos, idem |

Cada CPF/CNPJ conta uma vez no mês, independentemente do número de transações. **Atenção:** a série tem quebras bruscas (ver `qualidade_quebras_declarantes.csv`).

## Relatório 3 — Gênero, somente pessoas físicas (`base_genero_pf.csv`)
| Coluna | Significado |
|---|---|
| `ops_fem_pct`, `ops_masc_pct` | % do **número de operações** por gênero |
| `valor_fem_pct`, `valor_masc_pct` | % do **valor** das operações por gênero |
| `gap_fem_pp` | *Derivada.* `ops_fem_pct − valor_fem_pct`, em pontos percentuais |
| `ticket_relativo_fem` | *Derivada.* Ticket médio feminino ÷ masculino (1 = igual) |

## Relatório 4 — Por criptoativo (`base_criptoativos.csv`)
Unidade: **R$** (não milhões). Só **compra e venda dos principais criptoativos**.

| Coluna | Significado |
|---|---|
| `criptoativo` | Símbolo (campo de preenchimento livre na declaração; a Receita consolida variações de BTC e USDT) |
| `mes` | 1º dia do mês |
| `n_operacoes` | Número de operações |
| `valor_total` | Valor total das operações (R$) |
| `valor_medio` | Valor médio por operação (R$) |
| `grupo` | *Derivada.* Bitcoin, Ethereum, Stablecoins ou Outros ativos (ver premissa abaixo) |
| `valor_total_mi` | *Derivada.* Valor total em R$ milhões |

## Premissas do projeto (não vêm da Receita)
1. **Stablecoins:** `USDT, USDC, DAI, BUSD, TUSD, USDP, PAX, GUSD, BRZ, BRZX, BRLT, CBRL, BIDR` (lista em `src/config.py`). Ativos lastreados em ouro (PAXG), tokens embrulhados (WBTC) e tokens de ativos reais (IMOB01, MBPRK, MBCONS) ficam em "Outros ativos".
2. **Quebras em CPF/CNPJ:** mês com valor acima de 2× ou abaixo de 50% do mês anterior (limiares em `src/config.py`).
3. **Operações atípicas:** ticket médio < 20% da mediana do próprio ativo e nº de operações > 3× a mediana (indício de automação; é apenas um alerta).

## Limitações
- O Relatório 4 cobre em média 93% do total do Relatório 1 (varia de 75% a 100%) porque traz só compra e venda dos principais ativos.
- PF × PJ no Relatório 1 refere-se a **quem declara**, não a quem é o cliente final das exchanges.
- Sem recorte territorial, sem dados por idade e sem distinção entre compra e venda.
