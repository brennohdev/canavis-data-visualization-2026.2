# 0006 — Tiers de comparação por clusterização

**Status:** Proposta (ainda não implementada nem validada com os dados)
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

Diretrizes de método, quando for implementado (provavelmente na Etapa 2):

- Modelo simples e interpretável (K-means ou clusterização hierárquica), com variáveis
  padronizadas.
- Número de clusters decidido por métrica (silhueta / cotovelo) e sanidade agronômica, não por
  gosto. Com 15–17 microrregiões ou 27 UFs, o teto realista é de 2 a 3 grupos.
- Cada cluster precisa receber um rótulo em linguagem de negócio (ex.: "grande escala
  industrial", "pequena escala de sequeiro"), senão não serve ao usuário.
- Validação obrigatória: comprovar que a comparação de eficiência dentro do cluster é mais
  justa (menor dispersão de escala) do que na base inteira.

## Escopo em aberto

A decidir na implementação: clusterizar microrregiões da PB, UFs do Brasil, ou os dois níveis.
Recomendação inicial: começar pelas UFs, onde a distorção de escala é mais forte e os dados são
completos, e só então replicar para microrregiões.

## Situação

Registrada como direção validada em conversa. Não entra na entrega da Etapa 1 (que trata de
descoberta e enquadramento); pertence ao trabalho analítico da Etapa 2. Só passa a "Aceita"
depois de provada com os dados — se a clusterização não sustentar grupos reais (silhueta fraca,
grupos sem sentido agronômico), a proposta é descartada com evidência.
