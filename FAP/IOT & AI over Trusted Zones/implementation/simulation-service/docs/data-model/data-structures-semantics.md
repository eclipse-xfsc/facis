# Data Structures and Semantics Reference

**Project:** FACIS FAP — IoT & AI Demonstrator
**Version:** 1.0
**Date:** 07 March 2026
**Spec Reference:** Sections 5.6, 6 — Data Content Definition and Semantics

---

## 1. Purpose

This document provides a complete semantic specification for the five Smart Energy data structures produced by the simulation service. For each feed it defines every field's type, unit, and value range; explains the semantic meaning of key fields; provides a canonical JSON example that matches the specification; describes the feed's relationships with other feeds; and states the intended downstream usage.

This document complements the structural schema definitions in `schema-reference.md` and the Avro serialisation contracts in `avro-schema-reference.md`.

---

## 2. Feed Summary

The simulation service generates five Smart Energy feeds at a configurable interval (default 1 minute). All feeds share a common site context (`site_id`) for cross-correlation. A deterministic seed ensures reproducibility across runs.

| Feed | Record Type | Kafka Topic | Cardinality per Tick |
|---|---|---|---|
| Energy Meter | `MeterReading` | `sim.smart_energy.meter` | 1 per configured meter |
| Energy Price | `PriceRecord` | `sim.smart_energy.price` | 1 |
| Weather | `WeatherRecord` | `sim.smart_energy.weather` | 1 |
| PV Generation | `PVGeneration` | `sim.smart_energy.pv` | 1 per configured PV system |
| Consumer Load | `ConsumerState` | `sim.smart_energy.consumer` | 1 per configured device |

### 2.1 Generation Order and Dependencies

The correlation engine generates feeds in a strict dependency order within each simulation tick:

```
Step 1:  WeatherRecord      (independent — generated first)
             │
Step 2:  PVGeneration        (depends on WeatherRecord for irradiance + temperature)
             │
Step 3:  MeterReading        (independent of weather)
         PriceRecord         (independent — time-of-day only)
         ConsumerState       (independent — schedule + duty-cycle only)
             │
Step 4:  Derived Metrics     (computed from all five feeds)
```

Derived metrics (`total_consumption_kw`, `total_generation_kw`, `net_grid_power_kw`, `self_consumption_ratio`, `current_cost_eur_per_hour`) are bundled into the tick envelope but are not published as a separate Kafka topic.

---

## 3. MeterReading — Energy Meter

### 3.1 Description

Emulates a Janitza UMG 96RM three-phase industrial energy meter. Each reading captures instantaneous electrical parameters across three phases (L1, L2, L3) plus cumulative energy counters. The meter is the primary consumption measurement point for the site.

### 3.2 Intended Usage

MeterReading is the foundation for energy consumption analytics. Downstream consumers use it to calculate total site consumption, phase imbalance detection, power quality monitoring, and energy cost attribution (when joined with PriceRecord). The cumulative `total_energy_kwh` field supports billing-period calculations via delta computation between readings.

### 3.3 Example JSON

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "meter_id": "janitza-umg96rm-001",
  "asset_id": "janitza-umg96rm-001",
  "schema_version": "1.0",
  "type": "energy_meter",
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

### 3.4 Field Specification

#### Envelope Fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `timestamp` | string (ISO 8601) | Yes | — | Event time in UTC with `Z` suffix. Aligned to the simulation tick interval. |
| `site_id` | string | Yes | `"site-berlin-001"` | Logical site identifier shared across all feeds for cross-correlation. |
| `meter_id` | string | Yes | — | Unique meter identifier. Serves as Kafka partition key. |
| `asset_id` | string | Yes | — | Canonical asset identifier (computed, equals `meter_id`). |
| `schema_version` | string | Yes | `"1.0"` | Payload schema version for forward compatibility. |
| `type` | string (literal) | Yes | `"energy_meter"` | Discriminator for polymorphic deserialization. |

#### Measurement Fields

