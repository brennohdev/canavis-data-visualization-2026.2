from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd

from canavis.sources.base import DataSource
from canavis.sources.intl.esquema import COLUNAS, calcular_defasagem, validar


@dataclass(frozen=True)
class BrutoIntl:
    conteudo: bytes
    url: str
    versao_fonte: str | None
    extensao: str


class FonteIntl(DataSource):
    @abstractmethod
    def baixar(self) -> BrutoIntl: ...

    @abstractmethod
    def normalizar(self, bruto: BrutoIntl, coletado_em: datetime) -> pd.DataFrame: ...

    def _get(self, url: str) -> bytes:
        return self._client.get_bytes(url, headers=self._config.get("headers"))

    def fetch(self) -> pd.DataFrame:
        coletado_em = datetime.now(timezone.utc).replace(microsecond=0)
        return self.normalizar(self.baixar(), coletado_em)

    def _quadro(self, bruto: pd.DataFrame, coletado_em: datetime) -> pd.DataFrame:
        frame = bruto[["serie_id", "data", "valor", "unidade"]].copy()
        frame["data"] = pd.to_datetime(frame["data"], errors="coerce")
        frame["valor"] = pd.to_numeric(frame["valor"], errors="coerce")
        frame = frame.dropna(subset=["serie_id", "data", "valor"])
        desde = self._config.get("desde")
        if desde:
            frame = frame[frame["data"] >= pd.Timestamp(desde)]
        frame = frame.drop_duplicates(["serie_id", "data"], keep="last")
        frame = frame.sort_values(["serie_id", "data"], kind="stable").reset_index(drop=True)
        frame["valor"] = frame["valor"].astype("float64")
        frame["fonte_id"] = self.key
        frame["coletado_em"] = pd.Timestamp(coletado_em).tz_convert("UTC")
        frame["defasagem_dias"] = calcular_defasagem(frame["data"], coletado_em)
        frame["licenca"] = self._config["license"]
        return validar(frame[COLUNAS])
