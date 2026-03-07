# FACIS MS2 Technical Reference — End-to-End Pipeline

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Component Architecture](#2-component-architecture)
3. [Simulation Service](#3-simulation-service)
4. [ORCE — Orchestration Engine](#4-orce--orchestration-engine)
5. [Kafka Cluster](#5-kafka-cluster)
6. [Apache NiFi — Ingestion Pipeline](#6-apache-nifi--ingestion-pipeline)
7. [Trino + Iceberg Data Lakehouse](#7-trino--iceberg-data-lakehouse)
8. [Kubernetes Deployment (Stackable)](#8-kubernetes-deployment-stackable)
9. [TLS/mTLS Certificate Management](#9-tlsmtls-certificate-management)
10. [Authentication & Authorization](#10-authentication--authorization)
11. [Configuration Reference](#11-configuration-reference)
12. [Deployment Procedures](#12-deployment-procedures)
13. [Monitoring & Troubleshooting](#13-monitoring--troubleshooting)
14. [Data Schema Reference](#14-data-schema-reference)

---

## 1. System Overview

### Data Flow

```
Simulation Service (Docker, local)
    │
    │  HTTP POST /api/sim/tick (JSON envelope, ~1/sec)
    ▼
ORCE — Node-RED (Docker, local)
    │
    │  9x rdkafka producers (mTLS over port 9093)
    ▼
Kafka Cluster (Kubernetes, Stackable)
    │
    │  9 topics: sim.smart_energy.{meter,pv,weather,price,consumer}
    │            sim.smart_city.{light,traffic,event,weather}
    ▼
Apache NiFi 2.6 (Kubernetes, Stackable)
    │
    │  ConsumeKafka → ReplaceText (escape + build SQL) → PutSQL (JDBC)
    ▼
Trino + Iceberg (Kubernetes, Stackable)
    │
    │  Bronze (9 Iceberg tables, Parquet on S3)
    │  Silver (9 views, typed JSON extraction)
    │  Gold   (6 views, hourly/daily aggregation)
    ▼
S3 Storage (IONOS, bucket: fap-iotai-stackable)
    │
    ▼
Superset (Kubernetes) — dashboards on Gold views
```

### Component Inventory

| Component | Version | Deployment | Endpoint |
|-----------|---------|------------|----------|
| Simulation Service | Custom (Python 3.11) | Docker Compose (local) | `localhost:8080` |
| ORCE (Node-RED) | ecofacis/xfsc-orce:2.0.3 | Docker Compose (local) | `localhost:1880` |
| MQTT (Mosquitto) | 2.x | Docker Compose (local) | `localhost:1883` |
| Kafka | Stackable | Kubernetes | `212.132.83.222:9093` (TLS) |
| NiFi | 2.6 | Kubernetes (Stackable) | Internal only |
| Trino | Stackable | Kubernetes | `212.132.83.150:8443` (HTTPS) |
| Keycloak | Stackable | Kubernetes | `https://identity.facis.cloud` |
| S3 | IONOS | External | `s3.eu-central-1.ionoscloud.com` |
| Superset | Stackable | Kubernetes | `http://212.132.76.221:8088` |

---

## 2. Component Architecture

### 2.1 Simulation Service

```
src/
├── api/
│   ├── rest/           # FastAPI REST API (port 8080)
│   │   ├── app.py      # Lifespan, PublishOrchestrator, route registration
│   │   └── dependencies.py  # DI: SimulationState singleton
│   ├── kafka/          # Kafka producer (confluent-kafka)
│   │   └── producer.py # KafkaPublisher + KafkaFeedPublisher
│   ├── mqtt/           # MQTT publisher (paho-mqtt)
│   │   └── publisher.py # MQTTPublisher + MQTTFeedPublisher
│   └── orce/           # ORCE HTTP client (httpx)
│       ├── client.py   # ORCEClient async POST
│       └── envelope.py # TickEnvelope builder
├── core/
│   ├── engine.py       # SimulationEngine state machine
│   ├── clock.py        # SimulationClock (UTC, acceleration)
│   ├── random_generator.py  # DeterministicRNG (seed-based)
│   └── time_series.py  # BaseTimeSeriesGenerator framework
├── models/
│   ├── meter.py, pv.py, weather.py, price.py, consumer_load.py
│   ├── correlation.py  # CorrelatedSnapshot, DerivedMetrics
│   └── smart_city/     # streetlight.py, traffic.py, event.py, visibility.py
├── simulators/
│   ├── energy_meter/simulator.py    # 3-phase meter generation
│   ├── pv_generation/simulator.py   # PV physics model
│   ├── weather/simulator.py         # Atmospheric simulation
│   ├── energy_price/simulator.py    # EPEX Spot market model
│   ├── consumer_load/simulator.py   # Industrial device cycles
│   └── smart_city/
│       ├── correlation.py           # SmartCityCorrelationEngine
│       ├── streetlight.py           # Event-reactive dimming
│       ├── traffic.py               # Traffic flow patterns
│       ├── event.py                 # City event generation
│       └── visibility.py            # Atmospheric visibility
└── config.py           # Pydantic Settings (YAML + env vars)
```

### 2.2 Correlation Engines

**Smart Energy Correlation** (`src/simulators/correlation/engine.py`):
1. Weather generated first (dependency for PV)
2. PV uses weather irradiance + temperature
3. Meters, consumer loads, and prices generated in parallel
4. Derived metrics calculated: `total_consumption`, `total_generation`, `net_grid_power`, `self_consumption_ratio`, `current_cost_eur_per_hour`

**Smart City Correlation** (`src/simulators/smart_city/correlation.py`):
1. City events generated first
2. Events passed to streetlight simulator per zone
3. Streetlights apply dimming boost based on event severity (sev 2: +30%, sev 3: +50%)
4. Traffic and visibility generated independently

### 2.3 Publish Orchestrator

The `PublishOrchestrator` in `src/api/rest/app.py` runs as a background asyncio task:

```
Loop:
  1. Advance simulation clock by interval_minutes
  2. energy_snapshot = energy_correlation.generate_snapshot(sim_time)
  3. city_snapshot = smart_city_correlation.generate_snapshot(sim_time)
  4. Publish to MQTT (all feeds, per-topic)
  5. Publish to Kafka (all feeds, per-topic)
  6. POST tick envelope to ORCE (all feeds, single HTTP POST)
  7. Sleep for (interval_seconds / speed_factor)
```

**Timing:** With `speed_factor=60` and `interval_minutes=1`:
- Real interval = 60 seconds / 60 = **1 second** between ticks
- Each tick advances simulation time by 1 minute

---

## 3. Simulation Service

### 3.1 Configuration

**Primary config:** `config/default.yaml` (all defaults)
**Cluster overlay:** `config/cluster.yaml` (cluster-specific overrides)

Config loading priority:
1. `config/default.yaml` (base)
2. `config/{SIMULATOR_ENV}.yaml` (deep merge)
3. Environment variables `SIMULATOR_*` (override)
4. Pydantic validation

**Key cluster.yaml settings:**

```yaml
simulation:
  speed_factor: 60.0    # 60x faster (1 sim-minute per real-second)

kafka:
  enabled: false         # Direct Kafka disabled in cluster mode

orce:
  enabled: true          # ORCE handles Kafka publishing
  url: "http://orce:1880"
  webhook_path: "/api/sim/tick"
  timeout_seconds: 15
```

### 3.2 Docker Compose

**Local + Cluster mode** (`docker-compose.yml` + `docker-compose.cluster.yml`):

```bash
# Start with cluster mode (ORCE publishes to remote Kafka)
docker compose -f docker-compose.yml -f docker-compose.cluster.yml up --build
```

The cluster override:
- Sets `SIMULATOR_ENV=cluster` to load `config/cluster.yaml`
- Mounts TLS certificates into ORCE at `/certs/`
- Uses the cluster ORCE flow (`facis-simulation-cluster.json`)

### 3.3 Tick Envelope Format

Every tick, the simulation POSTs this JSON to ORCE:

```json
{
  "type": "sim.tick",
  "schema_version": "1.0",
  "timestamp": "2026-03-08T14:00:00Z",
  "mode": "normal",
  "seed": 12345,
  "site_id": "site-berlin-001",
  "smart_energy": {
    "meters": [
      {
        "timestamp": "2026-03-08T14:00:00Z",
        "site_id": "site-berlin-001",
        "meter_id": "janitza-umg96rm-001",
        "asset_id": "janitza-umg96rm-001",
        "schema_version": "1.0",
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
    ],
    "pv": [...],
    "weather": {...},
    "price": {...},
    "consumers": [...],
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
    "streetlights": [...],
    "traffic_readings": [...],
    "events": [...],
    "visibility": {...}
  }
}
```

---

## 4. ORCE — Orchestration Engine

### 4.1 Architecture

ORCE is a customized [Node-RED](https://nodered.org/) instance (ecofacis/xfsc-orce:2.0.3) with added Kafka support via `node-red-contrib-rdkafka` and a custom SSL/mTLS patch.

**Flow:** `orce/flows/facis-simulation-cluster.json`

```
HTTP POST /api/sim/tick
    ↓
Validate Schema (check required fields: type, schema_version, timestamp, site_id, smart_energy, smart_city)
    ↓
Split Feeds (extract individual messages from envelope)
    ↓
Route to Kafka Topic (9-output router based on msg.topic)
    ↓
9x rdkafka Producers (one per topic, mTLS to Kafka cluster)
    ↓
HTTP 200 OK (messages_queued count returned)
```

### 4.2 Dockerfile

```dockerfile
FROM ecofacis/xfsc-orce:2.0.3

# Build rdkafka native extension
RUN apk add --no-cache librdkafka-dev python3 make g++
RUN mkdir -p /opt/rdkafka-staging && \
    cd /opt/rdkafka-staging && \
    npm init -y && \
    npm install node-red-contrib-rdkafka

# SSL/mTLS patch for broker config
COPY rdkafka-patch.js /opt/rdkafka-staging/rdkafka-patch.js

# Custom entrypoint
COPY entrypoint.sh /usr/local/bin/entrypoint-rdkafka.sh
ENTRYPOINT ["/usr/local/bin/entrypoint-rdkafka.sh"]
```

### 4.3 SSL Patch (`rdkafka-patch.js`)

The stock `node-red-contrib-rdkafka` does not support SSL/mTLS. The patch:
- Adds `securityProtocol`, `sslCaLocation`, `sslCertLocation`, `sslKeyLocation` properties to `kafka-broker` config node
- `getBaseConfig()` injects `security.protocol=ssl` and cert paths into librdkafka config
- Applied at container startup by `entrypoint.sh`

### 4.4 Entrypoint (`entrypoint.sh`)

1. Copies `node-red-contrib-rdkafka` + dependencies from `/opt/rdkafka-staging/` to `/data/node_modules/`
2. Applies SSL patch: overwrites `rdkafka.js` with patched version
3. Registers the package in `/data/package.json`
4. Fixes ownership to `node-red` user
5. Delegates to original ORCE entrypoint

### 4.5 Kafka Broker Configuration (in flow JSON)

```json
{
  "id": "kafka-broker-config",
  "type": "kafka-broker",
  "name": "FACIS Kafka Cluster",
  "broker": "212.132.83.222:9093",
  "clientid": "facis-orce",
  "securityProtocol": "ssl",
  "sslCaLocation": "/certs/ca.crt",
  "sslCertLocation": "/certs/client.crt",
  "sslKeyLocation": "/certs/client.key"
}
```

### 4.6 Feed Splitting Logic

The "Split Feeds" function node extracts individual messages with Kafka routing keys:

| Envelope Path | Kafka Topic | Message Key |
|---------------|-------------|-------------|
| `smart_energy.meters[]` | `sim.smart_energy.meter` | `meter_id` or `asset_id` |
| `smart_energy.pv[]` | `sim.smart_energy.pv` | `pv_system_id` or `asset_id` |
| `smart_energy.weather` | `sim.smart_energy.weather` | `site_id` |
| `smart_energy.price` | `sim.smart_energy.price` | `"price"` |
| `smart_energy.consumers[]` | `sim.smart_energy.consumer` | `device_id` or `asset_id` |
| `smart_city.streetlights[]` | `sim.smart_city.light` | `light_id` |
| `smart_city.traffic_readings[]` | `sim.smart_city.traffic` | `zone_id` |
| `smart_city.events[]` | `sim.smart_city.event` | `zone_id` |
| `smart_city.visibility` | `sim.smart_city.weather` | `city_id` or `"city"` |

---

## 5. Kafka Cluster

### 5.1 Access

| Endpoint | Protocol | Use |
|----------|----------|-----|
| `212.132.83.222:9093` | TLS/mTLS | External access (ORCE, scripts) |
| `kafka-broker-default-headless.stackable.svc.cluster.local:9093` | TLS/mTLS | Internal K8s (NiFi) |

**Important:** The TLS certificate SANs include `kafka-broker-default-headless.stackable.svc.cluster.local` and the external IP `212.132.83.222`. The `kafka-broker-default-bootstrap` service name is **NOT** in the SANs — always use the headless service name for internal connections.

### 5.2 Topics

| Topic | Partitions | Key | Content |
|-------|-----------|-----|---------|
| `sim.smart_energy.meter` | Auto | meter_id | JSON meter readings |
| `sim.smart_energy.pv` | Auto | pv_system_id | JSON PV readings |
| `sim.smart_energy.weather` | Auto | site_id | JSON weather data |
| `sim.smart_energy.price` | Auto | "price" | JSON price data |
| `sim.smart_energy.consumer` | Auto | device_id | JSON consumer load |
| `sim.smart_city.light` | Auto | light_id | JSON streetlight data |
| `sim.smart_city.traffic` | Auto | zone_id | JSON traffic data |
| `sim.smart_city.event` | Auto | zone_id | JSON city events |
| `sim.smart_city.weather` | Auto | city_id | JSON visibility data |

### 5.3 TLS Certificates (External Access)

Required files in `certs/` directory:

| File | Description |
|------|-------------|
| `ca.crt` | Stackable self-signed CA certificate |
| `client.crt` | Client certificate signed by the CA |
| `client.key` | Client private key |

These are extracted from the Kubernetes secrets created by Stackable's secret-operator.

### 5.4 Consumer Group

NiFi uses consumer group `facis-nifi-lakehouse` to consume from all 9 topics.

---

## 6. Apache NiFi — Ingestion Pipeline

### 6.1 Architecture

NiFi 2.6 runs on Stackable Kubernetes as a 2-node cluster. The ingestion pipeline consists of:

- **1 Process Group:** "FACIS Lakehouse Ingestion"
- **3 Controller Services:** SSL Context, Kafka Connection, Trino JDBC Pool
- **9 Flows** (one per Kafka topic, 4 processors each = **36 processors total**)

### 6.2 Controller Services

#### StandardSSLContextService ("Stackable TLS Context")

| Property | Value |
|----------|-------|
| Keystore Filename | `/stackable/server_tls/keystore.p12` |
| Keystore Type | PKCS12 |
| Keystore Password | `secret` |
| Truststore Filename | `/stackable/server_tls/truststore.p12` |
| Truststore Type | PKCS12 |
| Truststore Password | `secret` |

#### Kafka3ConnectionService ("FACIS Kafka Connection")

| Property | Value |
|----------|-------|
| Bootstrap Servers | `kafka-broker-default-headless.stackable.svc.cluster.local:9093` |
| Security Protocol | SSL |
| SSL Context Service | Stackable TLS Context |

**Note:** Must use the headless service name — the bootstrap service name is not in the Kafka TLS certificate SANs.

#### DBCPConnectionPool ("Trino JDBC Pool")

| Property | Value |
|----------|-------|
| Database Connection URL | `jdbc:trino://trino-coordinator-default-headless.stackable.svc.cluster.local:8443/fap-iotai-stackable/bronze?SSL=true&SSLVerification=NONE` |
| Database Driver Class Name | `io.trino.jdbc.TrinoDriver` |
| Database Driver Location | `/tmp/jdbc/trino-jdbc-467.jar` |
| Database User | `<trino-user>` |
| Database Password | `<trino-password>` |
| database-session-autocommit | `true` |

**Critical Notes:**
- Must use headless Trino service name (`trino-coordinator-default-headless`) — the regular service name is not in TLS SANs
- `SSLVerification=NONE` because Trino uses Stackable self-signed certs
- `autocommit=true` is **required** — Trino Iceberg does not support managed transactions for writes
- The JDBC JAR is in `/tmp/` and will be lost on pod restart — see [Persistent JDBC Driver](#persistent-jdbc-driver) for production fix

### 6.3 Per-Topic Flow (x9)

Each Kafka topic has this processor chain:

```
ConsumeKafka
    │  (reads from topic, consumer group: facis-nifi-lakehouse)
    ▼
ReplaceText ("Escape Quotes")
    │  Search: '
    │  Replace: ''
    │  (prevents SQL injection from JSON single quotes)
    ▼
ReplaceText ("Build INSERT")
    │  Template:
    │  INSERT INTO "fap-iotai-stackable".bronze.{table} (
    │    ingestion_timestamp, kafka_topic, kafka_partition,
    │    kafka_offset, message_key, raw_value
    │  ) VALUES (
    │    CURRENT_TIMESTAMP, '${kafka.topic}',
    │    CAST(${kafka.partition} AS INTEGER),
    │    CAST(${kafka.offset} AS BIGINT),
    │    '${kafka.key}', '$1'
    │  )
    ▼
PutSQL
    │  (executes INSERT via Trino JDBC, autocommit=true)
    ▼
Bronze Iceberg Table (Parquet on S3)
```

### 6.4 Topic → Bronze Table Mapping

| Kafka Topic | Bronze Table |
|-------------|-------------|
| `sim.smart_energy.meter` | `bronze.energy_meter` |
| `sim.smart_energy.pv` | `bronze.pv_generation` |
| `sim.smart_energy.weather` | `bronze.weather` |
| `sim.smart_energy.price` | `bronze.energy_price` |
| `sim.smart_energy.consumer` | `bronze.consumer_load` |
| `sim.smart_city.light` | `bronze.streetlight` |
| `sim.smart_city.traffic` | `bronze.traffic` |
| `sim.smart_city.event` | `bronze.city_event` |
| `sim.smart_city.weather` | `bronze.city_weather` |

### 6.5 Persistent JDBC Driver

The Trino JDBC driver (`trino-jdbc-467.jar`) must be available on all NiFi nodes. For production:

**Option A: Kubernetes Volume Mount**
Mount the JAR from a ConfigMap or PersistentVolume to a stable path (e.g., `/opt/jdbc/trino-jdbc-467.jar`).

**Option B: NiFi `lib/` directory**
Copy the JAR into the NiFi installation's `lib/` directory in the container image or via an init container.

**Current workaround:** JAR manually copied to `/tmp/jdbc/` on each NiFi pod:
```bash
kubectl exec -n stackable nifi-node-default-0-0 -- \
  sh -c 'mkdir -p /tmp/jdbc && curl -L -o /tmp/jdbc/trino-jdbc-467.jar \
  https://repo1.maven.org/maven2/io/trino/trino-jdbc/467/trino-jdbc-467.jar'
```

### 6.6 Known Issues

| Issue | Impact | Mitigation |
|-------|--------|------------|
| JDBC JAR in `/tmp/` | Lost on pod restart | Volume mount or init container |
| Iceberg concurrent write conflicts | Occasional `AUTOCOMMIT_WRITE_CONFLICT` errors | PutSQL retries; Iceberg eventually accepts writes |
| NiFi 2-node partition distribution | One node may get all partitions temporarily | Kafka rebalance resolves within minutes |

---

## 7. Trino + Iceberg Data Lakehouse

### 7.1 Catalog

| Property | Value |
|----------|-------|
| Catalog Name | `fap-iotai-stackable` |
| Connector | Iceberg |
| Storage | S3 (`s3a://fap-iotai-stackable/warehouse/`) |
| Metastore | Likely Hive or internal |

### 7.2 Schemas

| Schema | Purpose | S3 Location |
|--------|---------|-------------|
| `bronze` | Raw ingestion (Iceberg tables) | `s3a://fap-iotai-stackable/warehouse/bronze.db/` |
| `silver` | Typed extraction (views) | N/A (views on Bronze) |
| `gold` | Aggregated analytics (views) | N/A (views on Silver) |

### 7.3 Bronze Tables (9)

All Bronze tables share the same schema:

```sql
CREATE TABLE IF NOT EXISTS "fap-iotai-stackable".bronze.{table} (
    ingestion_timestamp  TIMESTAMP(6) WITH TIME ZONE,
    kafka_topic          VARCHAR,
    kafka_partition      INTEGER,
    kafka_offset         BIGINT,
    message_key          VARCHAR,
    raw_value            VARCHAR   -- Full JSON payload
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['day(ingestion_timestamp)'],
    location = 's3a://fap-iotai-stackable/warehouse/bronze.db/{table}'
)
```

### 7.4 Silver Views (9)

Silver views extract and type fields from `raw_value` JSON using `json_extract_scalar()` and `from_iso8601_timestamp()`.

**Example — `silver.energy_meter`:**

```sql
CREATE OR REPLACE VIEW "fap-iotai-stackable".silver.energy_meter AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    json_extract_scalar(raw_value, '$.site_id')        AS site_id,
    json_extract_scalar(raw_value, '$.meter_id')       AS meter_id,
    CAST(json_extract_scalar(raw_value, '$.active_power_kw') AS DOUBLE) AS active_power_kw,
    CAST(json_extract_scalar(raw_value, '$.active_energy_kwh_total') AS DOUBLE) AS active_energy_kwh_total,
    CAST(json_extract_scalar(raw_value, '$.readings.voltage_l1_v') AS DOUBLE)   AS voltage_l1_v,
    -- ... (17 total columns)
    message_key
FROM "fap-iotai-stackable".bronze.energy_meter
```

**Important:** Timestamps use `from_iso8601_timestamp()` (returns `TIMESTAMP WITH TIME ZONE`), NOT `CAST(... AS TIMESTAMP)`, because the JSON timestamps include the `Z` UTC suffix.

### 7.5 Gold Views (6)

| View | Aggregation | Key Columns |
|------|-------------|-------------|
| `energy_balance_hourly` | Per-meter, per-hour | avg/peak consumption, energy consumed, reading count |
| `pv_performance_hourly` | Per-system, per-hour | avg/peak power, irradiance, efficiency |
| `net_grid_hourly` | Per-hour (joins meter + PV + price) | net grid kW, price, estimated cost EUR |
| `streetlight_zone_hourly` | Per-zone, per-hour | avg dimming %, total power, light count |
| `event_impact_daily` | Per-zone, per-day, per-type | event count, avg severity, active count |
| `weather_hourly` | Per-hour | temperature, irradiance, humidity, wind, cloud cover |

**Example — `gold.net_grid_hourly`** (the key demo metric):

```sql
CREATE OR REPLACE VIEW "fap-iotai-stackable".gold.net_grid_hourly AS
SELECT
    m.hour,
    m.avg_consumption_kw,
    COALESCE(p.avg_power_kw, 0) AS avg_generation_kw,
    m.avg_consumption_kw - COALESCE(p.avg_power_kw, 0) AS net_grid_kw,
    pr.avg_price_eur_per_kwh,
    (m.avg_consumption_kw - COALESCE(p.avg_power_kw, 0))
        * COALESCE(pr.avg_price_eur_per_kwh, 0) AS estimated_hourly_cost_eur
FROM "fap-iotai-stackable".gold.energy_balance_hourly m
LEFT JOIN (...PV subquery...) p ON m.hour = p.hour
LEFT JOIN (...Price subquery...) pr ON m.hour = pr.hour
```

### 7.6 Setup Script

```bash
# Create all schemas, Bronze tables, Silver views, Gold views
python scripts/setup_lakehouse.py --env-file .env.cluster

# Tear down everything (views, tables, schemas)
python scripts/setup_lakehouse.py --env-file .env.cluster --teardown
```

The script authenticates via Keycloak OIDC, connects to Trino with JWT, and executes DDL statements.

---

## 8. Kubernetes Deployment (Stackable)

### 8.1 Platform

The remote cluster runs [Stackable](https://stackable.tech/) — a Kubernetes-native data platform that manages Kafka, NiFi, Trino, and other data services as custom resources.

### 8.2 Namespace

All Stackable-managed services run in the `stackable` namespace.

### 8.3 Key Services

| Service | K8s Service Name | External IP | Port |
|---------|-----------------|-------------|------|
| Kafka Broker | `kafka-broker-default-headless` | 212.132.83.222 | 9093 (TLS) |
| Trino Coordinator | `trino-coordinator-default-headless` | 212.132.83.150 | 8443 (HTTPS) |
| NiFi | `nifi-node-default` | Internal only | 8443 |
| Keycloak | Via ingress | identity.facis.cloud | 443 |
| Superset | Direct | 212.132.76.221 | 8088 |

### 8.4 TLS Architecture

Stackable uses a `secret-operator` that provisions self-signed TLS certificates for all services:

- **CA:** Stackable self-signed CA (per-cluster)
- **Keystores:** PKCS12 format at `/stackable/tls-{service}-server/keystore.p12` or `/stackable/server_tls/keystore.p12`
- **Truststore:** PKCS12 at corresponding path
- **Passwords vary by service:**

| Service | Keystore Path | Password |
|---------|--------------|----------|
| NiFi | `/stackable/server_tls/keystore.p12` | `secret` |
| Kafka | `/stackable/tls-kafka-server/keystore.p12` | (empty string) |
| Trino | `/stackable/server_tls/keystore.p12` | `changeit` |

### 8.5 Certificate SANs (Critical)

Stackable generates TLS certificates with SANs matching the **headless** service FQDN:

| Service | Valid SAN | Invalid (not in cert) |
|---------|-----------|----------------------|
| Kafka | `kafka-broker-default-headless.stackable.svc.cluster.local` | `kafka-broker-default-bootstrap` |
| Trino | `trino-coordinator-default-headless.stackable.svc.cluster.local` | `trino-coordinator.stackable.svc.cluster.local` |

**Always use the headless service name for internal TLS connections.** Using the regular service name will cause `SSLPeerUnverifiedException: Hostname not verified`.

### 8.6 NiFi Pod Access

```bash
# List NiFi pods
kubectl get pods -n stackable -l app.kubernetes.io/name=nifi

# Shell into NiFi node
kubectl exec -it -n stackable nifi-node-default-0-0 -- /bin/bash

# Copy file to NiFi pod
kubectl cp local-file.jar stackable/nifi-node-default-0-0:/tmp/jdbc/
```

### 8.7 Kafka Pod Access

```bash
# List Kafka broker pods
kubectl get pods -n stackable -l app.kubernetes.io/name=kafka

# Shell into Kafka broker
kubectl exec -it -n stackable kafka-broker-default-0 -- /bin/bash

# Check consumer group lag
kubectl exec -n stackable kafka-broker-default-0 -- \
  /stackable/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9093 \
  --command-config /tmp/client.properties \
  --group facis-nifi-lakehouse --describe
```

### 8.8 Trino Pod Access

```bash
# Shell into Trino coordinator
kubectl exec -it -n stackable trino-coordinator-default-0 -- /bin/bash

# Run Trino CLI
kubectl exec -n stackable trino-coordinator-default-0 -- \
  /stackable/trino-cli --server https://localhost:8443 \
  --insecure --user admin --password
```

---

## 9. TLS/mTLS Certificate Management

### 9.1 External Kafka Access (ORCE → Kafka)

The ORCE container needs mTLS certificates to connect to Kafka:

```
certs/
├── ca.crt        # Stackable CA certificate
├── client.crt    # Client certificate
└── client.key    # Client private key
```

**Extracting from Kubernetes:**

```bash
# Get the Kafka TLS secret name
kubectl get secrets -n stackable | grep kafka

# Extract CA cert
kubectl get secret -n stackable kafka-broker-tls -o jsonpath='{.data.ca\.crt}' | base64 -d > certs/ca.crt

# Extract client cert and key (from a service account secret or generated cert)
# The exact secret name depends on your Stackable configuration
```

### 9.2 Docker Volume Mount

In `docker-compose.cluster.yml`, certs are mounted into ORCE:

```yaml
orce:
  volumes:
    - ./certs/ca.crt:/certs/ca.crt:ro
    - ./certs/client.crt:/certs/client.crt:ro
    - ./certs/client.key:/certs/client.key:ro
```

---

## 10. Authentication & Authorization

### 10.1 Keycloak OIDC (Trino)

| Property | Value |
|----------|-------|
| Realm URL | `https://identity.facis.cloud/realms/facis` |
| Client ID | `OIDC` |
| Client Secret | (in `.env.cluster`) |
| Grant Type | `password` |
| Scope | `openid` |
| Test User | Configured in `.env.cluster` |

**Token request:**

```bash
curl -k -X POST $FACIS_KEYCLOAK_URL/protocol/openid-connect/token \
  -d "client_id=OIDC" \
  -d "client_secret=$FACIS_OIDC_CLIENT_SECRET" \
  -d "username=$FACIS_OIDC_USERNAME" \
  -d "password=$FACIS_OIDC_PASSWORD" \
  -d "grant_type=password" \
  -d "scope=openid"
```

### 10.2 Trino Password Auth (NiFi JDBC)

For JDBC connections from NiFi (internal K8s), Trino uses file-based password auth. Credentials are managed by the infrastructure team and stored in `.env.cluster`.

### 10.3 Credentials File

`.env.cluster` stores all sensitive credentials. This file is **excluded from version control** via `.gitignore`. Copy from `.env.cluster.example` and fill in values provided by the infrastructure team.

Required variables: `FACIS_OIDC_USERNAME`, `FACIS_OIDC_PASSWORD`, `FACIS_OIDC_CLIENT_SECRET`, `FACIS_KEYCLOAK_URL`, `FACIS_TRINO_HOST`, `FACIS_TRINO_PORT`, `FACIS_TRINO_CATALOG`.

---

## 11. Configuration Reference

### 11.1 Simulation Parameters (`config/default.yaml`)

```yaml
simulation:
  seed: 12345                   # Deterministic RNG seed
  interval_minutes: 1           # Simulated time per tick
  speed_factor: 1.0             # 1.0=realtime, 60.0=60x faster
  mode: normal                  # normal or event
  start_time: "2026-03-08T00:00:00Z"  # Simulation start
```

### 11.2 Meters

```yaml
meters:
  - meter_id: "janitza-umg96rm-001"
    base_power_kw: 10.0
    peak_power_kw: 25.0
    nominal_voltage_v: 230.0
    power_factor_min: 0.95
    power_factor_max: 0.99
    initial_energy_kwh: 50000.0
```

### 11.3 PV Systems

```yaml
pv_systems:
  - system_id: "pv-system-001"
    nominal_capacity_kwp: 10.0
    system_losses_percent: 15.0
    temperature_coefficient_pct_per_c: -0.4
    noct_c: 45.0
```

### 11.4 Consumer Loads

```yaml
consumers:
  - device_id: "industrial-oven-001"
    device_type: INDUSTRIAL_OVEN
    rated_power_kw: 5.0
    duty_cycle_pct: 70.0
    operating_windows:
      - { start_hour: 7, end_hour: 9 }
      - { start_hour: 11, end_hour: 13 }
```

### 11.5 Smart City

```yaml
smart_city:
  city_id: "berlin-001"
  latitude: 52.52
  longitude: 13.405
  zones:
    - zone_id: "zone-mitte"
      streetlights:
        - { light_id: "light-mitte-001", rated_power_w: 150 }
        - { light_id: "light-mitte-002", rated_power_w: 150 }
        - { light_id: "light-mitte-003", rated_power_w: 100 }
    - zone_id: "zone-kreuzberg"
      streetlights:
        - { light_id: "light-kreuzberg-001", rated_power_w: 150 }
        - { light_id: "light-kreuzberg-002", rated_power_w: 100 }
        - { light_id: "light-kreuzberg-003", rated_power_w: 100 }
```

### 11.6 Output Channels

```yaml
mqtt:
  host: "mqtt"
  port: 1883
  qos: 1

kafka:
  enabled: true              # false in cluster mode
  bootstrap_servers: "kafka:9092"
  security_protocol: "PLAINTEXT"

orce:
  enabled: false             # true in cluster mode
  url: "http://orce:1880"
  webhook_path: "/api/sim/tick"
  timeout_seconds: 15
```

---

## 12. Deployment Procedures

### 12.1 Prerequisites

- Docker and Docker Compose
- Python 3.11+ with pip
- `kubectl` configured for the Stackable cluster
- TLS certificates in `certs/` directory
- `.env.cluster` with credentials

### 12.2 Install Python Dependencies

```bash
cd simulation-service
pip install -e ".[lakehouse]"
```

### 12.3 Set Up Lakehouse Structure (One-Time)

```bash
# Create schemas, Bronze tables, Silver views, Gold views
python scripts/setup_lakehouse.py --env-file .env.cluster
```

Expected output: `24/24 objects created` (9 Bronze + 9 Silver + 6 Gold).

### 12.4 Configure NiFi Pipeline (One-Time)

```bash
# Create NiFi processor groups and flows
python scripts/setup_nifi.py --env-file .env.cluster

# Or dry-run to preview configuration
python scripts/setup_nifi.py --env-file .env.cluster --dry-run
```

**Manual steps after script:**
1. Upload `trino-jdbc-467.jar` to each NiFi node (see [Persistent JDBC Driver](#persistent-jdbc-driver))
2. Verify all 36 processors are running in NiFi UI
3. Check NiFi bulletins for any SSL or connectivity errors

### 12.5 Start the Simulation

```bash
# Start simulation + ORCE in cluster mode
docker compose -f docker-compose.yml -f docker-compose.cluster.yml up --build
```

### 12.6 Verify End-to-End

```bash
# Full E2E validation (Kafka message schema + Bronze/Silver/Gold query)
python scripts/demo_e2e.py --bootstrap 212.132.83.222:9093 --tls \
  --ca-cert certs/ca.crt --client-cert certs/client.crt --client-key certs/client.key

# Lakehouse query validation
python scripts/demo_lakehouse.py --env-file .env.cluster
```

### 12.7 Stop the Simulation

```bash
docker compose -f docker-compose.yml -f docker-compose.cluster.yml down
```

NiFi will stop consuming (no new messages), but existing data in Bronze/Silver/Gold remains.

---

## 13. Monitoring & Troubleshooting

### 13.1 Simulation Health

```bash
# Check simulation API
curl http://localhost:8080/api/v1/health

# Check simulation logs
docker compose logs -f simulation

# Check ORCE logs (Kafka producer connections)
docker compose logs -f orce
```

**Healthy ORCE log:**
```
[rdkafka] SSL enabled for broker 212.132.83.222:9093
[rdkafka] Producer ready for broker 212.132.83.222:9093
```

### 13.2 Kafka Monitoring

```bash
# Check consumer group status
kubectl exec -n stackable kafka-broker-default-0 -- \
  /stackable/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9093 \
  --command-config /tmp/client.properties \
  --group facis-nifi-lakehouse --describe

# List topics
kubectl exec -n stackable kafka-broker-default-0 -- \
  /stackable/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9093 \
  --command-config /tmp/client.properties --list
```

### 13.3 NiFi Monitoring

```bash
# Check NiFi bulletins (errors)
# Via NiFi REST API from inside the cluster, or NiFi UI if accessible

# Check NiFi processor status
kubectl exec -n stackable nifi-node-default-0-0 -- \
  curl -sk https://localhost:8443/nifi-api/flow/process-groups/root/status
```

### 13.4 Trino Queries

```bash
# Quick Bronze check (uses credentials from .env.cluster)
python scripts/demo_lakehouse.py --env-file .env.cluster --schema bronze
```

### 13.5 Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| ORCE: `SSL handshake failed` | Wrong certs or expired | Regenerate certs from K8s secrets |
| NiFi: `SSLPeerUnverifiedException` | Using wrong service name | Use `*-headless` service name |
| NiFi: `AUTOCOMMIT_WRITE_CONFLICT` | Iceberg concurrent writes | Expected; PutSQL retries handle it |
| Trino: `Value cannot be cast to timestamp` | Silver views using `CAST AS TIMESTAMP` | Must use `from_iso8601_timestamp()` |
| Trino: `View is stale` | Silver view types changed | Recreate Gold views (run setup script) |
| Bronze: 0 rows | NiFi not consuming or PutSQL failing | Check NiFi bulletins + JDBC connection |
| OIDC: `invalid_client` | Wrong client_id | Client ID is `OIDC` (not `trino`) |

---

## 14. Data Schema Reference

### 14.1 Energy Meter JSON

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "meter_id": "janitza-umg96rm-001",
  "asset_id": "janitza-umg96rm-001",
  "schema_version": "1.0",
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

### 14.2 PV Generation JSON

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "pv_system_id": "pv-system-001",
  "asset_id": "pv-system-001",
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

### 14.3 Weather JSON

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "temperature_c": 18.3,
  "solar_irradiance_w_m2": 850.3,
  "location": { "latitude": 52.52, "longitude": 13.405 },
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

### 14.4 Energy Price JSON

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "price_eur_per_kwh": 0.102,
  "tariff_type": "MIDDAY",
  "schema_version": "1.0"
}
```

### 14.5 Consumer Load JSON

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "site_id": "site-berlin-001",
  "device_id": "industrial-oven-001",
  "asset_id": "industrial-oven-001",
  "device_type": "INDUSTRIAL_OVEN",
  "device_state": "ON",
  "device_power_kw": 4.85
}
```

### 14.6 Streetlight JSON

```json
{
  "timestamp": "2026-03-08T22:00:00Z",
  "city_id": "berlin-001",
  "zone_id": "zone-mitte",
  "light_id": "light-mitte-001",
  "asset_id": "light-mitte-001",
  "dimming_level_pct": 85.0,
  "power_w": 127.5
}
```

### 14.7 Traffic JSON

```json
{
  "timestamp": "2026-03-08T08:00:00Z",
  "city_id": "berlin-001",
  "zone_id": "zone-mitte",
  "traffic_index": 0.78
}
```

### 14.8 City Event JSON

```json
{
  "timestamp": "2026-03-08T21:00:00Z",
  "city_id": "berlin-001",
  "zone_id": "zone-mitte",
  "event_type": "ACCIDENT",
  "severity": 2,
  "active": true
}
```

### 14.9 City Weather / Visibility JSON

```json
{
  "timestamp": "2026-03-08T14:00:00Z",
  "city_id": "berlin-001",
  "fog_index": 0.1,
  "visibility": "good",
  "sunrise_time": "06:15",
  "sunset_time": "18:45"
}
```
