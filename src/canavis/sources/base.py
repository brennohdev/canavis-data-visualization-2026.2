from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from canavis.sources.http_client import HttpClient


class DataSource(ABC):
    """Contrato comum de toda fonte: entregar dado cru como DataFrame."""

    key: str
    name: str

    def __init__(self, config: dict, client: HttpClient) -> None:
        self._config = config
        self._client = client
        self.key = config.get("key", self.__class__.__name__)
        self.name = config["name"]

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """Baixa o dado da origem e o devolve sem transformação de negócio."""
