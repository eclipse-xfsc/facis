# Data Schema Reference

**Project:** FACIS FAP — IoT & AI Demonstrator
**Version:** 1.0
**Date:** 07 March 2026

---

## 1. Overview

The simulation service produces 9 data feeds organized into two domains. All payloads are JSON-encoded with an ISO 8601 `timestamp` field (UTC, `Z` suffix). Each feed includes a `schema_version` field for forward compatibility.

### Feed Inventory

| Domain | Feed | Kafka Topic | Key Field |
|---|---|---|---|
| Smart Energy | Energy Meter | `sim.smart_energy.meter` | `meter_id` |
| Smart Energy | PV Generation | `sim.smart_energy.pv` | `pv_system_id` |
| Smart Energy | Weather | `sim.smart_energy.weather` | `site_id` |
| Smart Energy | Energy Price | `sim.smart_energy.price` | `"price"` |
| Smart Energy | Consumer Load | `sim.smart_energy.consumer` | `device_id` |
| Smart City | Streetlight | `sim.smart_city.light` | `light_id` |
| Smart City | Traffic | `sim.smart_city.traffic` | `zone_id` |
| Smart City | City Event | `sim.smart_city.event` | `zone_id` |
| Smart City | City Weather | `sim.smart_city.weather` | `city_id` |

---

## 2. Smart Energy Schemas

### 2.1 Energy Meter

Emulates a Janitza UMG 96RM three-phase energy meter.

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "meter_id": "janitza-umg96rm-001",
  "asset_id": "janitza-umg96rm-001",
  "schema_version": "1.0",
  "type": "smart_energy.meter",
  "active_power_kw": 12.45,
  "active_energy_kwh_total": 54321.67,
  "readings": {
    "active_power_l1_w": 4200.3,
    "active_power_l2_w": 4100.1,
    "active_power_l3_w": 4149.6,
    "voltage_l1_v": 230.5,
    "voltage_l2_v": 229.8,
    "voltage_l3_v": 231.2,
    "current_l1_a": 18.9,
    "current_l2_a": 18.5,
    "current_l3_a": 18.7,
    "power_factor": 0.97,
    "frequency_hz": 50.01,
    "total_energy_kwh": 54321.67
  }
}
```

| Field | Type | Unit | Description |
|---|---|---|---|
| `active_power_kw` | float | kW | Total active power (sum of phases / 1000) |
| `active_energy_kwh_total` | float | kWh | Cumulative energy counter (monotonically increasing) |
| `readings.active_power_l{1,2,3}_w` | float | W | Per-phase active power |
| `readings.voltage_l{1,2,3}_v` | float | V | Per-phase voltage (nominal 230V) |
| `readings.current_l{1,2,3}_a` | float | A | Per-phase current |
| `readings.power_factor` | float | — | Power factor (0.0–1.0) |
| `readings.frequency_hz` | float | Hz | Grid frequency (nominal 50 Hz) |

### 2.2 PV Generation

Solar photovoltaic system output correlated with weather irradiance and temperature.

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "pv_system_id": "pv-system-001",
  "asset_id": "pv-system-001",
  "schema_version": "1.0",
  "type": "smart_energy.pv",
  "pv_power_kw": 7.82,
  "readings": {
    "power_output_kw": 7.82,
    "daily_energy_kwh": 28.5,
    "irradiance_w_m2": 850.3,
    "module_temperature_c": 42.1,
    "efficiency_percent": 15.8
  }
}
```

| Field | Type | Unit | Description |
|---|---|---|---|
| `pv_power_kw` | float | kW | Current PV output |
| `readings.daily_energy_kwh` | float | kWh | Cumulative daily energy |
| `readings.irradiance_w_m2` | float | W/m² | Solar irradiance at panel surface |
| `readings.module_temperature_c` | float | °C | PV module temperature (NOCT model) |
| `readings.efficiency_percent` | float | % | Current conversion efficiency |

### 2.3 Weather

Atmospheric conditions correlated with PV generation.

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "schema_version": "1.0",
  "type": "smart_energy.weather",
  "temperature_c": 18.3,
  "solar_irradiance_w_m2": 850.3,
  "location": {
    "latitude": 52.52,
    "longitude": 13.405
  },
  "conditions": {
    "humidity_percent": 55.2,
    "wind_speed_ms": 4.1,
    "wind_direction_deg": 225.0,
    "cloud_cover_percent": 30.0,
    "ghi_w_m2": 850.3,
    "dni_w_m2": 720.0,
    "dhi_w_m2": 130.3
  }
}
```

| Field | Type | Unit | Description |
|---|---|---|---|
| `temperature_c` | float | °C | Ambient temperature (diurnal + seasonal pattern) |
| `conditions.humidity_percent` | float | % | Relative humidity (inversely correlated with temperature) |
| `conditions.wind_speed_ms` | float | m/s | Wind speed (Weibull distribution) |
| `conditions.cloud_cover_percent` | float | % | Cloud cover (0–100) |
| `conditions.ghi_w_m2` | float | W/m² | Global Horizontal Irradiance |
| `conditions.dni_w_m2` | float | W/m² | Direct Normal Irradiance |
| `conditions.dhi_w_m2` | float | W/m² | Diffuse Horizontal Irradiance |

### 2.4 Energy Price

EPEX Spot day-ahead market pricing with tariff periods.

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "schema_version": "1.0",
  "type": "smart_energy.price",
  "price_eur_per_kwh": 0.102,
  "tariff_type": "MIDDAY"
}
```

