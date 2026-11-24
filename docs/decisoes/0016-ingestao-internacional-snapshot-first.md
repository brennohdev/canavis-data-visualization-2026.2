# 0016 — Ingestão internacional snapshot-first

**Status:** Proposta
**Evidência:** `docs/entrega-etapa3/planejamento-etapa3.md` (seção 7.4)
**Ancora em:** ADR 0010 (fontes internacionais de preço, câmbio e balanço)

## Contexto
O professor e a persona pediram sinal de preço, câmbio e balanço por país. As fontes têm
disponibilidade e licenças desiguais, e o trabalho precisa ser reproduzível offline.

## Decisão
- Adapters em `src/canavis/sources/intl/` sobre `DataSource`: BCB SGS (PTAX), FRED
  `PSUGAISAUSDM`, World Bank Pink Sheet, Yahoo `SB=F`, CFTC COT, USDA PSD.
- Esquema comum: `serie_id, data, valor, unidade, fonte_id, coletado_em, defasagem_dias, licenca`.
- O job `canavis-intl refresh` grava `data/external/*.parquet` e `manifest.json`
  (hash, data de coleta, versão). O snapshot é versionado no git e vai na imagem.
- Atualização ao vivo é opcional (`CANAVIS_INTL_LIVE=1`), com cache e TTL de 6 h (diário)
  e 24 h (mensal e semanal). Em falha, serve o snapshot com `origem=snapshot` e selo.
- Yahoo é não oficial: fallback para FRED mensal e rótulo explícito. CEPEA fica fora do
  núcleo (licença não comercial).
- Nenhuma fonte do núcleo exige chave; varredura de segredos no CI.
- Licença e URL de cada fonte aparecem em `dim_fonte` e em `/metodologia`.
