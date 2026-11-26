from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


def montar_spa(app: FastAPI, static_dir: Path) -> None:
    index = static_dir / "index.html"
    if not index.is_file():
        return
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
