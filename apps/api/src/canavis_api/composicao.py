from fastapi import FastAPI

from canavis_api.aplicacao.producao_uf import ConsultarProducaoUF
from canavis_api.aplicacao.saude import VerificarDados
from canavis_api.apresentacao.controladores.producao_uf import ProducaoUFControlador
from canavis_api.apresentacao.controladores.saude import SaudeControlador
from canavis_api.apresentacao.erros import registrar_erros
from canavis_api.apresentacao.spa import montar_spa
from canavis_api.repositorios.producao_duckdb import ProducaoDuckDB
from canavis_api.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    repositorio = ProducaoDuckDB(settings.data_dir)
    controladores = [
        SaudeControlador(VerificarDados(repositorio)),
        ProducaoUFControlador(ConsultarProducaoUF(repositorio)),
    ]
    app = FastAPI(title="CanaVis API", version="0.1.0")
    for controlador in controladores:
        app.include_router(controlador.router, prefix="/api/v1")
    registrar_erros(app)
    montar_spa(app, settings.static_dir)
    return app
