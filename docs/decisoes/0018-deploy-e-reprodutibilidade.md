# 0018 — Deploy e reprodutibilidade

**Status:** Proposta
**Evidência:** `docs/entrega-etapa3/planejamento-etapa3.md` (seção 7.7)

## Decisão
- Um comando: `docker compose up` (build multi-estágio: Node compila o web, Python serve API
  e estático). Alternativa sem Docker: `make dev` (uv + pnpm).
- Dependências fixadas: `uv.lock` com versões exatas no `pyproject`, `pnpm-lock.yaml` com
  versões exatas no `package.json`, imagem base com tag de versão.
- Hospedagem: Render, Web Service Docker no plano Free (revisado, ver abaixo). A escolha
  original era Hugging Face Spaces (SDK Docker), com Render como segunda opção.
- Plano B da demo: ping de aquecimento 10 minutos antes e `docker compose up` local.
- CI (GitHub Actions): `py`, `web`, `contract`, `e2e`, `secrets` (gitleaks). Deploy manual por tag.
- Malhas do IBGE baixadas uma vez, simplificadas e versionadas em `data/geo/`.

## Pendências com o professor
P3 (hospedagem que dorme) e P4 (zip com imagem Docker ou só Dockerfile e compose).

## Decisões da Task 4 (esqueleto andante, #28)

1. **Onde entram fastapi e duckdb:** no extra opcional `api` do `pyproject.toml` (com `==`), não
   em `dependencies`. O núcleo e o `canavis-pipeline` não ganham nada. `dev` ganha `ruff` e
   `httpx`. O pacote `canavis_api` fica em `apps/api/src`, entra no mesmo wheel e importa
   `canavis` (nunca o contrário), conforme o ADR 0003. Um único `uv.lock`. A imagem usa
   `uv sync --frozen --no-dev --extra api`.
2. **Parquet na imagem:** `data/processed/` (cerca de 1,4 MB, versionado) é copiado para
   `/app/data/processed`. Se faltar, o build do Docker falha. Em execução, a API sobe mesmo
   assim: `/api/v1/saude` responde 503 (`"status":"degradado"`) e a rota de produção responde 503
   com mensagem em português. Sem volume obrigatório (override opcional documentado no `compose.yaml`).
3. **README do Space:** o `README.md` da raiz (inglês, pipeline) não muda de propósito. O
   front-matter do Hugging Face ficava em `deploy/hf-space/README.md`, enviado pelo workflow
   manual `deploy-space.yml`. Ambos foram removidos na revisão abaixo.
4. **Onde documentar o app:** `docs/entrega-etapa3/como-executar.md`. O README da raiz ganhou só
   uma seção curta com link.
5. **Porta:** 7860, fixa no comando do uvicorn no `Dockerfile`. A ideia de `CANAVIS_PORT`
   configurável caiu no ADR 0021, e as variáveis `CANAVIS_PORT` e `CANAVIS_LOG_LEVEL` saíram do
   `Dockerfile` e do `.env.example` na revisão abaixo.
6. **Lint:** `ruff check` com regras mínimas (E9, F) e sem `notebooks/`; `ruff format --check`
   só em `apps/`, para não reescrever o código legado.
## Revisão: Hugging Face descartado, Render como hospedagem (26/11/2026)
**Motivo.** O primeiro deploy no Space falhou três vezes, por arquivos acima de 10 MiB, por
binários fora do armazenamento Xet e, por fim, por configuração: o Space foi criado com
ZeroGPU, que só aceita o SDK Gradio. A documentação do Hugging Face confirma que Spaces Gradio
ou Docker exigem plano PRO em contas pessoais. Contas gratuitas só podem usar ZeroGPU com
Gradio ou Spaces estáticos. O "CPU Basic grátis" da tabela de preços vale apenas para quem já
paga. A premissa da decisão original estava desatualizada.
**Alternativas.** Assinar o PRO (cerca de US$ 9 por mês), rodar o app como site estático com
DuckDB no navegador (perde a API própria e reescreve o ADR 0013) ou usar o Render no plano Free.
**Decisão.** Render, Web Service com runtime Docker e plano Free, sem mudança de código. App em
<https://canavis.onrender.com>. Configuração do serviço em `docs/entrega-etapa3/como-executar.md`.
**Consequências.**
- O serviço dorme após 15 minutos sem acesso e leva cerca de 1 minuto para acordar. A
  mitigação da demo continua: abrir o link antes e ter o `docker compose up` local.
