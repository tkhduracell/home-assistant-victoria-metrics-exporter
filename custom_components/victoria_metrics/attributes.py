"""Entity attribute extraction for domain-specific metrics."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import State

from .const import STATE_MAP

# Mapping of entity domain -> attribute names to extract as additional metrics.
# Each attribute becomes a separate metric line with suffix: base_metric + "_" + attr_name.
# Attributes whose runtime value is None/missing are silently skipped.
DOMAIN_ATTRIBUTES: dict[str, list[str]] = {
    "climate": [
        "current_temperature",
        "target_temperature",
        "target_temperature_high",
        "target_temperature_low",
        "current_humidity",
        "target_humidity",
        "hvac_action",
    ],
    "weather": [
        "temperature",
        "apparent_temperature",
        "humidity",
        "pressure",
        "wind_speed",
        "wind_bearing",
        "wind_gust_speed",
        "uv_index",
        "visibility",
        "dew_point",
        "cloud_coverage",
    ],
    "fan": [
        "percentage",
    ],
    "light": [
        "brightness",
        "color_temp",
        "color_temp_kelvin",
    ],
    "cover": [
        "current_position",
        "current_tilt_position",
    ],
    "humidifier": [
        "current_humidity",
        "target_humidity",
    ],
    "water_heater": [
        "current_temperature",
        "target_temperature",
    ],
    "media_player": [
        "volume_level",
        "media_position",
        "media_duration",
        "is_volume_muted",
    ],
    "vacuum": [
        "battery_level",
    ],
}


def _process_attribute(raw_value: Any) -> float | str | None:
    """Convert an attribute value to a float, mapped boolean, or string.

    Returns None for values that should be skipped.
    """
    # Booleans must be checked before int (bool is a subclass of int in Python)
    if isinstance(raw_value, bool):
        return 1.0 if raw_value else 0.0

    if isinstance(raw_value, (int, float)):
        return float(raw_value)

    if not isinstance(raw_value, str) or raw_value in ("unknown", "unavailable", ""):
        return None

    try:
        return float(raw_value)
    except (ValueError, TypeError):
        lower = raw_value.lower()
        return STATE_MAP.get(lower, raw_value)


def extract_attribute_lines(
    state: State,
    base_metric_name: str,
    tags: dict[str, str],
    timestamp_ns: int,
    format_line: Callable[[str, dict[str, str], float | str, int], str],
) -> list[str]:
    """Extract additional metric lines from entity attributes.

    Looks up the entity's domain in DOMAIN_ATTRIBUTES, converts each present
    attribute to a value, and produces an InfluxDB line protocol string per
    attribute using the caller-provided format_line function.

    Args:
        state: The HA state object with .entity_id and .attributes.
        base_metric_name: Primary metric name (e.g. "ha_thermostat").
        tags: Base tag dict shared with the primary metric line.
        timestamp_ns: Timestamp in nanoseconds since epoch.
        format_line: Writer's format_line static method.

    Returns:
        List of line protocol strings. Empty if domain has no configured
        attributes or all attribute values are None.
    """
    domain = state.entity_id.split(".", 1)[0]
    attr_names = DOMAIN_ATTRIBUTES.get(domain)
    if attr_names is None:
        return []

    lines: list[str] = []
    attrs = state.attributes

    # Drop the primary entity's unit tag — attributes may have different units.
    attr_tags = {k: v for k, v in tags.items() if k != "unit"}

    for attr_name in attr_names:
        raw_value = attrs.get(attr_name)
        value = _process_attribute(raw_value)
        if value is None:
            continue

        attr_metric_name = f"{base_metric_name}_{attr_name}"
        lines.append(format_line(attr_metric_name, attr_tags, value, timestamp_ns))

    return lines
