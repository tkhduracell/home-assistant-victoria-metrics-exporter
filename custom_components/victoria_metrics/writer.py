"""Victoria Metrics HTTP writer using InfluxDB line protocol."""

from __future__ import annotations

import asyncio
import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 1  # seconds


def _escape_tag_value(value: str) -> str:
    """Escape special characters in InfluxDB line protocol tag values."""
    return value.replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def _escape_measurement(name: str) -> str:
    """Escape special characters in measurement name."""
    return name.replace(" ", "\\ ").replace(",", "\\,")


class VictoriaMetricsWriter:
    """Async HTTP writer for Victoria Metrics using InfluxDB line protocol."""

    def __init__(
        self,
        host: str,
        port: int,
        ssl: bool = False,
        verify_ssl: bool = True,
        token: str | None = None,
    ) -> None:
        """Initialize the writer."""
        scheme = "https" if ssl else "http"
        self._base_url = f"{scheme}://{host}:{port}"
        self._write_url = f"{self._base_url}/write"
        self._verify_ssl = verify_ssl
        self._token = token
        self._session: aiohttp.ClientSession | None = None

    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            headers: dict[str, str] = {}
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"

            connector = aiohttp.TCPConnector(ssl=self._verify_ssl if self._verify_ssl else False)
            self._session = aiohttp.ClientSession(
                headers=headers,
                connector=connector,
            )
        return self._session

    async def test_connection(self) -> bool:
        """Test connectivity to Victoria Metrics."""
        try:
            session = self._get_session()
            async with session.get(
                f"{self._base_url}/health",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                return resp.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Failed to connect to Victoria Metrics at %s: %s", self._base_url, err)
            return False

    @staticmethod
    def format_line(
        metric_name: str,
        tags: dict[str, str],
        value: float | str,
        timestamp_ns: int,
    ) -> str:
        """Format a data point as InfluxDB line protocol.

        Format: measurement,tag1=val1,tag2=val2 field=value timestamp_ns
        """
        escaped_name = _escape_measurement(metric_name)

        tag_parts = []
        for key, val in sorted(tags.items()):
            if val:
                tag_parts.append(f"{_escape_tag_value(key)}={_escape_tag_value(str(val))}")

        tag_str = "," + ",".join(tag_parts) if tag_parts else ""

        if isinstance(value, str):
            field_str = f'state_text="{value}"'
        else:
            field_str = f"value={value}"

        return f"{escaped_name}{tag_str} {field_str} {timestamp_ns}"

    async def _post(self, data: str) -> bool:
        """POST data to Victoria Metrics with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                session = self._get_session()
                async with session.post(
                    self._write_url,
                    data=data.encode("utf-8"),
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 204 or resp.status == 200:
                        return True
                    if resp.status == 401:
                        _LOGGER.error(
                            "Authentication failed for Victoria Metrics (HTTP 401). "
                            "Check your token configuration."
                        )
                        return False
                    body = await resp.text()
                    _LOGGER.warning(
                        "Victoria Metrics returned HTTP %s: %s",
                        resp.status,
                        body[:200],
                    )
                    return False
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BACKOFF_BASE * (2**attempt)
                    _LOGGER.debug(
                        "Write attempt %d failed (%s), retrying in %ds",
                        attempt + 1,
                        err,
                        wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    _LOGGER.warning(
                        "Failed to write to Victoria Metrics after %d attempts: %s",
                        MAX_RETRIES,
                        err,
                    )
                    return False
        return False

    async def write_batch(self, lines: list[str]) -> bool:
        """Write multiple lines to Victoria Metrics in a single request."""
        if not lines:
            return True
        data = "\n".join(lines)
        _LOGGER.debug("Writing batch of %d metrics to Victoria Metrics", len(lines))
        return await self._post(data)

    async def write_single(self, line: str) -> bool:
        """Write a single line to Victoria Metrics."""
        return await self._post(line)

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
