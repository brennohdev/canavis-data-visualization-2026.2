from datetime import date

from canavis_api.aplicacao.consulta_mercado import consultar_mercado
from canavis_api.aplicacao.portas import MercadoRepositorio
from canavis_api.dominio.mercado import SERIES_COT, ConsultaMercado


class ConsultarCot:
    def __init__(self, repositorio: MercadoRepositorio) -> None:
        self._repositorio = repositorio

    def executar(self, desde: date | None) -> ConsultaMercado:
        return consultar_mercado(self._repositorio, ("cftc",), SERIES_COT, desde, "bruta")
