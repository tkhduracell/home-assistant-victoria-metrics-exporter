"""WebSocket API for Victoria Metrics panel."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
import voluptuous as vol

from .const import (
    CONF_BATCH_INTERVAL,
    CONF_EXPORT_ENTITIES,
    CONF_METRIC_PREFIX,
    DEFAULT_BATCH_INTERVAL,
    DEFAULT_METRIC_PREFIX,
    DOMAIN,
    build_metric_name,
)

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

    previews: list[dict[str, str]] = [
        {
            "entity_id": entity_id,
            "metric_name": build_metric_name(prefix, entity_id),
        }
        for entity_id in entities
    ]

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
