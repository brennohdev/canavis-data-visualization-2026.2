# Camada gold: modelo estrela da PAM

O comando `uv run canavis-pipeline --stage build` gera em `data/processed/`:

| Tabela | Grão | Chave |
| --- | --- | --- |
| `fato_producao` | território × ano de referência × fonte | `territorio_id`, `data_referencia`, `fonte_id` |
| `dim_territorio` | território da PAM | `territorio_id` |
| `dim_calendario` | dia, contínuo entre o primeiro e o último ano da série | `data_referencia` |
| `dim_fonte` | fonte/tabela | `fonte_id` |

As relações no Power BI são 1:N, da chave de cada dimensão para a coluna homônima na fato. `dim_calendario` é contínua e pode ser marcada como tabela de datas. A data `31/12` na fato é apenas a **âncora do ano de referência** da PAM; não representa a data de publicação. O ano aparece também em `ano_referencia`.

## Regras das medidas

- `quantidade_produzida_t` está em toneladas; `area_colhida_ha`, em hectares; `produtividade_t_ha = quantidade / área`. Área zero ou ausente produz produtividade ausente.
- `situacao_quantidade` e `situacao_area` preservam a classificação da camada silver: `presente`, `sem_producao` (zero real) e `suprimido` (valor ausente). Valor suprimido permanece nulo.
- Para somar territórios, use **um nível territorial por vez** (`municipio`, `microrregiao` ou `uf`). Os níveis já representam totais sobrepostos e somá-los entre si duplicaria a produção. A função `agregar_producao` soma quantidade e área e depois divide; nunca calcula a média das produtividades. Se houver parcela suprimida, o total agregado fica ausente para não apresentar um total parcial como completo.
- Para tendência longa, prefira microrregião e janela recente de dez anos; município serve ao retrato anual e UF ao comparativo nacional, conforme [ADR 0004](../decisoes/0004-granularidade-e-janela-temporal.md).

## Hierarquia territorial

`territorio_id` inclui o nível (`municipio:2500106`, `microrregiao:25020`, `uf:25`), evitando colisão entre códigos. A dimensão contém os 223 municípios, 23 microrregiões e 27 UFs presentes na extração atual. Para os municípios da PB, os códigos de microrregião, região imediata, região intermediária e UF vêm do [serviço oficial de localidades do IBGE](https://servicodados.ibge.gov.br/api/v1/localidades/estados/25/municipios), consultado em 29/10/2026. O recorte local versionado está em `data/reference/municipios_pb_ibge.parquet` e pode ser atualizado com `python scripts/atualizar_localidades_ibge.py`.

Uma microrregião antiga pode conter municípios de **várias** regiões da divisão de 2017. Nesses casos, `mapeamento_regiao_2017 = multiplas_regioes` e o código de região imediata fica nulo; o código de região intermediária só é preenchido quando for único. Não se faz uma junção 1:1 fictícia. Por exemplo, Litoral Norte cruza João Pessoa e Mamanguape–Rio Tinto; Brejo Paraibano cruza Guarabira e Campina Grande, inclusive em intermediárias diferentes. Por isso o de-para nominal preliminar da [ADR 0008](../decisoes/0008-tratamento-etapa2.md) **não é usado** nesta camada. A microrregião continua a chave da série 2003–2023.

## Formatos e reprodução

O formato padrão é Parquet com zstd. `storage.format` em `config/settings.yaml` aceita também `csv` e `xlsx` para a escrita das tabelas; para executar `build` isoladamente em outro formato, a camada `interim` precisa existir nesse mesmo formato (ou execute `transform` antes). O recorte de referência territorial permanece Parquet para garantir uma única fonte local independente do formato de exportação.

O arquivo Parquet da PAM na camada silver foi regenerado após a classificação de ausência da Task 1. Sem isso, o build perderia os zeros reais e os valores suprimidos. Os arquivos CSV ficam ignorados pelo Git, conforme `.gitignore`; são saídas locais para importação no Power BI.
