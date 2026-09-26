# Validação inicial dos dados e do dicionário — Etapa 1

**Data da verificação:** 24/09/2026

**Escopo:** Tabela 5 do documento da Etapa 1, descrições das fontes e amostras versionadas no repositório. Esta validação documenta a contribuição relacionada à [issue #1](https://github.com/brennohdev/canavis-data-visualization-2026.2/issues/1); não altera os dados nem o documento da entrega.

## Método e limites

- Comparei a [Tabela 5](entrega-etapa1/Etapa1_Cordeiro_Alex.tex) e o [mapeamento de dados](mapeamento_dados.md) com os recortes definidos em [`config/sources.yaml`](../config/sources.yaml).
- Conferi os campos e contei os registros das amostras [`ibge_pam_municipios_pb_2023.csv`](../data/samples/ibge_pam_municipios_pb_2023.csv), [`ibge_pam_serie_pb.csv`](../data/samples/ibge_pam_serie_pb.csv), [`conab_serie_cana.csv`](../data/samples/conab_serie_cana.csv) e [`anp_vendas_etanol_municipios_pb.csv`](../data/samples/anp_vendas_etanol_municipios_pb.csv).
- Para testar os códigos da ANP, usei os 223 pares código–nome da amostra municipal IBGE de 2023 como referência. Comparei os nomes após remover acentos, espaços e pontuação e considerei divergência somente quando foi possível identificar o município pelo nome. Assim, o total de divergências é um **mínimo observado na amostra**, não uma auditoria definitiva do arquivo nacional da ANP.
- Não comparei linha a linha a amostra ANP com um novo download do CSV oficial. Portanto, não é possível atribuir as divergências à fonte original, à coleta ou à geração da amostra. Também não validei em boletins individuais se cada valor histórico da CONAB é final ou provisório.

## Achados

### 1. O período disponível da PAM foi apresentado como se fosse o recorte usado

A Tabela 5 informa **1974–2025** para quantidade produzida, área colhida e rendimento médio, e **1994–2025** para valor da produção em mil reais. Esses intervalos descrevem a disponibilidade da [PAM/SIDRA, tabela 1612](https://servicodados.ibge.gov.br/api/v3/agregados/1612/metadados); a referência em mil reais a partir de 1994 também está de acordo com a [nota de moedas do SIDRA](https://sidra.ibge.gov.br/pesquisa/pam/tabelas/). O painel do IBGE já apresenta resultado da [PAM referente a 2025](https://www.ibge.gov.br/indicadores).

O projeto, porém, configura as três extrações da PAM para **2003–2023** em `config/sources.yaml`. A amostra da série da PB contém esses 21 anos; as amostras de municípios da PB e UFs são retratos de **2023**. No texto que antecede a tabela, “recorte temporal anual, de 1974 a 2025” pode levar o leitor a concluir que toda essa série foi extraída e analisada.

**Ajuste recomendado:** distinguir explicitamente “período disponível na fonte: 1974–2025” de “recorte configurado/analisado no projeto: 2003–2023”, identificando as consultas pontuais de 2023. Não trocar simplesmente o período da fonte pelo período da amostra.

### 2. A condição de levantamento da CONAB não aparece no dicionário

Nos **470 registros** da amostra CONAB, o campo `dsc_situacao_levantamento` contém `PREVISAO`, inclusive nas safras antigas. A amostra cobre **22 safras da PB**, de 2005/06 a 2026/27. O [arquivo público da Série Histórica da Cana](https://portaldeinformacoes.conab.gov.br/downloads/arquivos/SerieHistoricaCana.txt) também contém esse campo. A Tabela 5 lista produção de açúcar, etanol e ATR sem informar a natureza de levantamento/estimativa dos dados.

O valor `PREVISAO` **não prova, sozinho**, que todas as safras passadas ainda sejam previsões preliminares ou que não tenham sido atualizadas. A CONAB publica levantamentos sucessivos, inclusive um [4º levantamento da safra 2023/24](https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/safras/safra-de-cana-de-acucar/arquivos-boletins/4o-levantamento-safra-2023-24). A classificação de cada safra como final ou provisória exigiria cotejo com os boletins e a metodologia da fonte.

**Ajuste recomendado:** acrescentar nota de que os números da série são *levantamentos/estimativas da CONAB* e de que o arquivo consultado marca seus registros como `PREVISAO`; não apresentá-los indistintamente como produção definitiva.

### 3. O código IBGE não produz uma junção confiável em toda a amostra ANP

O [metadado da ANP](https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/vdpb/vaehdpm/etanol-hidratado/metadados-vendas-anuais-de-etanol-hidratado-por-municipio.pdf) define `CÓDIGO IBGE` como identificador do município. Portanto, ele **pode** servir de chave municipal. A ressalva é que, na amostra da PB versionada no repositório, há **445 linhas de 2003–2023** cujo código não corresponde ao município indicado pelo nome: **150 em 2015, 148 em 2016 e 147 em 2017**. Por exemplo, `AMPARO` aparece em 2015 com `2500700`, enquanto o par código–nome da amostra IBGE atribui a Amparo `2500734`. Em 2023, não houve divergência desse tipo entre os 159 registros ANP da amostra.

Uma verificação apenas de existência do código não basta: em muitos casos, o código divergente pertence a **outro município válido**. Além disso, uma junção entre séries anuais deve considerar **município e ano**, não só o município. O [mapeamento de dados](mapeamento_dados.md) afirma que o código permite juntar com a PAM “sem ambiguidade de nome”, e a [decisão 0002](decisoes/0002-fontes-publicas.md) fala em “junção limpa”; essas afirmações estão fortes demais diante da amostra.

**Ajuste recomendado:** validar pares nome–código por ano antes da junção, verificar duplicidades e documentar qualquer correção de chave. Até comparar a amostra com o CSV original da ANP, registrar o achado como **problema observado na amostra**, sem atribuir sua causa à agência.

### 4. “348 municípios” não é uma contagem municipal válida

O texto anterior à Tabela 5 e o [mapeamento de dados](mapeamento_dados.md) descrevem **5.079 registros da PB, 348 municípios** na amostra ANP. A recontagem confirma **5.079 linhas**, mas **348 é o número de textos distintos no campo `MUNICÍPIO`**; há **331 códigos distintos** na mesma amostra. Não se pode interpretar nomes ou códigos distintos nessa série histórica como quantidade de municípios da PB. A amostra IBGE de 2023 contém **223 municípios**.

**Ajuste recomendado:** retirar “348 municípios” ou substituí-lo por uma descrição literal, como “5.079 registros e 348 grafias/nomes distintos no campo `MUNICÍPIO`, antes da padronização e validação”. Para informar cobertura municipal, calcular municípios válidos no ano e no recorte escolhidos.

## Verificação adicional da série ANP

A amostra ANP contém **229 linhas exatamente duplicadas**, todas entre **1990 e 2002**. Elas não caem no recorte PAM configurado para 2003–2023, mas podem inflar totais caso alguém some a série ANP completa sem deduplicar e conferir a origem das repetições. Esse achado também é restrito à amostra local até haver comparação com o arquivo oficial.

## Ponto descartado

O separador CSV da ANP **não é um problema da extração**: o [arquivo oficial de vendas](https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/vdpb/vaehdpm/etanol-hidratado/vendas-anuais-de-etanol-hidratado-por-municipio.csv) usa `;`, valor definido em `config/sources.yaml` e utilizado pelo leitor em [`src/canavis/sources/delimited.py`](../src/canavis/sources/delimited.py). A amostra local foi salva com `,`; ela deve ser lida com o separador correspondente, mas isso não indica falha na coleta configurada.

## Próximas verificações antes de corrigir os dados

1. Confrontar as linhas divergentes de 2015–2017 e as duplicadas de 1990–2002 com um download novo do CSV oficial da ANP; localizar em qual etapa surgiram.
2. Definir e registrar uma regra de validação de `UF + município + código IBGE + ano` antes de qualquer junção ANP–PAM.
3. Conferir, nos boletins da CONAB, o tratamento das estimativas de safras encerradas antes de rotular cada observação como final ou provisória.
4. Atualizar a Tabela 5 e os trechos correlatos do documento e do mapeamento conforme os achados documentais confirmados acima.
