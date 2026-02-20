# Victoria Metrics Exporter for Home Assistant

## Home Assistant

Home Assistant is an open-source home automation platform that runs on Python. It tracks the state of all devices and services in a home and provides a UI for control and automation.

### Core Architecture

Home Assistant's core consists of four interconnected components:

- **Event Bus** — Central communication channel. All components broadcast and listen for events (e.g. `state_changed`, `call_service`, `time_changed`, `homeassistant_stop`).
- **State Machine** — Maintains current state of every entity. Fires `state_changed` events when state updates. States are stored in memory and accessed synchronously.
- **Service Registry** — Registers callable services and responds to `call_service` events on the bus. Services are how automations and the UI trigger actions.
- **Timer** — Fires `time_changed` events every second, providing a heartbeat for time-based automations.

### Entity / Device / Area Model

- **Entity** — The atomic unit. Has exactly one state value (e.g. `on`, `21.5`, `open`) and optional attributes (brightness, unit_of_measurement, friendly_name, device_class). Each entity has a unique `entity_id` in the format `<domain>.<object_id>` (e.g. `sensor.living_room_temperature`).
- **Device** — A physical or logical unit containing one or more entities. Has an ID, manufacturer, model, firmware version, and is matched via identifiers or connections (serial numbers, MAC addresses).
- **Area** — A logical room grouping of devices and entities. Areas can be assigned to floors for multi-level organization.

---

## Home Assistant Integrations

Integrations extend Home Assistant with support for devices, services, and platforms. They are Python packages placed in `custom_components/<domain>/`.

### Directory Structure

```
custom_components/<domain>/
  __init__.py          # Required — main integration module
  manifest.json        # Required — integration metadata
  config_flow.py       # Optional — UI-based configuration wizard
  const.py             # Optional — shared constants
  sensor.py            # Optional — sensor entity platform
  switch.py            # Optional — switch entity platform
  binary_sensor.py     # Optional — binary sensor platform
  light.py             # Optional — light platform
  services.yaml        # Optional — service definitions
  strings.json         # Optional — UI strings
  translations/        # Optional — localized strings
    en.json
```

### manifest.json

Describes the integration. Key fields:

| Field | Description |
|---|---|
| `domain` | Unique identifier (matches directory name) |
| `name` | Display name in the UI |
| `version` | Semver version string |
| `config_flow` | `true` if the integration has a config flow UI |
| `documentation` | URL to docs |
| `issue_tracker` | URL to bug tracker |
| `codeowners` | GitHub usernames of maintainers |
| `requirements` | External PyPI packages needed at runtime |
| `dependencies` | Other HA integrations required |
| `iot_class` | How the integration communicates (see below) |

### IoT Class

Describes how data flows between HA and the external system:

| Class | Description |
|---|---|
| `local_push` | Communicates locally; device/service pushes updates to HA |
| `local_polling` | Communicates locally; HA polls for updates |
| `cloud_push` | Communicates via cloud; pushes updates |
| `cloud_polling` | Communicates via cloud; HA polls |
| `assumed_state` | Cannot determine actual state; assumes last command |
| `calculated` | Derives values from other data; no direct communication |

### Setup Lifecycle

Two entry points:

- **`async_setup(hass, config)`** — Called once on HA startup. Receives the full YAML configuration. Used for YAML-based setup or to parse YAML config before the config entry loads.
- **`async_setup_entry(hass, entry)`** — Called when a config entry is created or loaded. Receives a `ConfigEntry` with data from the config flow and options from the options flow. This is the modern approach. The function initializes clients, registers listeners, and forwards platforms via `async_forward_entry_setups()`. Paired with `async_unload_entry()` which calls `async_unload_platforms()` for clean teardown.

### Config Flow

Defined in `config_flow.py`. Subclass `ConfigFlow` and implement `async_step_user()` (and optionally other steps). Each step either shows a form (`async_show_form()`) or creates an entry (`async_create_entry()`). The flow validates input and prevents duplicates via `async_set_unique_id()`.

Config entries are persistent — they survive restarts and can be removed/reconfigured from the UI without editing YAML.

### Entity Platforms

Platform files (`sensor.py`, `switch.py`, etc.) define entity classes:

