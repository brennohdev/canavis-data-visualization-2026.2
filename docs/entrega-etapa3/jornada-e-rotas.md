# CanaVis — Jornada, arquitetura de informação e rotas (Etapa 3)

Task 2 (issue #26). Derivado das seções 2 e 3 de `planejamento-etapa3.md`, com a persona da
Etapa 1 e as decisões dos ADRs 0004, 0006, 0009, 0010, 0011, 0014 e 0020.
**Status:** rascunho para revisão do time. Os itens marcados "A validar" dependem da equipe
ou da persona.

## 1. Persona e pergunta de decisão

Ricardo Meneses (fictício), gerente agrícola de usina na Paraíba. Usa o produto de forma
pontual, antes de reuniões de programação e planejamento de safra. Pergunta central: "como a
produtividade e a produção da minha região se comparam às de outras regiões e como isso
evoluiu ao longo das safras?"

## 2. Jornada em 9 passos

| Passo | Gatilho | Pergunta | Tela | Ação | Resultado |
|---|---|---|---|---|---|
| 1 | Reunião de programação em 2 dias | "Como estamos frente aos pares?" | `/` | Abre; lê KPIs e a leitura do recorte | Posição da PB (desvio vs grupo) com referência explícita |
| 2 | Estranha o desvio | "Contra quem estou me comparando?" | `/` | Troca a referência (seleção, grupo, participação) | Entende que a leitura muda com a referência |
| 3 | Quer a evolução | "Está melhorando ou foi 2023?" | `/uf/PB` | Ajusta a janela de tendência (5, 10, 21 anos) | Tendência com banda e aviso de quebra não confirmada |
| 4 | Quer localizar o problema | "Quais microrregiões caem?" | `/uf/PB` → `/microrregiao/:cod` | Clica na microrregião (drill-through) | Série, referência e ação sugerida |
| 5 | Quer fornecedores | "Quais municípios vejo?" | `/municipios` | Filtra microrregião e área mínima | Retrato com ausentes marcados |
| 6 | Sinal de mercado | "O açúcar subiu em reais?" | `/mercado` | Lê câmbio, ICE e países | Contexto com data e fonte |
| 7 | Hipótese | "E se a meta for 65?" | `/cenarios` | Mexe nos parâmetros | Leitura muda; o cenário vira link |
| 8 | Prepara a pauta | "Quais 3 casos levo?" | `/prioridades` | Copia o link | Resumo reabre idêntico em outro lugar |
| 9 | Dúvida de confiança | "De onde vem isso?" | `/metodologia` | Lê definições e limitações | Confiança calibrada |

## 3. Tabela 3.1 — rotas

Rotas com parâmetro de caminho: `/uf/:sigla`, `/microrregiao/:cod`, `/municipio/:cod`.

| Rota | Conteúdo | Parâmetros de consulta | Como o usuário chega |
|---|---|---|---|
| `/` | Panorama nacional: KPIs, mapa e barras divergentes por UF, leitura do recorte | `ano`, `ref` (`selecao`\|`grupo`\|`participacao`), `tier`, `ind` (`produtividade`\|`participacao`\|`mix`), `janela` | Abertura; clique no logo |
| `/uf/:sigla` | Série, tendência, microrregiões da UF, leitura | `ano`, `ref`, `janela`, `meta` | Clique em UF no mapa ou nas barras de `/` |
| `/microrregiao/:cod` | Série e referência da microrregião, municípios | `ano`, `janela` | Clique em microrregião em `/uf/PB` |
| `/municipios` | Retrato dos municípios da PB (só PB) | `ano`, `micro`, `area_min`, `ordem`, `pagina` | Botão em `/uf/PB`; clique na microrregião |
| `/municipio/:cod` | Retrato e série curta do município, com ausentes | `ano` | Clique na linha de `/municipios` |
| `/cenarios` | Parâmetros de hipótese e comparação base x alternativos | `uf`, `ano`, `meta`, `cambio`, `ice`, `janela`, `ref`, `base` | Menu; botão "simular" em `/uf/:sigla` |
| `/mercado` | Câmbio, ICE, balanço por país, COT, status das fontes | `periodo` (`3m`\|`12m`\|`5a`), `paises` (lista) | Menu; link no texto de cenário |
| `/prioridades` | 3 casos prioritários com ação sugerida | `ano`, `uf`, `n` | Menu; abertura recomendada |
| `/metodologia` | Fontes, definições, limitações, licenças, atualização | `ind` (âncora `#indicador`) | Rodapé de todas as telas e botão "?" na leitura |

Regras de URL (ADR 0014):
- Valor igual ao padrão é omitido.
- Parâmetro inválido ou fora de faixa não gera erro: cai no padrão e a tela avisa "ajustamos o parâmetro X".
- Padrões a fixar na Task 4/8: `ano` = último ano da PAM; `ref` = `grupo`; `janela` = 10; `ind` = `produtividade`.

## 4. Persistência de filtros (requisito b)

Controles globais: `ano`, território em foco (UF), `tier`, `ref`, `ind`, `janela`.
Controles de cenário: `meta`, `cambio`, `ice`. Controles locais: `micro`, `area_min`, `ordem`, `pagina`.
A coluna "Panorama → UF → micro → município" descreve a navegação por drill-through.

| Controle | Panorama → UF → micro → município | Para `/cenarios` | Para `/mercado` | Para `/metodologia` | Justificativa |
|---|---|---|---|---|---|
| `ano` | Persiste | Persiste | Não se aplica (usa `periodo`) | Reinicia | O ano é o eixo de leitura de toda a decisão |
| `ref` | Persiste até `/uf`; some em micro e município, mas fica na URL e volta ao retornar | Persiste | Reinicia | Reinicia | Mantém a leitura coerente; só esconde onde não faz sentido (ADR 0006) |
| `tier` | Persiste em `/` e `/uf`; irrelevante abaixo | Persiste | Reinicia | Reinicia | Tier só existe para UF |
| `janela` | Persiste | Persiste | Reinicia | Reinicia | Altera a tendência; mudar sem avisar enganaria |
| `ind` | Persiste | Reinicia (cenário tem indicador próprio) | Reinicia | Âncora | Evita indicador "preso" |
| `meta`, `cambio`, `ice` | Persistem na URL em `/uf` e `/cenarios`; reiniciam em `/` | Origem | `cambio` e `ice` persistem | Reinicia | Hipótese não pode vazar para a leitura do realizado sem rótulo |
| `micro`, `area_min`, `ordem`, `pagina` | Reiniciam ao trocar de nível ou de ano (paginação volta à 1) | Reinicia | Reinicia | Reinicia | Filtros locais valem só para a lista |
| Seleção de entidade (`:sigla`, `:cod`) | Muda por clique | Entra como `uf` | Reinicia | Reinicia | O caminho é parte do estado |

Toda tela com parâmetro de cenário ativo mostra o selo "Cenário: meta 65 t/ha" e o botão
"voltar ao realizado".

## 5. Arquitetura de informação de cada tela

Toda tela tem três faixas (planejamento, seção 6): (1) pergunta e filtros; (2) painel de
leitura com **Descrever**, **Destacar** e **Sugerir**, antes do gráfico; (3) evidência
(gráfico, com tabela equivalente). Máximo de 3 gráficos por tela, desktop-first (≥ 1280 px).

### Painel de leitura (componente comum)

```
┌ Leitura ──────────────────────────────────────────────────────────┐
│ DESCREVER  Recorte: PB, 2023. Produtividade de 64,69 t/ha (IBGE   │
│            PAM, dado de 2023). Referência: média de 6 UFs do grupo│
│ DESTACAR   A produtividade ficou 3,4% acima da referência.        │
│            Sem evidência confirmada de quebra estrutural.         │
│ SUGERIR    Vale revisar a priorização de área em Brejo; confira a │
│            área colhida (X ha) antes de decidir.   [por que vejo?]│
└───────────────────────────────────────────────────────────────────┘
```
"Por que vejo isto?" abre `regra_id`, evidências e limitações do insight (ADR 0015).

### `/` Panorama

```
┌ logo CanaVis   Panorama  Cenários  Mercado  Prioridades  Metodologia ┐
│ Ano [2023▾]  Referência [Grupo▾]  Tier [Média escala▾]  Indicador [▾]│
│ Janela [10 anos▾]                                                    │
├──────────────────────────────────────────────────────────────────────┤
│ KPI Produtividade PB │ KPI Desvio vs ref. │ KPI Posição no tier │ … │
├──────────────────────────────────────────────────────────────────────┤
│ [ Painel de leitura: descrever / destacar / sugerir ]                │
├───────────────────────────────┬──────────────────────────────────────┤
│ Mapa coroplético por UF       │ Barras divergentes vs referência     │
│ (clique → /uf/:sigla)         │ (clique → /uf/:sigla)                │
├──────────────────────────────────────────────────────────────────────┤
│ Rodapé: fontes e defasagem · Metodologia                            │
└──────────────────────────────────────────────────────────────────────┘
```

### `/uf/:sigla`

```
│ Filtros: Ano · Referência · Janela · Meta [slider]   [Simular →]     │
│ [ Painel de leitura ]                                                │
│ Série de produtividade + tendência com banda │ Múltiplos pequenos    │
│ (selo "quebra não confirmada")               │ por microrregião      │
│ Tabela de microrregiões (clique → /microrregiao/:cod)  [Municípios] │
```

### `/cenarios`

```
│ UF [PB▾]  Ano  Referência  Janela                                    │
│ P1 Meta (t/ha) [──●────] 65     P2 Câmbio [ ] ICE [ ]   Base [▾]     │
│ Selo: "Cenário ativo"                      [voltar ao realizado]     │
│ [ Painel de leitura (muda com os parâmetros) ]                       │
│ Base x alternativos: barras lado a lado │ Tabela 3.2                 │
│ Aviso fixo: hipóteses de leitura, não previsões                      │
```

### `/prioridades`

```
│ Ano · UF · Quantos casos [3▾]                                        │
│ ┌ 1 ─────────────┐ ┌ 2 ─────────────┐ ┌ 3 ─────────────┐             │
│ │ Caso, número,  │ │ …              │ │ …              │             │
│ │ referência,    │ │                │ │                │             │
│ │ cobertura,     │ │                │ │                │             │
│ │ ação, [abrir]  │ │                │ │                │             │
│ └────────────────┘ └────────────────┘ └────────────────┘             │
│ [Copiar link]   Quando faltam dados: "Dados insuficientes (motivo)"  │
```

### `/mercado`

```
│ Período [12m▾]  Países [Brasil, Índia, Tailândia, UE, EUA, China]    │
│ [ Painel de leitura: "açúcar em R$ subiu X% em 90 dias" ]            │
│ Câmbio (PTAX) │ ICE açúcar #11 │ Balanço por país (USDA PSD)         │
│ Posicionamento COT                                                   │
│ Status das fontes: selo "snapshot de dd/mm" ou "fonte fora do ar"    │
```

### `/metodologia`

```
│ Sumário (âncoras por indicador)                                      │
│ Fontes e licenças (tabela dim_fonte) · Definições dos indicadores    │
│ Limitações (supressão IBGE, série de 21 pontos, sem quebra confirmada)│
│ Atualização e defasagem · O que o app não afirma                     │
```

Wireframes de média e alta fidelidade (Figma) ainda precisam ser feitos a partir destes
esboços. A validar: o time desenha no arquivo CanaVis e anexa os links na issue #26.

## 6. Cenários de decisão (revisão)

Cada cenário indica dados, parâmetros, regras de texto (IDs do rascunho da Tabela 3.3) e o
que o app **não afirma**.

| # | Cenário | Dados | Parâmetros da URL | Regras | O app não afirma |
|---|---|---|---|---|---|
| S1 | Planejamento de plantio: onde priorizar área | PAM microrregião + tier | `ano`, `ref`, `janela` | R01, R02, R05, R07, R09, R13 | Causa da queda, produtividade futura, quebra estrutural (ADR 0009/0011; PB p ajustado 0,0606; série de 21 pontos) |
| S2 | Revisão de meta de safra | PAM UF/micro | `meta`, `ano`, `ref` | R05, R08 | Probabilidade de atingir a meta |
| S3 | Fornecedores: quais municípios olhar | PAM município (só PB) | `ano`, `micro`, `area_min`, `ordem`, `pagina` | R04, R12 | Que município sem dado "produz pouco" (ausente ≠ zero); ranking com menos de 5 municípios com dado |
| S4 | Dólar e ICE sobem: levar a pauta de mix à reunião? (INT) | PTAX, ICE, CONAB share ATR | `cambio`, `ice`, `uf` | R10, R11, R14 | Paridade açúcar x etanol, capacidade da usina, preço futuro, "mude o mix" |
| S5 | Safra fraca na Índia e Tailândia, estoques baixos (INT) | USDA PSD, ICE, COT | `periodo`, `paises` | R11, R15 | Que um fator cause o outro |
| S6 | 2023 foi pico: a meta deve subir? | PAM série, tendência | `janela`, `meta` | R06, R07, R16 | "Novo patamar" ou anomalia por clima (ADR 0007) |
| S7 | Cobertura insuficiente: o app recusa recomendar | Cobertura por fonte e território | qualquer combinação | R03, R04, R12 | Qualquer ação sugerida |
| S8 | Véspera da reunião: resumo em 10 minutos | `/prioridades` + link | `ano`, `uf`, `n` | R12, R13, R14 | Ação quando faltam dados |

Em S1 a S3, S6 e S7 só a PAM e a CONAB são necessárias. Se uma fonte internacional cair, as
telas de PAM seguem funcionando (degradação graciosa, ADR 0016).

A validar com a persona (Task 17 ou antes): limiares das regras, se a safra é a unidade de
tempo natural, se aceita o sinal de mercado como contexto, quem decide o mix e se o resumo
chega a essa pessoa.
