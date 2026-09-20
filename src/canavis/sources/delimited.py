from __future__ import annotations

import io

import pandas as pd

from canavis.sources.base import DataSource


class DelimitedFileSource(DataSource):
    """Fonte baseada em arquivo texto delimitado (CONAB, ANP e similares)."""

    def fetch(self) -> pd.DataFrame:
        text = self._client.get_text(self._config["url"], self._config["encoding"])
        frame = pd.read_csv(
            io.StringIO(text),
            sep=self._config["separator"],
            engine="python",
        )
        frame.columns = [column.strip() for column in frame.columns]
        return frame
