# canavis — Regional benchmarking of sugarcane in Paraíba

Project for the Data Visualization course (PSAE00218) — UFPB, Department of Economics.
A data product that positions Paraíba's sugarcane production against other regions of the country,
using public sources, to support decisions on planting, area, and relationships with suppliers.

**Team:** Alex Tavares Cordeiro · Brenno Henrique Alves da Silva Costa · Gustavo Henrique Rocha Oliveira

## Structure

```
config/            External configuration (sources, paths, logging) in YAML
data/              Data layers: raw (bronze), interim (silver), processed (gold)
  samples/         Samples collected during discovery, versioned as evidence
docs/              Documentation and project management
  entrega-etapa1/  Stage 1 document (.tex and .pdf)
  entrevista/      Persona interview script and notes
  decisoes/        Architecture Decision Records (ADR)
notebooks/         Exploration (data mapping)
src/canavis/       Python package
  domain/          Indicators as pure functions (no IO)
  sources/         Source adapters behind a common interface
  pipeline/        Extract, transform, and build across the layers
tests/             Indicator tests
```

The architecture follows the dependency rule: `domain` knows nothing about `sources` or `pipeline`.
Swapping or adding a source means registering an adapter, without touching the indicator computations.
Details are in [docs/decisoes](docs/decisoes/README.md).

## Data sources

| Source | Role | Granularity | Status |
|--------|------|-------------|--------|
| IBGE PAM (Table 1612) | Base — productivity | Municipality to Brazil, annual | Collected |
| CONAB Sugarcane Series | Base — sugar, ethanol, TRS | State, harvest | Collected |
| ANP (ethanol sales and production) | Context | Municipality and state | Collected |
| Comex Stat | Future expansion | Municipality and state | Out (API behind Cloudflare) |

## How to run

The environment is isolated with [uv](https://docs.astral.sh/uv/).

```bash
uv sync                      # installs dependencies into the project's .venv
uv run canavis-pipeline      # runs extract -> transform -> build
```

Stages can be run individually:

```bash
uv run canavis-pipeline --stage extract
uv run canavis-pipeline --stage transform --stage build
```

Outputs per layer (in Parquet with zstd compression, versioned in the repository):

- `data/raw/` — raw data, one copy per source
- `data/interim/` — cleaned and typed data
- `data/processed/fato_producao.parquet` — annual production fact table (quantity, harvested area, productivity)
- `data/processed/dim_territorio.parquet`, `dim_calendario.parquet`, `dim_fonte.parquet` — star-model dimensions
- `data/processed/fato_industria.parquet` — CONAB sugar, ethanol, TRS and mix by state/harvest
- `data/processed/fato_vendas_etanol_uf.parquet`, `fato_vendas_etanol_municipio.parquet` — annual ANP sales at separate grains

The storage format is configurable in `config/settings.yaml` (`storage.format`):
`parquet` (default), `csv`, or `xlsx`. The gold table grain, relationships, missing-value
rules, and Power BI guidance are in [docs/entrega-etapa2/camada-gold.md](docs/entrega-etapa2/camada-gold.md).
Industrial units, harvest alignment and ANP key validation are documented in
[docs/entrega-etapa2/medidas-industriais.md](docs/entrega-etapa2/medidas-industriais.md).
Historical productivity trend, oscillation and the exploratory regime-change test
are materialized in the production fact and documented in
[ADR 0009](docs/decisoes/0009-serie-temporal-quebra-regime.md).
The integrated Power BI model, Power Query steps, DAX measures and Desktop
validation evidence are documented in
[docs/entrega-etapa2/modelo-dados.md](docs/entrega-etapa2/modelo-dados.md).

## Tests

```bash
uv run --extra dev pytest
```

## Roadmap by stage

- **Stage 1 — Discovery (current).** Persona, problem, documented sources, and data layer.
- **Stage 2 — Prototype.** Power BI report on the `processed` layer.
- **Stage 3 — Application.** Dash consuming `canavis.domain` and `canavis.pipeline`.
