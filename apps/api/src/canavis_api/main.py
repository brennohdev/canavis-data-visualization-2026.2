from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from canavis_api.routers import saude, uf
from canavis_api.settings import get_settings


def create_app() -> FastAPI:
    app = FastAPI(title="CanaVis API", version="0.1.0")
    app.include_router(saude.router, prefix="/api/v1")
    app.include_router(uf.router, prefix="/api/v1")

    static_dir = get_settings().static_dir
    index = static_dir / "index.html"
    if index.is_file():
        if (static_dir / "assets").is_dir():
            app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

        @app.get("/{caminho:path}", include_in_schema=False)
        def spa(caminho: str) -> FileResponse:
            if caminho == "api" or caminho.startswith("api/"):
                raise HTTPException(404, "Rota inexistente.")
            arquivo = (static_dir / caminho).resolve()
            if caminho and arquivo.is_file() and arquivo.is_relative_to(static_dir.resolve()):
                return FileResponse(arquivo)
            return FileResponse(index)

    return app


app = create_app()
