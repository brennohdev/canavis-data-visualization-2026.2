# CanaVis — Conformidade do front com o design system (Etapa 3, Task 4)
Cruza as regras de `design-system.md`, `entrega-etapa2/paleta-acessibilidade.md`,
`jornada-e-rotas.md` e ADR 0017 que se aplicam ao front com o estado atual de `apps/web`.
Componentes em `catalogo-componentes.md`.
Estados: **Implementada**, **Coberta por teste (arquivo)** e **Adiada (#N)**. As issues estão no
GitHub: #28 Task 4, #30 Task 6, #32 Task 8, #35 Task 11, #37 Task 13, #38 Task 14, #40 Task 16.
## Tokens, cores e contraste (§1 a §4)
| Regra | Estado |
|---|---|
| `tokens.css` importado e tokens em `@theme` (`src/styles/index.css`) | Implementada |
| Cores só por token, sem paleta padrão do Tailwind nem hex em `src` | Coberta por teste (`src/design-system/conformidade.test.ts`) |
| Texto colorido usa a variante `-texto`, nunca `text-abaixo`, `text-serie-2` etc. | Coberta por teste (`src/design-system/conformidade.test.ts`) |
| Texto >= 4,5:1 e formas >= 3:1 sobre `fundo` (tabela da §3) | Coberta por teste (`src/design-system/contraste.test.ts`) |
| Âmbar, verde médio, etanol e cinza de dado só em preenchimento de forma | Coberta por teste (`src/design-system/conformidade.test.ts`) |
| Coroplético: rampa de 6 degraus e contorno de 1 px | Adiada (#38) |
| Pares sensíveis à tritanopia nunca como única pista | Adiada (#38) |
## Ausente não é zero (§5)
| Regra | Estado |
|---|---|
| `hachura-ausente` e `hachura-etanol` existem e aparecem na `Legenda` com rótulo | Coberta por teste (`src/routes/uf.test.tsx`, `src/design-system/componentes.test.tsx`) |
| Tabela mostra "sem informação" e zero real mostra "0" | Adiada (#38) |
| Valor nulo da API aparece como "dado ausente" | Implementada (`src/lib/formato.ts`, `src/lib/lib.test.ts`) |
## Estados e microcopy (§6)
| Regra | Estado |
|---|---|
| Carregando: `aria-busy="true"` e "Carregando dados…" | Coberta por teste (`src/design-system/componentes.test.tsx`) |
| Erro de carga: `role="alert"` e "Não foi possível carregar estes dados." | Coberta por teste (`src/design-system/componentes.test.tsx`, `src/routes/uf.test.tsx`) |
| Esqueleto com o formato do gráfico e botão "Tentar de novo" após 8 s | Adiada (#37) |
| Vazio, fonte fora do ar, defasagem, parâmetro ajustado, rota 404 | Adiada (#37 e #32) |
| Selo de cenário ativo | Adiada (#35) |
## Gráficos (§7, ADR 0017)
| Regra | Estado |
|---|---|
| Coroplético, slope e múltiplos pequenos | Adiada (#38) |
| Tabela equivalente e texto alternativo em todo gráfico | Adiada (#38) |
## Tipografia e espaçamento (§8)
| Regra | Estado |
|---|---|
| Inter e Source Serif 4 auto-hospedadas por Fontsource, sem CDN | Implementada (`src/styles/index.css`, `package.json`) |
| Escala de 14, 16, 20 e 28 px | Implementada (tokens `--text-*`) |
| Números tabulares (`.num`, `[data-kpi]`) | Implementada (`Kpi`) |
| Source Serif 4 só no painel de leitura | Implementada (`PainelLeitura`) |
| Espaçamento em múltiplos de 4 px | Implementada (`--spacing`) |
## Acessibilidade (§9, paleta-acessibilidade.md)
| Regra | Estado |
|---|---|
| Foco visível (`:focus-visible`, 3 px com 2 px de deslocamento) | Implementada (`tokens.css`) |
| `prefers-reduced-motion` respeitado | Implementada (`tokens.css`) |
| Informação nunca só por cor: amostra da legenda tem hachura e rótulo | Coberta por teste (`src/design-system/componentes.test.tsx`) |
| Análise estática de acessibilidade em JSX | Coberta por teste (`pnpm lint`, jsx-a11y recomendado) |
| Sem violações do axe em `/` e `/uf/PB` | Coberta por teste (`src/design-system/acessibilidade.test.tsx`) |
| `aria-live="polite"` no painel de leitura ao mudar o filtro | Adiada (#32; só há sentido quando houver filtro que mude o texto) |
| axe com contraste real e navegação por teclado no Playwright | Adiada (#32 e #40) |
## Rotas e dados (jornada-e-rotas.md)
| Regra | Estado |
|---|---|
| `/` e `/uf/:sigla` com o ano na URL e ano inválido caindo no padrão | Coberta por teste (`src/routes/uf.test.tsx`) |
| `ANO_MIN`, `ANO_MAX` e ano padrão 2021 contra o último ano da PAM | Adiada (#30 e #32) |
| Tipos gerados do OpenAPI no lugar de `src/lib/api.ts` | Adiada (#30) |
## Padronização do código
| Regra | Estado |
|---|---|
| Rotas sem `className`, `style`, `cn`, `clsx`, `cva` ou `tailwind-merge` | Coberta por teste (`src/design-system/conformidade.test.ts`) |
| Componentes sem `className` e `style` públicos | Coberta por teste (`src/design-system/componentes.test.tsx`, tipos) |
| Zero comentários em `src` (exceto `tokens.css`) | Coberta por teste (`src/test/sem-comentarios.test.ts`) |
## Fora de escopo (§9)
Celular, WCAG AAA, tema escuro e alto contraste, leitor de tela completo nos gráficos e
internacionalização. O motivo de cada um está na §9 do `design-system.md`.
