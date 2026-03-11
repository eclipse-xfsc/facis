# Configuration Reference

**Project:** FACIS FAP — IoT & AI Demonstrator
**Version:** 1.0
**Date:** 07 March 2026

---

## 1. Configuration Loading

Configuration is managed by Pydantic Settings v2. Values are resolved in priority order (highest wins):

1. Constructor parameters (passed to `Settings()`)
2. Environment variables with `SIMULATOR_` prefix
3. Environment-specific YAML file (`config/{env}.yaml`, where `env` defaults to `FACIS_ENV` or `"development"`)
4. Default YAML file (`config/default.yaml`)
5. Pydantic default values (defined in source code)

### 1.1 Environment Variable Convention

All environment variables use the prefix `SIMULATOR_` with double-underscore `__` as the nesting delimiter. Field names are case-insensitive.

```bash
# Top-level field
export SIMULATOR_SITE_ID="site-munich-001"

# Nested field (simulation.speed_factor)
export SIMULATOR_SIMULATION__SPEED_FACTOR=60.0

# Deeply nested (kafka.security_protocol)
export SIMULATOR_KAFKA__SECURITY_PROTOCOL=SSL
```

### 1.2 YAML Configuration

Place YAML files in `config/`. The file `default.yaml` is always loaded first; then `{FACIS_ENV}.yaml` (e.g., `development.yaml`, `cluster.yaml`) is deep-merged on top. Lists in the environment file replace (not merge with) lists in the default file.

```yaml
# config/default.yaml
site_id: "site-berlin-001"
simulation:
  seed: 12345
  interval_minutes: 1
mqtt:
  host: "localhost"
  port: 1883
```

---

## 2. Global Settings

| Field | Type | Default | Env Var | Description |
|---|---|---|---|---|
| `site_id` | string | `"site-berlin-001"` | `SIMULATOR_SITE_ID` | Logical site identifier shared by all feeds for cross-correlation. Min length 1. |

---

## 3. Simulation Settings

Section: `simulation`

| Field | Type | Default | Range | Env Var | Description |
|---|---|---|---|---|---|
| `seed` | int | `12345` | ≥ 0 | `SIMULATOR_SIMULATION__SEED` | Random seed for reproducibility. Same seed → identical output. |
| `interval_minutes` | int | `1` | 1–60 | `SIMULATOR_SIMULATION__INTERVAL_MINUTES` | Time between simulation ticks. |
| `start_time` | string (ISO 8601) | `null` | — | `SIMULATOR_SIMULATION__START_TIME` | Simulation start time. Null = use current wall-clock time. |
| `speed_factor` | float | `1.0` | 0.1–1000 | `SIMULATOR_SIMULATION__SPEED_FACTOR` | Time acceleration. 1.0 = real-time, 60.0 = 1 hour per minute. |
| `mode` | string | `"normal"` | `normal`, `event` | `SIMULATOR_SIMULATION__MODE` | Simulation mode. `event` triggers special scenarios. |

---

## 4. Meter Configuration

Section: `meters` (list)

Each entry configures one energy meter simulator. Default: one meter (`meter-001`).

| Field | Type | Default | Range | Description |
|---|---|---|---|---|
| `id` | string | — (required) | min 1 char | Unique meter identifier. |
| `base_load_kw` | float | `10.0` | ≥ 0 | Base load power (kW). Must be ≤ `peak_load_kw`. |
| `peak_load_kw` | float | `25.0` | ≥ 0 | Peak load power (kW). Must be ≥ `base_load_kw`. |
| `nominal_voltage_v` | float | `230.0` | 100–500 | Phase-to-neutral nominal voltage (V). |
| `voltage_variance_pct` | float | `5.0` | 0–15 | Voltage variance as percentage of nominal. |
| `nominal_frequency_hz` | float | `50.0` | 45–65 | Grid frequency (Hz). |
| `frequency_variance_hz` | float | `0.05` | 0–1 | Frequency variance (Hz). |
| `power_factor_min` | float | `0.95` | 0.5–1.0 | Minimum power factor. Must be ≤ `power_factor_max`. |
| `power_factor_max` | float | `0.99` | 0.5–1.0 | Maximum power factor. |
| `initial_energy_kwh` | float | `0.0` | ≥ 0 | Initial cumulative energy counter (kWh). |

**YAML example (two meters):**

