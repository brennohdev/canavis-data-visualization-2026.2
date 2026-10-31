# Medidas industriais e vendas — issue #7

## Tabelas geradas

| Tabela | Grão | Medidas / unidades |
| --- | --- | --- |
| fato_industria | UF × safra CONAB | Cana e açúcar em mil t; etanol anidro, hidratado e total em mil L; ATR em kg/t; área em mil ha |
| fato_vendas_etanol_uf | UF × ano civil ANP | Vendas de etanol hidratado em litros |
| fato_vendas_etanol_municipio | UF × código municipal de origem × ano | Vendas em litros, nome e código de origem, situação da chave municipal |

`uv run canavis-pipeline --stage transform --stage build` atualiza a silver e
materializa essas tabelas junto da estrela da PAM. O calendário compartilhado
abrange 1990–2026 no recorte atual e a dimensão fonte identifica IBGE, CONAB e ANP.
O formato segue `storage.format`, incluindo Parquet, CSV e XLSX. A fato municipal
tem menos de um milhão de linhas e cabe numa planilha XLSX.

## Cálculos e agregação

- `mix_etanol_acucar_l_t = etanol_total_mil_L / acucar_mil_t`: litros por tonelada
  de açúcar. É razão entre produtos em unidades diferentes, não percentual do
  destino da cana.
- `intensidade_acucar_t_t = acucar_mil_t / cana_mil_t`: toneladas de açúcar por
  tonelada de cana da mesma observação CONAB.
- Denominador zero ou ausente mantém razão ausente. Zero informado pela fonte
  continua zero. Não se preenche produção ausente com zero.
- Para agregar UFs/safras, recalcular as razões a partir das somas completas;
  nunca somar ou tirar média simples das razões. ATR é não aditivo: a agregação
  precisa ser ponderada pela cana, usando observações com cobertura compatível.
- As duas fatos ANP representam as mesmas vendas em grãos diferentes; usar
  uma por vez. Não somar fato municipal com total por UF.

## Alinhamento e ligação territorial

A regra de navegação é `2023/24 → 2023`, conservando safra e ano civil em fatos
separadas, conforme [ADR 0008](../decisoes/0008-tratamento-etapa2.md).
Para a indústria, usar `territorio_id`, `data_referencia` e `fonte_id` nas relações
com as dimensões. Na venda por UF, as chaves têm o mesmo padrão. Na venda
municipal, `uf_id` identifica a UF publicada; `territorio_id` só é preenchido
quando código e nome conferem com a referência municipal atual da PB.
O restante tem `status_chave` explícito e não deve ser juntado à PAM por código
bruto. Os nomes são comparados sem acentos/pontuação, sem correção automática.

O calendário mais amplo não amplia a PAM: ela continua em 2003–2023. A indústria
não é distribuída por município: sua fonte tem grão UF/safra.

## Verificação com os arquivos locais

- CONAB: **470 linhas**, únicas por UF/safra, 2005/06–2026/27.
- ANP: 160.692 linhas brutas; **7.598 repetições exatas** removidas (1990: 3.782;
  1991: 3.770; 2001: 14; 2002: 32), resultando em **153.094 observações**.
- Fato anual ANP: **945 linhas** (27 UFs × 35 anos, 1990–2024).
- Detalhe PB: 3.581 pares código/nome conferidos e 1.269 sem correspondência
  exata com a dimensão atual. Esta última contagem não é uma contagem de erros
  comprovados nem de municípios: são observações anuais preservadas para revisão.
- PB, safra 2023/24: cana **7.605,7 mil t**, açúcar **228 mil t**, etanol total
  **363.057 mil L**, ATR **124,4 kg/t**; mix **1.592,355263 L/t de açúcar**;
  intensidade **0,0299775 t/t de cana**.
- Vendas PB, 2023: **126.411.400 L**. O total antes e depois do tratamento de
  repetições coincide nesse ano.

A conversão numérica da silver foi corrigida para preservar colunas que já são
numéricas: `137.2` como float não pode virar `1372`. As colunas textuais em
formato brasileiro continuam aceitando vírgula decimal. As unidades e o rótulo
de levantamento são os da [série oficial CONAB](https://portaldeinformacoes.conab.gov.br/downloads/arquivos/SerieHistoricaCana.txt).