- Inherit from the domain base class (`SensorEntity`, `SwitchEntity`, etc.)
- Set `_attr_unique_id` for deduplication
- Set `_attr_name` for display
- Implement domain-specific properties (`native_value`, `is_on`, etc.)
- Optionally provide `extra_state_attributes` for additional metadata
- Optionally provide `device_info` to associate with a device

Entities are added via the `async_add_entities` callback passed to `async_setup_platform()` or `async_setup_entry()`.

### Data Fetching Patterns

- **Push model** — Subscribe to events/callbacks in `async_added_to_hass()`. Call `async_write_ha_state()` when new data arrives. Most efficient.
- **Polling model** — Set `should_poll = True` and implement `async_update()`. HA calls it periodically.
- **DataUpdateCoordinator** — Shared polling coordinator for multiple entities fetching from the same source. Manages intervals, retries, and error states.

---

## HACS (Home Assistant Community Store)

HACS is a custom integration that provides a UI for discovering, installing, and managing community-made integrations, themes, and frontend components. It works exclusively with public GitHub repositories.

### How It Works

1. HACS maintains a curated default list of repositories and allows users to add custom repos
2. It downloads repository contents into `config/custom_components/` (for integrations)
3. Version tracking uses GitHub releases (tag names set the version). Falls back to a 7-character commit hash if no releases exist
4. Users restart HA after installing to load the new integration

### Repository Requirements

To be HACS-compatible, a repository must:

- Be a public GitHub repository
- Have a descriptive README
- Have a description in GitHub repo settings
- Contain integration files in `custom_components/<DOMAIN>/`
- Have only ONE integration per repository
- Include a `hacs.json` in the repo root
- Have a `manifest.json` with required fields: `domain`, `name`, `version`, `documentation`, `issue_tracker`, `codeowners`

### hacs.json

Located at the repository root. Minimal example:

```json
{
  "name": "My Integration"
}
```

Optional fields: `content_in_root`, `zip_release`, `filename`, `hide_default_branch`, `country`, `homeassistant` (minimum HA version), `hacs` (minimum HACS version), `persistent_directory`.

### User Installation Flow

1. Install HACS as a custom integration and restart HA
2. Add HACS via Settings > Devices & Services
3. Search for an integration or add a custom repository URL
4. Click Install — HACS downloads the repo to `custom_components/`
5. Restart HA
6. Configure the new integration via Settings > Devices & Services

---

## This Repository — Victoria Metrics Exporter

