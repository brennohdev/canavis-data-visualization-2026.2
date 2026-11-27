from __future__ import annotations

import json
from datetime import date, datetime

import pandas as pd

from canavis.sources.intl.base import BrutoIntl, FonteIntl

_JANELA_ANOS = 9


class BcbSgsSource(FonteIntl):
    def baixar(self) -> BrutoIntl:
        inicio = date.fromisoformat(self._config["desde"])
        fim = date.today()
        registros: list[dict] = []
        ano = inicio.year
        while ano <= fim.year:
            ano_fim = min(ano + _JANELA_ANOS - 1, fim.year)
            janela_ini = max(inicio, date(ano, 1, 1))
            janela_fim = min(fim, date(ano_fim, 12, 31))
            url = (
                f"{self._config['url']}?formato=json"
                f"&dataInicial={janela_ini:%d/%m/%Y}&dataFinal={janela_fim:%d/%m/%Y}"
            )
            registros.extend(json.loads(self._get(url)))
            ano = ano_fim + 1
        datas = [datetime.strptime(r["data"], "%d/%m/%Y") for r in registros]
        ultima = max(datas).strftime("%Y-%m-%d") if datas else None
        conteudo = json.dumps(registros, ensure_ascii=False).encode("utf-8")
        return BrutoIntl(conteudo, self._config["url"], ultima, "json")

    def normalizar(self, bruto: BrutoIntl, coletado_em: datetime) -> pd.DataFrame:
        registros = json.loads(bruto.conteudo)
        frame = pd.DataFrame(registros, columns=["data", "valor"])
        frame["data"] = pd.to_datetime(frame["data"], format="%d/%m/%Y", errors="coerce")
        frame["valor"] = pd.to_numeric(frame["valor"], errors="coerce")
        frame["serie_id"] = self._config["serie_id"]
        frame["unidade"] = self._config["unit"]
        return self._quadro(frame, coletado_em)
