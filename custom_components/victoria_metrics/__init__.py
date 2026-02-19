"""Victoria Metrics Exporter integration for Home Assistant."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import timedelta
import logging
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    CALLBACK_TYPE,
    Event,
    EventStateChangedData,
    HomeAssistant,
    State,
    callback,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol

from .const import (
    CONF_BATCH_INTERVAL,
    CONF_ENTITIES,
    CONF_ENTITY_SETTINGS,
    CONF_EXPORT_ENTITIES,
    CONF_HOST,
    CONF_METRIC_NAME,
    CONF_METRIC_PREFIX,
    CONF_PORT,
    CONF_REALTIME,
    CONF_SSL,
    CONF_TAGS,
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

ENTITY_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_METRIC_NAME): cv.string,
        vol.Optional(CONF_TAGS, default={}): {cv.string: cv.string},
        vol.Optional(CONF_REALTIME, default=False): cv.boolean,
    }
)

# YAML schema — entity mappings and export settings only.
# Connection settings (host, port, token) come from the config flow UI.
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(
                    CONF_METRIC_PREFIX, default=DEFAULT_METRIC_PREFIX
                ): cv.string,
                vol.Optional(
                    CONF_BATCH_INTERVAL, default=DEFAULT_BATCH_INTERVAL
                ): cv.positive_int,
                vol.Optional(CONF_ENTITIES, default={}): {cv.entity_id: ENTITY_SCHEMA},
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def _build_tags(
    entity_id: str, state: State, extra_tags: dict[str, str]
) -> dict[str, str]:
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

    tags.update(extra_tags)
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
        metric_name = build_metric_name(prefix, entity_id)
        settings = entity_settings.get(entity_id, {})
        entity_configs[entity_id] = EntityConfig(
            entity_id=entity_id,
            metric_name=metric_name,
            extra_tags={},
            realtime=settings.get("realtime", False),
            batch_interval=int(settings.get("batch_interval", global_batch_interval)),
        )

    return entity_configs, global_batch_interval


class EntityConfig:
    """Parsed entity configuration."""

    __slots__ = ("batch_interval", "entity_id", "extra_tags", "metric_name", "realtime")

    def __init__(
        self,
        entity_id: str,
        metric_name: str,
        extra_tags: dict[str, str],
        realtime: bool,
        batch_interval: int = DEFAULT_BATCH_INTERVAL,
    ) -> None:
        self.entity_id = entity_id
        self.metric_name = metric_name
        self.extra_tags = extra_tags
        self.realtime = realtime
        self.batch_interval = batch_interval


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
        self._entity_unsubs: dict[str, CALLBACK_TYPE] = {}
        self._batch_timers: dict[int, CALLBACK_TYPE] = {}
        self._mode_change_listeners: list[Callable[[str, bool], None]] = []

    def on_mode_change(self, listener: Callable[[str, bool], None]) -> None:
        """Register a callback for when an entity's mode changes."""
        self._mode_change_listeners.append(listener)

    def _notify_mode_change(self, entity_id: str, realtime: bool) -> None:
        """Notify listeners of a mode change."""
        for listener in self._mode_change_listeners:
            listener(entity_id, realtime)

    def _format_state_line(
        self, entity_id: str, state: State, *, timestamp_ns: int | None = None
    ) -> str | None:
        """Format a state into an InfluxDB line protocol string."""
        ec = self.entity_configs.get(entity_id)
        if ec is None:
            return None

        value = _process_state(state.state)
        if value is None:
            return None

        tags = _build_tags(entity_id, state, ec.extra_tags)
        ts = timestamp_ns if timestamp_ns is not None else _state_to_timestamp_ns(state)
        return self.writer.format_line(ec.metric_name, tags, value, ts)

    def _register_realtime(self, entity_id: str) -> None:
        """Register a real-time state change listener for one entity."""

        @callback
        def _handle_realtime(event: Event[EventStateChangedData]) -> None:
            new_state: State | None = event.data.get("new_state")
            if new_state is None:
                return
            eid = event.data.get("entity_id", "")
            line = self._format_state_line(eid, new_state)
            if line is not None:
                self.hass.async_create_task(self.writer.write_single(line))

        unsub = async_track_state_change_event(self.hass, [entity_id], _handle_realtime)
        self._entity_unsubs[entity_id] = unsub

    def start(self) -> None:
        """Register all listeners based on current entity configs."""
        for entity_id, ec in self.entity_configs.items():
            if ec.realtime:
                self._register_realtime(entity_id)

        self._sync_batch_timers()

        realtime_ids = [eid for eid, ec in self.entity_configs.items() if ec.realtime]
        batch_ids = [eid for eid, ec in self.entity_configs.items() if not ec.realtime]
        if realtime_ids:
            _LOGGER.info(
                "Tracking %d entities in real-time mode: %s",
                len(realtime_ids),
                ", ".join(realtime_ids),
            )
        if batch_ids:
            _LOGGER.info(
                "Tracking %d entities in batch mode: %s",
                len(batch_ids),
                ", ".join(batch_ids),
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
                line = self._format_state_line(eid, state, timestamp_ns=now_ns)
                if line is not None:
                    lines.append(line)
            if lines:
                await self.writer.write_batch(lines)

        return _flush

    @callback
    def set_realtime(self, entity_id: str, realtime: bool) -> None:
        """Switch an entity between realtime and batch mode."""
        ec = self.entity_configs.get(entity_id)
        if ec is None:
            return

        if ec.realtime == realtime:
            return

        # Unsubscribe current listener (only realtime entities have listeners)
        if entity_id in self._entity_unsubs:
            self._entity_unsubs[entity_id]()
            del self._entity_unsubs[entity_id]

        # Update config and register new listener if switching to realtime
        ec.realtime = realtime
        if realtime:
            self._register_realtime(entity_id)
        # Batch: no listener needed, periodic timer handles sampling

        self._sync_batch_timers()

        mode_str = "real-time" if realtime else "batch"
        _LOGGER.info("Switched %s to %s mode", entity_id, mode_str)
        self._notify_mode_change(entity_id, realtime)

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

    async def shutdown(self) -> None:
        """Clean up all listeners and send final sample."""
        for unsub in self._entity_unsubs.values():
            unsub()
        self._entity_unsubs.clear()

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
            line = self._format_state_line(eid, state, timestamp_ns=now_ns)
            if line is not None:
                lines.append(line)
        if lines:
            await self.writer.write_batch(lines)
        await self.writer.close()


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Victoria Metrics Exporter — parse YAML entity mappings."""
    hass.data.setdefault(DOMAIN, {})
    async_register_websocket_commands(hass)

    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    prefix = conf.get(CONF_METRIC_PREFIX, DEFAULT_METRIC_PREFIX)
    batch_interval = conf.get(CONF_BATCH_INTERVAL, DEFAULT_BATCH_INTERVAL)
    entities_conf = conf.get(CONF_ENTITIES, {})

    entity_configs: dict[str, EntityConfig] = {}
    for entity_id, ent_conf in entities_conf.items():
        metric_name = build_metric_name(
            prefix, entity_id, ent_conf.get(CONF_METRIC_NAME)
        )
        entity_configs[entity_id] = EntityConfig(
            entity_id=entity_id,
            metric_name=metric_name,
            extra_tags=ent_conf.get(CONF_TAGS, {}),
            realtime=ent_conf.get(CONF_REALTIME, False),
        )

    # Store YAML config for use by async_setup_entry as fallback
    hass.data[DOMAIN]["yaml_entity_configs"] = entity_configs
    hass.data[DOMAIN]["yaml_batch_interval"] = batch_interval

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

    # Determine entity configs: options flow takes priority over YAML
    domain_data = hass.data.setdefault(DOMAIN, {})

    if CONF_EXPORT_ENTITIES in entry.options:
        entity_configs, batch_interval = _build_entity_configs_from_options(
            entry.options
        )
    else:
        # Fallback to YAML config (parsed in async_setup)
        entity_configs = domain_data.get("yaml_entity_configs", {})
        batch_interval = domain_data.get("yaml_batch_interval", DEFAULT_BATCH_INTERVAL)

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
    _reserved_keys = {"yaml_entity_configs", "yaml_batch_interval", "panel_registered"}
    remaining = [k for k in domain_data if k not in _reserved_keys]
    if not remaining and domain_data.get("panel_registered"):
        async_unregister_panel(hass)
        domain_data["panel_registered"] = False

    return unload_ok
