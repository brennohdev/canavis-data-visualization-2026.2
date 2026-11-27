from datetime import date

from canavis_api.aplicacao.consulta_mercado import consultar_mercado, validar_agregacao
from canavis_api.aplicacao.portas import MercadoRepositorio
from canavis_api.dominio.mercado import SERIES_CAMBIO, ConsultaMercado


class ConsultarCambio:
    def __init__(self, repositorio: MercadoRepositorio) -> None:
        self._repositorio = repositorio

    def executar(self, desde: date | None, agregacao: str) -> ConsultaMercado:
        validar_agregacao(agregacao)
        return consultar_mercado(self._repositorio, ("bcb_sgs",), SERIES_CAMBIO, desde, agregacao)
