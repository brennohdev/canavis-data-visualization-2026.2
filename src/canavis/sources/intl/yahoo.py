from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pandas as pd

from canavis.sources.intl.base import BrutoIntl, FonteIntl


class YahooSource(FonteIntl):
    def baixar(self) -> BrutoIntl:
        conteudo = self._get(self._config["url"])
        resultado = json.loads(conteudo)["chart"]["result"][0]
        marcos = resultado.get("timestamp") or []
        versao = None
        if marcos:
            versao = datetime.fromtimestamp(max(marcos), timezone.utc).strftime("%Y-%m-%d")
        return BrutoIntl(conteudo, self._config["url"], versao, "json")

    def normalizar(self, bruto: BrutoIntl, coletado_em: datetime) -> pd.DataFrame:
        resultado = json.loads(bruto.conteudo)["chart"]["result"][0]
        deslocamento = timedelta(seconds=resultado["meta"].get("gmtoffset", 0))
        marcos = resultado.get("timestamp") or []
        fechamentos = resultado["indicators"]["quote"][0]["close"]
        datas = [
            (datetime.fromtimestamp(m, timezone.utc) + deslocamento).strftime("%Y-%m-%d")
            for m in marcos
        ]
        frame = pd.DataFrame({"data": datas, "valor": fechamentos})
        frame["serie_id"] = self._config["serie_id"]
        frame["unidade"] = self._config["unit"]
        return self._quadro(frame, coletado_em)
