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
