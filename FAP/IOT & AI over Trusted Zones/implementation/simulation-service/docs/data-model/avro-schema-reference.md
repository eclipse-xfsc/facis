# Avro Schema Reference — Bronze & Silver Layers

**Project:** FACIS FAP — IoT & AI Demonstrator
**Version:** 1.0
**Date:** 07 March 2026
**Spec Reference:** Section 12.2–12.3 — Protocol-Agnostic Internal Data Model

---

## 1. Overview

This document defines the Apache Avro schemas used to consume simulation data into the Lakehouse medallion architecture. Schemas are organised into two layers following the protocol-agnostic internal data model described in the project specification.

The Bronze layer stores raw, unmodified JSON payloads exactly as received from the Kafka topics. The Silver layer applies harmonization: nested fields are flattened, metadata columns are added, and enum types enforce domain constraints.

All schema files are located in `schemas/avro/` relative to the simulation-service root.

```
schemas/avro/
├── bronze/
│   ├── bronze_energy_meter.avsc
│   ├── bronze_pv_generation.avsc
│   ├── bronze_weather.avsc
│   ├── bronze_energy_price.avsc
│   └── bronze_consumer_load.avsc
├── silver/
│   ├── silver_energy_meter.avsc
│   ├── silver_pv_generation.avsc
│   ├── silver_weather.avsc
│   ├── silver_energy_price.avsc
│   └── silver_consumer_load.avsc
└── examples/
    ├── bronze_energy_meter.json
    ├── bronze_pv_generation.json
    ├── bronze_weather.json
    ├── bronze_energy_price.json
    ├── bronze_consumer_load.json
    ├── silver_energy_meter.json
    ├── silver_pv_generation.json
    ├── silver_weather.json
    ├── silver_energy_price.json
    └── silver_consumer_load.json
```

---

## 2. Kafka Topic Naming Convention

All simulation topics follow the pattern `sim.<domain>.<feed>`. The domain is either `smart_energy` or `smart_city`. This document covers the 5 Smart Energy feeds.

| Feed | Kafka Topic | Partition Key | Partitions |
|---|---|---|---|
| Energy Meter | `sim.smart_energy.meter` | `meter_id` | 1 |
| PV Generation | `sim.smart_energy.pv` | `pv_system_id` | 1 |
| Weather | `sim.smart_energy.weather` | `site_id` | 1 |
| Energy Price | `sim.smart_energy.price` | (default) | 1 |
| Consumer Load | `sim.smart_energy.consumer` | `device_id` | 1 |

Topic configuration is managed by Stackable Kafka operator. The simulation service publishes to these topics via the ORCE (Node-RED) routing layer in cluster mode, or directly via `confluent-kafka` in local mode.

---

## 3. Bronze Layer Schema Design

The Bronze layer uses a uniform envelope schema across all feeds. Each record stores the verbatim JSON from Kafka plus ingestion metadata. No parsing, filtering, or transformation is applied.

### 3.1 Common Bronze Fields

| Field | Avro Type | Description |
|---|---|---|
| `ingest_timestamp` | `long` (timestamp-millis) | UTC wall-clock time when NiFi wrote the record to the Iceberg table |
| `source_topic` | `string` | Kafka topic name (e.g. `sim.smart_energy.meter`) |
| `kafka_partition` | `int` | Kafka partition number |
| `kafka_offset` | `long` | Kafka offset within the partition |
| `kafka_key` | `union(null, string)` | Kafka record key (feed-specific; see topic table above) |
| `raw_payload` | `string` | Verbatim JSON payload — no parsing or transformation |

### 3.2 Namespace Convention

All Bronze schemas use the Avro namespace `cloud.facis.fap.iotai.bronze`. Record names follow the pattern `Bronze<FeedName>` (e.g. `BronzeEnergyMeter`, `BronzePvGeneration`).

### 3.3 Iceberg Table Mapping

Each Bronze Avro schema maps to one Iceberg table in the `bronze` schema of the Trino catalog `fap-iotai-stackable`:

| Avro Schema | Iceberg Table |
|---|---|
| `BronzeEnergyMeter` | `bronze.energy_meter` |
| `BronzePvGeneration` | `bronze.pv_generation` |
| `BronzeWeather` | `bronze.weather` |
| `BronzeEnergyPrice` | `bronze.energy_price` |
| `BronzeConsumerLoad` | `bronze.consumer_load` |

---

## 4. Silver Layer Schema Design

The Silver layer applies three transformations to Bronze data: JSON field extraction and flattening, metadata enrichment (site_id, building_id), and type-safe enum encoding for categorical fields.

### 4.1 Common Silver Fields