```yaml
meters:
  - id: "meter-001"
    base_load_kw: 10.0
    peak_load_kw: 25.0
  - id: "meter-002"
    base_load_kw: 5.0
    peak_load_kw: 15.0
    nominal_voltage_v: 400.0   # 3-phase 400V system
```

---

## 5. PV System Configuration

Section: `pv_systems` (list)

Each entry configures one PV generation simulator. Default: one system (`pv-system-001`).

| Field | Type | Default | Range | Description |
|---|---|---|---|---|
| `id` | string | — (required) | min 1 char | Unique PV system identifier. |
| `nominal_capacity_kw` | float | `10.0` | 0.1–10000 | Nameplate capacity (kWp). |
| `losses` | float | `0.15` | 0–0.5 | System losses fraction (0.15 = 15% losses). |
| `temperature_coefficient` | float | `-0.004` | ≤ 0 | Power derating per °C above reference. |
| `reference_temperature_c` | float | `25.0` | 0–50 | STC reference temperature (°C). |
| `azimuth_deg` | float | `180.0` | 0–360 | Panel azimuth (180 = south). |
| `tilt_deg` | float | `35.0` | 0–90 | Panel tilt from horizontal (degrees). |
| `latitude` | float | `52.52` | -90 to 90 | Installation latitude (decimal degrees). |
| `longitude` | float | `13.405` | -180 to 180 | Installation longitude (decimal degrees). |

---

## 6. Consumer Device Configuration

Section: `consumers` (list)

Each entry configures one industrial device simulator. Default: two devices (oven-001, hvac-001).

| Field | Type | Default | Range | Description |
|---|---|---|---|---|
| `id` | string | — (required) | min 1 char | Unique device identifier. |
| `rated_power_kw` | float | `3.0` | 0–1000 | Rated power draw when ON (kW). |
| `duty_cycle` | float | `0.7` | 0–1.0 | Fraction of operating time the device is ON. |
| `device_type` | string | `"generic"` | see below | Device classification. |
| `power_variance_pct` | float | `5.0` | 0–30 | Power variance when ON (%). |
| `operating_windows` | list | 3 windows | — | Time windows when device may operate. |
| `operate_on_weekends` | bool | `false` | — | Whether device runs on weekends. |

**Device types:** `industrial_oven`, `hvac`, `compressor`, `pump`, `generic`.

**Operating window fields:** `start_hour` (0–23), `end_hour` (0–23).

**YAML example:**

```yaml
consumers:
  - id: "oven-001"
    rated_power_kw: 3.5
    device_type: "industrial_oven"
    duty_cycle: 0.7
    operating_windows:
      - start_hour: 7
        end_hour: 9
      - start_hour: 11
        end_hour: 13
      - start_hour: 15
        end_hour: 17
  - id: "hvac-001"
    rated_power_kw: 2.0
    device_type: "hvac"
    duty_cycle: 0.6
    operate_on_weekends: true
    operating_windows:
      - start_hour: 6
        end_hour: 22
```

---

## 7. Smart City Configuration

Section: `smart_city`

| Field | Type | Default | Description |
|---|---|---|---|
| `city_id` | string | `"city-berlin"` | City identifier. |
| `latitude` | float | `52.52` | City latitude. |
| `longitude` | float | `13.405` | City longitude. |
| `zones` | list | 2 zones | Zone configuration (see below). |

**Zone fields:** `id` (required), `lights` (list of streetlight configs).

**Streetlight fields:** `id` (required), `rated_power_w` (default 150.0, ≥ 0).

---

## 8. Transport Configuration

### 8.1 MQTT

Section: `mqtt`

| Field | Type | Default | Range | Env Var | Description |
|---|---|---|---|---|---|
| `host` | string | `"localhost"` | — | `SIMULATOR_MQTT__HOST` | Broker hostname or IP. |
| `port` | int | `1883` | 1–65535 | `SIMULATOR_MQTT__PORT` | Broker port. |
| `client_id` | string | `"facis-simulator"` | — | `SIMULATOR_MQTT__CLIENT_ID` | Client identifier. |
| `qos` | int | `1` | 0–2 | `SIMULATOR_MQTT__QOS` | MQTT QoS level. |
| `username` | string | `null` | — | `SIMULATOR_MQTT__USERNAME` | Authentication username. |
| `password` | string | `null` | — | `SIMULATOR_MQTT__PASSWORD` | Authentication password. |

### 8.2 Kafka

Section: `kafka`