| Field | Type | Unit | Range | Semantic Meaning |
|---|---|---|---|---|
| `active_power_kw` | float | kW | ≥ 0 | **Instantaneous.** Total three-phase active power. Derived as `sum(L1+L2+L3) / 1000`. Represents the site's total grid draw at this moment. Typical simulation range: 5–25 kW depending on configured base/peak load. |
| `active_energy_kwh_total` | float | kWh | ≥ 0 | **Cumulative.** Monotonically increasing energy counter since meter initialisation. Equivalent to a utility billing register. To calculate energy consumed in a period, compute the delta between two readings: `E = reading_t2 - reading_t1`. Never decreases unless the meter is reset. |
| `readings.active_power_l1_w` | float | W | ≥ 0 | **Instantaneous.** Phase L1 active power. Each phase carries approximately one-third of total load with a configurable variance (default ±5%). |
| `readings.active_power_l2_w` | float | W | ≥ 0 | **Instantaneous.** Phase L2 active power. Same semantics as L1. |
| `readings.active_power_l3_w` | float | W | ≥ 0 | **Instantaneous.** Phase L3 active power. Same semantics as L1. |
| `readings.voltage_l1_v` | float | V | ~207–253 | **Instantaneous.** Phase-to-neutral voltage. Nominal 230V (EU standard). Variance configurable 0–10%, default ±5% (218.5–241.5V). Values outside EN 50160 tolerance (±10%) indicate a power quality anomaly. |
| `readings.voltage_l2_v` | float | V | ~207–253 | **Instantaneous.** Same semantics as L1 voltage. |
| `readings.voltage_l3_v` | float | V | ~207–253 | **Instantaneous.** Same semantics as L1 voltage. |
| `readings.current_l1_a` | float | A | ≥ 0 | **Instantaneous.** Phase L1 current. Derived from `P = V × I × cos(φ)`. |
| `readings.current_l2_a` | float | A | ≥ 0 | **Instantaneous.** Phase L2 current. |
| `readings.current_l3_a` | float | A | ≥ 0 | **Instantaneous.** Phase L3 current. |
| `readings.power_factor` | float | — | 0.0–1.0 | **Instantaneous.** Ratio of real power to apparent power (cosφ). Values near 1.0 indicate efficient power usage; values below 0.8 suggest reactive power issues. Configurable range default: 0.95–0.99. |
| `readings.frequency_hz` | float | Hz | ~49.95–50.05 | **Instantaneous.** Grid frequency. Nominal 50 Hz (EU). Configurable variance default ±0.05 Hz. Deviations beyond ±0.2 Hz indicate grid instability. |
| `readings.total_energy_kwh` | float | kWh | ≥ 0 | **Cumulative.** Mirrors `active_energy_kwh_total`. Monotonically increasing. Provided within `readings` for consistency with the Janitza UMG 96RM register map. |

### 3.5 Relationships

| Related Feed | Relationship | Join Key |
|---|---|---|
| PriceRecord | Cost calculation: `cost = active_power_kw × price_eur_per_kwh` | `timestamp` (aligned) |
| PVGeneration | Net grid calculation: `net = meter_consumption - pv_generation` | `site_id` + `timestamp` |
| ConsumerState | Breakdown: meter total ≈ sum of individual consumer loads + unmetered base load | `site_id` + `timestamp` |
| WeatherRecord | Indirect: temperature extremes drive HVAC load which appears in meter readings | `site_id` + `timestamp` |

---

## 4. PriceRecord — Energy Price

### 4.1 Description

Simulates EPEX Spot day-ahead market pricing for the German bidding zone (DE). Prices follow a deterministic time-of-day tariff pattern with configurable volatility noise. This provides the economic dimension for energy analytics.

### 4.2 Intended Usage

PriceRecord enables energy cost attribution and economic optimisation analysis. Joining price with meter consumption yields real-time energy cost. Joining with PV generation identifies periods where self-consumption avoids grid purchase. Tariff-period segmentation supports peak-shaving and load-shifting analytics in Gold layer views.

