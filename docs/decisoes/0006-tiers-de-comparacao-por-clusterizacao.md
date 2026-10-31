# 0006 — Tiers de comparação por clusterização

**Status:** Aceita (implementada e validada com os dados reais da gold)
**Origem:** discussão do grupo (Alex e Brenno)

## Contexto

Comparar unidades territoriais de portes muito diferentes produz ranking injusto e pouco
informativo. Uma microrregião pequena de semiárido (por exemplo, Gado Bravo) sempre parecerá
pior que um polo de grande escala (por exemplo, a região de João Pessoa), mesmo que seja
eficiente na sua própria escala. O ranking vira ranking de porte, não de eficiência.

Esse problema já apareceu na validação: a participação regional teve coeficiente de variação
de 294% entre UFs, sintoma de que poucas unidades de grande escala dominam a distribuição e
achatam a comparação das demais (ver ADR 0005 e `notebooks/02_validacao_indicadores.ipynb`).

A disciplina reforça o ponto: todo indicador exige um par comparável. Agrupar unidades de
perfil semelhante é criar esses pares de forma defensável, em vez de comparar no chute.

## Proposta

Introduzir **tiers de comparação**: agrupar as unidades territoriais por escala e estrutura, e
comparar eficiência apenas dentro de cada grupo.

**Regra de ouro:** agrupar por um eixo (escala: área, volume, valor da produção) e comparar por
outro (eficiência: produtividade, tendência, resiliência). Nunca clusterizar pela mesma
variável que se vai comparar, sob pena de circularidade.

## Diagnóstico dos dados (27 UFs com produção, gold real)

Antes de escolher o método, mediu-se a forma da distribuição de escala sobre a gold:

- **Escala unidimensional:** `quantidade_produzida_t` e `area_colhida_ha` têm correlação
  1,000 (bruta) e 0,995 (em log). Os dois "eixos de escala" são na prática o mesmo eixo.
- **Distribuição log-normal:** assimetria bruta 4,66; em `log1p`, −0,46 (quase simétrica no
  log). A escala só é tratável no espaço logarítmico.
- **Concentração extrema:** top 1 UF (SP) = 56,8%; top 3 = 77,1%; top 5 = 88,7% da produção.
- **Gaps no log(quantidade):** há saltos visíveis na distribuição — SP destaca-se no topo
  (gap bruto 1,72) e há uma separação entre as pequenas (gap 1,55). Esses gaps indicam que a
  escala admite 2–3 grupos, coerente com o teto de "2 a 3 grupos" previsto para 27 UFs. Note,
  porém, que o maior gap bruto (o topo de SP) **não** vira fronteira: as fronteiras saem da
  minimização da variância intra-grupo (ver abaixo), que prefere cortar nos gaps interiores
  em vez de gastar uma fronteira isolando um único ponto. O gap de SP sinaliza concentração,
  não um tier só para SP.

## Decisão de método — cortes em log, NÃO K-means

Descartou-se **K-means multivariado**. Com escala efetivamente unidimensional, distribuição
log-normal e outliers (SP), o K-means cru produziria apenas um "ranking de porte" — exatamente
o resultado frágil que o gate deste ADR manda descartar. Também se descartou usar **valor da
produção** como critério de agrupamento: é nominal/monetário, tem correlação ~1 com a
quantidade e seria circular (contaminado por preço).

Método escolhido: **cortes em log(quantidade produzida) em 3 tiers**, sobre a média dos últimos
5 anos de cada UF (estabiliza o ruído anual). Os cortes são os *natural breaks* de Fisher-Jenks
— a partição que **minimiza a variância intra-grupo (SSE) do log** —, resolvidos por programação
dinâmica em `src/canavis/domain/tiers.py`. Em uma dimensão, essa solução coincide com a
clusterização hierárquica de Ward, o que torna o resultado reprodutível e defensável sem
dependência de bibliotecas externas.

É importante não confundir o método com "cortar nos maiores gaps brutos": o critério é a
minimização de SSE, não o tamanho absoluto de cada salto. Por isso o maior gap da série — o
topo isolado de SP — não produz uma fronteira: isolar SP num tier só gastaria uma das duas
fronteiras disponíveis com ganho de variância pequeno, enquanto cortar nos gaps interiores
reduz muito mais a dispersão total. SP acaba no tier grande, junto das demais UFs de grande
escala, que é o resultado agronomicamente correto.

