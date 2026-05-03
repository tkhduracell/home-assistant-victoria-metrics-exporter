"""WebSocket API for Victoria Metrics panel."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
import voluptuous as vol

from .const import (
    CONF_BATCH_INTERVAL,
    CONF_ENTITY_SETTINGS,
    CONF_EXPORT_ENTITIES,
    CONF_HOST,
    CONF_METRIC_PREFIX,
    CONF_PORT,
    CONF_SOURCES,
    CONF_SSL,
    CONF_TOKEN,
    CONF_VERIFY_SSL,
    DEFAULT_BATCH_INTERVAL,
    DEFAULT_METRIC_PREFIX,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    build_metric_name,
)
from .reader import VictoriaMetricsReader

if TYPE_CHECKING:
    from . import ExportManager

_LOGGER = logging.getLogger(__name__)

SOURCE_OPTIONAL_FIELDS = (
    "unit_of_measurement",
    "device_class",
    "state_class",
    "icon",
)

SOURCE_SCHEMA_FIELDS: dict[Any, Any] = {
    vol.Required("name"): str,
    vol.Required("query"): str,
    vol.Optional("scan_interval"): vol.All(int, vol.Range(min=5, max=86400)),
    vol.Optional("unit_of_measurement"): vol.Any(str, None),
    vol.Optional("device_class"): vol.Any(str, None),
    vol.Optional("state_class"): vol.Any(str, None),
    vol.Optional("icon"): vol.Any(str, None),
}


def _get_config_entry(hass: HomeAssistant) -> ConfigEntry | None:
    """Get the first Victoria Metrics config entry."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return None
    return entries[0]


