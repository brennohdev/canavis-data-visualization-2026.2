from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from canavis_api.dominio.erros import (
    DadosIndisponiveis,
    MercadoIndisponivel,
    ParametroMercadoInvalido,
    ProducaoNaoEncontrada,
)


def _nao_encontrada(_: Request, erro: Exception) -> JSONResponse:
    assert isinstance(erro, ProducaoNaoEncontrada)
    detalhe = f"Sem dados para a UF «{erro.sigla}» no ano {erro.ano}."
    return JSONResponse({"detail": detalhe}, status_code=404)


def _indisponiveis(_: Request, __: Exception) -> JSONResponse:
    detalhe = "Dados indisponíveis no momento. Tente novamente mais tarde."
    return JSONResponse({"detail": detalhe}, status_code=503)


def _mercado_indisponivel(_: Request, __: Exception) -> JSONResponse:
    detalhe = "Dados de mercado indisponíveis no momento. Tente novamente mais tarde."
    return JSONResponse({"detail": detalhe}, status_code=503)


def _parametro_invalido(_: Request, erro: Exception) -> JSONResponse:
    assert isinstance(erro, ParametroMercadoInvalido)
    detalhe = f"Valor inválido para «{erro.parametro}»: «{erro.valor}»."
    return JSONResponse({"detail": detalhe}, status_code=422)


def registrar_erros(app: FastAPI) -> None:
    app.add_exception_handler(ProducaoNaoEncontrada, _nao_encontrada)
    app.add_exception_handler(DadosIndisponiveis, _indisponiveis)
    app.add_exception_handler(MercadoIndisponivel, _mercado_indisponivel)
    app.add_exception_handler(ParametroMercadoInvalido, _parametro_invalido)
