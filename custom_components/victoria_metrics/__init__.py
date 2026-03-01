"""Victoria Metrics Exporter integration for Home Assistant."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from datetime import timedelta
import logging
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    CALLBACK_TYPE,
    HomeAssistant,
    State,
    callback,
)
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

from .attributes import extract_attribute_lines
from .const import (
    CONF_BATCH_INTERVAL,
    CONF_ENTITY_SETTINGS,
    CONF_EXPORT_ENTITIES,
    CONF_HOST,
    CONF_METRIC_PREFIX,
    CONF_PORT,
    CONF_SSL,
    CONF_TOKEN,
    CONF_VERIFY_SSL,
    DEFAULT_BATCH_INTERVAL,
    DEFAULT_METRIC_PREFIX,
    DOMAIN,
    PLATFORMS,
    STATE_MAP,
    build_metric_name,
)
from .panel import async_register_panel, async_unregister_panel
from .websocket import async_register_websocket_commands
from .writer import VictoriaMetricsWriter

_LOGGER = logging.getLogger(__name__)


def _build_tags(entity_id: str, state: State) -> dict[str, str]:
    """Build tag dict for a state object."""
    domain = entity_id.split(".", 1)[0]
    tags: dict[str, str] = {
        "entity_id": entity_id,
        "domain": domain,
    }

    attrs = state.attributes
    if friendly_name := attrs.get("friendly_name"):
        tags["friendly_name"] = str(friendly_name)
    if device_class := attrs.get("device_class"):
        tags["device_class"] = str(device_class)
    if unit := attrs.get("unit_of_measurement"):
        tags["unit"] = str(unit)

    return tags


def _process_state(state_value: str) -> float | str | None:
    """Convert a state string to a numeric value, mapped boolean, or string.

    Returns None for states that should be skipped.
    """
    if state_value in ("unknown", "unavailable"):
        return None

    try:
        return float(state_value)
    except (ValueError, TypeError):
        pass

    lower = state_value.lower()
    if lower in STATE_MAP:
        return STATE_MAP[lower]

    return state_value


def _state_to_timestamp_ns(state: State) -> int:
    """Convert state's last_updated to nanoseconds since epoch."""
    return int(state.last_updated.timestamp() * 1e9)


def _build_entity_configs_from_options(
    options: Mapping[str, Any],
) -> tuple[dict[str, EntityConfig], int]:
    """Build EntityConfig dict from config entry options.

    Returns (entity_configs, global_batch_interval).
    """
    prefix = options.get(CONF_METRIC_PREFIX, DEFAULT_METRIC_PREFIX)
    global_batch_interval = int(
        options.get(CONF_BATCH_INTERVAL, DEFAULT_BATCH_INTERVAL)
    )
    entity_ids: list[str] = options.get(CONF_EXPORT_ENTITIES, [])
    entity_settings: dict[str, dict[str, Any]] = options.get(CONF_ENTITY_SETTINGS, {})

    entity_configs: dict[str, EntityConfig] = {}
    for entity_id in entity_ids:
        settings = entity_settings.get(entity_id, {})
        metric_name = build_metric_name(
            prefix, entity_id, settings.get("metric_name") or None
        )
        entity_configs[entity_id] = EntityConfig(
            entity_id=entity_id,
            metric_name=metric_name,
            batch_interval=int(settings.get("batch_interval", global_batch_interval)),
        )

    return entity_configs, global_batch_interval


class EntityConfig:
    """Parsed entity configuration."""

    __slots__ = ("batch_interval", "entity_id", "metric_name")

    def __init__(
        self,
        entity_id: str,
        metric_name: str,
        batch_interval: int = DEFAULT_BATCH_INTERVAL,
    ) -> None:
        self.entity_id = entity_id
        self.metric_name = metric_name
        self.batch_interval = batch_interval


@dataclass(slots=True)
class AuditLogEntry:
    """A single audit log entry for an export event."""

    timestamp: float
    entity_id: str
    metric_name: str
    value: float | str | None
    mode: str
    lines_count: int


