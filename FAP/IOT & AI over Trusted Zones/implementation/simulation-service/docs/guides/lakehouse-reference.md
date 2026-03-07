# Lakehouse Technical Reference

**Project:** FACIS FAP — IoT & AI Demonstrator
**Query Engine:** Trino with Iceberg connector
**Storage:** S3-compatible object storage (Parquet format)
**Architecture:** Medallion (Bronze → Silver → Gold)

---

## 1. Overview

The FACIS Lakehouse implements a three-layer Medallion architecture on Apache Iceberg tables and Trino views. Raw IoT data lands in the Bronze layer via NiFi, is typed and cleaned in the Silver layer, and aggregated into analytics-ready KPIs in the Gold layer.

| Layer | Schema | Type | Count | Purpose |
|---|---|---|---|---|
| Bronze | `bronze` | Iceberg tables (Parquet on S3) | 9 | Raw JSON ingestion with Kafka metadata |
| Silver | `silver` | Trino views over Bronze | 9 | Typed extraction, data quality filtering, derived fields |
| Gold | `gold` | Trino views over Silver | 12 | Aggregated KPIs, curated analytics, anomaly detection |

## 2. Bronze Layer — Raw Ingestion

### 2.1 Table Schema

All 9 Bronze tables share an identical schema:

```sql
CREATE TABLE IF NOT EXISTS bronze.<table_name> (
    ingestion_timestamp  TIMESTAMP(6) WITH TIME ZONE,
    kafka_topic          VARCHAR,
    kafka_partition      INTEGER,
    kafka_offset         BIGINT,
    message_key          VARCHAR,
    raw_value            VARCHAR
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['day(ingestion_timestamp)']
)
```

- `ingestion_timestamp`: NiFi's `CURRENT_TIMESTAMP` at insert time
- `raw_value`: Complete JSON payload from Kafka (unparsed)
- Partitioned by day for efficient time-range queries
- S3 location: `s3a://<bucket>/warehouse/bronze.db/<table_name>/`

### 2.2 Table Inventory

| Table | Source Kafka Topic | Content |
|---|---|---|
| `bronze.energy_meter` | `sim.smart_energy.meter` | 3-phase energy meter readings |
| `bronze.pv_generation` | `sim.smart_energy.pv` | PV system generation data |
| `bronze.weather` | `sim.smart_energy.weather` | Weather conditions |
| `bronze.energy_price` | `sim.smart_energy.price` | Energy spot prices |
| `bronze.consumer_load` | `sim.smart_energy.consumer` | Consumer device loads |
| `bronze.streetlight` | `sim.smart_city.light` | Streetlight dimming/power |
| `bronze.traffic` | `sim.smart_city.traffic` | Zone traffic indices |
| `bronze.city_event` | `sim.smart_city.event` | City event records |
| `bronze.city_weather` | `sim.smart_city.weather` | Visibility and fog data |

## 3. Silver Layer — Typed Extraction with Data Quality

Silver views extract and type JSON fields from Bronze tables using `json_extract_scalar()` and `from_iso8601_timestamp()`. As of WP3 completion, Silver views also include data quality filtering and derived fields.

### 3.1 Design Principles

- All timestamps use `from_iso8601_timestamp()` (not `CAST AS TIMESTAMP`) to handle the `Z` UTC suffix
- Nested JSON fields are extracted with `$.path.to.field` notation
- Numeric fields are cast to `DOUBLE`; Integer fields to `INTEGER`; Boolean fields to `BOOLEAN`
- Original `ingestion_timestamp` is preserved for data lineage
- **Data quality WHERE clauses** filter null timestamps, invalid negatives, and out-of-range values
- **COALESCE** provides defaults for fields that may not exist in older messages (schema evolution)
- **Derived fields** add computed columns for downstream analytics

### 3.2 Data Quality Filters

Each Silver view includes WHERE clauses tailored to its domain:

