from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from canavis_api.dominio.erros import DadosIndisponiveis, ProducaoNaoEncontrada


def _nao_encontrada(_: Request, erro: Exception) -> JSONResponse:
    assert isinstance(erro, ProducaoNaoEncontrada)
    detalhe = f"Sem dados para a UF «{erro.sigla}» no ano {erro.ano}."
    return JSONResponse({"detail": detalhe}, status_code=404)


def _indisponiveis(_: Request, __: Exception) -> JSONResponse:
    detalhe = "Dados indisponíveis no momento. Tente novamente mais tarde."
    return JSONResponse({"detail": detalhe}, status_code=503)


def registrar_erros(app: FastAPI) -> None:
    app.add_exception_handler(ProducaoNaoEncontrada, _nao_encontrada)
    app.add_exception_handler(DadosIndisponiveis, _indisponiveis)
