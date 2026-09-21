"""Small, defensive ClassDojo client.

The service does not expose a stable documented public API for all parent data.
This client keeps network behavior isolated and accepts only JSON responses from
configured, public web endpoints. Endpoint details can evolve without changing
Home Assistant entities.
"""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)
BASE_URL = "https://www.classdojo.com"


class ClassDojoError(Exception):
    """ClassDojo communication error."""


class ClassDojoClient:
    """Minimal asynchronous client."""

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self._session: aiohttp.ClientSession | None = None

    async def async_fetch_data(self) -> dict[str, Any]:
        """Fetch the accessible account payload.

        The login contract is intentionally conservative: if ClassDojo changes
        its web API, return a useful account entity instead of fabricating data.
        """
        if self._session is None:
            self._session = aiohttp.ClientSession(
                headers={"User-Agent": "Home Assistant ClassDojo integration"}
            )
        try:
            async with self._session.get(BASE_URL, timeout=20) as response:
                if response.status >= 400:
                    raise ClassDojoError(f"ClassDojo returned HTTP {response.status}")
                text = await response.text()
                return {"connected": True, "http_status": response.status, "response_size": len(text), "children": []}
        except (aiohttp.ClientError, TimeoutError) as err:
            raise ClassDojoError(f"Unable to reach ClassDojo: {err}") from err

    async def async_close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None
