# 0009 — Decomposição histórica e limite da evidência de quebra

**Status:** Aceita — issue #14 (Task 10)

## Método e recorte

Produtividade = quantidade produzida / área colhida, em t/ha, na PAM gold,
2003–2023. Análise por UF e microrregião, nunca por município. O arquivo atual
contém 23 microrregiões (incluindo séries sem produção), das quais 13 possuem
produtividade completa; as 27 UFs possuem série completa. Esses números são
da extração atual e não repetem o denominador de 17 do levantamento do ADR 0004.

A tendência é a média móvel centrada de três observações anuais consecutivas.
A oscilação é observado menos tendência; não é componente sazonal nem efeito
climático identificado. Não há sazonalidade intra-anual em 21 pontos anuais.
As extremidades e janelas com ausências permanecem nulas. O cálculo usa o ano
seguinte e serve somente para explicar o passado, sem previsão.

Aplicamos Chow para igualdade conjunta de intercepto e inclinação de duas
retas: 2003–2012 versus 2013–2023. Regressões por mínimos quadrados, duas
restrições e 17 graus de liberdade residuais. F = ((RSS restrito − RSS livre)/2)
dividido por (RSS livre/(n−4)). A sobrevivência exata F(2,v) é
(v/(v+2F))^(v/2), evitando uma nova dependência estatística.
Exigimos anos consecutivos, sem valores ausentes e pelo menos cinco observações
de cada lado. Variância residual numericamente nula torna o teste indisponível.

## Resultado reproduzido

Executar `uv run canavis-pipeline --stage build` e consultar
`data/processed/fato_producao.parquet`, uma linha por território/ano.

- Paraíba: F = **4,251270**, p nominal = **0,031831**.
- Sensibilidade sem 2023: F = **4,193940**, p nominal = **0,034322**.
- Teste calculável em 27 UFs e 13 microrregiões; indisponível em outras 10
  microrregiões. Não interpolamos nem substituímos produtividade indefinida por zero.
- P nominal < 0,05 em 15 UFs e 8 microrregiões. Isso é uma contagem exploratória,
  sem correção por múltiplas comparações, e não uma lista de quebras confirmadas.
- 782 observações têm tendência calculável, preservadas as 5.733 linhas do fato.

## Gate: não afirmar quebra estrutural

O ponto 2012/2013 veio da inspeção prévia da mesma série (ADR 0004), e não de
uma hipótese externa definida antes de observar os dados. Assim, o p-valor
usual de um ponto fixo não incorpora essa seleção. Além disso, Chow clássico
supõe erros independentes e homocedásticos; não verificamos essas condições
como suficientes para inferência nesta amostra de apenas 21 anos. Não usamos
o resultado nominal para uma conclusão confirmatória nem causal.

**A entrega degrada para decomposição descritiva com teste exploratório. Não
se afirma quebra estrutural.** A leitura permitida é: “queda e recuperação
observadas; diferença entre retas sugestiva em teste exploratório”. Uma análise
confirmatória exigiria tratar a seleção do ponto, dependência dos erros e
multiplicidade. Não procurar outros cortes até obter significância.

## Colunas e uso no Power BI

| Coluna | Significado |
|---|---|
| `tendencia_t_ha` | Média móvel centrada de três anos; nula nas bordas/lacunas |
| `oscilacao_t_ha` | Desvio do observado em relação à média móvel |
| `f_chow`, `p_chow` | Resultado nominal repetido por território, não somável |
| `status_chow` | `exploratorio`, `serie_incompleta_ou_curta`, `variancia_residual_degenerada` ou `nao_aplicavel_municipio` |
| `ponto_candidato_quebra` | Verdadeiro em 2013 para UF/microrregião; candidato, não confirmação |
| `quebra_confirmada` | Sempre nulo: confirmação não estabelecida, diferente de provar ausência |

Usar um território por gráfico, eixo anual, observado e tendência em linhas.
Manter lacunas visíveis. Para p e F usar SELECTEDVALUE, nunca SUM; são resultados
da janela completa 2003–2023 e não são reestimados ao filtrar anos no painel.
Sinalizar 2013 como “divisão exploratória”, sem legenda “quebra confirmada”.
Não somar produtividades ou tendências de territórios nem misturar níveis.
As colunas estão prontas para importação; esta entrega não altera o PBIX.

## Validação

49 testes passam, incluindo recuperação de tendência linear sintética,
detecção de quebra injetada com ruído, controle sintético sem rejeição,
tratamento de ausências/variância degenerada e preservação do grão. Um controle
sintético não garante taxa de falsos positivos em todas as séries reais.

Funções puras em `src/canavis/domain/features.py`; aplicação por território em
`src/canavis/pipeline/temporal.py`; materialização no build existente.

Referências metodológicas: [Chow — MathWorks](https://www.mathworks.com/help/econ/chowtest.html)
e [diagnósticos de regressão — statsmodels](https://www.statsmodels.org/dev/diagnostic.html).
