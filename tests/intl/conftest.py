from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pytest

PASTA_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "intl"
COLETADO_EM = datetime(2026, 11, 27, 12, 0, 0, tzinfo=timezone.utc)


def ler_fixture(nome: str) -> bytes:
    return (PASTA_FIXTURES / nome).read_bytes()


class ClienteFalso:
    def __init__(self, resposta: Callable[[str], bytes]) -> None:
        self._resposta = resposta
        self.urls: list[str] = []
        self.headers: list[dict | None] = []

    def get_bytes(self, url: str, headers: dict | None = None) -> bytes:
        self.urls.append(url)
        self.headers.append(headers)
        return self._resposta(url)


@pytest.fixture
def fixture_bytes():
    return ler_fixture


@pytest.fixture
def cliente_falso():
    def _criar(resposta: Callable[[str], bytes]) -> ClienteFalso:
        return ClienteFalso(resposta)

    return _criar
