"""Victoria Metrics Exporter integration for Home Assistant."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Callable

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, State, callback
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_BATCH_INTERVAL,
    CONF_ENTITIES,
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
    STATE_MAP,
)
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
                vol.Required(CONF_ENTITIES): {cv.entity_id: ENTITY_SCHEMA},
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def _build_metric_name(prefix: str, entity_id: str, override: str | None) -> str:
    """Build metric name from entity_id or use override."""
    if override:
        return override
    domain, object_id = entity_id.split(".", 1)
    return f"{prefix}_{domain}_{object_id}"


def _build_tags(entity_id: str, state: State, extra_tags: dict[str, str]) -> dict[str, str]:
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


class EntityConfig:
    """Parsed entity configuration."""

    __slots__ = ("entity_id", "metric_name", "extra_tags", "realtime")

    def __init__(
        self,
        entity_id: str,
        metric_name: str,
        extra_tags: dict[str, str],
        realtime: bool,
    ) -> None:
        self.entity_id = entity_id
        self.metric_name = metric_name
        self.extra_tags = extra_tags
        self.realtime = realtime


class ExportManager:
    """Manages per-entity export listeners and the batch buffer."""

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
        self.batch_buffer: dict[str, str] = {}
        self._entity_unsubs: dict[str, CALLBACK_TYPE] = {}
        self._batch_timer_unsub: CALLBACK_TYPE | None = None
        self._mode_change_listeners: list[Callable[[str, bool], None]] = []

    def on_mode_change(self, listener: Callable[[str, bool], None]) -> None:
        """Register a callback for when an entity's mode changes."""
        self._mode_change_listeners.append(listener)

    def _notify_mode_change(self, entity_id: str, realtime: bool) -> None:
        """Notify listeners of a mode change."""
        for listener in self._mode_change_listeners:
            listener(entity_id, realtime)

    def _format_state_line(self, entity_id: str, state: State) -> str | None:
        """Format a state change into an InfluxDB line protocol string."""
        ec = self.entity_configs.get(entity_id)
        if ec is None:
            return None

        value = _process_state(state.state)
        if value is None:
            return None

        tags = _build_tags(entity_id, state, ec.extra_tags)
        timestamp_ns = _state_to_timestamp_ns(state)
        return self.writer.format_line(ec.metric_name, tags, value, timestamp_ns)

    def _register_realtime(self, entity_id: str) -> None:
        """Register a real-time state change listener for one entity."""

        @callback
        def _handle_realtime(event: Event) -> None:
            new_state: State | None = event.data.get("new_state")
            if new_state is None:
                return
            eid = event.data.get("entity_id", "")
            line = self._format_state_line(eid, new_state)
            if line is not None:
                self.hass.async_create_task(self.writer.write_single(line))

        unsub = async_track_state_change_event(
            self.hass, [entity_id], _handle_realtime
        )
        self._entity_unsubs[entity_id] = unsub

    def _register_batch(self, entity_id: str) -> None:
        """Register a batch state change listener for one entity."""

        @callback
        def _handle_batch(event: Event) -> None:
            new_state: State | None = event.data.get("new_state")
            if new_state is None:
                return
            eid = event.data.get("entity_id", "")
            line = self._format_state_line(eid, new_state)
            if line is not None:
                self.batch_buffer[eid] = line

        unsub = async_track_state_change_event(
            self.hass, [entity_id], _handle_batch
        )
        self._entity_unsubs[entity_id] = unsub

    def start(self) -> None:
        """Register all listeners based on current entity configs."""
        for entity_id, ec in self.entity_configs.items():
            if ec.realtime:
                self._register_realtime(entity_id)
            else:
                self._register_batch(entity_id)

        has_batch = any(
            not ec.realtime for ec in self.entity_configs.values()
        )
        if has_batch:
            self._start_batch_timer()

        realtime_ids = [
            eid for eid, ec in self.entity_configs.items() if ec.realtime
        ]
        batch_ids = [
            eid for eid, ec in self.entity_configs.items() if not ec.realtime
        ]
        if realtime_ids:
            _LOGGER.info(
                "Tracking %d entities in real-time mode: %s",
                len(realtime_ids),
                ", ".join(realtime_ids),
            )
        if batch_ids:
            _LOGGER.info(
                "Tracking %d entities in batch mode (interval: %ds): %s",
                len(batch_ids),
                self.batch_interval,
                ", ".join(batch_ids),
            )

    def _start_batch_timer(self) -> None:
        """Start the batch flush timer if not already running."""
        if self._batch_timer_unsub is not None:
            return
        self._batch_timer_unsub = async_track_time_interval(
            self.hass, self._flush_batch, timedelta(seconds=self.batch_interval)
        )

    def _stop_batch_timer_if_unused(self) -> None:
        """Stop the batch timer if no entities use batch mode."""
        has_batch = any(
            not ec.realtime for ec in self.entity_configs.values()
        )
        if not has_batch and self._batch_timer_unsub is not None:
            self._batch_timer_unsub()
            self._batch_timer_unsub = None

    @callback
    def set_realtime(self, entity_id: str, realtime: bool) -> None:
        """Switch an entity between realtime and batch mode."""
        ec = self.entity_configs.get(entity_id)
        if ec is None:
            return

        if ec.realtime == realtime:
            return

        # Unsubscribe current listener
        if entity_id in self._entity_unsubs:
            self._entity_unsubs[entity_id]()
            del self._entity_unsubs[entity_id]

        # Remove from batch buffer if switching to realtime
        if realtime:
            self.batch_buffer.pop(entity_id, None)

        # Update config and register new listener
        ec.realtime = realtime
        if realtime:
            self._register_realtime(entity_id)
            self._stop_batch_timer_if_unused()
        else:
            self._register_batch(entity_id)
            self._start_batch_timer()

        mode_str = "real-time" if realtime else "batch"
        _LOGGER.info("Switched %s to %s mode", entity_id, mode_str)
        self._notify_mode_change(entity_id, realtime)

    async def _flush_batch(self, _now=None) -> None:
        """Flush the batch buffer to Victoria Metrics."""
        if not self.batch_buffer:
            return

        lines = list(self.batch_buffer.values())
        self.batch_buffer.clear()
        await self.writer.write_batch(lines)

    async def shutdown(self) -> None:
        """Clean up all listeners and flush remaining data."""
        for unsub in self._entity_unsubs.values():
            unsub()
        self._entity_unsubs.clear()

        if self._batch_timer_unsub is not None:
            self._batch_timer_unsub()
            self._batch_timer_unsub = None

        await self._flush_batch()
        await self.writer.close()


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Victoria Metrics Exporter — parse YAML entity mappings."""
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    prefix = conf.get(CONF_METRIC_PREFIX, DEFAULT_METRIC_PREFIX)
    batch_interval = conf.get(CONF_BATCH_INTERVAL, DEFAULT_BATCH_INTERVAL)
    entities_conf = conf.get(CONF_ENTITIES, {})

    entity_configs: dict[str, EntityConfig] = {}
    for entity_id, ent_conf in entities_conf.items():
        metric_name = _build_metric_name(
            prefix, entity_id, ent_conf.get(CONF_METRIC_NAME)
        )
        entity_configs[entity_id] = EntityConfig(
            entity_id=entity_id,
            metric_name=metric_name,
            extra_tags=ent_conf.get(CONF_TAGS, {}),
            realtime=ent_conf.get(CONF_REALTIME, False),
        )

    # Store YAML config for use by async_setup_entry
    hass.data[DOMAIN]["yaml_entity_configs"] = entity_configs
    hass.data[DOMAIN]["yaml_batch_interval"] = batch_interval
    hass.data[DOMAIN]["yaml_config"] = config

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

    # Get entity configs from YAML (parsed in async_setup)
    domain_data = hass.data.setdefault(DOMAIN, {})
    entity_configs = domain_data.get("yaml_entity_configs", {})
    batch_interval = domain_data.get("yaml_batch_interval", DEFAULT_BATCH_INTERVAL)
    yaml_config = domain_data.get("yaml_config", {})

    if not entity_configs:
        _LOGGER.warning(
            "No entity mappings found in configuration.yaml under '%s'. "
            "Add entities to start exporting metrics.",
            DOMAIN,
        )

    manager = ExportManager(hass, writer, entity_configs, batch_interval)
    manager.start()

    domain_data["manager"] = manager
    domain_data["entry_id"] = entry.entry_id

    async def _shutdown(_event=None) -> None:
        await manager.shutdown()

    hass.bus.async_listen_once("homeassistant_stop", _shutdown)

    # Load sensor and switch platforms
    hass.async_create_task(
        discovery.async_load_platform(hass, "sensor", DOMAIN, {}, yaml_config)
    )
    hass.async_create_task(
        discovery.async_load_platform(hass, "switch", DOMAIN, {}, yaml_config)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    domain_data = hass.data.get(DOMAIN, {})
    manager = domain_data.get("manager")
    if manager:
        await manager.shutdown()
        domain_data.pop("manager", None)
    return True
