"""Constants for Victoria Metrics Exporter integration."""

from homeassistant.const import Platform

DOMAIN = "victoria_metrics"

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SSL = "ssl"
CONF_VERIFY_SSL = "verify_ssl"
CONF_TOKEN = "token"
CONF_METRIC_PREFIX = "metric_prefix"
CONF_BATCH_INTERVAL = "batch_interval"
CONF_ENTITIES = "entities"
CONF_METRIC_NAME = "metric_name"
CONF_TAGS = "tags"
CONF_REALTIME = "realtime"
CONF_EXPORT_ENTITIES = "export_entities"

DEFAULT_PORT = 8428
DEFAULT_BATCH_INTERVAL = 300
DEFAULT_METRIC_PREFIX = "ha"

STATE_MAP = {
    "on": 1.0,
    "off": 0.0,
    "open": 1.0,
    "closed": 0.0,
    "home": 1.0,
    "not_home": 0.0,
    "true": 1.0,
    "false": 0.0,
    "locked": 1.0,
    "unlocked": 0.0,
    "active": 1.0,
    "inactive": 0.0,
    "yes": 1.0,
    "no": 0.0,
    "connected": 1.0,
    "disconnected": 0.0,
}
