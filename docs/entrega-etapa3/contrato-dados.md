# Contrato de dados da gold (Task 5, issue #29)

Este documento congela o esquema da camada gold em `data/processed/`, a regra de ausência, o último ano de cada fonte e o que o domínio calcula em vez de gravar. O catálogo de indicadores está em [`config/indicadores.yaml`](../../config/indicadores.yaml). A matriz de cobertura gerada está em [`matriz-cobertura.md`](matriz-cobertura.md). As funções puras ficam em `src/canavis/domain` (ADR 0003 e [ADR 0021](../decisoes/0021-arquitetura-em-camadas-da-api.md)); a API as consome e não as reimplementa.

## 1. Tabelas da gold

Todas em Parquet, lidas por `pyarrow`, DuckDB e Power BI.

### Fatos de produção (IBGE PAM, tabela 1612)

| Tabela | Grão (chave) | Linhas |
|---|---|---|
| `fato_producao_uf` | `territorio_id` + `ano_referencia` | 567 |
| `fato_producao_microrregiao` | `territorio_id` + `ano_referencia` | 483 |
| `fato_producao_municipio` | `territorio_id` + `ano_referencia` | 4.683 |
| `fato_producao` | empilhado dos três níveis, mantido por retrocompatibilidade com o Power BI | |

Colunas comuns: `territorio_id`, `data_referencia`, `fonte_id`, `nivel_territorial`, `ano_referencia`, `quantidade_produzida_t`, `area_colhida_ha`, `produtividade_t_ha`, `situacao_quantidade`, `situacao_area`.

Colunas temporais, só em UF e microrregião: `nivel_suavizado_t_ha`, `oscilacao_t_ha`, `f_chow`, `p_chow`, `status_chow`, `ponto_candidato_quebra`, `quebra_confirmada`.

### Indústria e vendas

| Tabela | Grão (chave) | Observação |
|---|---|---|
| `fato_industria` | `territorio_id` + `ano_alinhamento` | CONAB, UF. Colunas: `uf`, `safra`, `ano_alinhamento`, `data_referencia`, `fonte_id`, `regra_alinhamento`, `situacao_levantamento`, `cana_mil_t`, `area_plantada_mil_ha`, `producao_acucar_mil_t`, `producao_etanol_anidro_mil_l`, `producao_etanol_hidratado_mil_l`, `producao_etanol_total_mil_l`, `atr_kg_t`, `mix_etanol_acucar_l_t`, `intensidade_acucar_t_t` |
| `fato_vendas_etanol_uf` | `territorio_id` + `ano_referencia` | ANP, UF. Colunas: `uf`, `ano_referencia`, `data_referencia`, `fonte_id`, `escopo_vendas`, `vendas_etanol_hidratado_l` |
| `fato_vendas_etanol_municipio` | `codigo_municipio_origem` + `ano_referencia` | ANP, município de origem. Colunas: `uf_id`, `uf`, `ano_referencia`, `data_referencia`, `fonte_id`, `escopo_vendas`, `codigo_municipio_origem`, `nome_municipio_origem`, `territorio_id`, `status_chave`, `vendas_etanol_hidratado_l`. `territorio_id` fica vazio fora da PB |

### Dimensões e cobertura

| Tabela | Chave | Observação |
|---|---|---|
| `dim_territorio` | `territorio_id` | 273 linhas: 27 UFs, 23 microrregiões e 223 municípios da PB. Traz `tier` (só UF), nomes com e sem acento e os códigos IBGE |
| `dim_calendario` | `data_referencia` | `ano`, `mes`, `trimestre`, `dia` |
| `dim_fonte` | `fonte_id` | `fonte`, `tabela`, `periodicidade`, `unidade_quantidade`, `unidade_area`, `url` |
| `matriz_cobertura` | `fonte_id` + `territorio_id` + `ano_referencia` | Gerada por `scripts/gerar_matriz_cobertura.py`. Colunas: `fonte_id`, `territorio_id`, `nivel_territorial`, `ano_referencia`, `situacao` |

`territorio_id` tem a forma `uf:25`, `microrregiao:25001` ou `municipio:2500106`.

## 2. Último ano por fonte e alinhamento de safra

| Fonte | `fonte_id` | Último ano | Observação |
|---|---|---|---|
| IBGE PAM | `ibge_pam_1612` | 2023 | série de 2003 a 2023 |
| ANP vendas de etanol | `anp_vendas_etanol` | 2024 | UF, série de 1990 a 2024 |
| CONAB cana | `conab_cana` | 2026 (safra 2026/27) | `situacao_levantamento = PREVISAO` em todas as linhas, 19 UFs no último ano |

A safra CONAB é alinhada ao ano civil pelo `ano_inicial_safra` (`regra_alinhamento`): a safra 2023/24 vira `ano_alinhamento = 2023`. Esses números saem de `matriz-cobertura.md`.

## 3. Regra "ausente não é zero"

`situacao_quantidade` e `situacao_area` separam três casos nos fatos da PAM. A matriz de cobertura acrescenta um quarto.

