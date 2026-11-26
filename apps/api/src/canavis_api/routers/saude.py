from fastapi import APIRouter
from fastapi.responses import JSONResponse

from canavis_api.repositories.producao import dados_disponiveis
from canavis_api.settings import get_settings

router = APIRouter()


@router.get("/saude")
def saude() -> JSONResponse:
    if dados_disponiveis(get_settings().data_dir):
        return JSONResponse({"status": "ok", "dados": True})
    return JSONResponse({"status": "degradado", "dados": False}, status_code=503)