| Field | Type | Default | Env Var | Description |
|---|---|---|---|---|
| `bootstrap_servers` | string | `"localhost:9092"` | `SIMULATOR_KAFKA__BOOTSTRAP_SERVERS` | Bootstrap servers (comma-separated). |
| `client_id` | string | `"facis-simulator"` | `SIMULATOR_KAFKA__CLIENT_ID` | Producer client identifier. |
| `enabled` | bool | `true` | `SIMULATOR_KAFKA__ENABLED` | Enable/disable Kafka publishing. |
| `security_protocol` | string | `"PLAINTEXT"` | `SIMULATOR_KAFKA__SECURITY_PROTOCOL` | `PLAINTEXT` or `SSL`. |
| `ssl_ca_location` | string | `null` | `SIMULATOR_KAFKA__SSL_CA_LOCATION` | Path to CA cert (for SSL). |
| `ssl_certificate_location` | string | `null` | `SIMULATOR_KAFKA__SSL_CERTIFICATE_LOCATION` | Path to client cert (for SSL). |
| `ssl_key_location` | string | `null` | `SIMULATOR_KAFKA__SSL_KEY_LOCATION` | Path to client key (for SSL). |

### 8.3 ORCE

Section: `orce`

| Field | Type | Default | Range | Env Var | Description |
|---|---|---|---|---|---|
| `url` | string | `"http://localhost:1880"` | — | `SIMULATOR_ORCE__URL` | ORCE base URL. |
| `webhook_path` | string | `"/api/sim/tick"` | — | `SIMULATOR_ORCE__WEBHOOK_PATH` | Webhook endpoint path. |
| `enabled` | bool | `false` | — | `SIMULATOR_ORCE__ENABLED` | Enable/disable ORCE publishing. |
| `timeout_seconds` | float | `10.0` | 1–60 | `SIMULATOR_ORCE__TIMEOUT_SECONDS` | HTTP request timeout. |

### 8.4 HTTP Server

Section: `http`

| Field | Type | Default | Env Var | Description |
|---|---|---|---|---|
| `host` | string | `"0.0.0.0"` | `SIMULATOR_HTTP__HOST` | Bind address. |
| `port` | int | `8080` | `SIMULATOR_HTTP__PORT` | Listen port. |

### 8.5 Modbus TCP

Section: `modbus`

| Field | Type | Default | Env Var | Description |
|---|---|---|---|---|
| `host` | string | `"0.0.0.0"` | `SIMULATOR_MODBUS__HOST` | Bind address. |
| `port` | int | `502` | `SIMULATOR_MODBUS__PORT` | Listen port. |

---

## 9. Logging

Section: `logging`

| Field | Type | Default | Env Var | Description |
|---|---|---|---|---|
| `level` | string | `"INFO"` | `SIMULATOR_LOGGING__LEVEL` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |
| `format` | string | `"%(asctime)s - ..."` | `SIMULATOR_LOGGING__FORMAT` | Python log format string. |

---

## 10. Complete YAML Example

```yaml
# config/default.yaml — Full configuration reference
site_id: "site-berlin-001"

simulation:
  seed: 12345
  interval_minutes: 1
  speed_factor: 1.0
  mode: "normal"

meters:
  - id: "meter-001"
    base_load_kw: 10.0
    peak_load_kw: 25.0
    nominal_voltage_v: 230.0
    voltage_variance_pct: 5.0
    nominal_frequency_hz: 50.0
    frequency_variance_hz: 0.05
    power_factor_min: 0.95
    power_factor_max: 0.99
    initial_energy_kwh: 0.0

pv_systems:
  - id: "pv-system-001"
    nominal_capacity_kw: 10.0
    losses: 0.15
    temperature_coefficient: -0.004
    reference_temperature_c: 25.0

consumers:
  - id: "oven-001"
    rated_power_kw: 3.5
    device_type: "industrial_oven"
    duty_cycle: 0.7
    operating_windows:
      - { start_hour: 7, end_hour: 9 }
      - { start_hour: 11, end_hour: 13 }
      - { start_hour: 15, end_hour: 17 }
  - id: "hvac-001"
    rated_power_kw: 2.0
    device_type: "hvac"
    duty_cycle: 0.6

mqtt:
  host: "localhost"
  port: 1883
  qos: 1

kafka:
  bootstrap_servers: "localhost:9092"
  enabled: true
  security_protocol: "PLAINTEXT"

orce:
  url: "http://localhost:1880"
  enabled: false

http:
  host: "0.0.0.0"
  port: 8080

modbus:
  host: "0.0.0.0"
  port: 502

logging:
  level: "INFO"
```

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