### 4.3 Example JSON

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "schema_version": "1.0",
  "type": "energy_price",
  "price_eur_per_kwh": 0.102,
  "tariff_type": "MIDDAY"
}
```

### 4.4 Field Specification

| Field | Type | Unit | Range | Semantic Meaning |
|---|---|---|---|---|
| `timestamp` | string (ISO 8601) | — | — | Event time (UTC). Aligned to tick interval. |
| `site_id` | string | — | — | Site identifier for join context. |
| `schema_version` | string | — | — | Payload version. Default `"1.0"`. |
| `type` | string (literal) | — | `"energy_price"` | Discriminator. |
| `price_eur_per_kwh` | float | EUR/kWh | ≥ 0.05 (floor) | **Instantaneous.** Spot energy price. The simulation applies a configurable volatility (default ±10%) around base tariff rates. A floor price (default 0.05 EUR/kWh) prevents negative pricing. Weekend prices receive a discount (default 7.5%). Base rates: NIGHT 0.15, MORNING_PEAK 0.33, MIDDAY 0.26, EVENING_PEAK 0.40, EVENING 0.22 EUR/kWh. |
| `tariff_type` | string (enum) | — | see below | **Categorical.** Time-of-day tariff classification. Determines the base price band. |

#### TariffType Enum Values

| Value | Time Band | Base Price (EUR/kWh) | Semantic Meaning |
|---|---|---|---|
| `NIGHT` | 00:00–06:00 | 0.15 | Off-peak overnight. Lowest demand and cost. Suitable for scheduled loads. |
| `MORNING_PEAK` | 06:00–09:00 | 0.33 | Morning demand ramp. Industrial and commercial start-up. |
| `MIDDAY` | 09:00–17:00 | 0.26 | Business hours. Moderate pricing, often offset by solar PV generation. |
| `EVENING_PEAK` | 17:00–20:00 | 0.40 | Highest demand period. Residential + commercial overlap. Most expensive. |
| `EVENING` | 20:00–00:00 | 0.22 | Declining demand. Transitional period before night tariff. |

### 4.5 Relationships

| Related Feed | Relationship | Join Key |
|---|---|---|
| MeterReading | Cost = `active_power_kw × price_eur_per_kwh` (hourly cost rate) | `timestamp` |
| PVGeneration | Avoided cost = `pv_power_kw × price_eur_per_kwh` (value of self-consumption) | `timestamp` |
| ConsumerState | Per-device cost = `device_power_kw × price_eur_per_kwh` | `timestamp` |

---

## 5. WeatherRecord — Weather Observations

### 5.1 Description

Simulates atmospheric conditions for a fixed weather station location (default: Berlin, 52.52°N 13.405°E). Weather is the upstream driver of the PV generation model: solar irradiance and temperature directly determine PV output. The simulation models diurnal temperature cycles, seasonal variation, cloud cover dynamics, and three components of solar radiation (GHI, DNI, DHI).

### 5.2 Intended Usage

WeatherRecord serves two primary purposes. First, it is the input to the PV generation correlation model — irradiance and temperature determine panel output. Second, it provides environmental context for dashboard visualisation and AI insight generation (e.g., explaining why PV output dropped due to cloud cover increase).

### 5.3 Example JSON

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "schema_version": "1.0",
  "type": "weather",
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

### 5.4 Field Specification

#### Location Fields

| Field | Type | Unit | Range | Semantic Meaning |
|---|---|---|---|---|
| `location.latitude` | float | degrees | -90.0 to 90.0 | **Static.** Weather station latitude in decimal degrees (WGS 84). Positive = North. Default: 52.52 (Berlin). |
| `location.longitude` | float | degrees | -180.0 to 180.0 | **Static.** Weather station longitude in decimal degrees (WGS 84). Positive = East. Default: 13.405 (Berlin). |

#### Atmospheric Conditions

| Field | Type | Unit | Range | Semantic Meaning |
|---|---|---|---|---|
| `temperature_c` | float | °C | ~-15 to +40 | **Instantaneous.** Ambient air temperature. Follows a sinusoidal diurnal pattern (peak ~14:00, trough ~05:00) with seasonal offset (summer base 20°C, winter base 2°C). Amplitude default ±8°C with ±2°C noise. Used by PV model to compute module temperature and efficiency derating. |
| `solar_irradiance_w_m2` | float | W/m² | ≥ 0 | **Instantaneous.** Top-level summary field equal to `conditions.ghi_w_m2`. Provided for convenience. Zero at night. Peak clear-sky value ~1000 W/m². |
| `conditions.humidity_percent` | float | % | 0–100 | **Instantaneous.** Relative humidity. Inversely correlated with temperature (high temp → low humidity). Base default 65% with ±15% variance. |
| `conditions.wind_speed_ms` | float | m/s | ≥ 0 | **Instantaneous.** Wind speed at station height. Modelled as Weibull distribution. Base default 4.0 m/s with ±3.0 m/s variance. |
| `conditions.wind_direction_deg` | float | degrees | 0–359 | **Instantaneous.** Compass direction wind is blowing FROM (meteorological convention). 0 = North, 90 = East, 180 = South, 270 = West. Prevailing default: 270° (westerly) with ±45° variance. |
| `conditions.cloud_cover_percent` | float | % | 0–100 | **Instantaneous.** Fraction of sky covered by cloud. Directly attenuates solar irradiance: effective GHI ≈ clear_sky_GHI × (1 - 0.75 × cloud_cover). Base default 40% with ±20% variance. |
| `conditions.ghi_w_m2` | float | W/m² | ≥ 0 | **Instantaneous.** Global Horizontal Irradiance — total solar energy on a horizontal surface. Sum of DNI (cos-projected) + DHI. Primary input to PV model. Zero between sunset and sunrise. Clear-sky maximum configurable, default 1000 W/m². |
| `conditions.dni_w_m2` | float | W/m² | ≥ 0 | **Instantaneous.** Direct Normal Irradiance — beam component perpendicular to the sun. Heavily attenuated by cloud cover. |
| `conditions.dhi_w_m2` | float | W/m² | ≥ 0 | **Instantaneous.** Diffuse Horizontal Irradiance — scattered sky component. Increases relative to DNI under overcast conditions. Relationship: GHI = DNI × cos(zenith) + DHI. |

### 5.5 Relationships

| Related Feed | Relationship | Join Key |
|---|---|---|
| PVGeneration | **Causal dependency.** Weather is generated first; PV simulator consumes `ghi_w_m2` and `temperature_c` to compute panel output. Higher irradiance → higher PV output. Higher temperature → lower efficiency (negative temperature coefficient). | Generated in same tick (Step 1 → Step 2) |
| MeterReading | **Indirect.** Temperature extremes drive HVAC loads, which contribute to meter consumption. Not modelled as a direct correlation in the current simulation but observable in analytics. | `site_id` + `timestamp` |

---

## 6. PVGeneration — Photovoltaic Generation

### 6.1 Description

Models the electrical output of a rooftop photovoltaic system using a simplified NOCT (Nominal Operating Cell Temperature) model. Output is physically correlated with the WeatherRecord: solar irradiance determines the available energy, and module temperature (derived from ambient temperature and irradiance) derates efficiency via a negative temperature coefficient.

### 6.2 Intended Usage

PVGeneration is essential for net-energy calculations. Subtracting PV output from meter consumption yields the net grid power (import/export). The `daily_energy_kwh` counter supports daily self-sufficiency calculations. Efficiency tracking enables performance monitoring and degradation detection. When joined with PriceRecord, PV output quantifies avoided energy costs.

### 6.3 Example JSON

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "pv_system_id": "pv-system-001",
  "asset_id": "pv-system-001",
  "schema_version": "1.0",
  "type": "pv_generation",
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

### 6.4 Field Specification

| Field | Type | Unit | Range | Semantic Meaning |
|---|---|---|---|---|
| `timestamp` | string (ISO 8601) | — | — | Event time (UTC). Aligned to tick interval. |
| `site_id` | string | — | — | Site identifier. Must match the WeatherRecord `site_id` for correlation. |
| `pv_system_id` | string | — | — | Unique PV system identifier. Serves as Kafka partition key. Default: `"pv-system-001"`. |
| `asset_id` | string | — | — | Canonical asset identifier (equals `pv_system_id`). |
| `schema_version` | string | — | `"1.0"` | Payload version. |
| `type` | string (literal) | — | `"pv_generation"` | Discriminator. |
| `pv_power_kw` | float | kW | ≥ 0 | **Instantaneous.** Current PV output. Top-level summary equal to `readings.power_output_kw`. Zero at night (no irradiance). Maximum bounded by `nominal_capacity_kwp` (default 10 kWp) minus system losses (default 15%) and temperature derating. Typical midday peak: 5–8 kW. |
| `readings.power_output_kw` | float | kW | ≥ 0 | **Instantaneous.** Same as `pv_power_kw`. Computed as: `irradiance / 1000 × capacity_kwp × efficiency_factor × (1 - system_losses)`. |
| `readings.daily_energy_kwh` | float | kWh | ≥ 0 | **Cumulative (daily).** Accumulated PV energy since midnight UTC. Resets to zero at 00:00 each day. Used for daily self-sufficiency and export calculations. Not monotonically increasing across days. |
| `readings.irradiance_w_m2` | float | W/m² | ≥ 0 | **Instantaneous.** Solar irradiance at the panel surface. Mirrored from the WeatherRecord's `ghi_w_m2`. Included in PV record for self-contained analysis without requiring a weather join. |
| `readings.module_temperature_c` | float | °C | ~0 to 70 | **Instantaneous.** PV module temperature computed via NOCT model: `T_module = T_ambient + (NOCT - 20) × irradiance / 800`. Default NOCT = 45°C. Higher module temperature reduces efficiency. |
| `readings.efficiency_percent` | float | % | 0–100 | **Instantaneous.** Current conversion efficiency accounting for temperature derating. Base efficiency ≈ 18–20%. Derating: `efficiency = base × (1 + temp_coeff × (T_module - T_ref))` where temp_coeff = -0.4%/°C and T_ref = 25°C. Typical operating range: 14–20%. |

### 6.5 Relationships

| Related Feed | Relationship | Join Key |
|---|---|---|
| WeatherRecord | **Causal input.** PV output is physically derived from `ghi_w_m2` (energy available) and `temperature_c` (efficiency derating). A 50% drop in irradiance produces a roughly proportional drop in PV power. | Same tick (weather generated first) |
| MeterReading | **Net energy.** `net_grid_kw = meter.active_power_kw - pv.pv_power_kw`. Positive = importing from grid; negative = exporting to grid. | `site_id` + `timestamp` |
| PriceRecord | **Avoided cost.** `avoided_cost_eur_h = pv_power_kw × price_eur_per_kwh` (when PV displaces grid purchase). | `timestamp` |

---

## 7. ConsumerState — Consumer Load

### 7.1 Description

Models individual industrial device state and power consumption. Each device operates on a configurable schedule (operating windows), duty cycle, and rated power. Devices transition between ON and OFF states based on schedule and duty-cycle probability. This provides device-level granularity for load disaggregation.

### 7.2 Intended Usage

ConsumerState enables device-level energy management. Aggregating all consumer devices and comparing with the meter total reveals unmetered base load. Duty-cycle analysis supports predictive maintenance (unusual ON/OFF patterns). Operating-window compliance checking identifies schedule violations. When combined with PriceRecord, per-device costs inform load-shifting decisions (e.g., move oven operation from EVENING_PEAK to NIGHT tariff).

### 7.3 Example JSON

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "device_id": "industrial-oven-001",
  "asset_id": "industrial-oven-001",
  "schema_version": "1.0",
  "type": "consumer",
  "device_type": "INDUSTRIAL_OVEN",
  "device_state": "ON",
  "device_power_kw": 4.85
}
```

