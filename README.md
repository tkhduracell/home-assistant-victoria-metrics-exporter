# Victoria Metrics Exporter for Home Assistant

[![CI](https://github.com/tkhduracell/home-assistant-victoria-metrics-exporter/actions/workflows/ci.yml/badge.svg)](https://github.com/tkhduracell/home-assistant-victoria-metrics-exporter/actions/workflows/ci.yml)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)

A [Home Assistant](https://www.home-assistant.io/) custom integration for [Victoria Metrics](https://victoriametrics.com/). Exports HA entity state to VM (InfluxDB line protocol) **and** reads VM series back as HA sensor entities.

## Features

- Real-time and batch export modes per entity
- Toggle between modes via switches in the HA UI
- Custom metric names and tags per entity
- InfluxDB line protocol over HTTP
- SSL/TLS and bearer token authentication
- Configurable batch interval
- **Source sensors:** define HA sensors backed by a Victoria Metrics PromQL/MetricsQL query — the latest value point becomes the sensor's state

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Victoria Metrics Exporter" and install
3. Restart Home Assistant

### Manual

Copy the `custom_components/victoria_metrics` directory to your Home Assistant `custom_components` folder.

## Configuration

### Connection (UI)

Add the integration via **Settings > Devices & Services > Add Integration > Victoria Metrics Exporter**.

Configure host, port, SSL, and optional bearer token.

### Entity mappings (YAML)

```yaml
victoria_metrics:
  metric_prefix: hass
  batch_interval: 300
  entities:
    sensor.temperature:
      metric_name: room_temperature
      realtime: true
      tags:
        room: living_room
    sensor.humidity:
      tags:
        room: living_room
```

## Source sensors (read from Victoria Metrics)

Define HA sensor entities whose state is the latest value point of a Victoria Metrics query. Each source is polled at its own `scan_interval` (default 60 seconds) via VM's `/api/v1/query` endpoint. The result is exposed as a regular HA sensor with `query`, matched series `labels`, and `last_value_timestamp` as attributes; when the query returns an empty vector or fails, the sensor goes `unavailable`.

Sources are managed via WebSocket commands (see below). A panel UI for source management will follow in a later release.

### WebSocket commands

| Command | Purpose |
|---|---|
| `victoria_metrics/get_sources` | List all configured sources |
| `victoria_metrics/add_source` | Add a new source |
| `victoria_metrics/update_source` | Edit an existing source by `id` |
| `victoria_metrics/remove_source` | Remove a source by `id` |
| `victoria_metrics/test_source` | Run a query once and return the result without saving |

Source fields: required `name` and `query`; optional `scan_interval` (5–86400s, default 60), `unit_of_measurement`, `device_class`, `state_class`, `icon`. The `id` is generated server-side on `add_source`.

### Example: add a source from Developer Tools

In the Home Assistant UI go to **Developer Tools → Services**, then run a quick test from the **Template** editor or use the websocket via your browser console / [HA WebSocket API tools](https://developers.home-assistant.io/docs/api/websocket/):

```js
// Add a 5-minute average kitchen temperature
await hass.callWS({
  type: "victoria_metrics/add_source",
  name: "Kitchen Avg Temp 5m",
  query: 'avg_over_time(ha_kitchen_temp[5m])',
  scan_interval: 60,
  unit_of_measurement: "°C",
  device_class: "temperature",
  state_class: "measurement",
});

// List all sources
await hass.callWS({ type: "victoria_metrics/get_sources" });

// Test a query without saving anything
await hass.callWS({
  type: "victoria_metrics/test_source",
  query: 'sum(ha_power)',
});
```

After adding a source you'll see a new sensor entity (e.g. `sensor.kitchen_avg_temp_5m`) populated with the latest value.

## License

MIT
