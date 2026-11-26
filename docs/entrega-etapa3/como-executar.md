# Como executar o CanaVis (Etapa 3)

Aplicação web em contêiner único: o FastAPI serve a API (`/api/v1`) e o build estático do React.
Decisões em [ADR 0013](../decisoes/0013-stack-etapa3.md) e
[ADR 0018](../decisoes/0018-deploy-e-reprodutibilidade.md).

## Pré-requisitos

- Docker com Compose (caminho recomendado), ou
- Python 3.13 + [uv](https://docs.astral.sh/uv/) e Node 24.13.0 com pnpm 12.23.0 (`corepack enable`).

## Um comando

```bash
docker compose up --build
```

Abra <http://localhost:7860/uf/PB?ano=2021>. A tela mostra a produtividade da Paraíba em 2021
(55,7 t/ha), a quantidade produzida e um texto dinâmico, todos calculados a partir de uma
consulta DuckDB sobre `data/processed/`.

## Sem Docker

```bash
make dev   # API em :7860 (uvicorn --reload) e Vite em :5173 com proxy de /api
```

Abra <http://localhost:5173/uf/PB?ano=2021>.

## Variáveis de ambiente

Copie `.env.example` para `.env` (ignorado pelo git) se quiser alterar algo.

| Variável | Padrão | Uso |
|---|---|---|
| `CANAVIS_DATA_DIR` | `data/processed` (`/app/data/processed` na imagem) | Pasta dos parquet da gold |
| `CANAVIS_STATIC_DIR` | `apps/web/dist` (`/app/static` na imagem) | Build do React servido pela API |
| `CANAVIS_PORT` | `7860` (usa `PORT` se existir, como no Render) | Porta HTTP |
| `CANAVIS_LOG_LEVEL` | `info` | Nível de log |

## Rotas da API

| Rota | Resposta |
|---|---|
| `GET /api/v1/saude` | `200 {"status":"ok","dados":true}`; `503` se os parquet não forem encontrados |
| `GET /api/v1/uf/{sigla}/producao?ano=2021` | Produtividade, quantidade e área da UF no ano; `404` para sigla ou ano inexistente; `503` sem dados |
| `GET /docs` | OpenAPI interativo |

## Testes e lint

```bash
make test    # pytest (pipeline + API) e vitest
make lint    # ruff, tsc e eslint
make build   # build do web
```

O `ruff check` usa regras mínimas (erros e pyflakes) e ignora `notebooks/`, para não reescrever
o código legado do pipeline. O `ruff format --check` vale só para `apps/`.

## Publicação no Hugging Face Spaces

O workflow `.github/workflows/deploy-space.yml` envia o repositório ao Space, trocando o
`README.md` pelo de `deploy/hf-space/README.md` (que tem o front-matter `sdk: docker`,
`app_port: 7860`). Passos manuais, uma única vez:

1. Em <https://huggingface.co/new-space>, crie um Space com SDK **Docker** (vazio).
2. Em <https://huggingface.co/settings/tokens>, gere um token com permissão de escrita.
3. No GitHub, em Settings > Secrets and variables > Actions: segredo `HF_TOKEN` (o token) e
   variável `HF_SPACE` (`usuario/nome-do-space`).
4. Em Actions, rode o workflow **Deploy no Hugging Face Space**.
5. Aguarde o build do Space e abra `https://huggingface.co/spaces/<usuario>/<nome>`, depois a
   rota `/uf/PB?ano=2021` (ou o domínio `*.hf.space` do Space).

Spaces gratuitos dormem após inatividade (pendência P3 do ADR 0018): abra a URL uns 10 minutos
antes da demonstração.

## Plano B: Render

Web Service com ambiente Docker apontando para este repositório (usa o `Dockerfile`). O Render
define `PORT`, que a API aceita como fallback de `CANAVIS_PORT`. Como o `CMD` da imagem fixa a
porta 7860, defina `CANAVIS_PORT`/`PORT` e o comando de início no painel só se o Render não
detectar a porta aberta (7860 é detectada automaticamente na maioria dos casos).

## Roteiro de verificação em máquina limpa (PENDENTE: manual do time)

Critério da issue #28: testar em máquina sem o ambiente do desenvolvedor, só com Docker.

1. `git clone` do repositório e `cd` na pasta.
2. `docker compose up --build` (sem instalar Python nem Node).
3. `curl -fsS localhost:7860/api/v1/saude` deve devolver `{"status":"ok","dados":true}`.
4. `curl -fsS 'localhost:7860/api/v1/uf/PB/producao?ano=2021'` deve devolver `produtividade_t_ha` 55,65… e
   `quantidade_produzida_t` 5630113.0.
5. Abrir <http://localhost:7860/uf/PB?ano=2021> no navegador: KPI "55,7 t/ha" e o texto dinâmico.
6. Repetir a URL do Space em aba anônima.

## Pontos em aberto

- `openapi-typescript` (tipos do front gerados do OpenAPI) entra na Task 6; hoje os tipos de
  `apps/web/src/lib/api.ts` são escritos à mão.
- P3 (hospedagem que dorme) e P4 (zip com imagem Docker ou só Dockerfile e compose) seguem com o professor.