### 7.4 Field Specification

| Field | Type | Unit | Range | Semantic Meaning |
|---|---|---|---|---|
| `timestamp` | string (ISO 8601) | — | — | Event time (UTC). Aligned to tick interval. |
| `site_id` | string | — | — | Site identifier for cross-feed correlation. |
| `device_id` | string | — | — | Unique device identifier. Serves as Kafka partition key. |
| `asset_id` | string | — | — | Canonical asset identifier (equals `device_id`). |
| `schema_version` | string | — | `"1.0"` | Payload version. |
| `type` | string (literal) | — | `"consumer"` | Discriminator. |
| `device_type` | string (enum) | — | see below | **Static.** Device classification. Does not change between readings. Determines typical power range and operational characteristics. |
| `device_state` | string (enum) | — | `ON`, `OFF` | **Instantaneous.** Current operational state. A device is ON only during its configured operating windows AND when the duty-cycle probability check passes. OFF devices report 0.0 kW power. |
| `device_power_kw` | float | kW | ≥ 0 | **Instantaneous.** Current power draw. When ON: `rated_power_kw ± power_variance_pct` (default ±5%). When OFF: exactly 0.0. No standby power in current model. |

#### DeviceType Enum Values

| Value | Typical Rated Power | Typical Duty Cycle | Description |
|---|---|---|---|
| `INDUSTRIAL_OVEN` | 3.0–5.0 kW | 70% | Continuous-process heating. High base load with thermal inertia. |
| `HVAC` | 1.5–3.0 kW | 60% | Heating, ventilation, air conditioning. Cyclical on/off. |
| `COMPRESSOR` | 2.0–4.0 kW | 50% | Compressed air system. Intermittent high-power draw. |
| `PUMP` | 1.0–2.5 kW | 40% | Fluid circulation. Moderate steady-state power. |
| `GENERIC` | Configurable | Configurable | Catch-all for custom device types. |

