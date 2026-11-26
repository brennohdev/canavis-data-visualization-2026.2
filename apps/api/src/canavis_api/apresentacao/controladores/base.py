from abc import ABC, abstractmethod

from fastapi import APIRouter


class ControladorBase(ABC):
    def __init__(self) -> None:
        self.router = APIRouter()
        self._registrar_rotas()

    @abstractmethod
    def _registrar_rotas(self) -> None: ...
