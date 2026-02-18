"""Sensor platform for Victoria Metrics Exporter.

Creates one sensor entity per configured export so users can see
all entity-to-metric mappings in the HA UI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

if TYPE_CHECKING:
    from . import EntityConfig, ExportManager


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up Victoria Metrics export mapping sensors."""
    if discovery_info is None:
        return

    data = hass.data.get(DOMAIN)
    if data is None:
        return

    manager: ExportManager = data["manager"]
    sensors = [
        VictoriaMetricsExportSensor(ec, manager)
        for ec in manager.entity_configs.values()
    ]
    async_add_entities(sensors)


class VictoriaMetricsExportSensor(SensorEntity):
    """Sensor showing the outgoing VM metric name for a configured entity."""

    _attr_has_entity_name = False
    _attr_icon = "mdi:chart-line"

    def __init__(self, entity_config: EntityConfig, manager: ExportManager) -> None:
        """Initialize the export mapping sensor."""
        self._ec = entity_config
        self._manager = manager
        source_object_id = entity_config.entity_id.replace(".", "_")
        self._attr_unique_id = f"vm_export_{source_object_id}"
        self._attr_name = f"VM Export: {entity_config.entity_id}"

    @property
    def native_value(self) -> str:
        """Return the outgoing metric name."""
        return self._ec.metric_name

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return details about this export mapping."""
        return {
            "source_entity": self._ec.entity_id,
            "metric_name": self._ec.metric_name,
            "mode": "realtime" if self._ec.realtime else "batch",
            "custom_tags": self._ec.extra_tags,
        }
