from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from canavis_api.repositories.producao import (
    ANO_MAX,
    ANO_MIN,
    DadosIndisponiveis,
    buscar_producao_uf,
)
from canavis_api.settings import get_settings

router = APIRouter()


@router.get("/uf/{sigla}/producao")
def producao_uf(sigla: str, ano: Annotated[int, Query()] = 2021) -> dict:
    if not ANO_MIN <= ano <= ANO_MAX:
        raise HTTPException(404, f"Ano fora do intervalo disponível ({ANO_MIN} a {ANO_MAX}).")
    try:
        producao = buscar_producao_uf(get_settings().data_dir, sigla.upper(), ano)
    except DadosIndisponiveis:
        raise HTTPException(503, "Dados indisponíveis no momento. Tente novamente mais tarde.")
    if producao is None:
        raise HTTPException(404, f"Sem dados para a UF «{sigla}» no ano {ano}.")
    return asdict(producao)
