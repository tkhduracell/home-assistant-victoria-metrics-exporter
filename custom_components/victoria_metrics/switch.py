"""Switch platform for Victoria Metrics Exporter.

Creates one switch per configured entity to toggle between
real-time and batch export mode.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

if TYPE_CHECKING:
    from . import EntityConfig, ExportManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Victoria Metrics real-time mode switches from a config entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    manager: ExportManager = entry_data["manager"]
    switches = [
        VictoriaMetricsRealtimeSwitch(ec, manager)
        for ec in manager.entity_configs.values()
    ]
    async_add_entities(switches)


class VictoriaMetricsRealtimeSwitch(SwitchEntity):
    """Switch to toggle real-time export for a configured entity."""

    _attr_has_entity_name = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:timer-sync-outline"

    def __init__(self, entity_config: EntityConfig, manager: ExportManager) -> None:
        """Initialize the real-time mode switch."""
        self._ec = entity_config
        self._manager = manager
        source_object_id = entity_config.entity_id.replace(".", "_")
        self._attr_unique_id = f"vm_realtime_{source_object_id}"
        self._attr_name = f"VM Realtime: {entity_config.entity_id}"

    async def async_added_to_hass(self) -> None:
        """Register for mode change notifications when added."""
        self._manager.on_mode_change(self._handle_mode_change)

    @callback
    def _handle_mode_change(self, entity_id: str, realtime: bool) -> None:
        """Update state when mode is changed externally."""
        if entity_id == self._ec.entity_id:
            self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        """Return true if entity is in real-time mode."""
        return self._ec.realtime

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Switch entity to real-time export mode."""
        self._manager.set_realtime(self._ec.entity_id, True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Switch entity to batch export mode."""
        self._manager.set_realtime(self._ec.entity_id, False)
        self.async_write_ha_state()
