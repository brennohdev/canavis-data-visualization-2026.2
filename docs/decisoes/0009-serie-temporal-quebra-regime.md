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

## Diagnóstico econométrico completo (execução dos métodos do ADR 0011) e confirmação do gate

**Hipótese da limitação.** A série é curta e limitada: 21 pontos anuais (2003–2023) por território,
forte supressão abaixo da UF (61,6% no município, 36,4% na microrregião, 0% na UF) e sem
sazonalidade intra-anual. A pergunta que orientou esta rodada foi: *a série sustenta uma afirmação
econométrica confirmatória de quebra?* Esperava-se que o próprio rigor mostrasse que **não** — e é
isso que os números abaixo mostram. "Não rejeitar" aqui é **falta de poder**, não prova de ausência
de quebra. Caso principal: Paraíba (`uf:25`) e Litoral Norte (`microrregiao:25020`).

A execução com números reais está em `notebooks/04_econometria_serie_temporal.ipynb` (statsmodels/scipy
vivem só no notebook; o núcleo do pacote permanece sem essas dependências). O ADR 0011 é o mapa
teórico dos métodos; este é o seu resultado medido.

**Descritiva (PB).** n=21; média 53,54 t/ha; desvio-padrão 4,21; CV 7,86%; assimetria 0,25;
mín 45,65 / máx 64,69. Amostra curtíssima: tudo a seguir é de baixo poder.

**Estacionariedade — ADF × KPSS (PB).** Em nível: ADF = −2,01 (p = 0,284, não rejeita raiz unitária)
e KPSS = 0,65 (p = 0,018, rejeita estacionariedade) — quadrante compatível com não-estacionariedade.
A 1ª diferença não entrega estacionariedade limpa (ADF = −1,06, p = 0,731). Ressalva: poder baixíssimo
e distorção de tamanho do KPSS em n~21.

**Raiz unitária com quebra — Zivot-Andrews (PB).** Em nível ZA = −4,21 (p = 0,236); em log ZA = −4,61
(p = 0,091). Em ambos a estatística fica **acima** do crítico de 5% (−4,81): mesmo permitindo uma
quebra endógena na constante, o teste **não separa** quebra determinística de passeio aleatório.
Ressalva: poder baixíssimo contra tendência com mudança de regime (Nelson/Piger/Zivot) — impraticável
cravar com 21 pontos. A execução concluiu sem instabilidade numérica.

**Normalidade dos resíduos da tendência (PB).** Jarque-Bera = 0,02 (p = 0,988) e Shapiro-Wilk = 0,97
(p = 0,806) em nível; em log JB p = 0,803. Resíduos **não rejeitam** normalidade; o log não é
necessário para normalizar. Ressalva: pouco poder para detectar não-normalidade em n~21.

**Decomposição.** MM-3 (pacote) e LOESS concordam no desenho "queda até ~2012, recuperação até 2023"
e são a leitura honesta. O STL só roda com período mínimo forçado (`period=2`) e produz sazonal
artificial (|máx| ≈ 2,0 t/ha): a série anual **não comporta** STL sazonal — isso é resultado, não
falha. O filtro HP não é usado (ciclo espúrio e instabilidade nas pontas, inclusive o pico de 2023).

**Quebra com ponto endógeno — supF/Quandt-Andrews × Chow fixo.** PB: supF = **4,96** maximizando
**exatamente em 2013** (o mesmo ponto do ADR 0004), contra Chow fixo F = 4,25 (p = 0,0318). Litoral
Norte: supF = **4,61** maximizando em **2010** (nem no ponto "conhecido"), contra Chow fixo F = 2,90
(p = 0,0822). Os supF observados ficam **muito abaixo** dos valores críticos de Quandt-Andrews a 5%
para 2 parâmetros e aparagem de 15% (faixa de ~11–12; Stock & Watson). Ou seja: **sem fixar o ponto a
olho, a evidência continua exploratória** — e fora da UF o corte a olho nem se sustenta. Ressalva: a
aparagem de 15% corta ainda mais os já escassos 21 pontos.

**Diagnóstico dos resíduos (PB).** Ljung-Box não acusa autocorrelação (lag 1 p = 0,889; lag 2
p = 0,981) e Breusch-Pagan não acusa heterocedasticidade (LM p = 0,793; F p = 0,805). As suposições do
Chow não são violadas de forma detectável — mas isso não valida inferência confirmatória, pois o viés
do ponto garimpado e a multiplicidade permanecem. Ressalva: diagnósticos quase sem poder em n~21.

**Múltiplas comparações — FDR Benjamini-Hochberg.** O Chow é calculável em **40 territórios**
(27 UF + 13 micro). A contagem **nominal** do gate original — "p < 0,05 em 15 UFs e 8 microrregiões"
(= 23) — é reescrita pelo controle de FDR (α = 0,05): **20 territórios sobrevivem (13 UFs e 7
microrregiões)**, confirmado tanto pela função pura `fdr_benjamini_hochberg` quanto por
`statsmodels.stats.multitest.multipletests(method="fdr_bh")`. O resultado mais eloquente: a **Paraíba**
(p nominal 0,0318) tem p ajustado BH **0,0606** e é o **primeiro território que NÃO sobrevive** ao
controle. O caso-vitrine cai justamente quando se corrige a multiplicidade.

**Confirmação do gate.** Com lastro agora **endógeno** (supF sem fixar o ponto), o veredito do ADR
0009 se mantém: **não se afirma quebra estrutural.** A busca endógena recai no mesmo 2013 da PB mas
fica muito aquém do crítico de Andrews; o Zivot-Andrews não distingue quebra de random walk; e o FDR
derruba o próprio caso da PB. A leitura permitida continua descritiva — "queda até ~2012 e recuperação
até 2023; diferença entre períodos sugestiva em teste exploratório" — com o rótulo "divisão
exploratória" em 2013 e `quebra_confirmada` sempre nula. A modelagem econométrica de série longa cabe
às séries internacionais do ADR 0010 na Etapa 3, **sem qualquer projeção/forecast** nesta entrega.

Evidência executável: `notebooks/04_econometria_serie_temporal.ipynb`. Mapa teórico: ADR 0011.
Referências dos testes endógenos:
[Zivot-Andrews — statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.zivot_andrews.html)
e [correção de múltiplas comparações — statsmodels](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html).
