.PHONY: dev test lint build up

# Desenvolvimento sem Docker: API em :7860 (uvicorn --reload) e Vite em :5173,
# com proxy de /api para a API. Abra http://localhost:5173/uf/PB?ano=2021.
dev:
	uv sync --extra api --extra dev
	cd apps/web && pnpm install --frozen-lockfile
	.venv/bin/uvicorn canavis_api.main:app --reload --port 7860 & trap "kill $$!" EXIT; cd apps/web && pnpm dev

test:
	.venv/bin/pytest -q
	cd apps/web && pnpm test

lint:
	.venv/bin/ruff check .
	.venv/bin/ruff format --check apps
	cd apps/web && pnpm typecheck && pnpm lint

build:
	cd apps/web && pnpm build

up:
	docker compose up --build
