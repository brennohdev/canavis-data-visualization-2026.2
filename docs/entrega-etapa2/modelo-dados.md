# Modelo de dados — Tasks 6 e 7

## Importação e Power Query

As sete tabelas vêm dos Parquets de `data/processed`. O script reproduzível `powerbi/modelo.tmdl` define as consultas M, tipos, relações e medidas. Execute `uv run python scripts/gerar_modelo_powerbi.py` para ajustar os caminhos à pasta local antes de aplicar o script na exibição TMDL do Power BI. Após aplicar, atualize **todas** as tabelas: aplicar TMDL altera os metadados, não garante a atualização dos dados importados.

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
| dim_territorio[territorio_id] | fato_industria[territorio_id] |
| dim_calendario[data_referencia] | fato_industria[data_referencia] |
| dim_fonte[fonte_id] | fato_industria[fonte_id] |
| dim_territorio[territorio_id] | fato_vendas_etanol_uf[territorio_id] |
| dim_calendario[data_referencia] | fato_vendas_etanol_uf[data_referencia] |
| dim_fonte[fonte_id] | fato_vendas_etanol_uf[fonte_id] |
| dim_territorio[territorio_id] | fato_vendas_etanol_municipio[territorio_id] |
| dim_calendario[data_referencia] | fato_vendas_etanol_municipio[data_referencia] |
| dim_fonte[fonte_id] | fato_vendas_etanol_municipio[fonte_id] |

O calendário é contínuo e sua data é chave. A data 31/12 na fato representa o ano de referência, não a publicação. Deve haver filtro de um único `nivel_territorial` para calcular produtividade; combinar município, microrregião e UF duplicaria totais.

O calendário foi definido com `dataCategory: Time` e `data_referencia` como `isKey` no modelo TMDL. A [captura inicial da visão de modelo](evidencias/modelo-estrela.png) registra as três relações originais da PAM. A ampliação passa a ter 12 relações ativas, todas muitos para um com filtro único, sem relação fato–fato.

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

### Entrega inicial

- As quatro tabelas e três relações foram aplicadas e carregadas no Power BI Desktop, sem erro de DAX.
- Consulta da medida `Produtividade`, filtrada para `uf:25` e calendário em 2023, retornou **64,69 t/ha**, consistente com a gold.
- A página **Validação UF** contém gráfico de barras da medida por nome do território e filtro de página `nivel_territorial = uf`.
- Alterar o filtro `dim_calendario[ano]` entre [2022](evidencias/produtividade-uf-2022.png) e [2023](evidencias/produtividade-uf-2023.png) mudou os valores e a ordem das barras. O arquivo foi salvo em 2023.
- O indicador de referência por tier está criado, mas sua validação final depende da coluna `tier` da Task 4. Até lá, retorna vazio.

## Ampliação — integração das issues #7 e #14

Branch `feat/powerbi-integracao-gold`, baseada na entrega temporal que inclui a
gold industrial. O PBIX inicial foi preservado; o script e as evidências da
primeira entrega foram recuperados da branch `feat/powerbi-modelo-medidas`.
Nenhuma alteração direta na `main`.

| Tabela | Grão e conteúdo | Linhas esperadas |
|---|---|---:|
| fato_producao | território × ano × nível; PAM e componentes temporais | 5.733 |
| fato_industria | UF × safra; CONAB | 470 |
| fato_vendas_etanol_uf | UF × ano; ANP, alternativa ao detalhe | 945 |
| fato_vendas_etanol_municipio | registro municipal de origem × ano; ANP | 153.094 |
| dim_territorio | identificador com prefixo de nível | 273 |
| dim_calendario | dias contínuos, 1990–2026 | 13.514 |
| dim_fonte | IBGE, CONAB, ANP | 3 |

### Regras de filtro e ausência

- Indústria e vendas UF respondem a territórios do nível `uf`. O detalhe ANP
  responde a municípios com código **e nome** conferidos na PB. `uf_id` do detalhe
  é campo de origem, não cria outra relação ativa com a mesma dimensão.
- Não relacionar fatos entre si. Não somar vendas UF com detalhe municipal:
  são duas representações das mesmas vendas. Para total UF usar a fato de UF,
  que preserva valores cuja chave municipal não foi validada.
- Linhas ANP sem `territorio_id` permanecem importadas para auditoria. Não atribuir
  esses valores à linha em branco como se fosse um município conhecido.
- Selecionar município não distribui produção industrial estadual: medidas
  industriais retornam vazio nesse nível.
- Calendário 2023 seleciona PAM/ANP do ano civil 2023 e CONAB da safra **2023/24**,
  por convenção do ano inicial. Isso não torna os períodos equivalentes. A coluna
  `safra` e a situação `PREVISAO` permanecem disponíveis; não chamar o dado CONAB
  de realizado sem verificar sua situação.
- `dim_fonte` filtra cada fato. Selecionar IBGE deve deixar indústria/ANP vazias.
- Indicadores temporais são da janela completa 2003–2023. Filtrar ano não
  reestima a análise. Tendência é média móvel centrada, com bordas/lacunas nulas;
  oscilação é observado menos tendência. `quebra_confirmada` continua nula:
  o p-valor de Chow é exploratório, não confirmação de quebra (ADR 0009).
