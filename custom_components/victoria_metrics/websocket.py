"""WebSocket API for Victoria Metrics panel."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
import voluptuous as vol

from .const import (
    CONF_BATCH_INTERVAL,
    CONF_ENTITY_SETTINGS,
    CONF_EXPORT_ENTITIES,
    CONF_METRIC_PREFIX,
    DEFAULT_BATCH_INTERVAL,
    DEFAULT_METRIC_PREFIX,
    DOMAIN,
    build_metric_name,
)

if TYPE_CHECKING:
    from . import ExportManager

_LOGGER = logging.getLogger(__name__)


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
        previews.append(
            {
                "entity_id": entity_id,
                "metric_name": build_metric_name(prefix, entity_id),
                "realtime": settings.get("realtime", False),
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
        vol.Optional("realtime"): bool,
        vol.Optional("batch_interval"): vol.All(int, vol.Range(min=10, max=3600)),
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

    if "realtime" in msg:
        current["realtime"] = msg["realtime"]
    if "batch_interval" in msg:
        current["batch_interval"] = msg["batch_interval"]

    entity_settings[entity_id] = current
    new_options[CONF_ENTITY_SETTINGS] = entity_settings

    # Persist to config entry options (survives restart)
    hass.config_entries.async_update_entry(entry, options=new_options)

    # Apply at runtime without reload
    domain_data = hass.data.get(DOMAIN, {})
    entry_data = domain_data.get(entry.entry_id)
    if entry_data:
        manager: ExportManager = entry_data["manager"]
        if "realtime" in msg:
            manager.set_realtime(entity_id, msg["realtime"])
        if "batch_interval" in msg:
            manager.set_batch_interval(entity_id, msg["batch_interval"])

    connection.send_result(msg["id"], {"success": True})
