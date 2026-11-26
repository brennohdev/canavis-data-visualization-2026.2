# 0018 — Deploy e reprodutibilidade

**Status:** Proposta
**Evidência:** `docs/entrega-etapa3/planejamento-etapa3.md` (seção 7.7)

## Decisão
- Um comando: `docker compose up` (build multi-estágio: Node compila o web, Python serve API
  e estático). Alternativa sem Docker: `make dev` (uv + pnpm).
- Dependências fixadas: `uv.lock` com versões exatas no `pyproject`, `pnpm-lock.yaml` com
  versões exatas no `package.json`, imagem base com tag de versão.
- Hospedagem: Hugging Face Spaces (SDK Docker). Segunda opção: Render (free). Os limites
  devem ser conferidos antes de depender deles.
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
   front-matter do Hugging Face fica em `deploy/hf-space/README.md`; o workflow manual
   `deploy-space.yml` o coloca no lugar do README ao enviar ao Space. `HF_TOKEN` e `HF_SPACE`
   ficam nos Secrets/Variables do GitHub.
4. **Onde documentar o app:** `docs/entrega-etapa3/como-executar.md`. O README da raiz ganhou só
   uma seção curta com link.
5. **Porta:** 7860 (exigência do Space); `CANAVIS_PORT` configurável, com `PORT` como fallback.
6. **Lint:** `ruff check` com regras mínimas (E9, F) e sem `notebooks/`; `ruff format --check`
   só em `apps/`, para não reescrever o código legado.
