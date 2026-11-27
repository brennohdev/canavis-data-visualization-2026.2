# Imagem única: o Node compila o React; o Python serve a API e o build estático.
# Porta 7860 e usuário sem privilégio (UID 1000). Publicado no Render (ADR 0018).

FROM node:24.13.0-slim AS web
RUN corepack enable
WORKDIR /app/apps/web
COPY apps/web/package.json apps/web/pnpm-lock.yaml apps/web/pnpm-workspace.yaml ./
RUN corepack prepare --activate && pnpm install --frozen-lockfile
COPY apps/web/ ./
RUN pnpm build

FROM python:3.13-slim AS final
COPY --from=ghcr.io/astral-sh/uv:0.11.3 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY apps/api ./apps/api
RUN uv sync --frozen --no-dev --no-editable --extra api

# Parquet da gold versionados no repositório. Se faltarem, o build falha cedo.
COPY data/processed ./data/processed
RUN test -f data/processed/fato_producao_uf.parquet && test -f data/processed/dim_territorio.parquet
COPY data/external ./data/external
COPY config/sources.yaml ./config/sources.yaml

COPY --from=web /app/apps/web/dist ./static

ENV PATH="/app/.venv/bin:$PATH" \
    CANAVIS_STATIC_DIR=/app/static \
    CANAVIS_DATA_DIR=/app/data/processed \
    CANAVIS_EXTERNAL_DIR=/app/data/external \
    CANAVIS_SOURCES_FILE=/app/config/sources.yaml

RUN useradd --create-home --uid 1000 app && chown -R app /app
USER app
EXPOSE 7860
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request as u; u.urlopen('http://localhost:7860/api/v1/saude', timeout=2)"
CMD ["uvicorn", "canavis_api.main:app", "--host", "0.0.0.0", "--port", "7860"]
