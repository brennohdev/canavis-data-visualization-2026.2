from __future__ import annotations

from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

import pandas as pd

from canavis.sources.intl.base import BrutoIntl, FonteIntl

_ARQUIVO = "psd_alldata.csv"


class UsdaPsdSource(FonteIntl):
    def baixar(self) -> BrutoIntl:
        conteudo = self._get(self._config["url"])
        with ZipFile(BytesIO(conteudo)) as arquivo:
            ano, mes, dia = arquivo.getinfo(_ARQUIVO).date_time[:3]
        return BrutoIntl(conteudo, self._config["url"], f"{ano:04d}-{mes:02d}-{dia:02d}", "zip")

    def normalizar(self, bruto: BrutoIntl, coletado_em: datetime) -> pd.DataFrame:
        paises = self._config["paises"]
        atributos = {int(k): v for k, v in self._config["atributos"].items()}
        blocos = []
        with ZipFile(BytesIO(bruto.conteudo)) as arquivo, arquivo.open(_ARQUIVO) as leitura:
            for bloco in pd.read_csv(
                leitura,
                usecols=[
                    "Commodity_Description",
                    "Country_Code",
                    "Market_Year",
                    "Attribute_ID",
                    "Value",
                ],
                chunksize=200000,
            ):
                filtro = (
                    (bloco["Commodity_Description"] == self._config["commodity"])
                    & bloco["Country_Code"].isin(list(paises))
                    & bloco["Attribute_ID"].isin(list(atributos))
                )
                blocos.append(bloco[filtro])
        frame = pd.concat(blocos, ignore_index=True)
        saida = pd.DataFrame(
            {
                "data": pd.to_datetime(frame["Market_Year"].astype(str) + "-01-01", errors="coerce"),
                "valor": frame["Value"],
                "serie_id": "psd_"
                + frame["Country_Code"].map(paises)
                + "_"
                + frame["Attribute_ID"].map(atributos),
                "unidade": self._config["unit"],
            }
        )
        return self._quadro(saida, coletado_em)
