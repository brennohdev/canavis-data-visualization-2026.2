# 0019 — Modelagem estatística e seus limites

**Status:** Proposta
**Evidência:** `docs/entrega-etapa3/planejamento-etapa3.md` (seção 8.2, extra 2)
**Ancora em:** ADR 0009 e 0011 (sem quebra estrutural confirmada; PB com p ajustado 0,0606)

## Decisão
- **Defensável:** tendência robusta (Theil-Sen ou OLS com erro-padrão) com intervalo e
  classificação sobe/estável/cai; `p_chow` com FDR já existente; clusterização dos tiers interpretada.
- **Exploratório, rotulado como tal:** sensibilidade do share de açúcar ao preço do açúcar
  em R$ (Spearman e regressão simples com IC por bootstrap, n da ordem de 20 safras).
- **Fora de escopo:** projeção de produtividade. A série tem 21 pontos e não há quebra
  confirmada; projetar seria confiança fabricada.
- Resultado nulo é reportado como nulo. Texto afirmativo de quebra é proibido por teste.
