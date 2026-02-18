# Victoria Metrics Exporter for Home Assistant

[![CI](https://github.com/tkhduracell/home-assistant-victoria-metrics-exporter/actions/workflows/ci.yml/badge.svg)](https://github.com/tkhduracell/home-assistant-victoria-metrics-exporter/actions/workflows/ci.yml)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)

A [Home Assistant](https://www.home-assistant.io/) custom integration that exports entity state changes to [Victoria Metrics](https://victoriametrics.com/) using the InfluxDB line protocol.

## Features

- Real-time and batch export modes per entity
- Toggle between modes via switches in the HA UI
- Custom metric names and tags per entity
- InfluxDB line protocol over HTTP
- SSL/TLS and bearer token authentication
- Configurable batch interval

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

## License

MIT
