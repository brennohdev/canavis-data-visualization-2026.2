# 0014 — URL como fonte de verdade e rotas

**Status:** Aceita
**Evidência:** `docs/entrega-etapa3/planejamento-etapa3.md` (seções 3.2 e 3.3)

## Contexto
O requisito (a) exige rotas com a URL refletindo o estado, e o teste de aceitação copia a
URL e a abre em aba anônima. Falhar nisso trava a nota em 3,0 (risco R3).

## Decisão
- Estado de visão (ano, território, tier, ref, ind, janela, parâmetros de cenário) vive na URL;
  componentes não guardam esse estado em memória própria.
- Roteamento com TanStack Router; validação e serialização dos parâmetros com zod.
- Valor igual ao padrão é omitido. Parâmetro inválido ou fora de faixa cai no padrão, sem
  erro, e a tela avisa "ajustamos o parâmetro X".
- Rotas da Tabela 3.1: `/`, `/uf/:sigla`, `/microrregiao/:cod`, `/municipios`,
  `/municipio/:cod`, `/cenarios`, `/mercado`, `/prioridades`, `/metodologia`.
- Persistência de filtros entre telas segue a tabela da seção 3.3 do planejamento.
- Teste e2e (Playwright) abre a URL em contexto limpo e compara leitura e KPIs, em CI.

## Consequências
- Toda interação que muda a visão precisa ter parâmetro correspondente.
- Hipóteses de cenário ficam visíveis na URL e na tela (selo "Cenário").
