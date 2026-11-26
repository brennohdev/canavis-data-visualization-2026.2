from typing import Protocol

from canavis_api.dominio.producao import ProducaoUF
from canavis_api.dominio.territorio import Uf


class ProducaoRepositorio(Protocol):
    def disponivel(self) -> bool: ...

    def buscar_uf(self, uf: Uf, ano: int) -> ProducaoUF | None: ...
