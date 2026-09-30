# Justificativa das visualizações

| Pergunta | Gráfico | Por que este gráfico | Princípios aplicados |
|---|---|---|---|
| O mercado cresce? | Barras (mês) + linha (média móvel 12m) | Barras mostram cada mês; a linha revela a tendência sem o ruído | Hierarquia visual: linha forte sobre barras claras |
| Por onde passam as operações? | Área empilhada (100% ou R$) | Mostra composição e sua mudança ao longo do tempo | Cores fixas por canal em todas as telas |
| PF ou PJ? | Duas linhas | Compara duas séries de mesma unidade (%) | Eixo 0–100% para não exagerar variações |
| Quantos declarantes? | Dois painéis (CPF e CNPJ) com marcadores ✕ nas quebras | CPF e CNPJ têm escalas muito diferentes; eixo duplo induziria erro | Redução de ruído: mediana móvel em destaque; alerta explícito |
| O que se negocia? | Área 100% empilhada por grupo | Composição ao longo do tempo | Paleta acessível (Okabe-Ito), ordem estável das camadas |
| Quais ativos lideram? | Barras horizontais ordenadas | Comparação entre categorias com rótulos legíveis | Ordenação, rótulo direto no fim da barra |
| Mulheres participam quanto? | Duas linhas (operações × valor) | Contraste entre frequência e valor | Linha tracejada para a série secundária (não depende só de cor) |
| Ticket médio | Linhas em escala logarítmica | Grupos com tickets em ordens de grandeza diferentes | Eixo identificado como log |

**Acessibilidade:** paleta Okabe-Ito (segura para daltonismo), contraste alto em fundo branco, redundância de codificação (linha tracejada/marcador ✕ além da cor), fonte ≥ 13 px, formatação numérica brasileira e fonte citada em cada gráfico.
**Consistência:** uma única função-base (`charts._base`) define fonte, margens, grade e legenda; cada grupo/canal tem cor fixa em todo o painel.
