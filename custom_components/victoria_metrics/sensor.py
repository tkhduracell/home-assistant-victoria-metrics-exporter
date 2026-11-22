"""Sensor platform for Victoria Metrics integration.

Provides two kinds of sensor:

1. Export-mapping sensors — one per configured export entity; show the
   outgoing VM metric name and current export settings.
2. Source sensors — one per configured Victoria Metrics source; expose the
   latest value point of a PromQL/MetricsQL query as the sensor's state,
   polled by a per-source DataUpdateCoordinator.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util import slugify

from .const import DOMAIN

if TYPE_CHECKING:
    from . import EntityConfig, ExportManager, SourceCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Victoria Metrics sensor entities from a config entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    manager: ExportManager = entry_data["manager"]

    sensors: list[SensorEntity] = [
        VictoriaMetricsExportSensor(ec, manager)
        for ec in manager.entity_configs.values()
    ]

    source_configs: list[dict[str, Any]] = entry_data.get("source_configs", [])
    coordinators: dict[str, SourceCoordinator] = entry_data.get(
        "source_coordinators", {}
    )
    for src in source_configs:
        source_id = src.get("id")
        if not source_id:
            continue
        coordinator = coordinators.get(source_id)
        if coordinator is None:
            continue
        sensors.append(VictoriaMetricsSourceSensor(coordinator, src))

    async_add_entities(sensors)


class VictoriaMetricsExportSensor(SensorEntity):
    """Sensor showing the outgoing VM metric name for a configured entity."""

    _attr_has_entity_name = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC
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
            "batch_interval": self._ec.batch_interval,
        }


class VictoriaMetricsSourceSensor(
    CoordinatorEntity[DataUpdateCoordinator[dict[str, Any] | None]], SensorEntity
):
    """Sensor whose state is the latest value of a Victoria Metrics query."""

    _attr_has_entity_name = False

    def __init__(
        self,
        coordinator: SourceCoordinator,
        source_config: dict[str, Any],
    ) -> None:
        """Initialize the source sensor."""
        super().__init__(coordinator)
        name = str(source_config.get("name") or source_config["id"])
        self._query = str(source_config["query"])
        self._attr_name = name
        self._attr_unique_id = f"vm_source_{slugify(source_config['id'])}"

        if unit := source_config.get("unit_of_measurement"):
            self._attr_native_unit_of_measurement = unit
        if device_class := source_config.get("device_class"):
            self._attr_device_class = device_class
        if state_class := source_config.get("state_class"):
            self._attr_state_class = state_class
        if icon := source_config.get("icon"):
            self._attr_icon = icon
        elif not source_config.get("device_class"):
            self._attr_icon = "mdi:database-search"

    @property
    def native_value(self) -> float | None:
        """Return the latest queried value, or None when unavailable."""
        data = self.coordinator.data
        if not data:
            return None
        value = data.get("value")
        return value if isinstance(value, (int, float)) else None

    @property
    def available(self) -> bool:
        """Sensor is available only when the last poll succeeded with data."""
        return (
            self.coordinator.last_update_success and self.coordinator.data is not None
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose query, matched series labels, and value timestamp."""
        attrs: dict[str, Any] = {"query": self._query}
        data = self.coordinator.data
        if data:
            attrs["labels"] = data.get("labels", {})
            attrs["last_value_timestamp"] = data.get("timestamp")
        return attrs
