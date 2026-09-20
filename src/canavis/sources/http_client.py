from __future__ import annotations

import requests

from canavis.config import load_settings


class HttpClient:
    """Cliente HTTP único, com timeout e user-agent vindos da configuração."""

    def __init__(self) -> None:
        settings = load_settings()
        self._timeout = settings.http.timeout_seconds
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": settings.http.user_agent})

    def get_json(self, url: str) -> object:
        response = self._session.get(url, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def get_text(self, url: str, encoding: str) -> str:
        response = self._session.get(url, timeout=self._timeout)
        response.raise_for_status()
        return response.content.decode(encoding)