Exports Home Assistant entity state changes to [Victoria Metrics](https://victoriametrics.com/) using the InfluxDB line protocol over HTTP. Supports real-time (immediate) and batch (buffered) export modes per entity.

- **Domain:** `victoria_metrics`
- **IoT Class:** `local_push`
- **Version:** 1.0.0
- **Codeowner:** @tkhduracell
- **No external Python dependencies** (uses `aiohttp` bundled with HA)

### Repository Structure

```
├── custom_components/victoria_metrics/
│   ├── __init__.py           # Core logic: setup, ExportManager, state processing
│   ├── config_flow.py        # Config flow (connection) + options flow (export settings)
│   ├── const.py              # Constants, defaults, STATE_MAP
│   ├── writer.py             # HTTP client: InfluxDB line protocol, retries
│   ├── sensor.py             # Sensor entities showing metric name per export
│   ├── switch.py             # Switch entities toggling realtime/batch per export
│   ├── manifest.json         # Integration metadata
│   ├── strings.json          # UI strings (config flow + options flow)
│   └── translations/en.json  # English translations
├── hacs.json                 # HACS metadata
├── pyproject.toml            # Ruff + MyPy configuration
└── README.md
```

### File Breakdown

#### `const.py`

Defines all configuration keys and defaults:

- Connection: `CONF_HOST`, `CONF_PORT`, `CONF_SSL`, `CONF_VERIFY_SSL`, `CONF_TOKEN`
- Export: `CONF_METRIC_PREFIX`, `CONF_BATCH_INTERVAL`, `CONF_ENTITIES`, `CONF_EXPORT_ENTITIES`
- Per-entity (YAML): `CONF_METRIC_NAME`, `CONF_TAGS`, `CONF_REALTIME`
- `PLATFORMS`: list of platforms to forward (`[Platform.SENSOR, Platform.SWITCH]`)
- Defaults: port `8428`, batch interval `300s`, metric prefix `"ha"`
- `STATE_MAP`: Maps boolean/state strings to numeric values — `on`/`off`, `open`/`closed`, `home`/`not_home`, `locked`/`unlocked`, `active`/`inactive`, `connected`/`disconnected`, `true`/`false`, `yes`/`no` → `1.0`/`0.0`

#### `__init__.py`

Core integration logic with two main classes:

**`EntityConfig`** — Stores parsed per-entity configuration: `entity_id`, `metric_name`, `extra_tags`, `realtime` flag.

**`ExportManager`** — Orchestrates state change listeners and the batch buffer:
- `start()` — Registers state change listeners (one per entity) based on mode
- `set_realtime(entity_id, bool)` — Switches an entity between modes at runtime, unsubscribes old listener, registers new one
- `_flush_batch()` — Sends all buffered lines in a single POST, clears buffer
- `shutdown()` — Unsubscribes all listeners, flushes remaining data, closes HTTP session

**Key functions:**
- `_build_metric_name(prefix, entity_id, override)` — Generates `{prefix}_{domain}_{object_id}` or uses a custom override. If prefix is empty, omits it: `{domain}_{object_id}`
- `_build_tags(entity_id, state, extra_tags)` — Produces tag dict with `entity_id`, `domain`, `friendly_name`, `device_class`, `unit`, plus custom tags
- `_process_state(state_value)` — Converts: numeric strings → float, `STATE_MAP` entries → float, unknown/unavailable → `None` (skipped), other strings → kept as text
- `_state_to_timestamp_ns(state)` — Converts `last_updated` to nanoseconds since epoch
- `_build_entity_configs_from_options(options)` — Builds `EntityConfig` dict from options flow data (entity selector list, prefix, batch interval). Returns `(entity_configs, batch_interval)`

**Setup flow:**
1. `async_setup()` parses YAML entity mappings, builds `EntityConfig` objects, stores in `hass.data[DOMAIN]` as fallback
2. `async_setup_entry()` creates `VictoriaMetricsWriter`, tests connection. Then determines entity configs: **options flow takes priority** over YAML fallback. Creates `ExportManager`, starts listeners, forwards sensor + switch platforms via `async_forward_entry_setups()`. Runtime data stored keyed by `entry.entry_id`
3. `async_unload_entry()` unloads platforms via `async_unload_platforms()`, shuts down manager, removes entry data

#### `config_flow.py`

**`VictoriaMetricsConfigFlow`** — Initial setup (connection):
- Fields: host (required), port (default 8428), SSL (default off), verify SSL (default on), bearer token (optional)
- Tests connection via `/health` endpoint before saving
- Prevents duplicates using `host:port` as unique ID
- Errors: `cannot_connect`, `unknown`
- Registers `async_get_options_flow()` to enable the options flow

**`VictoriaMetricsOptionsFlowHandler`** — Options flow for export settings (Settings > Configure):
- Extends `OptionsFlowWithConfigEntry`
- Single step (`async_step_init`) with three fields:
  - `metric_prefix` — Text input (default `"ha"`)
  - `batch_interval` — Number selector (10–3600 seconds, default 300)
  - `export_entities` — Entity selector (multi-select, picks which HA entities to export)
- Uses `add_suggested_values_to_schema()` to pre-populate with current options
- Saves to `entry.options`, which `async_setup_entry()` reads on next load

#### `writer.py`

`VictoriaMetricsWriter` — async HTTP client:

- **Endpoints:** `/write` (POST data), `/health` (GET connection test)
- **Protocol:** InfluxDB line protocol — `measurement,tag1=val1,tag2=val2 field=value timestamp_ns`
  - Numeric values: `value=21.5`
  - String values: `state_text="heating"`
  - Tags and measurements are escaped (spaces, commas, equals)
- **Auth:** Optional `Authorization: Bearer <token>` header
- **Retry logic:** Up to 3 attempts with exponential backoff (1s, 2s, 4s). Accepts HTTP 200/204. Detects 401 auth failures. 30s timeout per attempt.
- **Session:** Lazy-initialized `aiohttp.ClientSession` with configurable SSL verification

#### `sensor.py`

`VictoriaMetricsExportSensor` — One per configured entity:
- Set up via `async_setup_entry(hass, entry, async_add_entities)` (config entry pattern)
- Reads manager from `hass.data[DOMAIN][entry.entry_id]`
- State: the outgoing Victoria Metrics metric name
- Unique ID: `vm_export_{entity_id_underscored}`
- Icon: `mdi:chart-line`
- Attributes: `source_entity`, `metric_name`, `mode` (realtime/batch), `custom_tags`

#### `switch.py`

`VictoriaMetricsRealtimeSwitch` — One per configured entity:
- Set up via `async_setup_entry(hass, entry, async_add_entities)` (config entry pattern)
- Reads manager from `hass.data[DOMAIN][entry.entry_id]`
- State: ON = real-time, OFF = batch
- Unique ID: `vm_realtime_{entity_id_underscored}`
- Icon: `mdi:timer-sync-outline`
- Registers callback with `ExportManager.on_mode_change()` to sync external changes
- Calls `ExportManager.set_realtime()` on toggle

### Configuration

**Step 1: Config flow UI** — Connection settings (Settings > Devices & Services > Add Integration):

```
Host:       victoria-metrics.local
Port:       8428
SSL:        false
Verify SSL: true
Token:      (optional bearer token for vmauth)
```

**Step 2: Options flow UI** — Export settings (Settings > Devices & Services > Victoria Metrics > Configure):

```
Metric prefix:    ha               # Default: "ha"
Batch interval:   300              # 10–3600 seconds
Entities to export: [multi-select entity picker]
```

The options flow is the primary way to configure which entities are exported. Options flow data takes priority over YAML.

**YAML (configuration.yaml)** — Alternative/fallback entity mappings with advanced per-entity settings:

```yaml
victoria_metrics:
  metric_prefix: ha                # Default: "ha"
  batch_interval: 300              # Default: 300 seconds
  entities:
    sensor.living_room_temperature:
      metric_name: room_temp       # Optional override
      realtime: true               # Optional, default false
      tags:                        # Optional custom tags
        room: living_room
        floor: ground
    binary_sensor.front_door:
      tags:
        location: entrance
```

YAML config is used as a fallback when no entities are configured via the options flow. YAML provides additional per-entity settings (custom metric names, tags, realtime flag) not available in the options UI.

### Data Flow

```
Configuration:
  Options flow UI (entity selector) → entry.options
    OR YAML configuration.yaml → hass.data[DOMAIN] (fallback)
  → _build_entity_configs_from_options() or YAML parsing
  → EntityConfig objects created

Runtime:
  Entity state change
    → HA fires state_changed event
    → ExportManager listener catches event
    → _process_state() converts value (numeric, STATE_MAP, or string)
    → _build_tags() assembles tag dict
    → writer.format_line() produces InfluxDB line protocol string
    → Real-time: writer.write_single() POSTs immediately
    → Batch: stores in buffer, writer.write_batch() flushes every N seconds
```

### Export Modes

| Mode | Behavior | Latency | Efficiency |
|---|---|---|---|
| Real-time | POST on every state change | Immediate | Higher network load |
| Batch | Buffer changes, flush periodically | Up to `batch_interval` | Single POST per flush |

Users toggle modes per entity via the switch entity in the HA UI.

### CI/CD

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs:

1. **Hassfest** — Validates `manifest.json` against HA schema
2. **HACS validation** — Checks HACS repository requirements
3. **Ruff** — Linting with `ALL` rules enabled (Python 3.12, Google docstring convention)
4. **MyPy** — Strict type checking (Python 3.12)

---

## Quick Reference

```bash
# Setup dev environment (also runs automatically via conductor.json)
python3.12 -m venv .venv && .venv/bin/pip install -q -r requirements_dev.txt

# Lint
.venv/bin/ruff check custom_components/

# Format
.venv/bin/ruff format custom_components/

# Type check
.venv/bin/mypy custom_components/victoria_metrics
```

- Python target: 3.12
- Docstring convention: Google
- Ruff config: `pyproject.toml` (ALL rules with targeted ignores for HA patterns)
- MyPy config: `pyproject.toml` (strict mode with HA-specific relaxations)