#### DeviceState Enum Values

| Value | Semantic Meaning |
|---|---|
| `ON` | Device is operating and drawing rated power (with variance). |
| `OFF` | Device is idle. Power draw is 0.0 kW. |

### 7.5 Relationships

| Related Feed | Relationship | Join Key |
|---|---|---|
| MeterReading | **Composition.** Sum of all consumer `device_power_kw` (when ON) contributes to the meter's `active_power_kw`. The meter total also includes unmetered base load not captured by individual consumers. | `site_id` + `timestamp` |
| PriceRecord | **Per-device cost.** `device_cost_eur_h = device_power_kw × price_eur_per_kwh`. Enables per-device cost attribution and load-shifting analysis. | `timestamp` |
| WeatherRecord | **Indirect.** HVAC device duty cycle in reality correlates with temperature; the current simulation uses fixed schedules but this field supports future weather-responsive load modelling. | `site_id` + `timestamp` |

---

## 8. Cross-Feed Relationship Summary

The five feeds form an interconnected data model. The diagram below shows the causal and analytical relationships:

```
                 WeatherRecord
                      │
            ┌─────────┴─────────┐
            │  causal input     │  context
            ▼                   ▼
       PVGeneration        MeterReading ◄──── composition ──── ConsumerState
            │                   │                                    │
            │                   │                                    │
            └───── net grid ────┘                                    │
                      │                                              │
                      ▼                                              │
                 PriceRecord ◄────── cost attribution ───────────────┘
```

