from __future__ import annotations

from datetime import datetime
from io import BytesIO

import pandas as pd

from canavis.sources.intl.base import BrutoIntl, FonteIntl


class FredSource(FonteIntl):
    def baixar(self) -> BrutoIntl:
        conteudo = self._get(self._config["url"])
        frame = pd.read_csv(BytesIO(conteudo), dtype=str)
        versao = str(frame.iloc[-1, 0]) if len(frame) else None
        return BrutoIntl(conteudo, self._config["url"], versao, "csv")

    def normalizar(self, bruto: BrutoIntl, coletado_em: datetime) -> pd.DataFrame:
        frame = pd.read_csv(BytesIO(bruto.conteudo), dtype=str, na_values=["."])
        coluna = self._config["series_fred"]
        saida = pd.DataFrame(
            {
                "data": frame["observation_date"],
                "valor": frame[coluna],
                "serie_id": self._config["serie_id"],
                "unidade": self._config["unit"],
            }
        )
        return self._quadro(saida, coletado_em)
