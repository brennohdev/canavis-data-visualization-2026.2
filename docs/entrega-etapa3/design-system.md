# CanaVis — Design system, colorimetria e acessibilidade (Etapa 3)

Task 3 (issue #27). Tokens em `apps/web/src/styles/tokens.css`. Medições reproduzíveis com
`python scripts/contraste_paleta.py` (WCAG 2.1 e simulação de daltonismo, sem dependências).
Parte da paleta da Etapa 2 (`docs/entrega-etapa2/paleta-acessibilidade.md`).
**Status:** microcopy da seção 6 aprovada pelo time (24/11/2026). O front (`apps/web`, Task 4) usa os tokens
via mini design system: ver `catalogo-componentes.md` e `conformidade-design-system.md`.

## 1. O que mudou em relação à Etapa 2, e por quê

A medição com script mostrou que duas cores da Etapa 2 não passam em 3:1 como forma sobre o
fundo `#F2F2F2`, que é o mínimo do critério de aceitação desta task:

| Cor da Etapa 2 | Razão medida | Ajuste na Etapa 3 |
|---|---|---|
| Âmbar `#E08A1E` | 2,40:1 | `#C26F00` (3,37:1). Continua âmbar, só mais escuro |
| Verde claro `#7BA886` | 2,41:1 | `#5E9170` (3,26:1) como série secundária |

O verde-cana `#2F6B3C` mede 5,70:1 (a Etapa 2 anotava 5,0:1). A tela do Power BI e o tema
`powerbi/canavis-theme.json` continuam com os hex antigos; o app web usa os novos. Se o time
quiser coerência total, o tema do Power BI precisa ser atualizado (fora do escopo desta task).

## 2. Cores

### Dado

| Token | Hex | Papel | Texto? |
|---|---|---|---|
| `marca` | `#2F6B3C` | PB, acima da referência, barra principal | sim |
| `abaixo` | `#C26F00` | Abaixo da referência (barras divergentes) | não; usar `abaixo-texto` `#8A4B00` |
| `serie-2` | `#5E9170` | Série secundária, hover | não |
| `acucar` | `#3A6EA5` | Açúcar (mix) | usar `acucar-texto` `#2B5580` |
| `etanol` | `#A8641A` | Etanol (mix), sempre com hachura | usar `abaixo-texto` `#8A4B00` |
| `neutro-dado` | `#6B7785` | Demais regiões, linha de referência | usar `neutro-dado-texto` `#566170` |
| `ausente` | `#6B7785` + hachura | Sem informação | não |

### Neutros e estado

| Token | Hex | Papel |
|---|---|---|
| `fundo` | `#F2F2F2` | Fundo (`#FFFFFF` para projeção) |
| `superficie` | `#FFFFFF` | Cartões e painel de leitura |
| `texto` | `#1A1A1A` | Texto principal |
| `texto-secundario` | `#50565E` | Texto de apoio |
| `grade` | `#D5D9DE` | Linhas de grade (decorativa) |
| `eixo` | `#7C8691` | Eixos e contornos de forma |
| `foco` | `#1D4ED8` | Anel de foco, 3 px com 2 px de deslocamento |
| `cenario` | `#1D4ED8` | Borda e selo de cenário ativo |

### Escolha do par açúcar x etanol

| Par | ΔE normal | Protanopia | Deuteranopia | Tritanopia | Decisão |
|---|---|---|---|---|---|
| Azul-ardósia `#3A6EA5` x ocre `#A8641A` | 87,3 | 81,8 | 87,9 | 73,0 | **Escolhido** |
| Azul-ardósia x verde `#5E9170` | 54,2 | 49,3 | 48,9 | 14,3 | Descartado: falha na tritanopia |

ΔE é a distância em CIELAB; acima de 20 as cores se separam bem. O ocre do etanol lembra o
âmbar da divergência, então as duas cores nunca aparecem no mesmo gráfico. Além disso, o etanol
usa hachura e todo gráfico de mix tem rótulo direto, de modo que a cor não é a única pista.

### Rampa sequencial do coroplético

Seis degraus de verde com luminância monotônica decrescente (0,837 → 0,058), sem passar por
vermelho ou por par verde-vermelho: `#E3EFE5`, `#B5D3BB`, `#7BA886`, `#4A8057`, `#2F6B3C`,
`#1F4D2B`. Os degraus claros não chegam a 3:1 contra o fundo (o primeiro mede 1,14:1), então
**toda área da rampa tem contorno de 1 px em `#50565E` (6,6:1)**. Essa é a regra que atende
o critério de formas. Cada degrau da legenda mostra o intervalo numérico, e o valor aparece no
tooltip e na tabela equivalente.

## 3. Tabela de contraste (WCAG 2.1 AA)

Texto (mínimo 4,5:1) sobre `#F2F2F2`, salvo indicação:

| Par | Razão | Resultado |
|---|---|---|
| Texto principal `#1A1A1A` | 15,55:1 | Passa |
| Texto secundário `#50565E` | 6,62:1 | Passa |
| Verde-cana `#2F6B3C` | 5,70:1 | Passa |
| Âmbar escuro `#8A4B00` | 6,08:1 | Passa |
| Azul-ardósia escuro `#2B5580` | 6,91:1 | Passa |
| Cinza de dado escuro `#566170` | 5,62:1 | Passa |
| Branco sobre verde-cana | 6,38:1 | Passa |
| Branco sobre azul-ardósia escuro `#2B5580` | 7,74:1 | Passa |
| Texto principal sobre âmbar `#C26F00` | 4,61:1 | Passa |

Formas (mínimo 3:1) sobre `#F2F2F2`:

| Par | Razão | Resultado |
|---|---|---|
| Verde-cana `#2F6B3C` | 5,70:1 | Passa |
| Âmbar `#C26F00` | 3,37:1 | Passa |
| Verde médio `#5E9170` | 3,26:1 | Passa |
| Açúcar `#3A6EA5` | 4,74:1 | Passa |
| Etanol `#A8641A` | 4,17:1 | Passa |
| Cinza de dado `#6B7785` | 4,08:1 | Passa |
| Eixo e contorno `#7C8691` | 3,30:1 | Passa |
| Anel de foco `#1D4ED8` | 5,99:1 | Passa |
| Contorno de área da rampa `#50565E` | 6,62:1 | Passa |
| Degrau mais escuro da rampa `#1F4D2B` | 8,71:1 | Passa |

Exceções declaradas: a grade `#D5D9DE` é decorativa, e nenhuma informação depende dela. Os
degraus claros da rampa dependem do contorno, como descrito acima.

Regra de uso: âmbar `#C26F00`, verde médio, etanol e cinza de dado são preenchimento de formas.
Texto nessas cores usa a variante escura indicada na seção 2.

## 4. Daltonismo

Simulação de Machado et al. (2009), severidade 1,0, em `scripts/contraste_paleta.py`.

| Par | Normal | Protanopia | Deuteranopia | Tritanopia |
|---|---|---|---|---|
| Acima x abaixo (verde-cana x âmbar) | 72,6 | 32,0 | 47,5 | 77,5 |
| Açúcar x etanol (azul x ocre) | 87,3 | 81,8 | 87,9 | 73,0 |
| Verde-cana x azul-ardósia | 63,7 | 58,2 | 55,7 | 12,8 |
| Verde médio x cinza de dado | 32,2 | 25,4 | 20,9 | 15,2 |

Dois pares ficam abaixo de 20 na tritanopia: verde-cana x azul-ardósia e verde médio x cinza de
dado. Regra derivada: **esses pares não aparecem juntos como únicas pistas de um gráfico.** Quando
coexistem, a série da PB tem rótulo direto e a outra usa linha tracejada. Daltonismo é só um
dos testes; a informação nunca depende só da cor (direção da barra em relação ao zero,
rótulo direto, hachura).

## 5. Ausente não é zero, e zero real não é ausente

A PAM tem dois casos distintos (ADR 0008) e cada um tem tratamento próprio:

| Caso | Significado | Tratamento visual | Texto |
|---|---|---|---|
| `suprimido` | Dado não divulgado pelo IBGE | Cinza `#6B7785` com **hachura diagonal** (`hachura-ausente`); fora da rampa; lacuna em linhas | "Sem informação (dado não divulgado pelo IBGE)" |
| `sem_producao` | Zero registrado: o município não produz cana | Plotado como 0 (barra de comprimento zero, ponto em 0). No mapa: preenchimento `superficie` (`#FFFFFF`) com contorno, fora da rampa | "Sem produção de cana (zero registrado)" |

- Em tabela, suprimido mostra "sem informação" e zero real mostra "0" ou "sem produção"; nunca
  célula em branco.
- Médias e totais ignoram os suprimidos e dizem quantos foram ignorados (regra R04).
- Em 2023 na PB: 82 municípios produzem, 140 têm zero registrado e 1 está suprimido. Chamar os
  140 de "supressão" seria errado.

## 6. Estados e microcopy (pt-BR)

Aprovada pelo time em 24/11/2026.

| Estado | Comportamento | Texto |
|---|---|---|
| Carregando | Esqueleto com o formato do gráfico, `aria-busy="true"`. Nunca spinner infinito | "Carregando dados…" |
| Carregando, após 8 s | Mantém o esqueleto e mostra botão | "Ainda carregando. Isso está demorando mais que o normal." Botão: "Tentar de novo" |
| Vazio | Mostra o primeiro filtro que, removido, devolve resultado (calculado no backend) | "Nenhum registro atende a esta combinação de filtros." + "Tente: {remover o grupo (tier)}." Botão: "Aplicar sugestão" |
| Erro de carga | Linguagem simples, código técnico recolhido. Telas de PAM seguem funcionando se só o mercado falhou | "Não foi possível carregar estes dados." Detalhe recolhido: "Detalhes técnicos". Botão: "Tentar de novo" |
| Fonte fora do ar | Selo no card, sem derrubar a tela | "Fonte fora do ar. Mostrando dados de {data}." |
| Dado suprimido | Hachura cinza + legenda | "Sem informação (dado não divulgado pelo IBGE)." |
| Sem produção | Zero plotado; no mapa, branco com contorno | "Sem produção de cana (zero registrado)." |
| Produtividade municipal | Aviso junto à coluna | "Valores municipais tendem a se repetir; use a área para comparar municípios." |
| Tendência sem evidência | Selo no gráfico e na leitura | "Estável: o intervalo de confiança inclui zero." |
| Base pequena | Selo no gráfico e na leitura | "Base pequena: {n} municípios com dado." |
| Defasagem | Faixa no topo da tela, não só no rodapé | "Atenção: PAM vai até {ano}; CONAB até {safra} (estimativa)." |
| Recusa por cobertura | Sem ação sugerida | "Dados insuficientes para recomendar nesta combinação ({motivo})." |
| Parâmetro ajustado | Aviso discreto abaixo dos filtros | "Ajustamos o parâmetro {nome} para o valor padrão." |
| Cenário ativo | Selo com borda `cenario` e botão | "Cenário: meta {m} t/ha" · Botão: "Voltar ao realizado" |
| Rota inexistente | Página 404 com links | "Esta página não existe. Volte ao panorama." |

## 7. Gráficos não convencionais (extra 1)

Cada gráfico tem tabela equivalente (botão "Ver como tabela") e texto alternativo curto com a
mensagem. Biblioteca: Observable Plot (ADR 0017).

### 7.1 Coroplético de produtividade

- **Pergunta:** "Onde a PB está no mapa de produtividade?"
- **Dados:** produtividade (t/ha) por UF no Panorama e por microrregião da PB em `/uf/PB`.
- **Codificação:** rampa de 6 degraus (seção 2), contorno de 1 px, ausente com hachura.
  A PB tem contorno de 2 px em `marca`. Legenda com intervalos numéricos.
- **Interação:** clique leva a `/uf/:sigla` ou `/microrregiao/:cod`. Foco por teclado em cada
  região, com rótulo "PB, 64,69 t/ha".
- **Tabela equivalente:** território, produtividade, desvio vs referência.
- **Texto alternativo:** "Mapa de produtividade por UF em {ano}. A PB está em {n}º entre {N}."
- **Limite:** cobertura territorial depende das malhas versionadas em `data/geo/` (ADR 0018).

### 7.2 Slope chart: PB e pares do tier, 2013 → 2023

- **Pergunta:** "Quem ganhou ou perdeu posição desde a inversão de regime?"
- **Codificação:** duas colunas (ano inicial e final), uma linha por UF do tier. A PB em
  `marca` e traço grosso; as demais em `neutro-dado` e traço fino. Rótulo direto nas pontas.
  Sem cor extra para ganhou e perdeu: a inclinação da linha já mostra.
- **Interação:** selecionar o ano inicial e o final por controle (parâmetros de URL a definir na Task 14).
- **Tabela equivalente:** UF, valor inicial, valor final, variação, posição inicial e final.
- **Texto alternativo:** "A PB passou do {a}º ao {b}º lugar entre {ano0} e {ano1} no grupo {tier}."
- **Limite:** não afirma causa nem tendência futura.

### 7.3 Múltiplos pequenos de microrregiões

- **Pergunta:** "Quais microrregiões ganham ou perdem de forma consistente?"
- **Codificação:** uma série curta por microrregião, mesmos eixos em todas (escala comum, para
  comparar), linha `marca`, referência da PB em `neutro-dado` tracejada. Ausente com lacuna.
- **Ordenação:** pela inclinação (menor primeiro), nunca alfabética. Só rotula "queda" quando o intervalo exclui zero.
- **Interação:** clique abre `/microrregiao/:cod`.
- **Tabela equivalente:** microrregião, inclinação com intervalo (t/ha/ano), último valor, anos com dado.
- **Texto alternativo:** "{n} microrregiões; {k} com queda confirmada pelo intervalo na janela de {j} anos."
- **Limite:** série curta e com ausentes; a leitura traz o número de anos com dado.

## 8. Tipografia e espaçamento

- **Inter** para interface e números (`font-variant-numeric: tabular-nums`). **Source Serif 4**
  apenas no painel de leitura. Ambas auto-hospedadas (Fontsource), sem CDN.
- Escala de 14, 16, 20 e 28 px. Corpo em 16 px com entrelinha 1,5.
- Espaçamento em múltiplos de 4 px. Desktop-first (≥ 1280 px); tablet (1024 px) em modo leitura.
- Hierarquia de cada tela: pergunta e filtros, leitura em texto, evidência gráfica.
  Máximo de 3 gráficos por tela.

## 9. Política de acessibilidade

**Entra:**
- Contraste AA para texto e 3:1 para formas, medido por script (seção 3).
- Informação nunca só por cor: direção, rótulo direto, hachura.
- Foco visível e navegação por teclado em filtros, mapa e gráficos; componentes Radix/shadcn.
- `aria-live="polite"` no painel de leitura quando o filtro muda.
- Tabela equivalente e texto alternativo curto em todo gráfico.
- `prefers-reduced-motion` respeitado.
- Auditoria automatizada com axe no Playwright nas rotas principais.

**Fica de fora, e por quê:**

| Item | Motivo |
|---|---|
| Celular | O uso é pontual, em reunião com notebook. Tablet de 1024 px é a meta mínima. Limitação declarada no relatório |
| WCAG AAA | O produto tem um usuário conhecido e o custo supera o ganho. Mira-se AA |
| Leitor de tela completo nos gráficos | A tabela equivalente e o texto alternativo cobrem a informação; a navegação ponto a ponto no SVG não é testada |
| Alto contraste dedicado e tema escuro | Sem demanda da persona; o AA já cobre o uso previsto |
| Internacionalização | Produto só em pt-BR |

## 10. Pendências

- O front usa os tokens desde a Task 4. `tokens.css` é importado no CSS de entrada, os componentes
  estão em `catalogo-componentes.md` e o estado de cada regra em `conformidade-design-system.md`.
- Atualizar o tema do Power BI, se o time quiser coerência com os novos hex.