class ExportManager:
    """Manages per-entity export listeners and periodic state sampling."""

    def __init__(
        self,
        hass: HomeAssistant,
        writer: VictoriaMetricsWriter,
        entity_configs: dict[str, EntityConfig],
        batch_interval: int,
    ) -> None:
        self.hass = hass
        self.writer = writer
        self.entity_configs = entity_configs
        self.batch_interval = batch_interval
        self._batch_timers: dict[int, CALLBACK_TYPE] = {}
        self._audit_log: deque[AuditLogEntry] = deque(maxlen=100)

    def _record_audit_entry(
        self,
        entity_id: str,
        value: float | str | None,
        mode: str,
        lines_count: int,
    ) -> None:
        """Record an export event in the audit log."""
        ec = self.entity_configs.get(entity_id)
        if ec is None:
            return
        self._audit_log.append(
            AuditLogEntry(
                timestamp=time.time(),
                entity_id=entity_id,
                metric_name=ec.metric_name,
                value=value,
                mode=mode,
                lines_count=lines_count,
            )
        )

    def get_audit_log(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return recent audit log entries as dicts, newest first."""
        entries = list(self._audit_log)
        entries.reverse()
        return [asdict(e) for e in entries[:limit]]

    def _format_state_lines(
        self, entity_id: str, state: State, *, timestamp_ns: int | None = None
    ) -> list[str]:
        """Format a state and its attributes into InfluxDB line protocol strings."""
        ec = self.entity_configs.get(entity_id)
        if ec is None:
            return []

        tags = _build_tags(entity_id, state)
        ts = timestamp_ns if timestamp_ns is not None else _state_to_timestamp_ns(state)
        lines: list[str] = []

        # Primary state line
        value = _process_state(state.state)
        if value is not None:
            lines.append(self.writer.format_line(ec.metric_name, tags, value, ts))

        # Domain-specific attribute lines
        lines.extend(
            extract_attribute_lines(
                state, ec.metric_name, tags, ts, self.writer.format_line
            )
        )

        return lines

    def start(self) -> None:
        """Register batch timers for all entity configs."""
        self._sync_batch_timers()

        entity_ids = list(self.entity_configs)
        if entity_ids:
            _LOGGER.info(
                "Tracking %d entities in batch mode: %s",
                len(entity_ids),
                ", ".join(entity_ids),
            )

    def _get_needed_batch_intervals(self) -> set[int]:
        """Return the set of batch intervals currently in use."""
        return {ec.batch_interval for ec in self.entity_configs.values()}

    def _sync_batch_timers(self) -> None:
        """Ensure one timer is running per unique batch interval in use."""
        needed = self._get_needed_batch_intervals()

        # Stop timers that are no longer needed
        for interval in list(self._batch_timers):
            if interval not in needed:
                self._batch_timers.pop(interval)()

        # Start timers that are missing
        for interval in needed:
            if interval not in self._batch_timers:
                self._batch_timers[interval] = async_track_time_interval(
                    self.hass,
                    self._make_flush_callback(interval),
                    timedelta(seconds=interval),
                )

    def _make_flush_callback(self, interval: int) -> Callable[..., Any]:
        """Create a periodic sampling callback for a specific batch interval."""

        async def _flush(_now: object = None) -> None:
            entity_ids = {
                eid
                for eid, ec in self.entity_configs.items()
                if ec.batch_interval == interval
            }
            now_ns = int(time.time() * 1e9)
            lines: list[str] = []
            for eid in entity_ids:
                state = self.hass.states.get(eid)
                if state is None:
                    continue
                entity_lines = self._format_state_lines(eid, state, timestamp_ns=now_ns)
                if entity_lines:
                    value = _process_state(state.state)
                    self._record_audit_entry(eid, value, "batch", len(entity_lines))
                lines.extend(entity_lines)
            if lines:
                await self.writer.write_batch(lines)

        return _flush

    @callback
    def set_batch_interval(self, entity_id: str, interval: int) -> None:
        """Change the batch flush interval for an entity."""
        ec = self.entity_configs.get(entity_id)
        if ec is None:
            return
        if ec.batch_interval == interval:
            return
        ec.batch_interval = interval
        self._sync_batch_timers()
        _LOGGER.info("Changed batch interval for %s to %ds", entity_id, interval)

    @callback
    def set_metric_name(self, entity_id: str, metric_name: str) -> None:
        """Change the metric name for an entity."""
        ec = self.entity_configs.get(entity_id)
        if ec is None:
            return
        if ec.metric_name == metric_name:
            return
        ec.metric_name = metric_name
        _LOGGER.info("Changed metric name for %s to %s", entity_id, metric_name)

    async def shutdown(self) -> None:
        """Clean up all listeners and send final sample."""
        for unsub in self._batch_timers.values():
            unsub()
        self._batch_timers.clear()

        # Final sample of all entities before closing
        now_ns = int(time.time() * 1e9)
        lines: list[str] = []
        for eid in self.entity_configs:
            state = self.hass.states.get(eid)
            if state is None:
                continue
            lines.extend(self._format_state_lines(eid, state, timestamp_ns=now_ns))
        if lines:
            await self.writer.write_batch(lines)
        await self.writer.close()


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Victoria Metrics Exporter."""
    hass.data.setdefault(DOMAIN, {})
    async_register_websocket_commands(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Victoria Metrics connection from config entry (UI)."""
    writer = VictoriaMetricsWriter(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        ssl=entry.data.get(CONF_SSL, False),
        verify_ssl=entry.data.get(CONF_VERIFY_SSL, True),
        token=entry.data.get(CONF_TOKEN) or None,
    )

    if not await writer.test_connection():
        _LOGGER.error(
            "Cannot connect to Victoria Metrics at %s:%s",
            entry.data[CONF_HOST],
            entry.data[CONF_PORT],
        )
        await writer.close()
        return False

    _LOGGER.info(
        "Connected to Victoria Metrics at %s:%s",
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
    )

    domain_data = hass.data.setdefault(DOMAIN, {})
    entity_configs, batch_interval = _build_entity_configs_from_options(entry.options)

    if not entity_configs:
        _LOGGER.warning(
            "No entity mappings configured for Victoria Metrics. "
            "Use Settings > Devices & Services > Victoria Metrics > Configure "
            "to select entities for export.",
        )

    manager = ExportManager(hass, writer, entity_configs, batch_interval)
    manager.start()

    # Store runtime data keyed by entry_id
    domain_data[entry.entry_id] = {
        "manager": manager,
        "writer": writer,
    }

    # Register sidebar panel once
    if not domain_data.get("panel_registered"):
        await async_register_panel(hass)
        domain_data["panel_registered"] = True

    # Forward platform setup
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    domain_data = hass.data.get(DOMAIN, {})
    entry_data = domain_data.pop(entry.entry_id, None)
    if entry_data:
        manager = entry_data.get("manager")
        if manager:
            await manager.shutdown()

    # Remove sidebar panel when the last config entry is unloaded
    remaining = [k for k in domain_data if k != "panel_registered"]
    if not remaining and domain_data.get("panel_registered"):
        async_unregister_panel(hass)
        domain_data["panel_registered"] = False

    return unload_ok
