# 0005 — Vereditos de validação dos indicadores

**Status:** Aceita
**Evidência:** `notebooks/02_validacao_indicadores.ipynb`

## Contexto

Os cinco indicadores da proposta inicial foram sugeridos antes do contato com os dados. Além
deles, cinco features de longo prazo foram mineradas para as decisões estruturais do Ricardo.
Cada um passou por validação estatística: discriminação (mede diferença real entre unidades),
redundância (correlação com os demais) e agregação (soma corretamente entre níveis).

## Vereditos

| Indicador | Origem | Veredito | Evidência |
|-----------|--------|----------|-----------|
| Produtividade | herdado | mantém | CV 32% entre UFs; não aditivo (erro de 21,5% se agregado errado) |
| Participação regional | herdado | mantém | soma 100%; reflete concentração real da produção |
| Desvio vs referência | herdado | rebaixa | correlação 1,0 com produtividade; é forma de exibir, não indicador |
| Variação safra a safra | herdado | ajusta | CV das variações > 700%; ruidosa, serve como leitura pontual |
| Mix açúcar/etanol | herdado | mantém | decisão estratégica relatada na entrevista |
| Tendência de produtividade | minerado | mantém | discrimina entre microrregiões; exige janela recente |
| Resiliência climática | minerado | mantém | eixo de risco interpretável ("aguenta a seca") |
| Volatilidade | minerado | descarta | redundante com resiliência (correlação −0,75) |
| Elasticidade área × produtividade | minerado | mantém | informação independente das demais |
| Intensidade industrial | minerado | ajusta | serve como perfil da UF, não como série; ATR da CONAB é melhor para qualidade |

## Decisões que decorrem

1. **Desvio** deixa de ser card autônomo no produto. Vira uma opção de exibição da
   produtividade contra uma referência (média estadual, nacional, período anterior).
2. **Volatilidade** sai do conjunto. A resiliência climática cobre o mesmo eixo de risco de
   forma mais legível para a persona.
3. **Qualidade da matéria-prima** usa o ATR publicado pela CONAB, não a razão açúcar/cana
   derivada, que é instável por refletir decisão comercial de safra.
4. Toda medida de produtividade no produto é calculada como soma de quantidade sobre soma de
   área, nunca média de rendimentos.

## Conjunto final de indicadores do produto

Produtividade, participação regional, mix açúcar/etanol, tendência de produtividade,
resiliência climática, elasticidade área × produtividade e ATR (qualidade). O desvio é modo de
exibição; variação safra a safra é leitura de apoio.
