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
| 3 | Quer a evolução | "Está melhorando ou foi 2023?" | `/uf/PB` | Lê a média por fase (2003–12 e 2013–22) com 2023 destacado; abre a inclinação com intervalo (janela de 5, 10 ou 21 anos) como apoio | Fase e pico separados; "sobe" ou "cai" só quando o intervalo exclui zero; aviso de quebra não confirmada |
| 4 | Quer localizar o problema | "Quais microrregiões caem?" | `/uf/PB` → `/microrregiao/:cod` | Clica na microrregião (drill-through) | Série, referência e ação sugerida |
| 5 | Quer saber onde está a base de cana | "Onde está a cana na PB?" | `/municipios` | Ordena por área colhida; filtra microrregião e área mínima | Participação de cada município na área da PB; sem ranking de produtividade; zero real separado de dado suprimido |
| 6 | Sinal de mercado | "O açúcar subiu em reais?" | `/mercado` | Lê câmbio, ICE e países | Contexto com data e fonte |
| 7 | Hipótese | "E se a meta for 65?" | `/cenarios` | Mexe nos parâmetros | Leitura muda; o cenário vira link |
| 8 | Prepara a pauta | "Quais 3 casos levo?" | `/prioridades` | Copia o link | Resumo reabre idêntico em outro lugar |
| 9 | Dúvida de confiança | "De onde vem isso?" | `/metodologia` | Lê definições e limitações | Confiança calibrada |

## 3. Tabela 3.1 — rotas

Rotas com parâmetro de caminho: `/uf/:sigla`, `/microrregiao/:cod`, `/municipio/:cod`.

| Rota | Conteúdo | Parâmetros de consulta | Como o usuário chega |
|---|---|---|---|
| `/` | Panorama nacional: KPIs, mapa e barras divergentes por UF, leitura do recorte | `ano`, `ref` (`selecao`\|`grupo`\|`participacao`), `tier`, `ind` (`produtividade`\|`participacao`\|`mix`), `janela` | Abertura; clique no logo |
| `/uf/:sigla` | Série por fase, inclinação com intervalo, microrregiões da UF, leitura | `ano`, `ref`, `janela`, `meta` | Clique em UF no mapa ou nas barras de `/` |
| `/microrregiao/:cod` | Série e referência da microrregião, municípios | `ano`, `janela` | Clique em microrregião em `/uf/PB` |
| `/municipios` | Base de cana dos municípios da PB: área, participação e quantidade (só PB) | `ano`, `micro`, `area_min`, `ordem` (`area`\|`participacao`\|`nome`; padrão `area`), `pagina` | Botão em `/uf/PB`; clique na microrregião |
| `/municipio/:cod` | Retrato e série curta do município, com zero real e suprimido distintos | `ano` | Clique na linha de `/municipios` |
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
| `janela` | Persiste | Persiste | Reinicia | Reinicia | Altera a inclinação; mudar sem avisar enganaria |
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
│ Série por fase (médias 2003–12 e 2013–22),   │ Múltiplos pequenos    │
│ 2023 destacado; inclinação com intervalo     │ por microrregião      │
│ (selo "quebra não confirmada")               │                       │
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
│ Limitações (zero real x suprimido, estimativa municipal arredondada,  │
│ série de 21 pontos, sem quebra confirmada)                            │
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
| S3 | Base de cana: em quais municípios está a área | PAM município (só PB), área e quantidade | `ano`, `micro`, `area_min`, `ordem`, `pagina` | R04, R12 | Quem fornece à usina (dado privado); que um município é mais produtivo que outro (a produtividade municipal tem poucos valores distintos); que município sem produção "produz pouco" (é zero registrado) |
| S4 | Dólar e ICE sobem: levar a pauta de mix à reunião? (INT) | PTAX, ICE, CONAB share ATR | `cambio`, `ice`, `uf` | R10, R11, R14 | Paridade açúcar x etanol, capacidade da usina, preço futuro, "mude o mix" |
| S5 | Safra fraca na Índia e Tailândia, estoques baixos (INT) | USDA PSD, ICE, COT | `periodo`, `paises` | R11, R15 | Que um fator cause o outro |
| S6 | 2023 foi pico: a meta deve subir? | PAM série, médias por fase, inclinação com intervalo | `janela`, `meta` | R06, R07, R16 | "Novo patamar" ou anomalia por clima (ADR 0007) |
| S7 | Cobertura insuficiente: o app recusa recomendar | Cobertura por fonte e território | qualquer combinação | R03, R04, R12 | Qualquer ação sugerida |
| S8 | Véspera da reunião: resumo em 10 minutos | `/prioridades` + link | `ano`, `uf`, `n` | R12, R13, R14 | Ação quando faltam dados |

Em S1 a S3, S6 e S7 só a PAM e a CONAB são necessárias. Se uma fonte internacional cair, as
telas de PAM seguem funcionando (degradação graciosa, ADR 0016).

A validar com a persona (Task 17 ou antes): limiares das regras, se a safra é a unidade de
tempo natural, se aceita o sinal de mercado como contexto, quem decide o mix e se o resumo
chega a essa pessoa.

