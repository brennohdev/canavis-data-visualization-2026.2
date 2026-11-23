# 0013 — Stack da Etapa 3: React + TypeScript, FastAPI, DuckDB, contêiner único

**Status:** Aceita (stack confirmada pelo professor)
**Evidência:** `docs/entrega-etapa3/planejamento-etapa3.md` (seções 7.1 a 7.3)
**Ancora em:** ADR 0003 (regra de dependência: `domain` não conhece a camada de apresentação)

## Contexto
A Etapa 3 pede um produto web com rotas, filtros, textos dinâmicos e engenharia reproduzível.
O enunciado exige aprovação prévia do professor para stack diferente do Dash. O pipeline,
os indicadores e a engine de regras já estão em Python.

## Decisão
- **Front:** React + TypeScript com Vite.
- **Back:** FastAPI, publicando OpenAPI; `openapi-typescript` gera os tipos do front.
- **Consulta:** DuckDB em modo somente leitura, com views sobre os Parquet da gold e
  `execute(sql, params)` parametrizado. O volume é pequeno (cerca de 1,4 MB), então a escolha
  é por SQL parametrizado e pelo extra do enunciado, não por desempenho.
- **Empacotamento:** monorepo (`apps/api`, `apps/web`, `src/canavis` existente) e um único
  contêiner (build multi-estágio), subindo com `docker compose up`.
- `domain` continua sem conhecer `apps/`; a API importa `canavis` como biblioteca.

## Alternativas rejeitadas
- Next.js + API routes (Node): obriga reescrever indicadores e engine em TS.
- Node/Express ou Hono: mesma reescrita, sem ganho sobre FastAPI.
- SPA estática + DuckDB-WASM: não captura "API própria" e exige proxy para fontes externas.
  Fica como plano B de hospedagem.

## Consequências
- Duas linguagens e cold start em hospedagem gratuita.
- O risco R2 (professor não aprovar a stack) está encerrado.
