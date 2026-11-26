# CanaVis — Catálogo de componentes (Etapa 3, Task 4)
Mini design system do front, em `apps/web/src/components`. Implementa os tokens de
`design-system.md` e a decisão de UI do ADR 0017. Conformidade regra a regra em
`conformidade-design-system.md`.
## Princípio
Rotas só compõem componentes. Toda classe CSS mora em `src/components/` (e `src/lib/utils.ts`).
Um componente não aceita `className` nem `style`; o que muda entre usos é uma variante com nome.
## Como a padronização é imposta
Três camadas, todas falham em `pnpm typecheck`, `pnpm lint` ou `pnpm test`:
1. **Tipos.** Os props dos componentes omitem `className` e `style`, e as variantes são uniões
   TypeScript geradas por `class-variance-authority`. Passar uma classe a um componente não compila.
2. **ESLint** (`apps/web/eslint.config.js`, sem plugin de Tailwind). Fora de `src/components/**`
   e `src/lib/utils.ts` ficam proibidos o atributo `className`, o atributo `style` e os imports de
   `clsx`, `class-variance-authority`, `tailwind-merge` e `@/lib/utils`. Em todo `src/**` ficam
   proibidos, dentro de strings, cor da paleta padrão do Tailwind (`bg-red-500`, `text-gray-700`,
   `bg-white`), hex literal e token só de forma usado como texto (`text-serie-2`, `text-abaixo`).
   Para texto, use a variante `-texto` (`text-abaixo-texto`). `eslint-plugin-jsx-a11y`
   (config `recommended`) cobre `src/**/*.tsx`.
3. **Teste que prova a regra.** `src/design-system/conformidade.test.ts` roda o ESLint com a
   configuração real sobre trechos violadores e exige a mensagem certa; um trecho correto não
   gera mensagem.
Também por teste: `src/test/sem-comentarios.test.ts` (zero comentários em `src`, exceto
`tokens.css`, que é CSS e fica fora).
## Componentes
Primitivos genéricos em `components/ui/`; componentes do domínio em `components/dados/`.
| Componente | Arquivo | Variantes | Quando usar |
|---|---|---|---|
| `Pagina` | `ui/pagina.tsx` | nenhuma | Raiz de toda rota. Renderiza `<main>` com largura máxima e espaçamento |
| `Titulo` | `ui/titulo.tsx` | `nivel` 1 (h1, 28 px) ou 2 (h2, 14 px, secundário) | Título da tela e de seções |
| `Texto` | `ui/texto.tsx` | `tom` padrao, secundario, erro; `tamanho` base, pequeno | Parágrafo comum. `erro` usa `text-abaixo-texto` |
| `LinkTexto` | `ui/link-texto.tsx` | `tamanho` base, pequeno | Link interno. Usa `createLink` do TanStack Router e mantém o tipo de `to`, `params` e `search` |
| `Card` | `ui/card.tsx` | nenhuma | Superfície branca com raio e sombra dos tokens |
| `Kpi` | `dados/kpi.tsx` | nenhuma | Um número em destaque com rótulo e detalhe opcional. O valor leva `data-kpi` (tabular) e o detalhe usa `.num` |
| `PainelLeitura` | `dados/painel-leitura.tsx` | nenhuma | Texto dinâmico. Usa a classe global `.leitura` (Source Serif 4) |
| `Legenda` e `ItemLegenda` | `dados/legenda.tsx` | `padrao` etanol, ausente, marca | Legenda com amostra (`aria-hidden`) e rótulo. Etanol e ausente usam hachura |
| `Carregando` | `dados/estado-consulta.tsx` | nenhuma | `role="status"`, `aria-busy="true"`, "Carregando dados…" |
| `ErroCarga` | `dados/estado-consulta.tsx` | nenhuma | `role="alert"`, tom de erro. Mostra a mensagem da API ou "Não foi possível carregar estes dados." |
As classes globais `.leitura`, `.num`, `.hachura-ausente` e `.hachura-etanol` vêm de
`src/styles/tokens.css`. O teste `src/design-system/componentes.test.tsx` renderiza cada variante
e confere as classes de token.
## O que entra depois, e em qual issue
Nada abaixo existe hoje. Cada item nasce junto com a tela que o usa.
| Componente | Issue |
|---|---|
| Gráficos (Observable Plot), coroplético, slope, múltiplos pequenos e tabela equivalente | #38 |
| Filtros e controles ligados à URL | #32 |
| Painel de leitura completo (descrever, destacar, sugerir) e selo de cenário | #35 |
| Estados vazio, esqueleto e botão após 8 s | #37 |
## Como criar um componente novo
1. Crie o arquivo em `components/ui/` (genérico) ou `components/dados/` (domínio).
2. Tipe os props com `Omit<ComponentProps<"tag">, "className" | "style">` e exponha só
   variantes nomeadas, por `cva`.
3. Use somente classes dos tokens de `tokens.css`. Texto colorido usa a variante `-texto`.
4. Acrescente o caso em `componentes.test.tsx` e uma linha na tabela acima.
5. Rode `pnpm typecheck`, `pnpm lint` e `pnpm test`.
## Decisões
- **D4, imposição.** Tipos, ESLint nativo e um teste que prova a falha. `eslint-plugin-tailwindcss`
  foi rejeitado: o suporte a Tailwind v4 é incompleto e seria uma dependência a mais.
- **D5, organização.** `ui` para primitivos, `dados` para o domínio. Só há variante quando a
  fatia atual usa mais de um valor. Não há Botão, Select, Badge nem Tabela até alguma tela pedir.
- **D6, acessibilidade.** `eslint-plugin-jsx-a11y` (análise estática), `axe-core` no Vitest sobre
  `/` e `/uf/PB` com `color-contrast` desligado (o jsdom não calcula layout) e um teste de
  contraste WCAG calculado a partir de `tokens.css`. O contraste real e o teclado ficam para o
  axe no Playwright.
- **D7, sem página de amostra.** Uma rota só para mostrar componentes entra no bundle e não tem
  usuário. O catálogo, os testes e a `Legenda` em `/uf/PB` cumprem esse papel.
- **D8, sem comentários.** Imposto por teste, não por convenção.