O **valor da produção** entra apenas como variável descritiva (perfil por tier), nunca como
critério de agrupamento, e não é materializado na gold.

## Gate de validação (resultado)

1. **Cobertura exata:** cada uma das 27 UFs recebe exatamente um tier; nenhuma nula, nenhuma
   com dois. Municípios e microrregiões ficam com tier nulo (fora de escopo).
2. **Dispersão de escala intra-tier < global:** desvio-padrão do log cai de **2,982** (base
   inteira) para **1,005** dentro dos grupos — redução de **66%**. Comparar dentro do tier é
   comprovadamente mais justo.
3. **Concordância com Ward:** a clusterização hierárquica de Ward aglomerativo em 1D sobre o
   log recupera exatamente os mesmos três grupos (concordância 100%), confirmando os cortes.
4. **Sanidade agronômica:** os rótulos de negócio são coerentes — SP, MG, GO, MS e PR caem no
   tier grande, como esperado.
5. **Perfil de valor da produção por tier** (variável descritiva, não critério): o tier grande
   concentra **94,8%** do valor; a média escala, **5,1%**; a pequena/marginal, **~0,0%**.

Gate **aprovado**. Não foi necessário degradar para o plano B (faixas por quartis).

Toda evidência do gate é reproduzível, não apenas afirmada. Os itens (b) dispersão,
(c) concordância com Ward e (e) perfil de valor são recomputados sobre a camada silver real
(`data/interim/ibge_pam`) pelos testes `test_gate_real_cobertura_e_dispersao_das_27_ufs`,
`test_gate_real_concordancia_com_ward_hierarquico` e
`test_gate_real_perfil_de_valor_concentra_no_tier_grande` em `tests/test_tiers.py`. O perfil de
valor é calculado pela função pura `tiers.perfil_valor_por_tier`, que lê a variável "Valor da
produção" da silver só para perfilar e nunca para agrupar nem materializar na gold.

## Tiers resultantes

A minimização de SSE posiciona as duas fronteiras nos gaps interiores do log: entre Pernambuco
e Paraíba (gap 0,95) e entre Santa Catarina e Rondônia (gap 1,55) — e não no gap do topo de SP,
pela razão explicada na seção de método.

- **Grande escala industrial** (8 UFs, 94,8% do valor da produção): São Paulo, Goiás, Minas
  Gerais, Mato Grosso do Sul, Paraná, Mato Grosso, Alagoas, Pernambuco.
- **Média escala** (14 UFs, 5,1% do valor): Paraíba, Bahia, Rio Grande do Norte, Espírito
  Santo, Maranhão, Tocantins, Rio de Janeiro, Sergipe, Pará, Piauí, Ceará, Rio Grande do Sul,
  Amazonas, Santa Catarina.
- **Pequena/marginal** (5 UFs, ~0,0% do valor): Rondônia, Distrito Federal, Acre, Amapá,
  Roraima.

O perfil de valor por tier confirma a leitura de escala: a quase totalidade do valor monetário
concentra-se no tier grande, sem ter sido usado para formar os grupos.

## Escopo

Apenas **UFs** nesta task. Microrregiões (só 16 com produção recente) ficam de fora: poucos
pontos para clusterização defensável. A coluna `tier` é materializada em `dim_territorio` pela
camada de build; municípios e microrregiões ficam com tier nulo, o que o modelo do Power BI já
tolera (a etapa de Power Query mantém a coluna se existir e a medida "Desvio vs grupo" passa a
ter como filtrar por `dim_territorio[tier]`).

## Situação

Implementada na Etapa 2: módulo de domínio `src/canavis/domain/tiers.py` (funções puras —
classificação por cortes em log, dispersão global/intra-tier e `perfil_valor_por_tier`), com
integração no build (`_atribuir_tier` em `src/canavis/pipeline/build.py`) e testes em
`tests/test_tiers.py` e `tests/test_build.py`, incluindo os três testes de gate recomputados
sobre a silver real. A regra de ouro foi respeitada: agrupa-se por escala (quantidade física) e
compara-se por eficiência; o valor monetário fica só como perfil descritivo.
