from __future__ import annotations

from canavis.config import load_sources
from canavis.sources.base import DataSource
from canavis.sources.delimited import DelimitedFileSource
from canavis.sources.http_client import HttpClient
from canavis.sources.ibge import IbgePamSource
from canavis.sources.intl.bcb_sgs import BcbSgsSource
from canavis.sources.intl.cftc import CftcSource
from canavis.sources.intl.fred import FredSource
from canavis.sources.intl.usda_psd import UsdaPsdSource
from canavis.sources.intl.worldbank import WorldBankSource
from canavis.sources.intl.yahoo import YahooSource

_ADAPTERS: dict[str, type[DataSource]] = {
    "ibge": IbgePamSource,
    "conab": DelimitedFileSource,
    "anp": DelimitedFileSource,
    "bcb_sgs": BcbSgsSource,
    "fred": FredSource,
    "worldbank": WorldBankSource,
    "yahoo": YahooSource,
    "cftc": CftcSource,
    "usda_psd": UsdaPsdSource,
}

_ADAPTERS_INTL = frozenset({"bcb_sgs", "fred", "worldbank", "yahoo", "cftc", "usda_psd"})


def build_source(key: str, client: HttpClient | None = None) -> DataSource:
    config = dict(load_sources()[key], key=key)
    adapter = config["adapter"]
    if adapter not in _ADAPTERS:
        raise KeyError(f"Adapter '{adapter}' não registrado")
    return _ADAPTERS[adapter](config, client or HttpClient())


def available_sources() -> list[str]:
    return list(load_sources())


def intl_sources() -> list[str]:
    return [k for k, cfg in load_sources().items() if cfg["adapter"] in _ADAPTERS_INTL]
