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
| Silver | `silver` | Trino views over Bronze | 9 | Typed field extraction, timestamp parsing |
| Gold | `gold` | Trino views over Silver | 6 | Aggregated KPIs, curated analytics |

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

## 3. Silver Layer — Typed Extraction

Silver views extract and type JSON fields from Bronze tables using `json_extract_scalar()` and `from_iso8601_timestamp()`.

### 3.1 Design Principles

- All timestamps use `from_iso8601_timestamp()` (not `CAST AS TIMESTAMP`) to handle the `Z` UTC suffix
- Nested JSON fields are extracted with `$.path.to.field` notation
- Numeric fields are cast to `DOUBLE`
- Integer fields are cast to `INTEGER`
- Boolean fields are cast to `BOOLEAN`
- Original `ingestion_timestamp` is preserved for data lineage

### 3.2 Example: `silver.energy_meter`

```sql
CREATE OR REPLACE VIEW silver.energy_meter AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    json_extract_scalar(raw_value, '$.site_id')                          AS site_id,
    json_extract_scalar(raw_value, '$.meter_id')                         AS meter_id,
    CAST(json_extract_scalar(raw_value, '$.active_power_kw') AS DOUBLE)  AS active_power_kw,
    CAST(json_extract_scalar(raw_value, '$.active_energy_kwh_total') AS DOUBLE) AS active_energy_kwh_total,
    CAST(json_extract_scalar(raw_value, '$.readings.voltage_l1_v') AS DOUBLE) AS voltage_l1_v,
    CAST(json_extract_scalar(raw_value, '$.readings.voltage_l2_v') AS DOUBLE) AS voltage_l2_v,
    CAST(json_extract_scalar(raw_value, '$.readings.voltage_l3_v') AS DOUBLE) AS voltage_l3_v,
    CAST(json_extract_scalar(raw_value, '$.readings.current_l1_a') AS DOUBLE) AS current_l1_a,
    CAST(json_extract_scalar(raw_value, '$.readings.current_l2_a') AS DOUBLE) AS current_l2_a,
    CAST(json_extract_scalar(raw_value, '$.readings.current_l3_a') AS DOUBLE) AS current_l3_a,
    CAST(json_extract_scalar(raw_value, '$.readings.power_factor') AS DOUBLE) AS power_factor,
    CAST(json_extract_scalar(raw_value, '$.readings.frequency_hz') AS DOUBLE) AS frequency_hz,
    message_key
FROM bronze.energy_meter
```

### 3.3 Silver View Inventory

| View | Key Extracted Fields |
|---|---|
| `silver.energy_meter` | event_timestamp, meter_id, active_power_kw, energy_kwh, voltage L1-L3, current L1-L3, PF, frequency |
| `silver.pv_generation` | event_timestamp, pv_system_id, power_kw, daily_energy, irradiance, module_temp, efficiency |
| `silver.weather` | event_timestamp, temperature, humidity, wind_speed/direction, cloud_cover, GHI/DNI/DHI |
| `silver.energy_price` | event_timestamp, price_eur_per_kwh, tariff_type |
| `silver.consumer_load` | event_timestamp, device_id, device_type, device_state, power_kw |
| `silver.streetlight` | event_timestamp, zone_id, light_id, dimming_level_pct, power_w, is_on |
| `silver.traffic` | event_timestamp, zone_id, traffic_index |
| `silver.city_event` | event_timestamp, zone_id, event_type, severity, active |
| `silver.city_weather` | event_timestamp, city_id, fog_index, visibility, sunrise_time, sunset_time |

## 4. Gold Layer — Curated Analytics

Gold views aggregate Silver data into analytics-ready KPIs for dashboarding and AI services.

### 4.1 `gold.energy_balance_hourly`

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

### 4.2 `gold.pv_performance_hourly`

Hourly PV generation metrics per system.

| Column | Type | Description |
|---|---|---|
| `hour` | timestamp | Truncated to hour |
| `pv_system_id` | varchar | PV system identifier |
| `avg_power_kw` | double | Average PV output |
| `peak_power_kw` | double | Maximum PV output |
| `avg_irradiance` | double | Average solar irradiance (W/m²) |
| `avg_efficiency` | double | Average conversion efficiency (%) |

### 4.3 `gold.net_grid_hourly`

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

### 4.4 `gold.streetlight_zone_hourly`

Hourly streetlight metrics per zone.

| Column | Type | Description |
|---|---|---|
| `hour` | timestamp | Truncated to hour |
| `zone_id` | varchar | Zone identifier |
| `avg_dimming_pct` | double | Average dimming level |
| `total_power_w` | double | Total zone power consumption |
| `light_count` | bigint | Number of active lights |

### 4.5 `gold.event_impact_daily`

Daily event statistics per zone and type.

| Column | Type | Description |
|---|---|---|
| `day` | date | Truncated to day |
| `zone_id` | varchar | Zone identifier |
| `event_type` | varchar | Event classification |
| `event_count` | bigint | Number of events |
| `avg_severity` | double | Average severity level |
| `active_count` | bigint | Number of currently active events |

### 4.6 `gold.weather_hourly`

Hourly weather aggregations.

| Column | Type | Description |
|---|---|---|
| `hour` | timestamp | Truncated to hour |
| `avg_temperature_c` | double | Average temperature |
| `avg_humidity_pct` | double | Average relative humidity |
| `avg_wind_speed_ms` | double | Average wind speed |
| `avg_cloud_cover_pct` | double | Average cloud cover |
| `avg_ghi_w_m2` | double | Average Global Horizontal Irradiance |

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
# Validate all layers via Trino
python scripts/demo_lakehouse.py --env-file .env.cluster
```

Checks: Bronze row counts, Silver view accessibility, Gold query results, data freshness, and feed coverage.

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
| Gold view joins | Cross-feed joins (net_grid_hourly) depend on time alignment; timestamp truncation to hour ensures correct joins |
| S3 partitioning | Bronze tables are partitioned by `day(ingestion_timestamp)` for efficient time-range pruning |

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