**Causal relationships** (data dependency at generation time): WeatherRecord → PVGeneration.

**Analytical relationships** (join-time correlations for downstream queries): MeterReading + PVGeneration = net grid power. Any feed + PriceRecord = cost attribution. Sum of ConsumerState ≈ portion of MeterReading total.

### 8.1 Derived Metrics

The correlation engine computes the following metrics from all five feeds within each tick. These are included in the ORCE tick envelope but are not persisted as a separate Kafka topic.

| Metric | Formula | Unit | Semantic Meaning |
|---|---|---|---|
| `total_consumption_kw` | `sum(meter.active_power_kw) + sum(consumer.device_power_kw)` | kW | Total site electrical demand. |
| `total_generation_kw` | `sum(pv.pv_power_kw)` | kW | Total on-site generation (PV only). |
| `net_grid_power_kw` | `total_consumption_kw - total_generation_kw` | kW | Net grid exchange. Positive = importing; negative = exporting. |
| `self_consumption_ratio` | `min(generation, consumption) / generation` | ratio (0–1) | Fraction of PV output consumed on-site. 1.0 = all PV used locally. |
| `current_cost_eur_per_hour` | `max(0, net_grid_power_kw) × price_eur_per_kwh` | EUR/h | Instantaneous grid energy cost rate. Zero when exporting. |

---

## 9. Common Conventions

**Timestamps.** All five feeds use ISO 8601 format with UTC timezone suffix `Z`. Timestamps are aligned to the simulation tick interval (default 1 minute). Example: `"2026-03-08T14:00:00Z"`.

**Determinism.** Given the same seed (default 12345) and start time, the simulation produces identical output across runs. This enables reproducible testing and validation.

**Cumulative vs Instantaneous.** Fields marked "cumulative" increase monotonically within their reset period. `active_energy_kwh_total` and `total_energy_kwh` never decrease. `daily_energy_kwh` resets at midnight UTC.

**Null handling.** All fields in the five Smart Energy feeds are required (non-nullable) at the source. The Silver Avro schemas introduce `building_id` as an optional (nullable) field for future multi-building support.

**Units.** All electrical power values use kW (kilowatts) at the top level and W (watts) for per-phase readings. Energy values use kWh. Temperature uses Celsius. Irradiance uses W/m². Currency uses EUR.

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