- A instância tem 0,1 CPU e 512 MB de RAM. O consumo do app não foi medido.
- Cada deploy consome minutos de build da cota mensal. O deploy passou a ser controlado por workflow (seção seguinte).
- O deploy deixa de ser um workflow do GitHub: `deploy-space.yml` e `deploy/hf-space/` saem do
  repositório. A pendência P3 com o professor passa a valer para o Render.

## Decisões do deploy controlado (Task 7, #31)
1. **Render sem deploy automático.** O serviço fica com Auto-Deploy em Off. Quem publica é um
   workflow, por meio do Deploy Hook do Render, cuja URL é o segredo `RENDER_DEPLOY_HOOK_URL`
   do GitHub.
2. **Dois gatilhos.** (a) Job `deploy` em `ci.yml`, em push na `main`, com `needs` em
   `py`, `web`, `secrets` e `docker`. (b) Passo final de `atualizar-dados.yml`, quando houve
   commit de dados. Não há deploy duplicado: o push feito com o `GITHUB_TOKEN` não dispara o CI
   (regra do GitHub Actions), então o commit do bot só gera o deploy do próprio workflow diário.
   O grupo `concurrency: render-deploy` serializa os deploys do CI.
3. **Atualização diária.** `atualizar-dados.yml` roda `canavis-intl refresh` às 06:17 UTC
   (agendado e manual). O horário cai depois do fechamento do mercado de Nova York, o que evita
   gravar o preço intradiário do Yahoo como se fosse fechamento.
4. **Comparação de dados.** `coletado_em` e `defasagem_dias` mudam a cada coleta e entram em
   `sha256`. Por isso o manifesto ganhou `sha256_dados`, que cobre as demais colunas
   (`serie_id`, `data`, `valor`, `unidade`, `fonte_id`, `licenca`). O `refresh` só regrava o
   parquet de uma fonte se `sha256_dados` mudou (ou se a fonte estava em falha, ou sem o campo).
   Manifesto e `dim_fonte_intl.parquet` só são regravados quando alguma fonte mudou. Assim, sem
   mudança, o diretório fica byte a byte igual e `git status --porcelain data/external` vem
   vazio; o workflow então não faz commit nem deploy. Alternativas descartadas: comparar o
   parquet (contém `coletado_em`, sempre difere) e comparar `sha256` do manifesto (idem).
   Consequência: `coletado_em` de uma fonte sem mudança continua sendo o da última coleta que
   alterou o dado. Uma falha isolada de fonte também não gera commit; fica no log do workflow e
   entra no manifesto junto da próxima mudança de dados.
5. **Commit do bot em `main`.** Exceção ao fluxo de PR aceita pelo mantenedor, só para
   `data/external/`: o workflow faz `git add -- data/external` e nada mais. A `main` não tem
   proteção de branch (`gh api .../branches/main/protection` respondeu 404 "Branch not
   protected" e `/rulesets` respondeu `[]`, em 27/11/2026). Se a proteção for ativada, o push
   do bot passa a falhar e será preciso liberar o bot ou voltar ao PR. Antes do commit o
   workflow roda `pytest`; se falhar, não há commit nem deploy.
6. **Permissões mínimas.** `contents: read` no topo dos dois workflows. `contents: write` só no
   job `atualizar`. O job `deploy` do CI herda `read` e só usa o segredo.
7. **Dockerfile.** A imagem ganhou `COPY data/external ./data/external`, `COPY config/sources.yaml`
   e as variáveis `CANAVIS_EXTERNAL_DIR` e `CANAVIS_SOURCES_FILE`, esta usada pelo modo ao vivo.
8. **Procedimento manual** no Render e no GitHub: `docs/entrega-etapa3/como-executar.md`,
   seção "Deploy controlado no Render". O segredo `RENDER_DEPLOY_HOOK_URL` deve existir antes do
   primeiro merge na `main`, senão o job `deploy` do CI falha.
9. **Falha sem mudança de dado.** Uma fonte em `falha` sem mudança em nenhuma outra não é
   persistida no manifesto; fica no log do workflow. Decisão aceita para evitar commit diário sem dado novo.