## 7. Revisão dos passos 3 e 5 (evidência dos dados)

Reproduzível com `python scripts/analise_tendencia_base_municipal.py`.

### 7.1 Passo 3: o que a tendência sustenta

A coluna `nivel_suavizado_t_ha` da gold é uma média móvel centrada de 3 anos. Ela é um nível suavizado,
não uma taxa, e fica vazia em 2003 e 2023. A inclinação em t/ha/ano (função `tendencia_anual`)
não está na gold e não traz erro-padrão. A coluna se chamava `tendencia_t_ha` e foi renomeada para `nivel_suavizado_t_ha` na Task 5, para não sugerir uma taxa. A inclinação com IC 95% agora é calculada em `canavis.domain.tendencia`. Para a PB:

| Janela | Mínimos quadrados (t/ha/ano) | IC 95% | Theil-Sen | Sem 2023 (mín. quadrados) |
|---|---|---|---|---|
| 5 anos (2019–23) | +1,81 | −1,29 a +4,91 | +0,77 | +0,56 (2018–22) |
| 10 anos (2014–23) | +0,49 | −0,24 a +1,22 | +0,04 | +0,30 (2013–22) |
| 21 anos (2003–23) | +0,40 | +0,13 a +0,66 | +0,31 | não se aplica |

- Nas janelas de 5 e 10 anos o intervalo inclui zero: o dado não sustenta "sobe". Na de 10 anos
  o Theil-Sen (+0,04) discorda do mínimos quadrados (+0,49), sinal de que um ponto puxa a reta.
- 2023 variou +8,42 t/ha, contra desvio-padrão de 4,47 t/ha na variação anual. Sem 2023, a
  inclinação de 2013 a 2022 cai de +0,666 (valor do ADR 0004) para +0,302.
- A inclinação de 21 anos é significativa, mas mistura duas fases: média de 50,9 t/ha em
  2003–12 e 55,0 t/ha em 2013–22.

Decisão para o app:
1. A leitura principal do passo 3 é a **média por fase com 2023 destacado**. A inclinação fica
   como apoio, com intervalo.
2. Classificação: **sobe** ou **cai** só quando o IC 95% exclui zero; caso contrário **estável
   (sem evidência de tendência)**. Com o dado atual, a PB fica "estável" em 5 e 10 anos.
3. Quando a inclinação mudaria de classe ao retirar o último ano, o texto avisa
   ("a leitura depende de {ano}").
4. **R07 reescrita:** dispara quando as classes de 5 e 10 anos diferem e ambas têm IC que exclui
   zero. Texto: "A tendência mudou: {a} t/ha/ano nos últimos 5 anos contra {b} nos últimos 10
   (intervalos de confiança em {tabela})." Com a PB atual, a R07 não dispara, e isso é o
   comportamento correto. O hedge "sem evidência confirmada de quebra estrutural" permanece.
5. Trabalho de código (fora desta branch, vai para as Tasks 5 e 15): renomear a coluna da média
   móvel para `nivel_suavizado_t_ha`, materializar inclinação, erro-padrão e IC na gold, e
   substituir `ponto_candidato_quebra` fixo em 2013 pela varredura supF já existente.

### 7.2 Passo 5: o que os dados municipais sustentam

O que há por município: cana (IBGE PAM, 223 municípios, 2003–2023) e vendas de etanol
hidratado (ANP, medem consumo). Produção de etanol existe só por UF. Não há dado de fornecedor
de uma usina (privado, fora de escopo).

- **Zero real não é supressão.** Em 2023: 82 municípios produzem cana, 140 têm `sem_producao`
  (zero registrado) e 1 está `suprimido`. Em 2003–2023 há 26 linhas suprimidas, no máximo 1 por
  ano (6 em 2017). A taxa de "62% ausentes" do ADR 0004 mistura os dois casos.
- **A produtividade municipal quase não varia.** Em 2023 os 82 municípios têm 13 valores
  distintos, e 39% estão em exatamente 65,0 t/ha. No total há 77 valores distintos em 1.797
  linhas. Isso é compatível com estimativa arredondada (inferência; não conferida na
  documentação do IBGE). A produtividade não diferencia municípios.
- **A quantidade não é informação independente**, pois deriva de produtividade vezes área.
- **A área colhida carrega o sinal**: em 2023 os 5 maiores municípios concentram 57% da área.

Decisão para o app:
1. O passo 5 deixa de falar em fornecedores. Passa a responder "onde está a base de cana na PB".
2. `/municipios` ordena por área colhida e mostra participação na área da PB, com a
   produtividade só como coluna informativa e o aviso "valores municipais tendem a se repetir".
3. O app diz "82 de 223 municípios produzem cana em {ano}; os demais têm produção zero" e
   mostra suprimidos à parte ("1 sem informação").
4. **R04 reescrita:** "{n} de {N} municípios produzem cana em {ano}; {z} têm produção zero
   registrada e {s} estão sem informação (dado não divulgado pelo IBGE)." Suprimido nunca é somado
   nem plotado como 0; zero real é plotado como 0.
5. O ranking é recusado (R12) quando restam menos de 5 municípios com produção.
6. A narrativa e o relatório não prometem análise de fornecedores.