| View | Quality Filters Applied |
|---|---|
| `energy_meter` | Non-null timestamp, `active_power_kw >= 0` |
| `pv_generation` | Non-null timestamp, `power_kw >= 0` |
| `weather` | Non-null timestamp, temperature in `[-50, 60]°C` |
| `energy_price` | Non-null timestamp, `price_eur_per_kwh >= 0` |
| `consumer_load` | Non-null timestamp |
| `streetlight` | Non-null timestamp, `power_w >= 0` |
| `traffic` | Non-null timestamp, `traffic_index` in `[0, 1]` |
| `city_event` | Non-null timestamp |
| `city_weather` | Non-null timestamp |

### 3.3 Derived Fields

Silver views expose the following computed columns for direct use in Gold aggregations and dashboards:

| View | Derived Field | Formula |
|---|---|---|
| `energy_meter` | `total_active_power_w` | `voltage_l1_v * current_l1_a + voltage_l2_v * current_l2_a + voltage_l3_v * current_l3_a` |
| `energy_meter` | `apparent_power_va` | Same formula (apparent ≈ active at unity PF) |
| `pv_generation` | `capacity_factor` | `power_kw / 10.0` (nominal 10 kWp system) |
| `energy_price` | `is_peak_hour` | `tariff_type IN ('morning_peak', 'afternoon_peak', 'evening_peak')` |
| `consumer_load` | `is_active` | `device_state = 'on'` |
| `streetlight` | `energy_wh_estimate` | `power_w / 60.0` (per-minute energy estimate) |
| `traffic` | `is_congested` | `traffic_index > 0.7` |
| `city_event` | `severity_label` | Mapped from severity integer: 1→low, 2→medium, 3→high, 4+→critical |
| `city_weather` | `is_fog_alert` | `fog_index > 0.6` |

### 3.4 Schema Evolution Handling

Fields that may not exist in older messages use COALESCE with sensible defaults:

- `asset_id`: Falls back to `meter_id`, `device_id`, `pv_system_id`, or `light_id` as appropriate
- `schema_version`: Defaults to `'1.0'`

### 3.5 Example: `silver.energy_meter` (Updated)

```sql
CREATE OR REPLACE VIEW silver.energy_meter AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    json_extract_scalar(raw_value, '$.site_id')    AS site_id,
    COALESCE(json_extract_scalar(raw_value, '$.asset_id'),
             json_extract_scalar(raw_value, '$.meter_id')) AS meter_id,
    CAST(json_extract_scalar(raw_value, '$.active_power_kw') AS DOUBLE) AS active_power_kw,
    -- ... voltage, current, PF, frequency fields ...
    -- Derived fields:
    (voltage_l1_v * current_l1_a
     + voltage_l2_v * current_l2_a
     + voltage_l3_v * current_l3_a) AS total_active_power_w,
    (voltage_l1_v * current_l1_a
     + voltage_l2_v * current_l2_a
     + voltage_l3_v * current_l3_a) AS apparent_power_va,
    message_key
FROM bronze.energy_meter
WHERE json_extract_scalar(raw_value, '$.timestamp') IS NOT NULL
  AND CAST(json_extract_scalar(raw_value, '$.active_power_kw') AS DOUBLE) >= 0
```

### 3.6 Silver View Inventory

| View | Key Extracted Fields | Derived Fields |
|---|---|---|
| `silver.energy_meter` | event_timestamp, meter_id, active_power_kw, energy_kwh, voltage L1-L3, current L1-L3, PF, frequency | `total_active_power_w`, `apparent_power_va` |
| `silver.pv_generation` | event_timestamp, pv_system_id, power_kw, daily_energy, irradiance, module_temp, efficiency | `capacity_factor` |
| `silver.weather` | event_timestamp, temperature, humidity, wind_speed/direction, cloud_cover, GHI/DNI/DHI | — |
| `silver.energy_price` | event_timestamp, price_eur_per_kwh, tariff_type | `is_peak_hour` |
| `silver.consumer_load` | event_timestamp, device_id, device_type, device_state, power_kw | `is_active` |
| `silver.streetlight` | event_timestamp, zone_id, light_id, dimming_level_pct, power_w, is_on | `energy_wh_estimate` |
| `silver.traffic` | event_timestamp, zone_id, traffic_index | `is_congested` |
| `silver.city_event` | event_timestamp, zone_id, event_type, severity, active | `severity_label` |
| `silver.city_weather` | event_timestamp, city_id, fog_index, visibility, sunrise_time, sunset_time | `is_fog_alert` |

