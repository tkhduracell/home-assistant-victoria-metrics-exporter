"""Victoria Metrics HTTP reader for instant queries."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 1  # seconds


class VictoriaMetricsReader:
    """Async HTTP reader for Victoria Metrics instant queries."""

    def __init__(
        self,
        host: str,
        port: int,
        ssl: bool = False,
        verify_ssl: bool = True,
        token: str | None = None,
    ) -> None:
        """Initialize the reader."""
        scheme = "https" if ssl else "http"
        self._base_url = f"{scheme}://{host}:{port}"
        self._query_url = f"{self._base_url}/api/v1/query"
        self._verify_ssl = verify_ssl
        self._token = token
        self._session: aiohttp.ClientSession | None = None

    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            headers: dict[str, str] = {}
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"

            connector = aiohttp.TCPConnector(ssl=self._verify_ssl or False)
            self._session = aiohttp.ClientSession(
                headers=headers,
                connector=connector,
            )
        return self._session

    async def query_instant(
        self, query: str
    ) -> tuple[float, dict[str, str], int] | None:
        """Run an instant query and return (value, labels, timestamp_s).

        Returns None when the result vector is empty, the query fails,
        or the value cannot be parsed as a float.
        """
        payload = await self._get_query(query)
        if payload is None:
            return None

        if payload.get("status") != "success":
            _LOGGER.warning(
                "Victoria Metrics query failed for %r: %s",
                query,
                payload.get("error") or payload,
            )
            return None

        data = payload.get("data") or {}
        result = data.get("result") or []
        if not result:
            _LOGGER.debug("Victoria Metrics query %r returned empty vector", query)
            return None

        if len(result) > 1:
            _LOGGER.warning(
                "Victoria Metrics query %r returned %d series; using the first",
                query,
                len(result),
            )

        first = result[0]
        labels = {str(k): str(v) for k, v in (first.get("metric") or {}).items()}

        value_pair = first.get("value")
        if not value_pair or len(value_pair) < 2:
            _LOGGER.warning(
                "Victoria Metrics query %r returned malformed value: %s",
                query,
                value_pair,
            )
            return None

        ts_raw, val_raw = value_pair[0], value_pair[1]
        try:
            value = float(val_raw)
        except (TypeError, ValueError):
            _LOGGER.warning(
                "Victoria Metrics query %r returned non-numeric value %r",
                query,
                val_raw,
            )
            return None

        try:
            timestamp_s = int(float(ts_raw))
        except (TypeError, ValueError):
            timestamp_s = 0

        return value, labels, timestamp_s

    async def _get_query(self, query: str) -> dict[str, Any] | None:
        """GET an instant query with retry logic; return decoded JSON or None."""
        for attempt in range(MAX_RETRIES):
            try:
                session = self._get_session()
                async with session.get(
                    self._query_url,
                    params={"query": query},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 401:
                        _LOGGER.error(
                            "Authentication failed for Victoria Metrics (HTTP 401). "
                            "Check your token configuration."
                        )
                        return None
                    if resp.status >= 400:
                        body = await resp.text()
                        _LOGGER.warning(
                            "Victoria Metrics query returned HTTP %s for %r: %s",
                            resp.status,
                            query,
                            body[:200],
                        )
                        return None
                    payload: dict[str, Any] = await resp.json(content_type=None)
                    return payload
            except (TimeoutError, aiohttp.ClientError) as err:
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BACKOFF_BASE * (2**attempt)
                    _LOGGER.debug(
                        "Query attempt %d failed (%s), retrying in %ds",
                        attempt + 1,
                        err,
                        wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    _LOGGER.warning(
                        "Failed to query Victoria Metrics after %d attempts: %s",
                        MAX_RETRIES,
                        err,
                    )
                    return None
        return None

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