def async_register_websocket_commands(hass: HomeAssistant) -> None:
    """Register WebSocket commands for the Victoria Metrics panel."""
    websocket_api.async_register_command(hass, handle_get_config)
    websocket_api.async_register_command(hass, handle_save_entities)
    websocket_api.async_register_command(hass, handle_update_entity_settings)
    websocket_api.async_register_command(hass, handle_get_audit_log)
    websocket_api.async_register_command(hass, handle_add_entity)
    websocket_api.async_register_command(hass, handle_remove_entity)
    websocket_api.async_register_command(hass, handle_get_sources)
    websocket_api.async_register_command(hass, handle_add_source)
    websocket_api.async_register_command(hass, handle_update_source)
    websocket_api.async_register_command(hass, handle_remove_source)
    websocket_api.async_register_command(hass, handle_test_source)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "victoria_metrics/get_config",
    }
)
@callback
def handle_get_config(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the current Victoria Metrics export configuration."""
    entry = _get_config_entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "No config entry found")
        return

    prefix = entry.options.get(CONF_METRIC_PREFIX, DEFAULT_METRIC_PREFIX)
    batch_interval = entry.options.get(CONF_BATCH_INTERVAL, DEFAULT_BATCH_INTERVAL)
    entities: list[str] = entry.options.get(CONF_EXPORT_ENTITIES, [])
    entity_settings: dict[str, dict[str, Any]] = entry.options.get(
        CONF_ENTITY_SETTINGS, {}
    )

    previews: list[dict[str, Any]] = []
    for entity_id in entities:
        settings = entity_settings.get(entity_id, {})
        metric_name_override: str = settings.get("metric_name", "")
        previews.append(
            {
                "entity_id": entity_id,
                "metric_name": build_metric_name(
                    prefix, entity_id, metric_name_override or None
                ),
                "metric_name_override": metric_name_override,
                "batch_interval": settings.get("batch_interval", batch_interval),
            }
        )

    connection.send_result(
        msg["id"],
        {
            "entry_id": entry.entry_id,
            "metric_prefix": prefix,
            "batch_interval": batch_interval,
            "entities": previews,
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "victoria_metrics/save_entities",
        vol.Required("entities"): [str],
    }
)
@websocket_api.async_response
async def handle_save_entities(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update the exported entities list and reload."""
    entry = _get_config_entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "No config entry found")
        return

    new_entities: list[str] = msg["entities"]

    # Merge with existing options, updating only the entities list
    new_options = dict(entry.options)
    new_options[CONF_EXPORT_ENTITIES] = new_entities

    hass.config_entries.async_update_entry(entry, options=new_options)
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "victoria_metrics/update_entity_settings",
        vol.Required("entity_id"): str,
        vol.Optional("batch_interval"): vol.All(int, vol.Range(min=10, max=3600)),
        vol.Optional("metric_name"): vol.Any(str, None),
    }
)
@websocket_api.async_response
async def handle_update_entity_settings(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update per-entity settings and apply at runtime without reload."""
    entry = _get_config_entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "No config entry found")
        return

    entity_id: str = msg["entity_id"]
    entities: list[str] = entry.options.get(CONF_EXPORT_ENTITIES, [])
    if entity_id not in entities:
        connection.send_error(msg["id"], "not_found", "Entity not in export list")
        return

    # Build updated entity_settings dict
    new_options = dict(entry.options)
    entity_settings: dict[str, dict[str, Any]] = dict(
        new_options.get(CONF_ENTITY_SETTINGS, {})
    )
    current = dict(entity_settings.get(entity_id, {}))

    if "batch_interval" in msg:
        current["batch_interval"] = msg["batch_interval"]
    if "metric_name" in msg:
        if msg["metric_name"]:
            current["metric_name"] = msg["metric_name"]
        else:
            current.pop("metric_name", None)

    entity_settings[entity_id] = current
    new_options[CONF_ENTITY_SETTINGS] = entity_settings

    # Persist to config entry options (survives restart)
    hass.config_entries.async_update_entry(entry, options=new_options)

    # Apply at runtime without reload
    domain_data = hass.data.get(DOMAIN, {})
    entry_data = domain_data.get(entry.entry_id)
    if entry_data:
        manager: ExportManager = entry_data["manager"]
        if "batch_interval" in msg:
            manager.set_batch_interval(entity_id, msg["batch_interval"])
        if "metric_name" in msg:
            prefix = entry.options.get(CONF_METRIC_PREFIX, DEFAULT_METRIC_PREFIX)
            override = msg["metric_name"] or None
            new_name = build_metric_name(prefix, entity_id, override)
            manager.set_metric_name(entity_id, new_name)

    connection.send_result(msg["id"], {"success": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "victoria_metrics/get_audit_log",
        vol.Optional("limit", default=50): vol.All(int, vol.Range(min=1, max=200)),
    }
)
@callback
def handle_get_audit_log(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return recent export audit log entries."""
    entry = _get_config_entry(hass)
    if entry is None:
        connection.send_result(msg["id"], {"entries": []})
        return

    domain_data = hass.data.get(DOMAIN, {})
    entry_data = domain_data.get(entry.entry_id)
    if not entry_data:
        connection.send_result(msg["id"], {"entries": []})
        return

    manager: ExportManager = entry_data["manager"]
    entries = manager.get_audit_log(limit=msg.get("limit", 50))
    connection.send_result(msg["id"], {"entries": entries})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "victoria_metrics/add_entity",
        vol.Required("entity_id"): str,
    }
)
@websocket_api.async_response
async def handle_add_entity(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add a single entity to the export list and reload."""
    entry = _get_config_entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "No config entry found")
        return

    entity_id: str = msg["entity_id"]
    entities: list[str] = list(entry.options.get(CONF_EXPORT_ENTITIES, []))

    if entity_id in entities:
        connection.send_result(msg["id"], {"success": True, "already_tracked": True})
        return

    entities.append(entity_id)
    new_options = dict(entry.options)
    new_options[CONF_EXPORT_ENTITIES] = entities

    hass.config_entries.async_update_entry(entry, options=new_options)
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True, "already_tracked": False})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "victoria_metrics/remove_entity",
        vol.Required("entity_id"): str,
    }
)
@websocket_api.async_response
async def handle_remove_entity(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove a single entity from the export list and reload."""
    entry = _get_config_entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "No config entry found")
        return

    entity_id: str = msg["entity_id"]
    entities: list[str] = list(entry.options.get(CONF_EXPORT_ENTITIES, []))

    if entity_id not in entities:
        connection.send_result(msg["id"], {"success": True, "was_tracked": False})
        return

    entities.remove(entity_id)
    new_options = dict(entry.options)
    new_options[CONF_EXPORT_ENTITIES] = entities

    # Clean up per-entity settings for the removed entity
    entity_settings: dict[str, dict[str, Any]] = dict(
        new_options.get(CONF_ENTITY_SETTINGS, {})
    )
    entity_settings.pop(entity_id, None)
    new_options[CONF_ENTITY_SETTINGS] = entity_settings

    hass.config_entries.async_update_entry(entry, options=new_options)
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True, "was_tracked": True})


# ---------------------------------------------------------------------------
# Source sensors (read-from-Victoria-Metrics) CRUD
# ---------------------------------------------------------------------------


