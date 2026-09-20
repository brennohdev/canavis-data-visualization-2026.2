from __future__ import annotations

from pathlib import Path

from canavis import storage
from canavis.config import load_settings
from canavis.logging import get_logger
from canavis.sources import available_sources, build_source

_log = get_logger(__name__)


def extract_all() -> dict[str, Path]:
    """Camada bronze: baixa cada fonte e persiste o dado cru em data/raw."""
    settings = load_settings()

    written: dict[str, Path] = {}
    for key in available_sources():
        source = build_source(key)
        frame = source.fetch()
        destination = storage.write(frame, settings.paths.raw, key)
        _log.info("bronze | %s | %d linhas | %s", key, len(frame), destination.name)
        written[key] = destination
    return written
