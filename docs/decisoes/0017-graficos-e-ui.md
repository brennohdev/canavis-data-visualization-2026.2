# 0017 — Bibliotecas de gráficos e UI

**Status:** Proposta
**Evidência:** `docs/entrega-etapa3/planejamento-etapa3.md` (seção 6)

## Decisão
- **Gráficos:** Observable Plot + D3 (d3-geo, d3-scale) com wrapper React fino. Saída SVG,
  que facilita rótulo, teste e `role`/`aria`. Cobre barras divergentes, linhas, facetas,
  slope e coroplético.
- **UI:** Tailwind CSS v4 + shadcn/ui (Radix), para primitivos acessíveis e tokens de cor
  em um só lugar.
- **Tipografia:** Inter (números tabulares) e Source Serif 4 no bloco de leitura, auto-hospedadas.
- Cada gráfico tem tabela equivalente e texto alternativo curto. Informação nunca só por cor.
- Contraste WCAG 2.1 AA, medido por script na Task 3; axe no Playwright.

## Alternativas rejeitadas
ECharts (canvas e bundle grande), Recharts (fraco para mapa, slope e facetas), visx (mais código).

## Riscos
Tooltips e interação são mais manuais no Plot; mitigação com a marca `tip` e a tabela equivalente.