## 4. Gold Layer — Curated Analytics

Gold views aggregate Silver data into analytics-ready KPIs for dashboarding and AI services. The Gold layer now contains 12 views: 6 original hourly/daily aggregations plus 6 new views added in WP3 completion.

### 4.1 Original Gold Views

#### `gold.energy_balance_hourly`

Hourly energy consumption metrics per meter.

| Column | Type | Description |
|---|---|---|
| `hour` | timestamp | Truncated to hour |
| `meter_id` | varchar | Meter identifier |
| `avg_consumption_kw` | double | Average active power |
| `peak_consumption_kw` | double | Maximum active power |
| `energy_consumed_kwh` | double | Energy consumed in the hour |
| `avg_power_factor` | double | Average power factor |
| `reading_count` | bigint | Number of readings |

#### `gold.pv_performance_hourly`

Hourly PV generation metrics per system.

| Column | Type | Description |
|---|---|---|
| `hour` | timestamp | Truncated to hour |
| `pv_system_id` | varchar | PV system identifier |
| `avg_power_kw` | double | Average PV output |
| `peak_power_kw` | double | Maximum PV output |
| `avg_irradiance` | double | Average solar irradiance (W/m²) |
| `avg_efficiency` | double | Average conversion efficiency (%) |

#### `gold.net_grid_hourly`

Hourly grid balance joining consumption, generation, and pricing.

| Column | Type | Description |
|---|---|---|
| `hour` | timestamp | Truncated to hour |
| `avg_consumption_kw` | double | Total consumption from meters |
| `avg_generation_kw` | double | Total PV generation |
| `net_grid_kw` | double | Net grid power (consumption − generation) |
| `avg_price_eur_per_kwh` | double | Average energy price |
| `estimated_hourly_cost_eur` | double | Estimated hourly cost (net_grid × price) |

This view is the primary KPI for the Smart Energy demonstrator, showing the economic impact of PV self-consumption.

#### `gold.streetlight_zone_hourly`

Hourly streetlight metrics per zone.

| Column | Type | Description |
|---|---|---|
| `hour` | timestamp | Truncated to hour |
| `zone_id` | varchar | Zone identifier |
| `avg_dimming_pct` | double | Average dimming level |
| `total_power_w` | double | Total zone power consumption |
| `light_count` | bigint | Number of active lights |

#### `gold.event_impact_daily`

Daily event statistics per zone and type.

| Column | Type | Description |
|---|---|---|
| `day` | date | Truncated to day |
| `zone_id` | varchar | Zone identifier |
| `event_type` | varchar | Event classification |
| `event_count` | bigint | Number of events |
| `avg_severity` | double | Average severity level |
| `active_count` | bigint | Number of currently active events |

#### `gold.weather_hourly`

Hourly weather aggregations.

| Column | Type | Description |
|---|---|---|
| `hour` | timestamp | Truncated to hour |
| `avg_temperature_c` | double | Average temperature |
| `avg_humidity_pct` | double | Average relative humidity |
| `avg_wind_speed_ms` | double | Average wind speed |
| `avg_cloud_cover_pct` | double | Average cloud cover |
| `avg_ghi_w_m2` | double | Average Global Horizontal Irradiance |

### 4.2 New Gold Views (WP3 Completion)

#### `gold.energy_cost_daily`

Daily energy cost summary with peak/off-peak breakdown. Joins `silver.energy_meter` with `silver.energy_price`.

| Column | Type | Description |
|---|---|---|
| `day` | date | Truncated to day |
| `meter_id` | varchar | Meter identifier |
| `total_consumption_kwh` | double | Total energy consumed |
| `avg_price_eur` | double | Average price across all hours |
| `peak_cost_eur` | double | Cost during peak tariff hours |
| `offpeak_cost_eur` | double | Cost during off-peak hours |
| `total_estimated_cost_eur` | double | Total estimated daily cost |

#### `gold.pv_self_consumption_daily`

Daily self-consumption vs grid export analysis. Joins `silver.energy_meter` with `silver.pv_generation` on hourly time buckets.

