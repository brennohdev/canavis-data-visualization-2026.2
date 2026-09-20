from __future__ import annotations

import logging

from canavis.config import load_settings

_configured = False


def configure() -> None:
    global _configured
    if _configured:
        return
    settings = load_settings()
    logging.basicConfig(level=settings.log_level, format=settings.log_format)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    configure()
    return logging.getLogger(name)
