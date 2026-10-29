# 0008 — Tratamento Etapa 2: defasagem da PAM, classificação de ausência e de-para territorial

**Status:** Aceita
**Evidência:** `notebooks/03_etapa2_tratamento.ipynb`

> **Atualização de 29/10/2026 (camada gold):** o de-para nominal abaixo era
> preliminar. A consulta ao [serviço oficial de localidades do IBGE](https://servicodados.ibge.gov.br/api/v1/localidades/estados/25/municipios)
> mostrou relações múltiplas: Litoral Norte e Sapé cruzam duas regiões imediatas;
> Brejo Paraibano cruza duas imediatas e duas intermediárias. O módulo
> `domain/territorio.py` e a dimensão gold foram corrigidos para representar
> essas relações sem atribuir uma região única indevida. O recorte consultado
> está versionado em `data/reference/municipios_pb_ibge.parquet`.

## Contexto

A Etapa 2 (protótipo em Power BI) começa resolvendo as pendências de dados do
feedback da Etapa 1, antes de construir qualquer visual. Três pontos precisavam
ficar explícitos e lastreados:

1. **Defasagem e ano de referência da PAM.** Era preciso confirmar o último ano
   disponível e separar o *período de referência* (ano a que o dado se refere) da
   *data de publicação* (quando o IBGE divulga), para que nenhum visual anuncie
   como "mais recente" um ano que ainda não existe na série.
2. **Ausência de produção × supressão.** A Etapa 1 tratava toda ausência como um
   único balde descartado. O `transform.py` tinha `_MISSING_TOKENS =
   {"-","..","...","X"}` e `_to_numeric` convertia TODOS para `NA`; em seguida
   `_transform_ibge` fazia `dropna(subset=["valor"])`, colapsando "sem produção"
   (zero real) e "suprimido" (dado sonegado) no mesmo descarte. Isso corrompe
   participações e rankings, porque trata zero verdadeiro e dado faltante de forma
   idêntica.
3. **Recorte territorial.** Em 2017 o IBGE substituiu meso/microrregiões pela
   Divisão Regional do Brasil (regiões geográficas imediatas e intermediárias). A
   série da PAM vai de 2003 a 2023 e atravessa essa mudança, então era preciso
   fixar qual unidade é a chave estável de agrupamento e documentar sua relação
   com as divisões novas.

## Evidência

Diagnóstico sobre `data/raw/ibge_pam.parquet` (shape `(28665, 6)`; colunas
`extracao, cod_local, local, variavel, periodo, valor`), confirmado no notebook:

- **Último ano:** `max(periodo) == 2023` (série 2003–2023).
- **Distinção temporal:** 2023 é o **período de referência**. A PAM é publicada
  com cerca de **um ano de defasagem** — o ano-referência 2023 foi divulgado em
  2024. Logo "ano mais recente do dado" (2023) não é "ano corrente".
- **Tokens não-numéricos presentes hoje:** `-` em 15.176 células e `...` em 130.
  Não há `0` explícito, nem `..` nem `X` no dado cru atual (a regra os cobre por
  conformidade com a convenção IBGE e robustez futura).
- **Microrregiões canavieiras:** as cinco do ADR 0007 aparecem em `local` como
  `Litoral Norte - PB`, `Litoral Sul - PB`, `Sapé - PB`, `João Pessoa - PB` e
  `Brejo Paraibano - PB`.
- Aplicando a nova classificação ao nível municipal, a ausência da Etapa 1 (~62%)
  deixa de ser um bloco único: separa-se em `sem_producao` (zero real) e
  `suprimido` (dado não disponível), que exigem tratamento oposto num visual.

## Decisão

### (a) Ano de referência × data de publicação

O último ano da PAM é **2023** (confirmado programaticamente por `max(periodo)`).
Todo visual e indicador distingue **período de referência** (2023) de **data de
publicação** (ref. 2023 publicada em 2024, ~1 ano de defasagem). A defasagem é
declarada, não escondida.

### (b) Classificação explícita de ausência

Nova função `classificar_ausencia(valor)` em `src/canavis/pipeline/transform.py`,
que deriva a situação **exclusivamente do token publicado pelo IBGE** (SIDRA),
**nunca** do porte do município. Tabela completa de tokens:

| Token IBGE | Significado IBGE                                   | Rótulo (`situacao_valor`) |
|------------|----------------------------------------------------|---------------------------|
| valor numérico | dado informado                                 | `presente`                |
| `-`        | zero absoluto / o fenômeno não existe              | `sem_producao`            |
| `...`      | dado numérico não disponível (inclui sigilo)       | `suprimido`               |
| `X`        | omitido para não identificar o informante          | `suprimido`               |
| `..`       | não se aplica à célula                             | `outra_condicao`          |
| vazio / `None` / `NaN` | ausência sem token semântico           | `outra_condicao`          |

`_transform_ibge` passa a: (1) gravar `situacao_valor` a partir do valor cru,
**antes** da conversão numérica; (2) converter `valor` com `_to_numeric`; (3)
mapear `sem_producao` (token `-`) para `valor = 0.0` (zero real), mantendo
`suprimido` e `outra_condicao` como `NA`; (4) **não descartar mais linhas** — as
três situações são preservadas para que o downstream/Power BI as distinga.

**Princípio:** a ausência é classificada pelo token, nunca atribuída ao tamanho
do município. "Sem produção" e "suprimido" são fenômenos distintos e recebem
tratamento distinto no visual (zero plotável vs. "sem informação").

### (c) De-para territorial e regra de agrupamento estável

A **microrregião** permanece a **chave estável de agrupamento** ao longo de toda a
série 2003–2023, por ser a única unidade sub-UF presente em toda a série com
completude alta o bastante (ADR 0004). A DRB 2017 (regiões imediatas e
intermediárias) só existe a partir de 2017, então **não** substitui a chave; o
de-para serve para *comparar* a leitura antiga com as divisões novas sem
reprocessar a série.

De-para **preliminar da Etapa 2**, substituído pela atualização acima, das cinco
microrregiões canavieiras (ADR 0007) → regiões geográficas (IBGE DRB 2017),
ao **nível de nome**:

| Microrregião (PAM) | Região imediata | Região intermediária |
|--------------------|-----------------|----------------------|
| Litoral Norte - PB | Mamanguape      | João Pessoa          |
| Litoral Sul - PB   | João Pessoa     | João Pessoa          |
| Sapé - PB          | João Pessoa     | João Pessoa          |
| João Pessoa - PB   | João Pessoa     | João Pessoa          |
| Brejo Paraibano - PB | Guarabira     | João Pessoa          |

O de-para atualizado mora em `src/canavis/domain/territorio.py`
(`MICRORREGIOES_CANAVIEIRAS`, `regiao_de`). As listas retornam todos os códigos
oficiais encontrados; os campos singulares `cod_imediata`/`cod_intermediaria`
ficam `None` quando há mais de uma região possível. A flag
`CONFIRMACAO_FONTE_OFICIAL_PENDENTE` passou a `False` para esse recorte.

## Consequências

- `_transform_ibge` passa a devolver todas as linhas (28.665) com a coluna
  `situacao_valor`; os 15.176 `-` viram zero real e os 130 `...` ficam `NA`
  rotulados como `suprimido`. Quem consome a camada silver precisa filtrar por
  `situacao_valor` em vez de assumir que `valor` ausente significa a mesma coisa.
- Rankings e participações ganham lastro: zero real conta como zero; dado
  suprimido é exibido como "sem informação", nunca como zero (coerente com o ADR
  0004).
- O recorte territorial fica auditável: a chave de série continua microrregião, e
  a comparação com as divisões novas usa o de-para oficial atualizado, que
  preserva relações múltiplas quando não existe correspondência 1:1.
- A defasagem de ~1 ano da PAM está registrada, evitando que o protótipo prometa
  atualidade que o dado não tem.
