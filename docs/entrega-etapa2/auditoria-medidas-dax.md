# Auditoria das medidas DAX + indicadores de volume/mix (Etapa 2, CanaVis)

**Projeto:** CanaVis — Benchmarking regional da produção de cana-de-açúcar na Paraíba
**Pedido de origem:** revisão das medidas (colega Alex) — Desvio vs seleção, Desvio vs grupo,
Participação regional, Produtividade, Vendas etanol (municípios e UF) — e revisão da modelagem
para não depender do filtro manual de nível territorial nas páginas do Power BI.
**Reproduzido em:** `notebooks/05_auditoria_medidas_dax.ipynb` (números reais, executável de ponta a ponta)
**Ancora em:** ADR 0002 (fontes públicas — CONAB só nível UF), ADR 0006 (tiers por clusterização),
ADR 0008 (tratamento Etapa 2 — zero ≠ ausente)

---

## Escopo e regra desta rodada (leia primeiro)

Esta rodada é **analítica**: auditar, reproduzir, diagnosticar, documentar e **propor**. Nada aqui
foi aplicado ao modelo. `powerbi/modelo.tmdl` e `powerbi/canavis.pbix` **não** foram tocados — a
decisão de aplicar (ou não) qualquer ajuste de DAX é do usuário, depois de ler este relatório.

**Regra de ouro:** todo bloco DAX do apêndice é **sugestão, não aplicada**. O DAX atual de cada
medida é citado verbatim de `powerbi/modelo.tmdl` só para explicá-lo e diagnosticá-lo.

Todos os números deste relatório são reproduzíveis no notebook `05_auditoria_medidas_dax.ipynb`
(célula de setup com asserts de sanidade que falham alto se a gold mudar). Onde uma premissa não é
100% verificável (p. ex. a classificação do açúcar CONAB para o fator ATR), ela é marcada
**"a confirmar"** em vez de inventar um valor.

---

## Tabela-resumo

