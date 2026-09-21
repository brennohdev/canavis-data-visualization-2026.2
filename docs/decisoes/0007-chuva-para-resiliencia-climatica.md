# 0007 — Dados de chuva para ancorar a resiliência climática

**Status:** Rejeitada (a chuva anual não explica a produtividade onde a cana está)
**Origem:** spike de validação a pedido do grupo

## Contexto

A resiliência climática, hoje, é uma proxy: infere seca a partir da própria queda de
produtividade nos piores anos da série. Para dar lastro físico ao indicador, testamos ligar a
produtividade a dados públicos de precipitação, verificando se os anos de baixa produtividade
coincidem com os de baixa chuva.

A cana da Paraíba concentra-se em cinco microrregiões do leste úmido, que somam 98% da
produção: Litoral Norte (34%), Litoral Sul (23,5%), Sapé (21,8%), João Pessoa (15,9%) e Brejo
(3,1%).

## Investigação: três fontes de chuva

**1. INMET — estações automáticas.** ZIPs anuais em
`portal.inmet.gov.br/uploads/dadoshistoricos/{ano}.zip` (acesso confirmado). A Paraíba tem
apenas 9 estações automáticas, a maioria no Agreste, Cariri e Sertão, onde quase não há cana.
As duas maiores regiões produtoras (Litoral Norte e Sapé) não têm estação dedicada. Cobertura
insuficiente na faixa canavieira.

**2. ANA / HidroWeb — postos pluviométricos.** WebService legado
`telemetriaws1.ana.gov.br/ServiceANA.asmx/HidroInventario` (aberto, sem token). A Paraíba tem
**462 postos pluviométricos**, dos quais **116 na faixa leste canavieira**, cobrindo 46
municípios (Alhandra, Caaporã, Conde, Mamanguape, entre outros). Cobertura espacial excelente,
uma ordem de grandeza acima do INMET.

**3. CHIRPS — precipitação por satélite em grade.** Grade de 0,05° via API do ClimateSERV
(`climateserv.servirglobal.net`), série desde 1981, cobrindo qualquer ponto sem depender de
estação. Acesso confirmado: coletamos a série anual 2012–2023 das microrregiões canavieiras.
Resolve o problema de cobertura de raiz.

## Teste estatístico final

Com os caminhos 2 e 3 a cobertura deixa de ser o problema. O teste decisivo passa a ser: a
chuva anual explica a produtividade da cana? Correlacionamos a série de chuva (CHIRPS) com a
produtividade por microrregião:

| Microrregião | Anos | Correlação chuva × produtividade | Produtividade anos secos vs. úmidos |
|--------------|------|----------------------------------|-------------------------------------|
| Litoral Norte | 12 | +0,21 (fraca) | 51,5 vs. 54,2 t/ha (diferença pequena) |
| Litoral Sul | 5 | −0,50 (sinal contrário) | 57,7 vs. 53,9 t/ha |

A relação é fraca e inconsistente, com sinais opostos entre regiões vizinhas.

## Veredito

**Rejeitada.** Não por falta de dado — o caminho da ANA e o CHIRPS resolvem a cobertura —, mas
porque **a chuva anual total não explica a produtividade da cana onde ela é cultivada**. Duas
razões agronômicas sustentam o resultado:

1. **A Zona da Mata não é limitada por água.** Ali chove de 1.000 a 1.600 mm por ano, o
   suficiente para a cana. O que limita produtividade nessa faixa é manejo, variedade e solo,
   não seca. A seca é gargalo no Agreste e no Sertão, onde não há cana. O cruzamento é
   geograficamente irônico: onde a cana está, a chuva não é o fator escasso.
2. **Chuva anual é a métrica errada.** Para a cana importa a distribuição da chuva ao longo do
   ciclo (crescimento versus maturação), não o total do ano. O acumulado anual mistura fases.

## Consequências

- A resiliência climática permanece como proxy baseada na própria série de produtividade
  (ADR 0005), com a limitação declarada.
- Fica registrado, para uma etapa futura, que o caminho tecnicamente promissor **não** é buscar
  mais chuva, e sim mudar a métrica: precipitação na janela fenológica da cana (não anual),
  possivelmente combinada a um índice de seca (SPI) e ao balanço hídrico. A fonte para isso já
  está mapeada e acessível (ANA para estação, CHIRPS para grade).
- Os três caminhos foram levados até o teste final. O que reprova a hipótese não é acesso nem
  cobertura, é a ausência de relação estatística — e isso é um resultado, não uma falha.
