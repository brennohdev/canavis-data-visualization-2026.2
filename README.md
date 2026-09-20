# canavis — Benchmarking regional da cana-de-açúcar na Paraíba

Projeto da disciplina Visualização de Dados (PSAE00218) — UFPB, Departamento de Economia.
Produto de dados que situa a produção de cana da Paraíba frente a outras regiões do país,
usando fontes públicas, para apoiar decisões de plantio, área e relação com fornecedores.

**Grupo:** Alex Tavares Cordeiro · Brenno Henrique Alves da Silva Costa · Gustavo Henrique Rocha Oliveira

## Estrutura

```
config/            Configuração externa (fontes, caminhos, logging) em YAML
data/              Camadas de dados: raw (bronze), interim (silver), processed (gold)
  samples/         Amostras coletadas na descoberta, versionadas como evidência
docs/              Documentação e gestão de projeto
  entrega-etapa1/  Documento da Etapa 1 (.tex e .pdf)
  entrevista/      Roteiro e anotações da persona
  decisoes/        Registros de decisão de arquitetura (ADR)
notebooks/         Exploração (mapeamento de dados)
src/canavis/       Pacote Python
  domain/          Indicadores como funções puras (sem IO)
  sources/         Adaptadores de fonte atrás de interface comum
  pipeline/        Extract, transform e build entre as camadas
tests/             Testes dos indicadores
```

A arquitetura segue a regra de dependência: `domain` não conhece `sources` nem `pipeline`.
Trocar ou acrescentar uma fonte é registrar um adaptador, sem tocar no cálculo dos indicadores.
O detalhamento está em [docs/decisoes](docs/decisoes/README.md).

## Fontes de dados

| Fonte | Papel | Granularidade | Situação |
|-------|-------|---------------|----------|
| IBGE PAM (Tabela 1612) | Base — produtividade | Município a Brasil, anual | Coletada |
| CONAB Série da Cana | Base — açúcar, etanol, ATR | UF, safra | Coletada |
| ANP (vendas e produção de etanol) | Contexto | Município e UF | Coletada |
| Comex Stat | Ampliação futura | Município e UF | Fora (API atrás de Cloudflare) |

## Como rodar

O ambiente é isolado com [uv](https://docs.astral.sh/uv/).

```bash
uv sync                      # instala as dependências no .venv do projeto
uv run canavis-pipeline      # executa extract -> transform -> build
```

Estágios podem ser executados isoladamente:

```bash
uv run canavis-pipeline --stage extract
uv run canavis-pipeline --stage transform --stage build
```

Saídas por camada (em Parquet com compressão zstd, versionadas no repositório):

- `data/raw/` — dado cru, uma cópia por fonte
- `data/interim/` — dado limpo e tipado
- `data/processed/produtividade_regional.parquet` — dataset pronto, com produtividade e desvio

O formato de armazenamento é configurável em `config/settings.yaml` (`storage.format`), caso
alguma etapa precise de CSV.

## Testes

```bash
uv run --extra dev pytest
```

## Roadmap por etapa

- **Etapa 1 — Descoberta (atual).** Persona, problema, fontes documentadas e camada de dados.
- **Etapa 2 — Protótipo.** Relatório em Power BI sobre a camada `processed`.
- **Etapa 3 — Aplicação.** Dash consumindo `canavis.domain` e `canavis.pipeline`.