Every Silver schema starts with these metadata columns:

| Field | Avro Type | Description |
|---|---|---|
| `event_timestamp` | `long` (timestamp-millis) | Original event time from the simulation (UTC) |
| `ingest_timestamp` | `long` (timestamp-millis) | Inherited from the Bronze record |
| `site_id` | `string` | Logical site identifier for cross-feed correlation |
| `building_id` | `union(null, string)` | Optional sub-site identifier (reserved for multi-building) |
| `schema_version` | `string` | Source payload schema version (default `1.0`) |

### 4.2 Namespace Convention

All Silver schemas use the Avro namespace `cloud.facis.fap.iotai.silver`. Record names follow the pattern `Silver<FeedName>`.

---

## 5. Field Mapping — Energy Meter

### 5.1 Bronze → Silver Transformation

| Silver Field | Source Path (JSON) | Type | Unit |
|---|---|---|---|
| `event_timestamp` | `$.timestamp` | timestamp-millis | UTC |
| `site_id` | `$.site_id` | string | — |
| `meter_id` | `$.meter_id` | string | — |
| `asset_id` | `$.asset_id` | string | — |
| `active_power_kw` | `$.active_power_kw` | double | kW |
| `active_energy_kwh_total` | `$.active_energy_kwh_total` | double | kWh |
| `active_power_l1_w` | `$.readings.active_power_l1_w` | double | W |
| `active_power_l2_w` | `$.readings.active_power_l2_w` | double | W |
| `active_power_l3_w` | `$.readings.active_power_l3_w` | double | W |
| `voltage_l1_v` | `$.readings.voltage_l1_v` | double | V |
| `voltage_l2_v` | `$.readings.voltage_l2_v` | double | V |
| `voltage_l3_v` | `$.readings.voltage_l3_v` | double | V |
| `current_l1_a` | `$.readings.current_l1_a` | double | A |
| `current_l2_a` | `$.readings.current_l2_a` | double | A |
| `current_l3_a` | `$.readings.current_l3_a` | double | A |
| `power_factor` | `$.readings.power_factor` | double | — |
| `frequency_hz` | `$.readings.frequency_hz` | double | Hz |
| `total_energy_kwh` | `$.readings.total_energy_kwh` | double | kWh |

Flattened fields: 12 fields extracted from the nested `readings` object to top-level columns.

---

## 6. Field Mapping — PV Generation

### 6.1 Bronze → Silver Transformation

| Silver Field | Source Path (JSON) | Type | Unit |
|---|---|---|---|
| `event_timestamp` | `$.timestamp` | timestamp-millis | UTC |
| `site_id` | `$.site_id` | string | — |
| `pv_system_id` | `$.pv_system_id` | string | — |
| `asset_id` | `$.asset_id` | string | — |
| `pv_power_kw` | `$.pv_power_kw` | double | kW |
| `power_output_kw` | `$.readings.power_output_kw` | double | kW |
| `daily_energy_kwh` | `$.readings.daily_energy_kwh` | double | kWh |
| `irradiance_w_m2` | `$.readings.irradiance_w_m2` | double | W/m² |
| `module_temperature_c` | `$.readings.module_temperature_c` | double | °C |
| `efficiency_percent` | `$.readings.efficiency_percent` | double | % |

Flattened fields: 5 fields extracted from the nested `readings` object.

---

## 7. Field Mapping — Weather

### 7.1 Bronze → Silver Transformation

| Silver Field | Source Path (JSON) | Type | Unit |
|---|---|---|---|
| `event_timestamp` | `$.timestamp` | timestamp-millis | UTC |
| `site_id` | `$.site_id` | string | — |
| `temperature_c` | `$.temperature_c` | double | °C |
| `solar_irradiance_w_m2` | `$.solar_irradiance_w_m2` | double | W/m² |
| `latitude` | `$.location.latitude` | double | degrees |
| `longitude` | `$.location.longitude` | double | degrees |
| `humidity_percent` | `$.conditions.humidity_percent` | double | % |
| `wind_speed_ms` | `$.conditions.wind_speed_ms` | double | m/s |
| `wind_direction_deg` | `$.conditions.wind_direction_deg` | double | degrees |
| `cloud_cover_percent` | `$.conditions.cloud_cover_percent` | double | % |
| `ghi_w_m2` | `$.conditions.ghi_w_m2` | double | W/m² |
| `dni_w_m2` | `$.conditions.dni_w_m2` | double | W/m² |
| `dhi_w_m2` | `$.conditions.dhi_w_m2` | double | W/m² |

Flattened fields: 2 from `location.*` + 7 from `conditions.*` = 9 fields extracted.

---

## 8. Field Mapping — Energy Price

