# Registro de decisões de arquitetura (ADR)

Decisões relevantes do projeto ficam aqui, uma por arquivo, em ordem cronológica. O objetivo é
que a disciplina de "iterar e registrar a mudança" tenha lastro: quando uma escolha for
revista nas Etapas 2 ou 3, o motivo original estará documentado.

| # | Decisão | Status |
|---|---------|--------|
| [0001](0001-camadas-de-dados.md) | Organizar os dados em camadas bronze/silver/gold | Aceita |
| [0002](0002-fontes-publicas.md) | IBGE e CONAB como base; ANP como contexto; Comex fora | Aceita |
| [0003](0003-clean-architecture.md) | Separar domínio, fontes e pipeline com regra de dependência | Aceita |
| [0004](0004-granularidade-e-janela-temporal.md) | Granularidade por tipo de análise e janela temporal para tendência | Aceita |
| [0005](0005-vereditos-de-indicadores.md) | Vereditos de validação dos indicadores (mantém/ajusta/descarta) | Aceita |
| [0006](0006-tiers-de-comparacao-por-clusterizacao.md) | Tiers de comparação por clusterização (agrupar por escala, comparar por eficiência) | Proposta |
