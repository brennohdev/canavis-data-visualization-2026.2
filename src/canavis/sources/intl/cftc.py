from __future__ import annotations

from datetime import date, datetime
from io import BytesIO, StringIO

import pandas as pd

from canavis.sources.intl.base import BrutoIntl, FonteIntl


class CftcSource(FonteIntl):
    def baixar(self) -> BrutoIntl:
        codigo = self._config["codigo_contrato"]
        inicio = date.fromisoformat(self._config["desde"]).year
        partes = []
        colunas: list[str] | None = None
        for ano in range(inicio, date.today().year + 1):
            url = self._config["url_historico"].format(ano=ano)
            conteudo = self._get(url)
            for bloco in pd.read_csv(
                BytesIO(conteudo), compression="zip", dtype=str, chunksize=20000
            ):
                colunas = list(bloco.columns)
                partes.append(bloco[bloco["CFTC_Contract_Market_Code"].str.strip() == codigo])
        if colunas is None:
            raise ValueError("Nenhum arquivo histórico da CFTC lido")
        semana = pd.read_csv(
            BytesIO(self._get(self._config["url_semana"])),
            header=None,
            names=colunas,
            dtype=str,
            skipinitialspace=True,
            usecols=range(len(colunas)),
        )
        partes.append(semana[semana["CFTC_Contract_Market_Code"].str.strip() == codigo])
        frame = pd.concat(partes, ignore_index=True)
        frame = frame.drop_duplicates("Report_Date_as_YYYY-MM-DD", keep="last")
        frame = frame.sort_values("Report_Date_as_YYYY-MM-DD", kind="stable")
        versao = str(frame["Report_Date_as_YYYY-MM-DD"].max()) if len(frame) else None
        saida = StringIO()
        frame.to_csv(saida, index=False)
        return BrutoIntl(saida.getvalue().encode("utf-8"), self._config["url_historico"], versao, "csv")

    def normalizar(self, bruto: BrutoIntl, coletado_em: datetime) -> pd.DataFrame:
        frame = pd.read_csv(BytesIO(bruto.conteudo), dtype=str)
        frame = frame[frame["CFTC_Contract_Market_Code"].str.strip() == self._config["codigo_contrato"]]
        partes = []
        for coluna, serie_id in self._config["series_cot"].items():
            partes.append(
                pd.DataFrame(
                    {
                        "data": frame["Report_Date_as_YYYY-MM-DD"],
                        "valor": frame[coluna].str.strip(),
                        "serie_id": serie_id,
                        "unidade": self._config["unit"],
                    }
                )
            )
        return self._quadro(pd.concat(partes, ignore_index=True), coletado_em)