### 8.1 Bronze → Silver Transformation

| Silver Field | Source Path (JSON) | Type | Unit |
|---|---|---|---|
| `event_timestamp` | `$.timestamp` | timestamp-millis | UTC |
| `site_id` | `$.site_id` | string | — |
| `price_eur_per_kwh` | `$.price_eur_per_kwh` | double | EUR/kWh |
| `tariff_type` | `$.tariff_type` | enum(TariffType) | — |

Enum values for `TariffType`: `NIGHT`, `MORNING_PEAK`, `MIDDAY`, `EVENING_PEAK`, `EVENING`.

Tariff time bands: NIGHT 00:00–06:00, MORNING_PEAK 06:00–09:00, MIDDAY 09:00–17:00, EVENING_PEAK 17:00–20:00, EVENING 20:00–00:00.

No nested fields to flatten — this feed is flat at source.

---

## 9. Field Mapping — Consumer Load

### 9.1 Bronze → Silver Transformation

| Silver Field | Source Path (JSON) | Type | Unit |
|---|---|---|---|
| `event_timestamp` | `$.timestamp` | timestamp-millis | UTC |
| `site_id` | `$.site_id` | string | — |
| `device_id` | `$.device_id` | string | — |
| `asset_id` | `$.asset_id` | string | — |
| `device_type` | `$.device_type` | enum(DeviceType) | — |
| `device_state` | `$.device_state` | enum(DeviceState) | — |
| `device_power_kw` | `$.device_power_kw` | double | kW |

Enum values for `DeviceType`: `INDUSTRIAL_OVEN`, `HVAC`, `COMPRESSOR`, `PUMP`, `GENERIC`.

Enum values for `DeviceState`: `ON`, `OFF`, `STANDBY`.

No nested fields to flatten — this feed is flat at source.

---

## 10. Schema Validation

Schemas can be validated using Apache Avro tools or any Avro-compatible library.

### 10.1 Using avro-tools CLI

```bash
# Download avro-tools (one-time)
curl -O https://dlcdn.apache.org/avro/avro-1.11.4/java/avro-tools-1.11.4.jar

# Validate a schema file
java -jar avro-tools-1.11.4.jar compile schema \
  schemas/avro/bronze/bronze_energy_meter.avsc /tmp/avro-out

# Validate all Bronze schemas
for f in schemas/avro/bronze/*.avsc; do
  echo "Validating $f ..."
  java -jar avro-tools-1.11.4.jar compile schema "$f" /tmp/avro-out
done

# Validate all Silver schemas
for f in schemas/avro/silver/*.avsc; do
  echo "Validating $f ..."
  java -jar avro-tools-1.11.4.jar compile schema "$f" /tmp/avro-out
done
```

### 10.2 Using Python (fastavro)

```python
import json
from fastavro.schema import parse_schema

for layer in ("bronze", "silver"):
    for path in sorted(Path(f"schemas/avro/{layer}").glob("*.avsc")):
        with open(path) as f:
            schema = json.load(f)
        parse_schema(schema)
        print(f"  OK  {path}")
```

### 10.3 Example Record Validation

```python
from fastavro import writer, reader, parse_schema
import json, io

schema = json.load(open("schemas/avro/silver/silver_energy_meter.avsc"))
parsed = parse_schema(schema)
record = json.load(open("schemas/avro/examples/silver_energy_meter.json"))

buf = io.BytesIO()
writer(buf, parsed, [record])
buf.seek(0)
for rec in reader(buf):
    print(rec)
```

---

## 11. Design Decisions

**Why Avro over Parquet for schema definitions?** Avro provides a schema-first contract that is language-neutral, supports schema evolution (field addition with defaults), and is natively supported by Kafka, NiFi, and Trino. The Iceberg tables use Parquet as the storage format, but the logical schema is defined in Avro for interchange.

**Why a uniform Bronze schema?** All five Bronze schemas share the same structure (ingest metadata + raw payload). This simplifies the NiFi pipeline: a single ConsumeKafka → PutIceberg template handles all feeds, differing only in topic name and table name. The raw_payload field preserves the original JSON for reprocessing if the Silver schema evolves.

**Why flatten at Silver?** Trino SQL does not natively query nested JSON fields efficiently. Flattening nested structures (readings.*, location.*, conditions.*) to top-level columns enables direct SQL access with standard WHERE, GROUP BY, and JOIN operations. This aligns with the specification's protocol-agnostic internal data model (Section 12.2–12.3).

**Why add building_id at Silver?** The current simulation targets a single site (site-berlin-001). The building_id field (nullable, defaulting to null) is reserved for future multi-building deployments without requiring a schema migration.

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