| Column | Type | Description |
|---|---|---|
| `day` | date | Truncated to day |
| `total_consumption_kw` | double | Total meter consumption |
| `total_generation_kw` | double | Total PV generation |
| `self_consumed_kw` | double | PV consumed on-site (min of consumption, generation) |
| `exported_kw` | double | PV surplus exported to grid |
| `imported_kw` | double | Grid energy imported |
| `self_consumption_ratio` | double | Self-consumed / generated (0–1) |
| `autarky_ratio` | double | Self-consumed / consumed (0–1) |

#### `gold.traffic_pattern_hourly`

Hourly traffic patterns with rush-hour classification from `silver.traffic`.

| Column | Type | Description |
|---|---|---|
| `hour` | timestamp | Truncated to hour |
| `zone_id` | varchar | Zone identifier |
| `avg_traffic_index` | double | Average traffic index |
| `max_traffic_index` | double | Peak traffic index |
| `congested_count` | bigint | Readings with `is_congested = true` |
| `reading_count` | bigint | Total readings |
| `period` | varchar | `morning_rush` / `evening_rush` / `night` / `normal` |

#### `gold.city_dashboard_summary`

Combined Smart City KPIs per zone per day. Joins `silver.city_event`, `silver.traffic`, and `silver.streetlight`.

| Column | Type | Description |
|---|---|---|
| `day` | date | Truncated to day |
| `zone_id` | varchar | Zone identifier |
| `event_count` | bigint | Total events in zone |
| `avg_severity` | double | Average event severity |
| `avg_traffic_index` | double | Average traffic index |
| `congestion_pct` | double | Percentage of congested readings |
| `avg_dimming_pct` | double | Average streetlight dimming |
| `total_light_energy_wh` | double | Total streetlight energy |

#### `gold.device_utilization_daily`

Consumer device utilization rates and energy consumption from `silver.consumer_load`.

| Column | Type | Description |
|---|---|---|
| `day` | date | Truncated to day |
| `device_id` | varchar | Device identifier |
| `device_type` | varchar | Device type classification |
| `total_readings` | bigint | Total readings |
| `active_readings` | bigint | Readings where `is_active = true` |
| `utilization_rate` | double | Active / total readings (0–1) |
| `avg_active_power_kw` | double | Average power when active |
| `estimated_energy_kwh` | double | Estimated daily energy consumption |

#### `gold.anomaly_candidates`

Statistical outlier detection for AI pipeline input. Identifies values > 2σ from the mean using z-score analysis across three anomaly types.

| Column | Type | Description |
|---|---|---|
| `anomaly_type` | varchar | `energy_spike` / `pv_underperformance` / `voltage_deviation` |
| `event_timestamp` | timestamp | When the anomaly occurred |
| `entity_id` | varchar | Meter or PV system ID |
| `metric_value` | double | Observed value |
| `mean_value` | double | Population mean |
| `stddev_value` | double | Population standard deviation |
| `z_score` | double | Number of standard deviations from mean |

This view uses UNION ALL across: energy consumption spikes (active_power_kw > mean + 2σ), PV underperformance (power_kw < mean − 2σ, excluding zero/night), and voltage deviations (voltage > ±10% of 230V nominal). It may return zero rows if data is within normal bounds — this is expected and validated.

## 5. Setup and Management

### 5.1 Automated Setup

```bash
# Create all schemas, tables, and views
python scripts/setup_lakehouse.py --env-file .env.cluster

# Tear down (drops everything)
python scripts/setup_lakehouse.py --env-file .env.cluster --teardown
```

The script authenticates via Keycloak OIDC and executes DDL statements against Trino.

### 5.2 Validation

```bash
# Full WP3 validation (39 checks across all layers)
python scripts/validate_lakehouse.py --env-file .env.cluster

# Legacy demo validation
python scripts/demo_lakehouse.py --env-file .env.cluster
```

The `validate_lakehouse.py` script (added in WP3) performs 39 automated checks:

- **Bronze (9 checks):** Verify all 9 Iceberg tables exist and contain data
- **Silver (14 checks):** Verify all 9 views return data + 5 derived field checks (`total_active_power_w`, `apparent_power_va`, `capacity_factor`, `is_peak_hour`, `is_active`, `severity_label`)
- **Gold (13 checks):** Verify all 12 views return data (`anomaly_candidates` allowed empty)
- **Cross-layer (3 checks):** Utilization rates in [0,1], self-consumption ratios in [0,1], traffic indices in [0,1]

