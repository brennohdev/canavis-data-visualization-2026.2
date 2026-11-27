# 0016 — Ingestão internacional snapshot-first

**Status:** Aceita
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

## Implementação (Task 7)

**Fontes reais.** Seis adapters em `src/canavis/sources/intl/`, registrados em `registry.py` e
`config/sources.yaml`: `bcb_sgs`, `fred`, `worldbank`, `yahoo`, `cftc` e `usda_psd`. Todas
coletaram com sucesso na execução real de 26–27/11/2026 (evidência por fonte em
`.agents/tasks/e3-task7/evidencias-fontes.md` e no `manifest.json`). Ajustes ao que a fonte devolve:

- BCB: a série 1 do SGS é a PTAX de venda (o SGS a rotula como "câmbio livre", mas os valores
  coincidem com o serviço PTAX do BCB; conferido em 19, 23, 24, 25 e 26/11/2026). É a taxa que o
  demandante usa. O `serie_id` é `cambio_usd_brl`. A API
  limita séries diárias a 10 anos, então o adapter baixa em janelas de 9 anos.
- USDA PSD: o arquivo `psd_sugar.csv.zip` citado no ADR 0010 não existe mais; usa-se
  `psd_alldata_csv.zip` filtrado por `Sugar, Centrifugal`. China é `CH`, UE é `E4`, e o consumo
  é `Human Dom. Consumption`.
- World Bank: o link do xlsx muda de hash a cada edição e é descoberto na página por regex.
- CFTC: zips anuais desde 2015 mais a semana corrente, filtrados no código `080732`.
- Yahoo: `SB=F` não oficial (`nao_oficial=true`), moeda `USX`. User-Agent de navegador recebe 429;
  o do projeto funciona.

**FRED (risco R6).** O servidor derruba a conexão quando o User-Agent é `canavis/…` ou `Mozilla/…`
(timeout de 180 s na primeira execução). Com o User-Agent do `python-requests` responde em
menos de 1 s, e `config/sources.yaml` ganhou `headers` por fonte só para o FRED. A fonte
não foi removida. Se o bloqueio voltar, o job grava `status=falha` com o erro, mantém o snapshot
anterior, e `/mercado/acucar` troca a série mensal pelo Banco Mundial (`Sugar, world`, mesmo preço
do FMI) com observação explícita na resposta.

**Decisões.**

1. **Snapshots.** `data/external/<fonte_id>.parquet` (zstd, esquema comum), `dim_fonte_intl.parquet`
   (licença, atribuição, URL, `nao_oficial`) e `manifest.json`. Brutos em `data/raw/intl/` (ignorado
   pelo git) com `.meta.json` ao lado. `data/processed/dim_fonte.parquet` não muda.
2. **Hash reproduzível.** `sha256` do CSV canônico do quadro normalizado, com `coletado_em` lido do
   `.meta.json` do bruto. `canavis-intl reprocess` reconstrói do bruto e reproduziu o hash nas seis
   fontes. O hash muda a cada `refresh`, porque `coletado_em` muda. Para decidir se o dado mudou, o
   manifesto traz também `sha256_dados`, sem `coletado_em` e `defasagem_dias`; o `refresh` só
   regrava uma fonte quando ele muda (ADR 0018).
3. **Modo ao vivo só para BCB e Yahoo.** Com `CANAVIS_INTL_LIVE=1` (desligada por padrão), a API busca
   `bcb_sgs` (dólar diário) e `yahoo` (açúcar nº 11 diário) na própria requisição, com timeout de 4 s,
   guarda o resultado 6 h em memória e volta ao snapshot de `data/external/` se a busca falhar, estourar
   o tempo ou vier vazia. A falha fica lembrada por 5 minutos. FRED, Banco Mundial, CFTC e USDA PSD
   seguem só com snapshot. Cada fonte na resposta traz `origem` (`ao_vivo` ou `snapshot`), `dado_ate`
   (data do último dado) e o status da última coleta (`ok`, `falha`, `ausente`). O cache em memória some
   quando o Render suspende o serviço. O Yahoo é não oficial e pode bloquear IPs de nuvem; nesse caso a
   resposta continua 200 com `origem="snapshot"`. O código fica em `repositorios/mercado_ao_vivo.py` e a
   flag em `Settings.from_env`.
4. **Alinhamento à safra.** Sem coluna nova no esquema. `ano_safra(data)` em `dominio/mercado.py`
   usa abril a março, rotulado pelo ano de início (mesma convenção do ADR 0008: `2023/24 → 2023`).
   O ADR 0004 não fixa calendário de safra; esta é a convenção do projeto para o Centro-Sul.
   `agregacao=bruta|mensal|safra` vale para câmbio e açúcar, com média simples. O período inicial
   ou final da série pode ter safra incompleta. A PSD é anual por Market Year e não é reagregada.
5. **Licença e atribuição.** Saem em cada resposta no bloco `fontes`, lidas de `dim_fonte_intl.parquet`
   e do manifesto, gerados pelo job a partir de `sources.yaml`.
6. **Tamanho.** `data/external` ocupa 240 KB, com nenhum parquet acima de 115 KB. A janela de cada
   fonte é limitada em `sources.yaml` (`desde`).
7. **Degradação.** Fonte em `falha` ou `ausente` não gera erro: a série vem do snapshot anterior ou
   vazia, com o status marcado. Só a falta do `manifest.json` produz 503 em `/mercado/*`; a PAM e
   `/saude` não são afetadas.

**Endpoints novos** (`/api/v1`), todos `GET` e com `fontes`, `series` e `observacoes` na resposta:

| Rota | Parâmetros | Séries |
|---|---|---|
| `/mercado/cambio` | `desde`, `agregacao` | `cambio_usd_brl` |
| `/mercado/acucar` | `desde`, `agregacao` | `acucar_ny11_fechamento` e `acucar_isa_fred` (ou `acucar_mundo_wb` se o FRED falhar) |
| `/mercado/paises` | `desde`, `pais` (`br,in,th,cn,ue,us`) | `psd_<pais>_<atributo>` |
| `/mercado/cot` | `desde` | cinco séries `cot_acucar_*` |

**Implantação.** O Dockerfile precisa de `COPY data/external ./data/external` e
`ENV CANAVIS_EXTERNAL_DIR=/app/data/external`. Sem isso, `/mercado/*` responde 503 no Render, sem
afetar a PAM.