def _normalize_source_input(
    msg: dict[str, Any], existing_id: str | None = None
) -> dict[str, Any]:
    """Build a normalized source dict from a websocket message."""
    src: dict[str, Any] = {
        "id": existing_id or uuid4().hex,
        "name": msg["name"],
        "query": msg["query"],
        "scan_interval": int(msg.get("scan_interval", DEFAULT_SCAN_INTERVAL)),
    }
    for field in SOURCE_OPTIONAL_FIELDS:
        value = msg.get(field)
        if value:
            src[field] = value
    return src


@websocket_api.websocket_command(
    {
        vol.Required("type"): "victoria_metrics/get_sources",
    }
)
@callback
def handle_get_sources(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return the list of configured Victoria Metrics source sensors."""
    entry = _get_config_entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "No config entry found")
        return

    sources: list[dict[str, Any]] = list(entry.options.get(CONF_SOURCES, []))
    connection.send_result(msg["id"], {"sources": sources})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "victoria_metrics/add_source",
        **SOURCE_SCHEMA_FIELDS,
    }
)
@websocket_api.async_response
async def handle_add_source(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Add a new Victoria Metrics source sensor and reload."""
    entry = _get_config_entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "No config entry found")
        return

    sources: list[dict[str, Any]] = list(entry.options.get(CONF_SOURCES, []))
    if any(s.get("name") == msg["name"] for s in sources):
        connection.send_error(
            msg["id"],
            "duplicate_name",
            f"A source named {msg['name']!r} already exists",
        )
        return

    new_source = _normalize_source_input(msg)
    sources.append(new_source)

    new_options = dict(entry.options)
    new_options[CONF_SOURCES] = sources
    hass.config_entries.async_update_entry(entry, options=new_options)
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True, "source": new_source})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "victoria_metrics/update_source",
        vol.Required("id"): str,
        **SOURCE_SCHEMA_FIELDS,
    }
)
@websocket_api.async_response
async def handle_update_source(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Update an existing source by id and reload."""
    entry = _get_config_entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "No config entry found")
        return

    source_id: str = msg["id"]
    sources: list[dict[str, Any]] = list(entry.options.get(CONF_SOURCES, []))
    target_index = next(
        (i for i, s in enumerate(sources) if s.get("id") == source_id), None
    )
    if target_index is None:
        connection.send_error(msg["id"], "not_found", "Source not found")
        return

    if any(s.get("name") == msg["name"] and s.get("id") != source_id for s in sources):
        connection.send_error(
            msg["id"],
            "duplicate_name",
            f"A source named {msg['name']!r} already exists",
        )
        return

    updated = _normalize_source_input(msg, existing_id=source_id)
    sources[target_index] = updated

    new_options = dict(entry.options)
    new_options[CONF_SOURCES] = sources
    hass.config_entries.async_update_entry(entry, options=new_options)
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True, "source": updated})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "victoria_metrics/remove_source",
        vol.Required("id"): str,
    }
)
@websocket_api.async_response
async def handle_remove_source(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Remove a source by id and reload."""
    entry = _get_config_entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "No config entry found")
        return

    source_id: str = msg["id"]
    sources: list[dict[str, Any]] = list(entry.options.get(CONF_SOURCES, []))
    new_sources = [s for s in sources if s.get("id") != source_id]
    if len(new_sources) == len(sources):
        connection.send_result(msg["id"], {"success": True, "was_present": False})
        return

    new_options = dict(entry.options)
    new_options[CONF_SOURCES] = new_sources
    hass.config_entries.async_update_entry(entry, options=new_options)
    await hass.config_entries.async_reload(entry.entry_id)

    connection.send_result(msg["id"], {"success": True, "was_present": True})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "victoria_metrics/test_source",
        vol.Required("query"): str,
    }
)
@websocket_api.async_response
async def handle_test_source(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Run a one-shot Victoria Metrics query and return the result."""
    entry = _get_config_entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "No config entry found")
        return

    reader = VictoriaMetricsReader(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        ssl=entry.data.get(CONF_SSL, False),
        verify_ssl=entry.data.get(CONF_VERIFY_SSL, True),
        token=entry.data.get(CONF_TOKEN) or None,
    )
    try:
        result = await reader.query_instant(msg["query"])
    finally:
        await reader.close()

    if result is None:
        connection.send_result(
            msg["id"], {"success": False, "reason": "no_data_or_error"}
        )
        return

    value, labels, timestamp_s = result
    connection.send_result(
        msg["id"],
        {
            "success": True,
            "value": value,
            "labels": labels,
            "timestamp": timestamp_s,
        },
    )
