# Relatório Técnico — Projeto Integrador Extensionista

**Título:** Painel analítico de criptoativos declarados à Receita Federal para apoio à decisão de [ORGANIZAÇÃO]
**Autora/Equipe:** [PREENCHER] · **Disciplinas:** Técnicas de Visualização de Dados e Business Intelligence · **Data:** [PREENCHER]

> Itens marcados **[PREENCHER]** dependem da organização parceira. Itens marcados **[AUTO]** têm os números em `docs/achados_gerados.md` e `data/processed/`.

## 1. Organização parceira
**Estrutura Contábil** — escritório de contabilidade de natureza privada, sediado em Valparaíso de Goiás-GO, atuando na prestação de serviços de assessoria contábil e tributária. O vínculo com o projeto foi estabelecido por relação familiar: a representante da organização, Luciana, proprietária e gestora do escritório, é tia do autor do projeto.

## 2. Necessidade ou problema identificado
Segundo a representante da organização, clientes do escritório frequentemente perguntam "onde o dinheiro está indo" e "vale a pena entrar nisso [em criptoativos]?". O público do painel são os clientes do escritório que investem ou pensam em investir em criptoativos. A decisão que o painel deve apoiar é a de investimento desses clientes, mostrando quais criptoativos concentram mais recursos e qual a tendência de movimentação da massa. A representante fez duas observações importantes, incorporadas ao projeto: (i) o painel precisa deixar claro que **não é recomendação de investimento**, e sim um retrato do que foi declarado à Receita Federal; (ii) a linguagem deve ser simples, já que nem todo cliente é da área financeira — por isso cada aba do painel tem um título que já resume a conclusão (ex.: "os 5 maiores ativos concentram X% do valor"). O resultado esperado pela organização é ter esse material de apoio visual disponível para usar nas orientações a clientes (detalhamento completo em `docs/registro_interacoes.md`).

## 3. Interação com a organização
A primeira interação ocorreu em **29/09/2026**, por troca de mensagens de texto via WhatsApp entre o autor do projeto e Luciana (proprietária/gestora da Estrutura Contábil), na qual foi apresentada a proposta do painel e levantada a necessidade descrita acima; Luciana aprovou o escritório como organização parceira e autorizou a continuidade do projeto (transcrição completa em `evidencias/whatsapp_luciana_29-09-2026.txt`). As etapas seguintes — validação dos KPIs junto à organização, apresentação/devolutiva do painel e coleta de feedback — ainda não ocorreram; serão registradas em `docs/registro_interacoes.md` conforme acontecerem, com evidências em `evidencias/`.

## 4. Objetivos
- Geral: transformar os dados abertos de criptoativos da Receita em informação para a decisão da Estrutura Contábil.
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
**Pendente de devolutiva.** A apresentação final do painel à organização e a coleta de feedback ainda não ocorreram; esta seção será concluída após esse encontro, com base no que for registrado em `docs/registro_interacoes.md`.

De forma preliminar, com base na necessidade identificada, espera-se que o painel contribua ao oferecer à organização:
- uma visão objetiva de **quais criptoativos vêm ganhando participação** no mercado declarado à Receita (achados 2 e 3 em `docs/achados_gerados.md`), apoiando a conversa sobre tendências de investimento da "massa";
- um indicador de **concentração e diversificação** do mercado (achado 3), útil para alertar clientes sobre o risco de concentrar investimentos em poucos ativos;
- contexto sobre **canais de intermediação** (achado 4), relevante para orientar clientes sobre conformidade na declaração.

## 11. Conclusões e recomendações
Principais achados da base de dados (08/2019–06/2026; detalhamento em `docs/achados_gerados.md`):
1. o volume declarado de criptoativos está em expansão (+21,6% nos últimos 12 meses);
2. stablecoins passaram a dominar o mercado (87,0% do valor negociado nos últimos 12 meses, ante 10,6% no início da série), enquanto o Bitcoin caiu de 57,3% para 7,3%;
3. o mercado é altamente concentrado: os 5 maiores ativos somam 98,9% do valor (HHI de 5.061/10.000);
4. exchanges no Brasil continuam à frente na intermediação, mas perderam espaço para operações sem exchange — P2P (de 17,0% para 22,4%);
5. mulheres participam mais em número de operações do que em valor movimentado (ticket médio feminino ≈ 39% do masculino);
6. os indicadores de declarantes únicos exigem leitura cautelosa, por quebras na série que a planilha não permite explicar.

**Recomendação para a organização:** usar o painel como apoio visual nas conversas com clientes sobre tendência e popularidade de mercado (achados 1–4), deixando claro aos clientes que os dados mostram volume e participação declarados — não rentabilidade ou previsão de preço, que exigiria outra fonte de dados (a base da Receita não contém cotações).

**Limitações:** dados nacionais e agregados (sem recorte por estado ou cliente); valores sujeitos a revisão pela própria Receita; a classificação de stablecoins é uma premissa do projeto, não um critério oficial da Receita; o Relatório 4 cobre em média 93% do total do Relatório 1.

**Trabalhos futuros:** recorte territorial, caso a organização priorize clientes de uma região específica; atualização mensal da base conforme novos dados forem publicados pela Receita; incorporar dados de preço/mercado (fonte externa) caso a organização queira, no futuro, discutir rentabilidade e não apenas volume.

## Apêndice — Reprodutibilidade
**Painel publicado:** https://projetointegradorcripto-ny8jdxyeju9jnj9cjaw2ak.streamlit.app/

```
pip install -r requirements.txt
python -m src.pipeline
streamlit run app/dashboard.py
pytest -q
```
