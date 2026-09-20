from __future__ import annotations

from canavis.config import load_sources
from canavis.sources.base import DataSource
from canavis.sources.delimited import DelimitedFileSource
from canavis.sources.http_client import HttpClient
from canavis.sources.ibge import IbgePamSource

_ADAPTERS: dict[str, type[DataSource]] = {
    "ibge": IbgePamSource,
    "conab": DelimitedFileSource,
    "anp": DelimitedFileSource,
}


def build_source(key: str, client: HttpClient | None = None) -> DataSource:
    config = dict(load_sources()[key], key=key)
    adapter = config["adapter"]
    if adapter not in _ADAPTERS:
        raise KeyError(f"Adapter '{adapter}' não registrado")
    return _ADAPTERS[adapter](config, client or HttpClient())


def available_sources() -> list[str]:
    return list(load_sources())
