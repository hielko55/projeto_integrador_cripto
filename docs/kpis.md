# Indicadores-chave (KPIs)

Cada KPI precisa ser **justificado para a decisão da organização parceira**. A coluna "Decisão que apoia" está em branco de propósito: preencha junto com o representante da organização.

| # | KPI | Fórmula | Fonte | Por que importa | Decisão que apoia (PREENCHER) | Cuidado |
|---|---|---|---|---|---|---|
| 1 | Volume declarado (mensal, acumulado 12m e variação anual) | `total_geral`; soma de 12 meses; variação sobre os 12 meses anteriores | R1 | Dimensiona o mercado e sua tendência | | Valores sujeitos a revisão pela Receita |
| 2 | Participação por canal | canal ÷ total geral (exchange BR, exchange exterior, P2P) | R1 | Mostra onde as operações são intermediadas e quanto escapa de exchanges nacionais | | P2P e exterior só aparecem acima de R$ 30 mil/mês |
| 3 | Perfil do declarante (PF × PJ) | PF ÷ (exterior + sem exchange) | R1 | Quem opera por conta própria | | Exclui exchanges BR (sempre PJ) |
| 4 | Declarantes únicos (CPF e CNPJ) | contagem mensal; mediana móvel de 6 meses | R2 | Tamanho da base de participantes | | 12 quebras bruscas: ler pela mediana móvel |
| 5 | Participação feminina | % ops, % valor, ticket relativo | R3 | Inclusão e perfil de ticket | | Só PF |
| 6 | Composição por grupo de ativo | grupo ÷ total do R4 | R4 | Mudança de "o que se negocia" (Bitcoin → stablecoins) | | Classificação é premissa do projeto |
| 7 | Concentração (Top-5 e HHI) | soma das 5 maiores participações; Σ(part²)×10.000 | R4 | Risco de dependência de poucos ativos | | R4 cobre só parte do R1 |
| 8 | Ticket médio por grupo | valor ÷ nº de operações | R4 | Distingue varejo de operações grandes | | Sensível a automação (bots) |

Implementação: `src/kpis.py`. Saídas conferíveis em `data/processed/kpi_*.csv`.
