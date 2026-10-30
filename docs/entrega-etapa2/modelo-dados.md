# Modelo de dados — Tasks 6 e 7

## Importação e Power Query

As quatro tabelas vêm dos Parquets de `data/processed`. O script reproduzível `powerbi/modelo.tmdl` define as consultas M, tipos, relações e medidas. Execute `python scripts/gerar_modelo_powerbi.py` para ajustar os caminhos à pasta local antes de aplicar o script na exibição TMDL do Power BI.

| Etapa | O que faz | Por que / decisão |
| --- | --- | --- |
| File.Contents | Lê o Parquet local da gold | O tratamento e os cálculos de origem permanecem no pipeline |
| Parquet.Document | Importa a tabela com os tipos publicados | Preserva nulos e zeros reais sem conversão textual |
| Verificação de tier (território) | Mantém a coluna `tier` se já existir; cria nulo caso contrário | A Task 4 fornece os grupos; não inferir pares sem validação |
| Tipagem do modelo | Códigos como texto, medidas como número, datas como DateTime | Identificadores não são grandezas aditivas |

## Relacionamentos

Cada dimensão filtra a fato em direção única, em relação 1:N:

| Dimensão (lado 1) | Fato (lado N) |
| --- | --- |
| dim_territorio[territorio_id] | fato_producao[territorio_id] |
| dim_calendario[data_referencia] | fato_producao[data_referencia] |
| dim_fonte[fonte_id] | fato_producao[fonte_id] |

O calendário é contínuo e sua data é chave. A data 31/12 na fato representa o ano de referência, não a publicação. Deve haver filtro de um único `nivel_territorial` para calcular produtividade; combinar município, microrregião e UF duplicaria totais.

O calendário foi definido com `dataCategory: Time` e `data_referencia` como `isKey` no modelo TMDL. A [captura da visão de modelo](evidencias/modelo-estrela.png) registra as três relações muitos para um e suas direções.

## Tabela 2.2 — medidas

As expressões completas estão no script TMDL, como medidas da fato.

| Nome | DAX / regra | Pergunta | Onde usar |
| --- | --- | --- | --- |
| Produtividade | `IF(HASONEVALUE(dim_territorio[nivel_territorial]), DIVIDE(SUM(fato_producao[quantidade_produzida_t]), SUM(fato_producao[area_colhida_ha])))` | Quanto se produz por hectare? | Ranking por UF e cartão |
| Participação regional | `VAR Nivel = SELECTEDVALUE(dim_territorio[nivel_territorial]) VAR Total = CALCULATE(SUM(fato_producao[quantidade_produzida_t]), ALL(dim_territorio), dim_territorio[nivel_territorial] = Nivel) RETURN IF(NOT ISBLANK(Nivel), DIVIDE(SUM(fato_producao[quantidade_produzida_t]), Total))` | Quanto o território representa no total desse nível? | Participação por UF |
| Desvio vs seleção | `VAR Referencia = CALCULATE([Produtividade], ALLSELECTED(dim_territorio)) RETURN DIVIDE([Produtividade] - Referencia, Referencia)` | Quanto difere do conjunto selecionado? | Comparação geral |
| Desvio vs grupo | `VAR Tier = SELECTEDVALUE(dim_territorio[tier]) VAR Referencia = CALCULATE([Produtividade], ALLSELECTED(dim_territorio), KEEPFILTERS(dim_territorio[tier] = Tier)) RETURN IF(NOT ISBLANK(Tier), DIVIDE([Produtividade] - Referencia, Referencia))` | Quanto difere dos pares selecionados? | Comparação por tier após Task 4 |

**Dependência pendente:** a issue #8 (Task 4) ainda precisa materializar tiers validados na gold. O desvio de grupo não deve ser apresentado como validado antes disso. O desvio da seleção é uma referência geral e não substitui a comparação por pares.

## Referência numérica para conferência

Na gold atual, Paraíba, nível UF, ano 2023: produção de 7.066.802 t e área de 109.237 ha; produtividade esperada **64,6923844485 t/ha**. A alteração do filtro de ano deve alterar o visual por UF. Zero dividido por área zero permanece vazio.

## Validação executada em 30/10/2026

- As quatro tabelas e três relações foram aplicadas e carregadas no Power BI Desktop, sem erro de DAX.
- Consulta da medida `Produtividade`, filtrada para `uf:25` e calendário em 2023, retornou **64,69 t/ha**, consistente com a gold.
- A página **Validação UF** contém gráfico de barras da medida por nome do território e filtro de página `nivel_territorial = uf`.
- Alterar o filtro `dim_calendario[ano]` entre [2022](evidencias/produtividade-uf-2022.png) e [2023](evidencias/produtividade-uf-2023.png) mudou os valores e a ordem das barras. O arquivo foi salvo em 2023.
- O indicador de referência por tier está criado, mas sua validação final depende da coluna `tier` da Task 4. Até lá, retorna vazio.