| Medida / indicador | Veredito | Problema | Ajuste / proposta | Fundamentação |
|---|---|---|---|---|
| **Produtividade** (`SUM(q)/SUM(área)`) | CORRETA | Nenhum no cálculo. Risco só de leitura: é razão de agregados (média ponderada 77,90 t/ha), não média das produtividades (61,14 t/ha). | Manter. Rotular como "rendimento médio ponderado" no painel. | Rendimento como razão de agregados — [IBGE/PAM](https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9117-producao-agricola-municipal-culturas-temporarias-e-permanentes.html) |
| **Participação regional** | CORRETA-COM-RESSALVA | O cálculo se protege (denominador por nível, guarda ISBLANK), mas um visual que não fixa o nível mistura UF+micro+município: a soma cega dos 3 níveis em 2023 dá **101,8%** do total UF. | Manter o DAX. Eliminar a dependência do filtro manual na arquitetura (ver seção de arquitetura). | Quociente locacional / concentração regional — [IPEA](https://www.ipea.gov.br/) *(a confirmar o link metodológico específico)* |
| **Desvio vs seleção** | CORRETA-COM-RESSALVA | `ALLSELECTED` sem nível fixado deixa a referência variar com a seleção; num visual multinível a referência perde sentido. PB vs todas as UFs = **−16,96%**. | Manter o DAX. Resolver nível na arquitetura; documentar que a referência é "a seleção visível". | Desvio percentual padrão (estatística descritiva) |
| **Desvio vs grupo** | CORRETA-COM-RESSALVA | `tier` só é não-nulo nas 27 UFs; fora do nível UF a medida retorna BLANK (micro/município têm tier NA). PB (tier "média escala", 14 UFs) = **+3,41%**. | Manter o DAX. Documentar que só tem sentido no nível UF; expor isso no painel. | Tiers por clusterização — ADR 0006 |
| **Vendas etanol UF (L)** | CORRETA-COM-RESSALVA | Correta no nível UF. PB 2023 = **126.411.400 L**. Só fixa `nivel = "uf"`. | Manter. | CONAB/ANP (séries de vendas) |
| **Vendas etanol municípios validados (L)** | CORRETA-COM-RESSALVA | Filtra `nivel = "municipio"`; a validação da chave depende de `status_chave`/`territorio_id`, preenchido só para a PB conferida. Soma municipal PB 2023 = **126.411.400 L** (coincide com a UF). | Manter. Documentar que só PB está validada (fora da PB a soma municipal não é confiável). | ADR 0008 (tratamento/validação de chave) |
| **Volume/mix cana → açúcar+etanol** (indicador novo, só-UF) | PROPOSTA (não existe hoje) | As razões atuais (`Mix etanol açúcar`, `Intensidade açúcar`, `ATR ponderado`) reduzem o destino da cana a um número; falta uma visão de **composição/volume**. | Propor share em **ATR-equivalente** como medida de volume que **complementa** as razões. Ver apêndice (sugestão, não aplicada). | ATR/CONSECANA como base comum — [CONSECANA-SP](https://www.consecana.com.br/), [Piracicaba Engenharia](https://www.piracicabaengenharia.com.br/resumo-das-formulas-de-rendimentos-e-eficiencia-utilizadas-na-industria-acucareira/) |
| **Arquitetura — filtro de nível** | AJUSTE RECOMENDADO | O fato `fato_producao` empilha 3 níveis que são totais sobrepostos; somar cegamente dá **101,8%** do total verdadeiro. Hoje isso se resolve com um filtro manual em cada página. | **Opção A** (separar fatos por nível). Ver seção de arquitetura. | ADR 0002 (CONAB só UF) |

---

## 1. Produtividade

### DAX atual (verbatim de `powerbi/modelo.tmdl`)

```dax
Produtividade =
IF(
    HASONEVALUE(dim_territorio[nivel_territorial])
    && COUNTROWS(FILTER(fato_producao,
         ISBLANK(fato_producao[quantidade_produzida_t])
         || ISBLANK(fato_producao[area_colhida_ha]))) = 0,
    DIVIDE(SUM(fato_producao[quantidade_produzida_t]),
           SUM(fato_producao[area_colhida_ha]))
)
```

**Leitura termo a termo.** `HASONEVALUE(dim_territorio[nivel_territorial])` só deixa a medida
calcular quando há **um único nível** no contexto (impede misturar UF com município no mesmo número).
`COUNTROWS(FILTER(... ISBLANK ...)) = 0` é a guarda de ausência: se **qualquer** parcela de quantidade
ou área estiver em branco, a medida devolve BLANK em vez de somar um total incompleto (coerente com
ADR 0008: ausência não vira zero). `DIVIDE(SUM(q), SUM(área))` é a **razão de agregados** — soma todas
as quantidades e divide pela soma de todas as áreas.

### Reprodução (nível UF, 2023)

PB: q = 7.066.802 t, área = 109.237 ha → **64,6923844485 t/ha** (bate com `modelo-dados.md`).
Contraste de métodos sobre todas as UFs: média ponderada (razão de agregados) = **77,9009038820 t/ha**;
média simples das produtividades por UF = **61,1388677983 t/ha**. A medida usa a ponderada.

### Diagnóstico: **CORRETA**

O cálculo está certo. `SUM(q)/SUM(área)` é o rendimento médio ponderado pela área — o padrão de
produção agrícola (uma UF grande pesa mais que uma pequena, como deve ser). A diferença entre 77,90
(ponderada) e 61,14 (simples) **não** é erro: é a diferença conceitual entre "quantos t por ha a região
produz no total" e "a média dos rendimentos de cada UF". A medida escolhe a primeira, que é a correta
para benchmarking de produção.

A única ressalva é **de leitura**: apresentar o número como "rendimento médio" sem dizer que é ponderado
pode confundir quem esperaria a média simples. É rótulo, não cálculo.

### Uso no Power BI

Linha do observado na série temporal e cartão de rendimento por território. O `HASONEVALUE` já força
um território/nível por visual — não somar produtividades de territórios diferentes.

### Fundamentação

Rendimento como razão de agregados (produção total / área total) é a convenção da
[Produção Agrícola Municipal do IBGE](https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9117-producao-agricola-municipal-culturas-temporarias-e-permanentes.html).
*Conteúdo reformulado para conformidade de licenciamento.*

---

## 2. Participação regional

### DAX atual (verbatim)

```dax
Participação regional =
VAR Nivel = SELECTEDVALUE(dim_territorio[nivel_territorial])
VAR Quantidade =
    IF(COUNTROWS(FILTER(fato_producao,
         ISBLANK(fato_producao[quantidade_produzida_t]))) = 0,
       SUM(fato_producao[quantidade_produzida_t]))
VAR Total =
    CALCULATE(
        IF(COUNTROWS(FILTER(fato_producao,
             ISBLANK(fato_producao[quantidade_produzida_t]))) = 0,
           SUM(fato_producao[quantidade_produzida_t])),
        ALL(dim_territorio),
        dim_territorio[nivel_territorial] = Nivel)
RETURN
    IF(NOT ISBLANK(Nivel) && NOT ISBLANK(Quantidade),
       DIVIDE(Quantidade, Total))
```

**Leitura termo a termo.** `SELECTEDVALUE(dim_territorio[nivel_territorial])` captura o nível do
contexto (vira BLANK se houver mais de um nível). `Quantidade` é a produção do território selecionado,
com a mesma guarda de ausência. `Total` usa `ALL(dim_territorio)` para remover o filtro de território
**mas** reaplica `nivel_territorial = Nivel` — ou seja, o denominador é o total **daquele nível**, não
a soma de todos os níveis. O `RETURN` só divide se o nível for único e a quantidade existir.

### Reprodução

PB 2023 no total das UFs: total UF = 782.058.236 t → PB = **0,9036158274%**. As 27 UFs têm
`situacao_quantidade = presente`, então o denominador está completo.

### Diagnóstico: **CORRETA-COM-RESSALVA**

O cálculo está **defendido corretamente**: o `ALL(...) + nivel = Nivel` garante que a participação
compara maçãs com maçãs (UF dentro do total de UFs, município dentro do total de municípios). Quando o
contexto mistura níveis, `SELECTEDVALUE` vira BLANK e a medida se recusa a calcular. Então a **medida
em si não produz o número errado**.

A ressalva é de **modelagem/painel**: `fato_producao` empilha município (4.683 linhas), UF (567) e
microrregião (483), e os três são **totais sobrepostos do mesmo fenômeno**. Em 2023, somar os três
níveis dá 796.191.840 t = **101,8%** do total UF verdadeiro (782.058.236 t) — a PB aparece no total UF,
de novo na microrregião e de novo no município. Um visual que **não fixa o nível** (ou um ranking que
lista município ao lado de UF) engana, mesmo com a medida se protegendo. Hoje isso é contornado com o
**filtro manual de nível** em cada página — exatamente a dor que a Alex pediu para eliminar (ver seção
de arquitetura).

### Uso no Power BI

Participação de um território no seu nível. Sempre com nível fixado. Nunca em ranking multinível.

### Fundamentação

Participação regional é a lógica do **quociente locacional** da economia regional
([IPEA](https://www.ipea.gov.br/)). *O link metodológico específico do QL deve ser reconferido na
publicação final — marcado "a confirmar".* *Conteúdo reformulado para conformidade de licenciamento.*

---

## 3. Desvio vs seleção

### DAX atual (verbatim)

```dax
Desvio vs seleção =
VAR Atual = [Produtividade]
VAR Referencia = CALCULATE([Produtividade], ALLSELECTED(dim_territorio))
RETURN
    IF(NOT ISBLANK(Atual) && NOT ISBLANK(Referencia),
       DIVIDE(Atual - Referencia, Referencia))
```

**Leitura termo a termo.** `Atual` é a produtividade do território no contexto. `ALLSELECTED` calcula a
produtividade sobre **tudo o que está selecionado** no visual (a seleção do usuário, ignorando o filtro
de linha mas respeitando o filtro externo). `DIVIDE(Atual - Referencia, Referencia)` é o desvio
percentual padrão, protegido contra referência nula.

### Reprodução

PB vs todas as UFs (`ALLSELECTED` = 27 UFs): referência = **77,9009038820 t/ha** → PB = **−16,96%**
(−16,9555406617%). A PB rende ~17% abaixo da média ponderada nacional.

### Diagnóstico: **CORRETA-COM-RESSALVA**

A aritmética do desvio está correta. A ressalva é o comportamento de `ALLSELECTED` **sem nível
fixado**: a referência é "a produtividade da seleção visível", que muda conforme o usuário filtra. Isso
é uma escolha legítima (comparar com o que está na tela), mas, se o visual misturar níveis, a
referência vira uma razão de agregados sobre níveis sobrepostos e **perde sentido**. O número só é
interpretável quando a seleção é homogênea de nível (p. ex. só UFs).

### Uso no Power BI

Cartão/indicador "quanto o território desvia da seleção". Rotular explicitamente que a referência é **a
seleção visível** (não "o Brasil", não "a média fixa"). Fixar nível.

### Fundamentação

Desvio percentual simples `(atual − referência) / referência` — estatística descritiva básica, sem
fonte externa obrigatória.

---

## 4. Desvio vs grupo

### DAX atual (verbatim)

```dax
Desvio vs grupo =
VAR Tier = SELECTEDVALUE(dim_territorio[tier])
VAR Atual = [Produtividade]
VAR Referencia =
    CALCULATE([Produtividade],
        ALLSELECTED(dim_territorio),
        KEEPFILTERS(dim_territorio[tier] = Tier))
RETURN
    IF(NOT ISBLANK(Tier) && NOT ISBLANK(Atual) && NOT ISBLANK(Referencia),
       DIVIDE(Atual - Referencia, Referencia))
```

**Leitura termo a termo.** `Tier` captura o grupo de comparação do território (classificação por
clusterização — ADR 0006). `ALLSELECTED + KEEPFILTERS(tier = Tier)` calcula a produtividade sobre a
seleção **mas só das UFs do mesmo tier**. O `RETURN` exige `Tier` não-nulo: se o território não tem
tier, a medida é BLANK.

### Reprodução

PB está no tier **"média escala"** (14 UFs). Referência ponderada do grupo = **62,5608197218 t/ha** →
PB = **+3,41%** (+3,4071879750%). A PB rende ~3% acima das UFs do seu porte.

### Diagnóstico: **CORRETA-COM-RESSALVA**

Correta, e conceitualmente a mais interessante (compara a PB com pares de porte semelhante, não com o
Brasil inteiro). A ressalva estrutural: **`tier` só é não-nulo nas 27 UFs** (micro e município têm tier
NA — ADR 0006). Logo, **fora do nível UF a medida sempre retorna BLANK**. Isso é correto por
construção, mas precisa estar documentado no painel: "Desvio vs grupo" é um indicador **exclusivo da
tela de UF**. Num visual de município ele aparecerá vazio, e o usuário pode ler o vazio como erro.

### Uso no Power BI

Só na tela/contexto de UF. Rotular o grupo ("comparado com UFs de média escala"). Esconder ou
explicar o vazio fora do nível UF.

### Fundamentação

Grupos de comparação por clusterização — ADR 0006 (`docs/decisoes/0006-tiers-de-comparacao-por-clusterizacao.md`).

---

## 5. Vendas etanol (UF e municípios)

### DAX atual (verbatim)

```dax
Vendas etanol UF (L) =
IF(SELECTEDVALUE(dim_territorio[nivel_territorial]) = "uf",
   SUM(fato_vendas_etanol_uf[vendas_etanol_hidratado_l]))

Vendas etanol municípios validados (L) =
IF(SELECTEDVALUE(dim_territorio[nivel_territorial]) = "municipio",
   SUM(fato_vendas_etanol_municipio[vendas_etanol_hidratado_l]))
```

**Leitura termo a termo.** Cada medida fixa o nível (`"uf"` ou `"municipio"`) via `SELECTEDVALUE` e só
então soma as vendas de etanol hidratado (L). Fora do nível correspondente, é BLANK.

### Reprodução

PB 2023: vendas UF = **126.411.400 L**. Soma dos municípios PB validados = **126.411.400 L** —
coincidem porque os 159 municípios PB de 2023 têm `status_chave = codigo_nome_conferidos_pb` (todos
validados), então a soma municipal validada fecha com o total UF.

### Diagnóstico: **CORRETA-COM-RESSALVA**

As duas medidas estão corretas no nível para o qual foram feitas. A ressalva crítica está na versão
municipal: a **validação da chave** depende de `status_chave`/`territorio_id`, e **só a PB foi
conferida** (`territorio_id` preenchido). Globalmente: 3.581 linhas `codigo_nome_conferidos_pb`,
148.244 `nao_validada_fora_pb`, 1.269 `divergente_ou_sem_correspondencia`. A medida filtra por
`nivel = "municipio"`, mas a confiabilidade da soma municipal **só existe dentro da PB**. Fora da PB, a
soma municipal **não** deve ser lida como total confiável. Isso precisa estar explícito no painel.

### Uso no Power BI

UF: total de vendas por estado. Município: só para a PB (drill-down validado). Nunca somar municípios
fora da PB como se fossem conferidos.

### Fundamentação

Tratamento e validação de chave — ADR 0008 (`docs/decisoes/0008-tratamento-etapa2.md`). Vendas de
etanol hidratado seguem a convenção de litros das séries setoriais (CONAB/ANP).

---

## 6. Indicadores de volume e composição do mix (cana → açúcar + etanol)

Esta seção **propõe** um indicador novo (não existe no modelo hoje) que responde à correção do usuário:
comparar **visualmente as quantidades** (açúcar vs etanol vs cana) sem reduzir tudo a uma razão
unitária. Fonte: `fato_industria` (CONAB), que é **só nível UF** (ADR 0002 — CONAB não chega a
microrregião/município). No nível UF, a dor do filtro de nível **desaparece**, porque não há níveis
sobrepostos.

### 6.1 Por que não empilhar açúcar e etanol crus

Açúcar está em **mil t** e etanol em **mil L** — unidades diferentes que **não** empilham direto.
Comparar t com L seria enganoso. A solução setorial é converter ambos a uma **base comum: o ATR
(Açúcar Total Recuperável)** em kg-equivalente, usando os fatores do CONSECANA.

### 6.2 Normalização ATR correta (com fatores CONSECANA distintos)

`atr_kg_t` na gold é o **rendimento médio** (kg ATR por t de cana), **não** o ATR total nem o ATR por
produto. Para repartir açúcar vs etanol, o ATR-equivalente de **cada produto** é reconstruído a partir
dos **volumes**, com fatores distintos:

| Produto | Fator ATR | Uso |
|---|---|---|
| 1 kg açúcar branco | **1,0495 kg ATR** | adotado (açúcar CONAB genérico) |
| 1 kg açúcar VHP | 1,0453 kg ATR | alternativa sensível |
| 1 L álcool anidro (AA) | **1,7651 kg ATR** | aplicado ao `producao_etanol_anidro_mil_l` |
| 1 L álcool hidratado (AH) | **1,6913 kg ATR** | aplicado ao `producao_etanol_hidratado_mil_l` |

**Premissa "a confirmar":** o CONAB informa açúcar genérico; adotamos o fator do açúcar branco
(1,0495), com VHP (1,0453) como alternativa. A diferença é < 0,5 p.p. no share e **não muda a
conclusão** — mas a classificação exata CONAB (branco vs VHP) não é 100% verificável, então fica
marcada "a confirmar". O etanol é reconstruído com **anidro e hidratado separados** (fatores distintos),
**nunca** só pelo total. Qualquer insumo NaN → resultado NaN (nunca coagir zero).

Fontes: [CONSECANA-SP](https://www.consecana.com.br/),
[Piracicaba Engenharia — fórmulas de rendimento](https://www.piracicabaengenharia.com.br/resumo-das-formulas-de-rendimentos-e-eficiencia-utilizadas-na-industria-acucareira/),
[novaCana — ATR por estado](https://data.novacana.com/indicadores/atr-mapa).
*Conteúdo reformulado para conformidade de licenciamento.*

### 6.3 Cobertura e ausência — ANTES dos visuais (ADR 0008)

`fato_industria`: **470 linhas, 24 UFs, 22 safras** (2005/06–2026/27), só nível UF. Perfil de
ausência/zeros reproduzido na gold:

- `producao_acucar_mil_t`: **7 NaN + 71 zeros**
- `producao_etanol_total_mil_l`: **6 zeros** (0 NaN)
- `cana_mil_t`: **4 zeros** (0 NaN)
- `atr_kg_t`: **6 zeros** (0 NaN)
- **Paraíba: série completa** nas 22 safras (cana, açúcar, etanol, ATR, mix, intensidade todos presentes).

**Convenção (ADR 0008 — zero ≠ ausente, nunca inferir um do outro):**

- NaN é sempre "não reportado"; **nunca** coagido a zero.
- Zero só quando a fonte afirma zero.
- Share/mix com denominador zero ou ausente = **INDEFINIDO** (nunca 0%, nunca 50/50).
- No comparativo ATR, uma UF entra numa safra **só se** tiver os campos exigidos não-nulos; as demais
  são marcadas **"sem dado"**.

**Regra de produto por UF** (com exemplos reais):

- **Produto = 0 COM cana > 0** ⇒ **mix real**: a fatia zero é legítima (a UF não produziu aquele
  derivado). Ex.: **TO** tem açúcar = 0 em 19 safras COM cana > 0 → ~100% etanol. Isso é **informação**,
  não problema.
- **Produto NaN OU cana = 0** ⇒ **"sem informação / não processou"** ⇒ a UF-safra fica **fora** do
  visual daquela safra, marcada "sem dado", **nunca** zero plotável.

**Situações por safra (contagem de UFs, reproduzida):** p. ex. 2023/24 = 18 presente, 1 mix_real, 0
sem_dado; 2018/19 = 16 presente, 0 mix_real, 6 sem_dado (pior safra de cobertura).

### 6.4 Opção de escopo = Opção 1 (todas as UFs, "sem dado" quando faltar)

Mostrar **todas** as UFs, cada uma entrando por safra conforme a completude; "sem dado" onde faltar.
**Não** usar a Opção 2 (só UFs com série completa), que excluiria TO e as mono-produto e **enviesaria o
painel** para as acucareiras tradicionais.

**Impacto de tratar zero = ausente (quantificado):**

- **TO** apareceria vazia ou 50/50 num visual de mix, em vez de ~100% etanol (19 safras açúcar = 0
  legítimo).
- **6 UF-safra com atr = 0** (RO 2019/20, AC 2017/18, AC 2018/19, CE 2017/18, SC 2005/06, SC 2006/07)
  → INDEFINIDO, não 0%/50-50.
- **4 UF-safra com cana = 0** (RO 2019/20, AC 2017/18, AC 2018/19, CE 2017/18) → INDEFINIDO.
- **7 UF-safra com açúcar NaN** (RO 2018/19; TO 2018/19, 2019/20, 2020/21; RS 2018/19, 2019/20,
  2020/21) → entrariam como fatia zero espúria se NaN→0.

### 6.5 Ressalva visual (zero ≠ ausente no nível do gráfico)

- Num visual de UFs ao longo do tempo: nota/rótulo de que a composição **só aparece onde há dado** —
  **não ler lacuna como queda**.
- Num visual de uma safra entre UFs: a barra "sem dado" deve ser **visualmente distinta** de um zero
  real (hachura/cinza vs fatia cheia). É a distinção do ADR 0008 levada ao visual.

### 6.6 Números reais de volume/mix (share em ATR-equivalente)

- **PB 2023/24:** share açúcar (ATR) = **27,54%** (72,46% etanol). Perfil da PB mais **etanoleiro** que
  o Sudeste.
- **Contraste 2023/24:** SP 55,4%, PR 56,2%, AL 65,5% (mais acucareiros); **TO 0,0% açúcar / 100%
  etanol** (mono-produto; açúcar = 0 COM cana > 0, sem divisão por zero).
- **Ranking share açúcar ATR 2023/24** (maior→menor): AL 65,5 > PE 64,0 > AM 61,9 > PR 56,2 > PI 55,5 >
  SP 55,4 > MG 50,3 > RN 49,5 > PA 48,8 > ES 43,8 > SE 42,5 > MS 32,0 > **PB 27,5** > GO 26,0 > MT 23,0 >
  RJ 20,3 > BA 16,8 > MA 6,8 > TO 0,0.
- **PB ao longo do tempo:** 2005/06 = 33,1% → 2016/17 = 28,6% → 2026/27 = 15,8% de açúcar — tendência de
  queda do share de açúcar (série completa, sem lacuna espúria).
- **Validação de borda (assert verde no notebook):** TO 2023/24 = 0%/100% sem div/0; RO 2019/20
  (cana = 0) = INDEFINIDO/NaN; todos os shares em [0, 1]; nenhum DIVIDE estourou.

### 6.7 Por que volume complementa (não substitui) as razões existentes

As razões atuais (`Mix etanol açúcar (L por t)`, `Intensidade açúcar (t por t)`, `ATR ponderado
(kg por t)`) são úteis mas reduzem o destino da cana a **um número** — perdem a noção de **quanto** de
cada derivado saiu. O share em ATR-equivalente dá a **composição visual** (quanto da cana virou açúcar
vs etanol, em base comparável). As duas visões convivem: a razão para o "quão intensivo", o share para o
"em que proporção, e quanto". Esses indicadores são **exclusivos da tela de UF** (ADR 0002), e no nível
UF a dor do filtro de nível some.

---

## 7. Arquitetura — eliminar o filtro de nível territorial

### 7.1 Diagnóstico (quantificado)

`fato_producao` guarda os três níveis (município, microrregião, UF) na mesma tabela, e eles são
**totais sobrepostos do mesmo fenômeno**: a produção da PB aparece no total UF, de novo agregada na
microrregião e de novo nos municípios. Somar cegamente duplica.

- Soma cega dos 3 níveis em 2023 = **796.191.840 t = 101,8%** do total UF verdadeiro (782.058.236 t).
- Em 2023, a soma por microrregião da PB (7.066.802 t), por município da PB (7.066.802 t) e a PB-UF
  (7.066.802 t) **coincidem** — evidência de que cada nível repete o mesmo total.

Hoje isso é contornado com um **filtro manual de nível** em cada página. É frágil (depende de o usuário
nunca esquecer de aplicá-lo) e é exatamente o que a Alex pediu para eliminar.

### 7.2 Opções

**Opção A — separar os fatos por nível** (p. ex. `fato_producao_uf`, `fato_producao_microrregiao`,
`fato_producao_municipio`), ou uma camada semântica que exponha cada nível como um fato distinto. O
nível deixa de ser um filtro e passa a ser a **estrutura** do modelo: nunca mais há como somar níveis
sobrepostos por engano.

- *Prós:* elimina a classe de erro na origem; cada página consome o fato do seu nível; medidas ficam
  mais simples (sem guarda de nível); alinhado ao dashboard ser "PB vs UFs" (maioria das páginas em
  nível UF, inclusive a nova seção de volume/mix, que é só-UF).
- *Contras:* exige reprocessar a camada gold (Etapa 3) e reapontar as relações no `.tmdl`; mais tabelas
  para manter.

**Opção B — medidas cientes de nível** (level-aware): manter o fato único e blindar cada medida com
`HASONEVALUE`/`SELECTEDVALUE` para recusar misturas (padrão que já existe em `Produtividade` e
`Participação regional`).

- *Prós:* não mexe na gold; já é parcialmente o estado atual.
- *Contras:* é **paliativo** — a tabela continua somável por engano em qualquer visual novo que não use
  as medidas blindadas; não remove o filtro manual, só o compensa medida a medida.

### 7.3 Recomendação: **Opção A** (sugestão, não aplicada)

Para um dashboard cuja narrativa é **"PB vs UFs"** — maioria das páginas em nível UF, e a seção nova de
volume/mix sendo **só-UF** (ADR 0002) — separar os fatos por nível resolve o problema na raiz e torna o
filtro manual desnecessário. A Opção B fica como mitigação de curto prazo se a reestruturação da gold
não couber nesta etapa. **Nada disso foi aplicado** — é recomendação para o usuário decidir.

---

## Apêndice — Blocos DAX PROPOSTOS

> **SUGESTÃO, NÃO APLICADA.** Nenhum bloco abaixo foi escrito em `powerbi/modelo.tmdl` nem em
> `powerbi/canavis.pbix`. São propostas para o usuário avaliar depois de ler o relatório.
>
> **Premissas no topo (válidas para todos os blocos de volume/mix):**
> - Fatores CONSECANA: açúcar branco **1,0495** kg ATR/kg *(a confirmar — CONAB informa açúcar
>   genérico; VHP 1,0453 é a alternativa)*; anidro **1,7651** kg ATR/L; hidratado **1,6913** kg ATR/L.
> - Reconstruir etanol com **anidro e hidratado separados**, nunca só pelo total.
> - Unidades: açúcar `mil_t` → kg (× 1.000.000); etanol `mil_l` → L (× 1.000) **antes** de aplicar os
>   fatores.
> - Só nível UF (CONAB — ADR 0002).
> - `zero ≠ ausente` (ADR 0008): NaN nunca vira zero; denominador 0/nulo ⇒ resultado em branco
>   (INDEFINIDO), **nunca** 0% nem 50/50.
> - Todo `DIVIDE` abaixo protege o denominador (terceiro argumento ou guarda explícita).

### A.1 — ATR-equivalente do açúcar (medida proposta)

```dax
-- PROPOSTA (sugestão, não aplicada)
ATR equivalente açúcar (kg) =
IF(
    SELECTEDVALUE(dim_territorio[nivel_territorial]) = "uf"
    && NOT ISBLANK(SUM(fato_industria[producao_acucar_mil_t])),
    SUM(fato_industria[producao_acucar_mil_t]) * 1000000 * 1.0495  -- açúcar branco (a confirmar)
)
```

### A.2 — ATR-equivalente do etanol (anidro + hidratado separados)

```dax
-- PROPOSTA (sugestão, não aplicada)
ATR equivalente etanol (kg) =
IF(
    SELECTEDVALUE(dim_territorio[nivel_territorial]) = "uf"
    && NOT ISBLANK(SUM(fato_industria[producao_etanol_anidro_mil_l]))
    && NOT ISBLANK(SUM(fato_industria[producao_etanol_hidratado_mil_l])),
    SUM(fato_industria[producao_etanol_anidro_mil_l])     * 1000 * 1.7651   -- anidro
    + SUM(fato_industria[producao_etanol_hidratado_mil_l]) * 1000 * 1.6913  -- hidratado
)
```

> Nota: se uma UF-safra tiver anidro ou hidratado NaN, a medida fica em branco (não coage zero). Se o
> modelo preferir tolerar um dos dois ausentes, isso é uma decisão de produto a declarar — não assumida
> aqui.

### A.3 — Share de açúcar em ATR (composição, denominador protegido)

```dax
-- PROPOSTA (sugestão, não aplicada)
Share açúcar (ATR) =
VAR AtrAcucar = [ATR equivalente açúcar (kg)]
VAR AtrEtanol = [ATR equivalente etanol (kg)]
VAR AtrTotal  = AtrAcucar + AtrEtanol
RETURN
    IF(
        NOT ISBLANK(AtrAcucar) && NOT ISBLANK(AtrEtanol) && AtrTotal > 0,
        DIVIDE(AtrAcucar, AtrTotal)   -- INDEFINIDO (BLANK) se total 0/nulo; nunca 50/50
    )
```

```dax
-- PROPOSTA (sugestão, não aplicada)
Share etanol (ATR) =
VAR AtrAcucar = [ATR equivalente açúcar (kg)]
VAR AtrEtanol = [ATR equivalente etanol (kg)]
VAR AtrTotal  = AtrAcucar + AtrEtanol
RETURN
    IF(
        NOT ISBLANK(AtrAcucar) && NOT ISBLANK(AtrEtanol) && AtrTotal > 0,
        DIVIDE(AtrEtanol, AtrTotal)
    )
```

> Com TO (mono-etanol): `Share açúcar (ATR)` = 0% e `Share etanol (ATR)` = 100% — soma 100%, sem divisão
> por zero (açúcar = 0 COM cana > 0 é mix real, não ausência). Com RO 2019/20 (cana = 0, tudo zerado):
> ambos BLANK (INDEFINIDO), nunca 50/50.

### A.4 — Marcador de cobertura para a ressalva visual

```dax
-- PROPOSTA (sugestão, não aplicada)
-- Rótulo de situação para distinguir "sem dado" de zero real no visual.
Situação mix (UF/safra) =
VAR Cana    = SUM(fato_industria[cana_mil_t])
VAR Acucar  = SUM(fato_industria[producao_acucar_mil_t])
VAR Etanol  = SUM(fato_industria[producao_etanol_total_mil_l])
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(Cana) || Cana = 0, "sem dado",                 -- não processou / não reportado
        ISBLANK(Acucar) || ISBLANK(Etanol), "sem dado",        -- derivado não reportado
        (Acucar = 0 || Etanol = 0), "mix real",                -- fatia zero legítima (ex.: TO)
        "presente"
    )
```

> Uso: controlar cor/hachura no visual (barra "sem dado" distinta de zero real) e alimentar tooltip de
> ressalva ("a composição só aparece onde há dado — não leia lacuna como queda").

### A.5 — Nota sobre as razões existentes (não alterar)

As razões `Mix etanol açúcar (L por t)`, `Intensidade açúcar (t por t)` e `ATR ponderado (kg por t)`
(todas já corretas e já guardadas por `nivel = "uf"` + `ISBLANK`) **permanecem como estão**. As medidas
de share acima **complementam** (visão de volume/composição), não substituem. Nenhuma alteração
proposta nelas.

---

## Verificações finais

Registradas no FEAT-003 (notebook reexecutado headless sem erro; `pytest` verde;
`git status --short powerbi/` e `git diff --stat powerbi/` sem qualquer alteração em `modelo.tmdl` ou
`canavis.pbix`).

## Referências

- ADR 0002 — fontes públicas (CONAB só UF): `docs/decisoes/0002-fontes-publicas.md`
- ADR 0006 — tiers por clusterização: `docs/decisoes/0006-tiers-de-comparacao-por-clusterizacao.md`
- ADR 0008 — tratamento Etapa 2 (zero ≠ ausente): `docs/decisoes/0008-tratamento-etapa2.md`
- `docs/entrega-etapa2/modelo-dados.md`, `docs/entrega-etapa2/medidas-industriais.md`,
  `docs/entrega-etapa2/camada-gold.md`
- Notebook reproduzível: `notebooks/05_auditoria_medidas_dax.ipynb`
- [IBGE — PAM](https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9117-producao-agricola-municipal-culturas-temporarias-e-permanentes.html),
  [IPEA](https://www.ipea.gov.br/) *(QL — a confirmar)*,
  [CONSECANA-SP](https://www.consecana.com.br/),
  [Piracicaba Engenharia](https://www.piracicabaengenharia.com.br/resumo-das-formulas-de-rendimentos-e-eficiencia-utilizadas-na-industria-acucareira/),
  [novaCana — ATR](https://data.novacana.com/indicadores/atr-mapa),
  [CONAB — Série Histórica da Cana](https://portaldeinformacoes.conab.gov.br/downloads/arquivos/SerieHistoricaCana.txt)

*Conteúdo de fontes externas reformulado para conformidade de licenciamento.*