| Field | Type | Description |
|---|---|---|
| `price_eur_per_kwh` | float | Energy price in EUR/kWh |
| `tariff_type` | string | Tariff period: `NIGHT`, `MORNING_PEAK`, `MIDDAY`, `EVENING_PEAK`, `EVENING` |

### 2.5 Consumer Load

Industrial device state and power consumption based on schedule and duty cycles.

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "device_id": "industrial-oven-001",
  "asset_id": "industrial-oven-001",
  "schema_version": "1.0",
  "type": "smart_energy.consumer",
  "device_type": "INDUSTRIAL_OVEN",
  "device_state": "ON",
  "device_power_kw": 4.85
}
```

| Field | Type | Description |
|---|---|---|
| `device_type` | string | `INDUSTRIAL_OVEN`, `HVAC`, `COMPRESSOR`, `PUMP` |
| `device_state` | string | `ON`, `OFF`, `STANDBY` |
| `device_power_kw` | float | Current power draw in kW |

---

## 3. Smart City Schemas

### 3.1 Streetlight

Zone-based streetlight with event-reactive dimming.

```json
{
  "timestamp": "2026-03-08T22:00:00Z",
  "city_id": "berlin-001",
  "zone_id": "zone-mitte",
  "light_id": "light-mitte-001",
  "asset_id": "light-mitte-001",
  "schema_version": "1.0",
  "type": "smart_city.light",
  "dimming_level_pct": 85.0,
  "power_w": 127.5,
  "is_on": true
}
```

| Field | Type | Description |
|---|---|---|
| `dimming_level_pct` | float | Dimming level 0–100% (event severity boosts: sev 2 → +30%, sev 3 → +50%) |
| `power_w` | float | Current power draw in watts |
| `is_on` | boolean | Light operating state |

### 3.2 Traffic

Zone-level traffic flow index.

```json
{
  "timestamp": "2026-03-08T08:00:00Z",
  "city_id": "berlin-001",
  "zone_id": "zone-mitte",
  "schema_version": "1.0",
  "type": "smart_city.traffic",
  "traffic_index": 0.78
}
```

| Field | Type | Description |
|---|---|---|
| `traffic_index` | float | Traffic flow index 0.0–1.0 (rush hours 07–09, 17–19 show peaks) |

### 3.3 City Event

Deterministic city events with severity classification.

```json
{
  "timestamp": "2026-03-08T21:00:00Z",
  "city_id": "berlin-001",
  "zone_id": "zone-mitte",
  "schema_version": "1.0",
  "type": "smart_city.event",
  "event_type": "ACCIDENT",
  "severity": 2,
  "active": true
}
```

| Field | Type | Description |
|---|---|---|
| `event_type` | string | `ACCIDENT`, `EMERGENCY`, `PUBLIC_EVENT` |
| `severity` | integer | 1 (low), 2 (medium), 3 (high) |
| `active` | boolean | Event currently active |

### 3.4 City Weather / Visibility

Atmospheric visibility and fog conditions for city operations.

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "city_id": "berlin-001",
  "schema_version": "1.0",
  "type": "smart_city.weather",
  "fog_index": 0.1,
  "visibility": "good",
  "sunrise_time": "06:15",
  "sunset_time": "18:45"
}
```

| Field | Type | Description |
|---|---|---|
| `fog_index` | float | Fog intensity 0.0–1.0 (peaks at dawn) |
| `visibility` | string | `good`, `medium`, `poor` |
| `sunrise_time` | string | Sunrise time (HH:MM, local) |
| `sunset_time` | string | Sunset time (HH:MM, local) |

---

## 4. Tick Envelope Format

When publishing to ORCE, all 9 feeds are bundled into a single JSON envelope:

```json
{
  "type": "sim.tick",
  "schema_version": "1.0",
  "timestamp": "2026-03-08T14:00:00Z",
  "mode": "normal",
  "seed": 12345,
  "site_id": "site-berlin-001",
  "smart_energy": {
    "meters": [ ... ],
    "pv": [ ... ],
    "weather": { ... },
    "price": { ... },
    "consumers": [ ... ],
    "metrics": {
      "total_consumption_kw": 24.8,
      "total_generation_kw": 8.2,
      "net_grid_power_kw": 16.6,
      "self_consumption_ratio": 1.0,
      "current_cost_eur_per_hour": 2.99
    }
  },
  "smart_city": {
    "city_id": "berlin-001",
    "streetlights": [ ... ],
    "traffic_readings": [ ... ],
    "events": [ ... ],
    "visibility": { ... }
  }
}
```

The `smart_energy.metrics` block contains derived values calculated by the correlation engine. These are not stored as a separate Kafka topic but are included in the envelope for downstream consumers.

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