| Situação | Significado | Valor na gold |
|---|---|---|
| `presente` | a fonte informou um valor positivo | número |
| `sem_producao` | a fonte registrou zero | `0.0` (zero real) |
| `suprimido` | a fonte omitiu o valor por sigilo | vazio |
| `sem_registro` | não há linha da fonte para o território e o ano | linha só existe na matriz |

Município da Paraíba em 2023 (PAM): 82 `presente`, 140 `sem_producao` e 1 `suprimido`. A soma da quantidade e da área dos 82 produtores bate com o fato UF da PB (7.066.802 t e 109.237 ha).

Toda fórmula do domínio devolve vazio (`pd.NA`) quando um insumo é ausente e preserva o zero real. Denominador zero devolve vazio, nunca 0% nem 50/50. Uma parcela ausente numa soma anula o agregado, como no DAX.

## 4. Renomeio `tendencia_t_ha` para `nivel_suavizado_t_ha`

A coluna é uma média móvel centrada de 3 anos. É um nível, não uma taxa de variação, e fica vazia em 2003 e 2023 e em lacunas. Mudou de nome em `fato_producao`, `fato_producao_uf` e `fato_producao_microrregiao`, no TMDL (`powerbi/modelo.tmdl`) e em `powerbi/validacao-integracao.dax`. A medida do Power BI também foi renomeada, de "Tendência histórica (t por ha)" para "Nível suavizado (t por ha)". O Power BI é da Etapa 2 e não é mais mantido, então visuais do `.pbix` que usavam o nome antigo não foram ajustados.

A inclinação em t/ha/ano é outra coisa e vem de `canavis.domain.tendencia.tendencia_janela`.

## 5. O que a gold não traz

Não existem colunas gravadas para estes indicadores. Eles são calculados pelo domínio, a partir dos fatos:

- desvio contra a seleção e contra o grupo de tier (`desvio_vs_selecao`, `desvio_vs_grupo`);
- participação regional e participação do município na área da PB (`participacao`);
- share de açúcar e de etanol no ATR (`share_atr_acucar`, `share_atr_etanol`);
- inclinação por janela de 5, 10 e 21 anos, erro-padrão, IC 95%, classe e inclinação sem o último ano (`tendencia_por_janelas`).

Valores de paridade, PB 2023: produtividade 64,69 t/ha; desvio contra a seleção −16,96%; desvio contra o grupo +3,41% (14 UFs no tier); participação 0,90%; share de açúcar 27,54% na safra 2023/24. Inclinações da PB: 5 anos +1,808 (IC 95% −1,29 a +4,91), 10 anos +0,490 (−0,24 a +1,22), 21 anos +0,396 (+0,13 a +0,66); sem o último ano, 5 anos +0,555 e 10 anos +0,302. A classe é `sobe` ou `cai` só quando o IC exclui zero.

## 6. Uso da matriz para recusar recomendações

Antes de gerar uma regra ou texto sobre um território, o consumidor consulta a matriz pelo `fonte_id`, `territorio_id` e `ano_referencia`:

1. `presente`: pode usar o valor.
2. `sem_producao`: o território não produziu. Pode dizer isso, mas não calcula produtividade.
3. `suprimido`: o valor existe, mas a fonte o omitiu. Recusar a recomendação e dizer que o dado está sob sigilo.
4. `sem_registro`: não há dado. Recusar a recomendação e nunca tratar como zero.

Um ano acima do `ultimo_ano` da fonte também não tem dado. A CONAB no último ano é previsão e deve ser rotulada assim.

Regerar a matriz: `.venv/bin/python scripts/gerar_matriz_cobertura.py`. O teste `tests/test_cobertura.py` falha se o Parquet ou o Markdown versionado estiver fora de dia.

## 7. Metodologia (`/metodologia`): fatores CONSECANA

| Fator | Valor | Status |
|---|---|---|
| ATR do açúcar | 1,0495 kg ATR por kg | premissa |
| ATR do etanol anidro | 1,7651 kg ATR por litro | premissa |
| ATR do etanol hidratado | 1,6913 kg ATR por litro | premissa |

Os valores vêm da auditoria das medidas DAX (`docs/entrega-etapa2/auditoria-medidas-dax.md`, seção 6.2), que cita o CONSECANA-SP e a Piracicaba Engenharia. O Manual de Instruções e as circulares do CONSECANA ficam em áreas de assinante, e o PDF do MAPA sobre rendimento de ATR não respondeu na verificação. Só sites secundários repetem os valores. Por isso os fatores continuam como premissa. A alternativa de açúcar VHP, 1,0453, muda o share em menos de 0,5 ponto percentual. Se surgir uma fonte pública primária, trocar `status` para `confirmado` em `config/indicadores.yaml` e citar a URL.

Limitações do share ATR: fatores são premissa, só vale em nível UF, o último ano da CONAB é previsão, e anidro e hidratado entram separados.

Limitações da tendência: IC e erro-padrão são nominais (OLS com erros iid), janela curta tem IC largo e o último ano pesa na inclinação. O quantil t de 95% bicaudal vem de tabela para 1 a 30 graus de liberdade e 1,96 acima, sem depender de `scipy`.