The script authenticates via Keycloak OIDC using a `fresh_conn()` helper that acquires a new token for each query batch (tokens are short-lived).

### 5.3 NiFi Ingestion

The NiFi pipeline is configured via:

```bash
python scripts/setup_nifi.py --env-file .env.cluster
```

See [Deployment & Operations](../deployment/deployment-operations.md) for full NiFi setup details.

## 6. Known Considerations

| Topic | Detail |
|---|---|
| Iceberg write conflicts | Occasional `AUTOCOMMIT_WRITE_CONFLICT` errors during concurrent NiFi inserts; retries resolve them |
| Trino JDBC driver | Must be present on each NiFi node; currently deployed to `/tmp/jdbc/` (requires volume mount for persistence) |
| Silver view performance | Views query raw JSON; for high-volume production, consider materializing Silver as Iceberg tables |
| Gold view joins | Cross-feed joins (net_grid_hourly, energy_cost_daily, pv_self_consumption_daily) depend on time alignment; timestamp truncation to hour/day ensures correct joins |
| S3 partitioning | Bronze tables are partitioned by `day(ingestion_timestamp)` for efficient time-range pruning |
| OIDC token expiry | Keycloak tokens are short-lived; long-running scripts must refresh tokens between query batches (see `fresh_conn()` in validate_lakehouse.py) |
| Anomaly detection | `gold.anomaly_candidates` uses z-scores (>2σ) and may return zero rows for well-behaved data — this is expected, not an error |
| Correlated subqueries | Trino does not support correlated subqueries inside GROUP BY; use proper JOINs between pre-aggregated subqueries instead |

## 7. Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| `401 Invalid credentials` during script run | OIDC token expired or wrong `.env.cluster` credentials | Verify `FACIS_OIDC_USERNAME`, `PASSWORD`, and `CLIENT_SECRET` in `.env.cluster`. Tokens are short-lived; scripts use `fresh_conn()` to auto-refresh. |
| `SCHEMA_NOT_FOUND: Schema 'bronze' does not exist` | Schemas not created yet | Run `python scripts/setup_lakehouse.py --env-file .env.cluster` (without `--teardown`). |
| Bronze tables exist but are empty | NiFi pipeline not running or Kafka topics have no data | 1) Verify simulation is posting to ORCE/Kafka. 2) Run `python scripts/setup_nifi.py --env-file .env.cluster`. 3) Check NiFi UI for error bulletins. |
| `AUTOCOMMIT_WRITE_CONFLICT` errors in NiFi logs | Concurrent Iceberg writes from multiple NiFi tasks | Transient; NiFi automatically retries. Reduce NiFi concurrent task count if persistent. |
| Gold view returns NULL for price/cost columns | Meter and price data don't overlap at the same hour | Expected for `net_grid_hourly`; use `gold.energy_cost_daily` (daily granularity) which has broader time alignment. |
| `gold.anomaly_candidates` returns zero rows | No statistical outliers (values within 2σ of mean) | Expected behavior for well-behaved data. The view will populate when genuine outliers appear. |
| `TrinoUserError: EXPRESSION_NOT_AGGREGATE` | Correlated subquery used inside GROUP BY | Trino limitation. Refactor to use JOINs between pre-aggregated subqueries (CTEs). |
| `Connection refused` or timeout on Trino | Trino pod not running or network unreachable | Verify `212.132.83.150:8443` is reachable. Check K8s: `kubectl get pods -n stackable` for Trino coordinator status. |
| `pip install -e ".[lakehouse]"` fails | Python version < 3.11 or missing build tools | Run `python --version` (need 3.11+). Install build tools: `pip install setuptools wheel`. |
| Silver view returns fewer rows than Bronze | Data quality WHERE clauses filtering malformed records | By design. Check Bronze for records with null timestamps or invalid values (negative power, out-of-range temperatures). |

## 8. Quick Start

For a step-by-step reproduction guide, see [QUICKSTART_LAKEHOUSE.md](QUICKSTART_LAKEHOUSE.md).

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