- As colunas booleanas, inclusive marcadores nulos, são tipadas como `boolean`,
  e taxas têm `summarizeBy: none`. Usar as medidas abaixo nos visuais.

### Medidas adicionais

O DAX completo de todas as 12 medidas é versionado em `powerbi/modelo.tmdl` e
gerado em `scripts/gerar_modelo_powerbi.py`; permanecem as quatro medidas da
Tabela 2.2 e são acrescentadas oito:

| Medida | Regra | Uso |
|---|---|---|
| Tendência histórica (t por ha) | MAX da tendência, somente um território e ano | Linha anual histórica |
| Oscilação histórica (t por ha) | MAX do componente, somente um território e ano | Desvio da linha histórica |
| P Chow exploratório (2003-2023) | MAX por território único, sem somar p-valores | Tooltip com ressalva do ADR 0009 |
| Mix etanol açúcar (L por t) | Soma de etanol total / soma de açúcar | Comparação industrial UF/safra; não percentual |
| Intensidade açúcar (t por t) | Soma de açúcar / soma de cana CONAB | Rendimento industrial |
| ATR ponderado (kg por t) | Soma(ATR × cana) / soma(cana) | Evita média simples entre UFs/safras |
| Vendas etanol UF (L) | Soma de vendas da fato UF, somente nível UF | Consumo comercial por UF/ano |
| Vendas etanol municípios validados (L) | Soma do detalhe filtrado pela dimensão municipal | Apenas municípios com junção validada |

Mix, intensidade e ATR ficam vazios se alguma parcela necessária estiver
ausente; denominador zero também fica vazio. Não usar média das razões nem
média simples de ATR. As vendas até 2006 incluem consumo próprio na fonte:
preservar o campo `escopo_vendas` na interpretação (ADR 0008).

### Como reproduzir a conferência

1. Gerar a gold: `uv run canavis-pipeline --stage build`.
2. Gerar o TMDL: `uv run python scripts/gerar_modelo_powerbi.py`.
3. Abrir `powerbi/canavis.pbix`, criar um script TMDL e aplicar `powerbi/modelo.tmdl`.
4. Atualizar o modelo completo na Página Inicial, incluindo as dimensões.
5. Executar `powerbi/validacao-integracao.dax` no editor de consultas DAX.
   Conferir a coluna `Confere` contra `Esperado` (tolerância 0,000001 para taxas) e as
   contagens da tabela acima. Vazio esperado deve continuar vazio, não zero.
6. Na página Validação UF, alternar 2022 e 2023 no calendário; salvar em 2023.

O teste de tier continua dependente da Task 4. Esta ampliação do modelo não
substitui a criação das telas finais de apresentação da equipe.

### Validação final executada em 31/10/2026

O PBIX foi reaberto no Power BI Desktop e as consultas foram executadas no
modelo importado, sem reaplicar o script sobre os dados já salvos.

- **11 de 11 cenários retornaram `Confere = True`**, incluindo comparação
  numérica com tolerância de 0,000001 e distinção explícita entre nulo e zero.
  A consulta fica salva como **Consulta 2** no PBIX e no arquivo DAX do repositório.
- Produtividade PB: **56,2766042637 t/ha em 2022** e **64,6923844485 t/ha em 2023**.
- Mix PB 2023/24: **1.592,3552631579 L/t**; ATR: **124,4 kg/t**.
- ANP PB: **124.006.860 L em 2022** e **126.411.400 L em 2023**;
  Água Branca: **67.000 L em 2023**, pelo relacionamento municipal validado.
- Permaneceram vazios: mix para município, tendência na borda de 2023,
  produtividade sem nível territorial único e desvio por grupo sem tier.
  Esse último teste confirma apenas a ausência de resultado indevido, não
  valida comparação entre grupos que ainda não existem na gold.
- As sete contagens importadas coincidiram com a tabela de referência acima;
  foram carregadas **782 observações não nulas de tendência**.
- O gerenciador do Desktop confirmou as **12 relações ativas, muitos para um,
  todas com direção de filtro único**. O detalhe ANP contém chaves municipais
  nulas deliberadamente; isso não equivale a chaves desconhecidas preenchidas.
- O filtro do gráfico foi alterado de 2023 para 2022: valores e ordenação das
  barras mudaram. Depois foi restaurado para **2023** e o PBIX foi salvo.
- A issue #8 permanece aberta e a dimensão territorial local não tem `tier`.
  Portanto, a pendência de validação de pares da #11 continua explícita.
- Checagem final: **49 testes Python passaram**; o gerador TMDL executou sem
  erro e `git diff --check` não encontrou problemas de espaços.

Evidências desta rodada:

- [Valores e coluna Confere](evidencias/integracao-medidas.png), com
  [registro textual dos 11 resultados](evidencias/integracao-medidas.txt).
- [Contagens importadas](evidencias/integracao-contagens.png), com
  [registro textual](evidencias/integracao-contagens.txt).
- [Diagrama integrado](evidencias/modelo-integrado.png) e
  [lista das 12 relações com cardinalidade, direção e status](evidencias/relacoes-integradas.txt).
- [Gerenciador de relações](evidencias/relacoes-integradas.png).
- Gráfico atualizado em [2022](evidencias/integracao-uf-2022.png) e
  [2023](evidencias/integracao-uf-2023.png).

Referência da operação TMDL e necessidade de atualização posterior:
[documentação Microsoft](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-tmdl-view).
