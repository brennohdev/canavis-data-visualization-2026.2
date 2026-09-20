from __future__ import annotations

import pandas as pd

from canavis.sources.base import DataSource

_COLUMN_RENAME = {
    "D1C": "cod_local",
    "D1N": "local",
    "D2N": "variavel",
    "D3N": "periodo",
    "V": "valor",
}


class IbgePamSource(DataSource):
    """Produção Agrícola Municipal via API SIDRA (uma requisição por extração)."""

    def fetch(self) -> pd.DataFrame:
        frames = [
            self._fetch_extraction(name, params)
            for name, params in self._config["extractions"].items()
        ]
        return pd.concat(frames, ignore_index=True)

    def _fetch_extraction(self, name: str, params: dict) -> pd.DataFrame:
        payload = self._client.get_json(self._build_url(params))
        rows = payload[1:]
        frame = pd.DataFrame(rows)[list(_COLUMN_RENAME)].rename(columns=_COLUMN_RENAME)
        frame.insert(0, "extracao", name)
        return frame

    def _build_url(self, params: dict) -> str:
        variables = ",".join(self._config["variables"].values())
        localities = params["localities"].replace(" ", "%20")
        return (
            f"{self._config['base_url']}"
            f"/t/{self._config['table']}"
            f"/n{params['level']}/{localities}"
            f"/v/{variables}"
            f"/p/{params['periods']}"
            f"/{self._config['product_classifier']}/{self._config['product_code']}"
            f"?formato=json"
        )
