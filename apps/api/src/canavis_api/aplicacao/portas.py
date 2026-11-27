from datetime import date
from typing import Protocol

from canavis_api.dominio.mercado import FonteMercado, PontoSerie
from canavis_api.dominio.producao import ProducaoUF
from canavis_api.dominio.territorio import Uf


class ProducaoRepositorio(Protocol):
    def disponivel(self) -> bool: ...

    def buscar_uf(self, uf: Uf, ano: int) -> ProducaoUF | None: ...


class MercadoRepositorio(Protocol):
    def disponivel(self) -> bool: ...
    def fontes(self, fonte_ids: tuple[str, ...]) -> tuple[FonteMercado, ...]: ...
    def pontos(
        self, serie_ids: tuple[str, ...], desde: date | None, ate: date | None
    ) -> list[PontoSerie]: ...
