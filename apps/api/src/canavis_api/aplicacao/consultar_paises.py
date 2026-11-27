from datetime import date

from canavis_api.aplicacao.consulta_mercado import consultar_mercado
from canavis_api.aplicacao.portas import MercadoRepositorio
from canavis_api.dominio.erros import ParametroMercadoInvalido
from canavis_api.dominio.mercado import PAISES, ConsultaMercado, series_de_paises


class ConsultarPaises:
    def __init__(self, repositorio: MercadoRepositorio) -> None:
        self._repositorio = repositorio

    def executar(self, pais: str | None, desde: date | None) -> ConsultaMercado:
        if pais is not None and pais not in PAISES:
            raise ParametroMercadoInvalido("pais", pais)
        return consultar_mercado(
            self._repositorio, ("usda_psd",), series_de_paises(pais), desde, "bruta"
        )
