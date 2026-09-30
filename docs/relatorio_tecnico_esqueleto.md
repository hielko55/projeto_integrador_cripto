# Relatório Técnico — Projeto Integrador Extensionista

**Título:** Painel analítico de criptoativos declarados à Receita Federal para apoio à decisão de [ORGANIZAÇÃO]
**Autora/Equipe:** [PREENCHER] · **Disciplinas:** Técnicas de Visualização de Dados e Business Intelligence · **Data:** [PREENCHER]

> Itens marcados **[PREENCHER]** dependem da organização parceira. Itens marcados **[AUTO]** têm os números em `docs/achados_gerados.md` e `data/processed/`.

## 1. Organização parceira
[PREENCHER: identificação, natureza (pública/privada/sem fins lucrativos), setor, breve contextualização.]

## 2. Necessidade ou problema identificado
[PREENCHER: a necessidade nas palavras da organização, público do painel e decisões a apoiar — copiar de `registro_interacoes.md`.]

## 3. Interação com a organização
[PREENCHER: resumo do diário de interações (datas, formatos, participantes) e referência às evidências em `evidencias/`.]

## 4. Objetivos
- Geral: transformar os dados abertos de criptoativos da Receita em informação para a decisão de [ORGANIZAÇÃO].
- Específicos: (a) mensurar volume e tendência; (b) identificar canais e perfil de declarantes; (c) caracterizar o mercado por ativo; (d) avaliar a qualidade dos dados; (e) entregar painel interativo e recomendações.

## 5. Base de dados
- **Origem:** Receita Federal do Brasil, Relatório de Dados Abertos de Criptoativos (IN RFB 1.888/2019), versão de 26/08/2026. Dados públicos e agregados.
- **Conteúdo:** 4 relatórios, 83 meses (08/2019 a 06/2026): valores por canal, declarantes únicos, gênero e 66 criptoativos (4.519 linhas no Relatório 4).
- **Tratamentos:** localização das tabelas nas abas, conversão de meses por extenso em datas, conversão numérica, colunas derivadas e classificação de ativos em grupos (premissa do projeto).
- **Validações:** 13 verificações automáticas (somas, percentuais, médias, duplicatas, continuidade); ver `data/processed/qualidade_validacoes.csv`.
- **Limitações:** ver `docs/dicionario_dados.md`.

## 6. Indicadores (KPIs)
[Copiar a tabela de `docs/kpis.md` com a coluna "Decisão que apoia" preenchida.]

## 7. Visualizações e justificativas
[Copiar/ajustar `docs/justificativa_visualizacoes.md`; inserir prints do painel.]

## 8. Principais análises
[AUTO: usar os 6 achados de `docs/achados_gerados.md`, com gráficos e tabelas de apoio.]

## 9. Narrativa (Data Storytelling)
[Seguir `docs/roteiro_storytelling.md`.]

## 10. Resultados e contribuições para a organização
[PREENCHER com base no feedback da devolutiva registrado em `registro_interacoes.md`.]

## 11. Conclusões e recomendações
[PREENCHER usando o modelo de recomendações do roteiro; incluir limitações e trabalhos futuros, como recorte territorial e atualização mensal da base.]

## Apêndice — Reprodutibilidade
```
pip install -r requirements.txt
python -m src.pipeline
streamlit run app/dashboard.py
pytest -q
```
