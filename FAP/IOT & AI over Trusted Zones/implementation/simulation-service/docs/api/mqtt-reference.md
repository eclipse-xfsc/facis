# MQTT Topic & Payload Reference

**Project:** FACIS FAP — IoT & AI Demonstrator
**Broker:** Eclipse Mosquitto (default port 1883)
**Topic Prefix:** `facis/`

---

## Topic Structure

### Smart Energy Topics

| Topic | QoS | Description |
|---|---|---|
| `facis/energy/meter/{meter_id}` | 1 | Energy meter readings (3-phase power, voltage, current) |
| `facis/energy/pv/{system_id}` | 1 | PV generation data (power, irradiance, efficiency) |
| `facis/weather/current` | 0 | Weather conditions (temperature, wind, irradiance) |
| `facis/prices/spot` | 1 | Current energy spot price |
| `facis/prices/forecast` | 1 | 24-hour price forecast |
| `facis/loads/{device_type}` | 0 | Consumer device load data |

### Smart City Topics

| Topic | QoS | Description |
|---|---|---|
| `facis/city/light/{light_id}` | 1 | Streetlight dimming and power |
| `facis/city/traffic/{zone_id}` | 0 | Zone traffic index |
| `facis/city/event/{zone_id}` | 2 | City events (accidents, emergencies) |
| `facis/city/weather` | 0 | Visibility and fog index |

### System Topics

| Topic | QoS | Description |
|---|---|---|
| `facis/simulation/status` | 1 | Simulation state changes |
| `facis/events/alerts` | 2 | System alerts and notifications |

## Payload Format

All MQTT payloads are JSON-encoded with an ISO 8601 `timestamp` field. See [Schema Reference](../data-model/schema-reference.md) for complete payload definitions.

## Configuration

MQTT publishing is configured in `config/default.yaml`:

```yaml
mqtt:
  host: "mqtt"       # Broker hostname
  port: 1883         # Broker port
  qos: 1             # Default QoS level
  topic_prefix: "facis"
```

---

© ATLAS IoT Lab GmbH — Licensed under Apache License 2.0
