# Indicadores-chave (KPIs)

Cada KPI é **justificado para a decisão da organização parceira** (Estrutura Contábil — necessidade levantada com Luciana, proprietária/gestora, em 29/09/2026: ver `docs/registro_interacoes.md`).

> **Limitação importante:** a base da Receita Federal registra volume e número de operações declaradas, não preço ou retorno dos ativos. Os KPIs abaixo apoiam a conversa sobre **tendência de movimentação e popularidade** entre os criptoativos — não uma previsão de rentabilidade/lucratividade, que exigiria dados de preço/mercado que esta fonte não tem.

| # | KPI | Fórmula | Fonte | Por que importa | Decisão que apoia | Cuidado |
|---|---|---|---|---|---|---|
| 1 | Volume declarado (mensal, acumulado 12m e variação anual) | `total_geral`; soma de 12 meses; variação sobre os 12 meses anteriores | R1 | Dimensiona o mercado e sua tendência | Contextualizar para os clientes se o mercado de criptoativos está em expansão ou retração | Valores sujeitos a revisão pela Receita |
| 2 | Participação por canal | canal ÷ total geral (exchange BR, exchange exterior, P2P) | R1 | Mostra onde as operações são intermediadas e quanto escapa de exchanges nacionais | Orientar clientes sobre canais mais usados e seus impactos na declaração/conformidade | P2P e exterior só aparecem acima de R$ 30 mil/mês |
| 3 | Perfil do declarante (PF × PJ) | PF ÷ (exterior + sem exchange) | R1 | Quem opera por conta própria | Situar o cliente (pessoa física) frente ao perfil predominante de quem declara | Exclui exchanges BR (sempre PJ) |
| 4 | Declarantes únicos (CPF e CNPJ) | contagem mensal; mediana móvel de 6 meses | R2 | Tamanho da base de participantes | Mostrar se o número de investidores (a "massa") está crescendo ou estagnando | 12 quebras bruscas: ler pela mediana móvel |
| 5 | Participação feminina | % ops, % valor, ticket relativo | R3 | Inclusão e perfil de ticket | Dar contexto de diversidade do público investidor ao orientar clientes | Só PF |
| 6 | Composição por grupo de ativo | grupo ÷ total do R4 | R4 | Mudança de "o que se negocia" (Bitcoin → stablecoins) | Indicar quais criptoativos vêm ganhando participação — a tendência de investimento da massa que a organização quer acompanhar | Classificação é premissa do projeto |
| 7 | Concentração (Top-5 e HHI) | soma das 5 maiores participações; Σ(part²)×10.000 | R4 | Risco de dependência de poucos ativos | Alertar clientes sobre concentração/diversificação ao decidir entre ativos | R4 cobre só parte do R1 |
| 8 | Ticket médio por grupo | valor ÷ nº de operações | R4 | Distingue varejo de operações grandes | Ajudar a situar o porte típico de operação por ativo ao conversar com o cliente | Sensível a automação (bots) |

Implementação: `src/kpis.py`. Saídas conferíveis em `data/processed/kpi_*.csv`.
