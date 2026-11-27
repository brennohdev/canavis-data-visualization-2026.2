from __future__ import annotations

import re
from datetime import datetime
from io import BytesIO

import pandas as pd

from canavis.sources.intl.base import BrutoIntl, FonteIntl

_PADRAO_LINK = re.compile(r"https://thedocs\.worldbank\.org/[^\"'\s<>]*CMO-Historical-Data-Monthly\.xlsx")
_PERIODO = re.compile(r"^(\d{4})M(\d{2})$")
_ABA = "Monthly Prices"
_LINHA_NOMES = 4
_LINHA_UNIDADES = 5
_PRIMEIRA_LINHA_DADOS = 6


class WorldBankSource(FonteIntl):
    def baixar(self) -> BrutoIntl:
        pagina = self._get(self._config["url"]).decode("utf-8", errors="replace")
        achado = _PADRAO_LINK.search(pagina)
        if achado is None:
            raise ValueError("Link da planilha Pink Sheet não encontrado na página do Banco Mundial")
        link = achado.group(0)
        conteudo = self._get(link)
        cabecalho = pd.read_excel(BytesIO(conteudo), sheet_name=_ABA, header=None, nrows=4)
        versao = str(cabecalho.iloc[3, 0]).removeprefix("Updated on ").strip()
        return BrutoIntl(conteudo, link, versao, "xlsx")

    def normalizar(self, bruto: BrutoIntl, coletado_em: datetime) -> pd.DataFrame:
        planilha = pd.read_excel(BytesIO(bruto.conteudo), sheet_name=_ABA, header=None)
        nomes = planilha.iloc[_LINHA_NOMES].astype(str).str.strip()
        unidades = planilha.iloc[_LINHA_UNIDADES].astype(str).str.strip()
        periodos = planilha.iloc[_PRIMEIRA_LINHA_DADOS:, 0].astype(str).str.strip()
        casados = periodos.str.extract(_PERIODO)
        datas = pd.to_datetime(casados[0] + "-" + casados[1] + "-01", errors="coerce")
        partes = []
        for nome, serie_id in self._config["series_wb"].items():
            colunas = nomes[nomes == nome].index
            if len(colunas) == 0:
                raise ValueError(f"Coluna '{nome}' ausente na planilha do Banco Mundial")
            coluna = colunas[0]
            unidade = unidades[coluna].strip("()").replace("$", "USD")
            partes.append(
                pd.DataFrame(
                    {
                        "data": datas,
                        "valor": planilha.iloc[_PRIMEIRA_LINHA_DADOS:, coluna],
                        "serie_id": serie_id,
                        "unidade": unidade,
                    }
                )
            )
        return self._quadro(pd.concat(partes, ignore_index=True), coletado_em)
