# 0012 — Reestruturação da gold de produção em fatos por nível territorial

**Status:** Aceita
**Evidência:** `docs/entrega-etapa2/auditoria-medidas-dax.md` (seção 7),
`docs/entrega-etapa2/design-reestruturacao-gold.md`,
`src/canavis/pipeline/build.py` (`separar_por_nivel`), `tests/test_build.py`
**Ancora em:** ADR 0002 (CONAB só nível UF), ADR 0006 (tiers por clusterização),
ADR 0008 (tratamento Etapa 2 — zero ≠ ausente)

## Contexto

O fato `fato_producao` guarda os três níveis territoriais (município, microrregião
e UF) empilhados na mesma tabela. Esses níveis são **totais sobrepostos do mesmo
fenômeno**: a produção da Paraíba aparece no registro da UF, de novo na
microrregião e de novo no município. Somar cegamente duplica.

A auditoria quantificou o problema sobre a gold real (seção 7.1 de
`auditoria-medidas-dax.md`, reproduzível em
`notebooks/05_auditoria_medidas_dax.ipynb`):

- A soma cega dos três níveis em 2023 dá **796.191.840 t = 101,8%** do total UF
  verdadeiro (782.058.236 t).
- Cada nível repete o mesmo total do recorte: em 2023, a soma por microrregião da
  PB, por município da PB e a PB-UF coincidem (7.066.802 t), confirmando que a
  tabela empilhada mistura agregados que não são aditivos entre si.

Hoje isso só não produz número errado porque cada página do Power BI aplica um
**filtro manual de nível territorial**. Esse contorno é frágil: depende de o autor
do visual lembrar de fixar o nível em toda página; um visual que não fixa (ou um
ranking que lista município ao lado de UF) engana mesmo com as medidas se
protegendo por `HASONEVALUE`/guardas de nível. A leitura também fica enganosa
quando o filtro cai num recorte estreito (por exemplo, "só Mamanguape/2010"),
dando a impressão de que a série municipal é esparsa quando na verdade é o empilhamento
e o filtro que distorcem a leitura.

## Decisão

Adotar a **Opção A** do relatório de auditoria: materializar na gold três fatos
de produção separados por nível territorial e **manter** o `fato_producao`
empilhado por retrocompatibilidade.

- `separar_por_nivel(fato)` em `src/canavis/pipeline/build.py` recebe o
  `fato_producao` já enriquecido e devolve `fato_producao_uf`
  (`nivel_territorial == "uf"`), `fato_producao_microrregiao`
  (`== "microrregiao"`) e `fato_producao_municipio` (`== "municipio"`). A
  partição é exata por nível: nenhuma linha perdida nem sobreposta.
- O **município não tem colunas temporais**: as 7 colunas de série
  (`tendencia_t_ha`, `oscilacao_t_ha`, `f_chow`, `p_chow`, `status_chow`,
  `ponto_candidato_quebra`, `quebra_confirmada`) são preenchidas apenas para
  micro/UF (ADR 0009/0011) e por isso são dropadas no município. UF e
  microrregião preservam todas as colunas. Nenhuma coluna é renomeada.
- O `fato_producao` empilhado **permanece** materializado. Nada que já consome o
  empilhado quebra; a migração para os fatos por nível é incremental.
- O gerador do TMDL (`scripts/gerar_modelo_powerbi.py`) registra os três fatos
  novos na lista `FATOS`, gerando para cada um a tabela, a partição
  `Parquet.Document(Web.Contents(...))` e as três relações
  (`territorio_id → dim_territorio`, `data_referencia → dim_calendario`,
  `fonte_id → dim_fonte`). Os três fatos novos entram **sem medidas** — as
  medidas de produção continuam emitidas só para `fato_producao` — por decisão
  deliberada do design, deixando a migração das medidas para um passo posterior.
- O modelo Power BI (páginas/visuais) deve migrar para os fatos por nível,
  eliminando o filtro manual de nível em cada página.

## Consequências

- O contrato do TMDL passa a **7 fatos / 21 relações** (7 × 3), com 17 medidas
  (as 12 originais + 5 de ATR do Bloco B); as contagens são fixadas pelos testes
  do gerador em `tests/test_gerar_modelo_powerbi.py`.
- `fato_producao_municipio` não oferece as colunas temporais de série; análises de
  tendência/quebra continuam disponíveis apenas em micro/UF, como já era o caso na
  modelagem de série (ADR 0009/0011).
- Os três Parquet novos (`fato_producao_uf`, `fato_producao_microrregiao`,
  `fato_producao_municipio`) só ficam visíveis no Power BI **publicado** depois de
  chegarem ao `main`, porque o modelo lê cada fato por URL raw do `main`. Até lá o
  dashboard publicado continua servido pelo `fato_producao` empilhado. Isso é um
  requisito de ordem de merge, **não um bloqueio** da reestruturação.
- Durante o período em que o empilhado e os fatos por nível coexistem, o empilhado
  segue exigindo o filtro manual de nível para não somar agregados sobrepostos; a
  recomendação é usar os fatos por nível nos visuais novos.

### Follow-up (Etapa 3)

- Substituir o `fato_producao` empilhado pelos fatos por nível depois que as
  páginas migrarem, aposentando o contorno do filtro manual.
- Migrar as medidas de produção (Produtividade, Participação regional, Desvio vs
  seleção, Desvio vs grupo) para os fatos por nível, de modo que a medida já
  nasça amarrada ao nível correto sem depender de `HASONEVALUE` como guarda.
