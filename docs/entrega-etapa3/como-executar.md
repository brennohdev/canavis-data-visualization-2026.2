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
| `CANAVIS_EXTERNAL_DIR` | `data/external` (`/app/data/external` na imagem) | Snapshots das fontes internacionais |
| `CANAVIS_INTL_LIVE` | `0` | `1` liga o modo ao vivo de `/mercado/cambio` e `/mercado/acucar` |
| `CANAVIS_SOURCES_FILE` | `config/sources.yaml` | Configuração das fontes lida pelo modo ao vivo |

A porta é fixa em 7860, no comando do uvicorn no `Dockerfile`; a API não lê variável de porta.

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

## Publicação no Render

App publicado: <https://canavis.onrender.com/uf/PB?ano=2021>. Um único Web Service roda o contêiner
inteiro (API e front). O deploy é disparado por workflow, não pelo Render (seção "Deploy controlado no Render").

Configuração do serviço (Settings, seção Build & Deploy), para recriar do zero:

| Campo | Valor |
|---|---|
| Language | Docker |
| Branch | `main` |
| Root Directory | em branco |
| Dockerfile Path | `./Dockerfile` |
| Docker Build Context Directory | `.` (a pasta raiz; com `./Dockerfile` aqui o build falha com "not a directory") |
| Instance Type | Free |
| Health Check Path | `/api/v1/saude` |
| Variável de ambiente | `PORT=7860`, para o Render procurar a porta certa (o padrão dele é 10000) |

Limites do plano Free: o serviço dorme após 15 minutos sem acesso e leva cerca de 1 minuto para
acordar; a instância tem 0,1 CPU e 512 MB. Abra a URL alguns minutos antes da demonstração.

O Hugging Face Spaces foi descartado: Spaces com SDK Docker exigem plano PRO em contas pessoais
(ADR 0018).

## Deploy controlado no Render

O Render não publica sozinho. Quem dispara o deploy é um workflow do GitHub, por meio do Deploy
Hook do serviço. Há dois gatilhos: o job `deploy` de `.github/workflows/ci.yml` (push na `main`
com CI verde) e o último passo de `.github/workflows/atualizar-dados.yml` (só quando a
atualização diária commitou dados novos).

Passo a passo (nomes de campos conforme <https://render.com/docs/deploy-hooks> e
<https://render.com/docs/deploys>; confira o painel, que pode mudar):

1. **Criar o segredo do GitHub antes de qualquer merge na `main`.** Sem ele o job `deploy` do CI
   falha com URL vazia.
2. No Render Dashboard, abra o serviço, página *Settings*, seção *Deploy > Deploy Hook*, e copie a
   URL. Ela é secreta; se vazar, use *Regenerate hook* e atualize o segredo do GitHub.
3. No GitHub, repositório, *Settings*, *Secrets and variables > Actions*, *New repository secret*.
   Nome `RENDER_DEPLOY_HOOK_URL`, valor a URL copiada.
4. No Render, na página *Settings* do serviço, em *Auto-Deploy*, escolha *Off*. As opções são *On
   Commit* (padrão de serviço novo), *After CI Checks Pass* e *Off*. Com *Off*, só o Deploy Hook (ou
   um deploy manual) publica.
5. Teste: em *Actions*, rode "Atualizar dados internacionais" (*Run workflow*) ou faça um push na
   `main` e confira a página *Deploys* do serviço. Resposta 200 do hook indica deploy iniciado; 202
   indica que já havia um deploy em andamento.
6. Para o modo ao vivo, crie `CANAVIS_INTL_LIVE=1` nas variáveis de ambiente do serviço no Render.

Se a `main` ganhar proteção de branch, o push do bot da atualização diária passa a falhar (ver
ADR 0018).

## Modo ao vivo (BCB e Yahoo)

Com `CANAVIS_INTL_LIVE=1`, `/mercado/cambio` (BCB) e `/mercado/acucar` (Yahoo, açúcar nº 11)
buscam a janela recente na hora e mesclam com o snapshot. FRED, Banco Mundial, CFTC e USDA PSD
seguem só com snapshot.

- Cada fonte traz `origem` (`ao_vivo` ou `snapshot`) e `dado_ate`.
- Cache em memória de 6 h; timeout de 4 s de conexão e 4 s de leitura. Falha, timeout ou resposta
  vazia: a fonte volta ao snapshot, a resposta continua 200 e a falha é lembrada por 5 minutos.
- A busca ocorre dentro da requisição: a primeira após o cache vencer (ou após o Render acordar)
  paga a busca.
- O Yahoo não é oficial e pode bloquear IPs de nuvem; nesse caso a origem fica `snapshot`.
- Padrão desligado. O arquivo lido é `CANAVIS_SOURCES_FILE` (`config/sources.yaml`).
- **Limitação atual da imagem:** o `Dockerfile` não copia `config/sources.yaml` nem define
  `CANAVIS_SOURCES_FILE`. Sem o arquivo, o modo ao vivo se desliga sozinho (aviso no log) e tudo
  vem do snapshot, mesmo com `CANAVIS_INTL_LIVE=1`. Para habilitar, falta `COPY config/sources.yaml
  ./config/` e `ENV CANAVIS_SOURCES_FILE=/app/config/sources.yaml`, pendente de aprovação.

## Roteiro de verificação em máquina limpa (PENDENTE: manual do time)

Critério da issue #28: testar em máquina sem o ambiente do desenvolvedor, só com Docker.

1. `git clone` do repositório e `cd` na pasta.
2. `docker compose up --build` (sem instalar Python nem Node).
3. `curl -fsS localhost:7860/api/v1/saude` deve devolver `{"status":"ok","dados":true}`.
4. `curl -fsS 'localhost:7860/api/v1/uf/PB/producao?ano=2021'` deve devolver `produtividade_t_ha` 55,65… e
   `quantidade_produzida_t` 5630113.0.
5. Abrir <http://localhost:7860/uf/PB?ano=2021> no navegador: KPI "55,7 t/ha" e o texto dinâmico.
6. Abrir <https://canavis.onrender.com/uf/PB?ano=2021> em aba anônima e conferir a mesma tela.

## Pontos em aberto

- `openapi-typescript` (tipos do front gerados do OpenAPI) entra na Task 6; hoje os tipos de
  `apps/web/src/lib/api.ts` são escritos à mão.
- P3 (hospedagem que dorme) e P4 (zip com imagem Docker ou só Dockerfile e compose) seguem com o professor.
