# System Architecture

**Project:** FACIS FAP — IoT & AI Demonstrator
**Version:** 1.0
**Date:** 07 March 2026

---

## 1. Overview

The FACIS FAP IoT & AI Demonstrator implements a complete end-to-end data pipeline for Smart Energy Monitoring and Smart City Environmental Monitoring. The system generates deterministic IoT data through a simulation layer, routes it through an orchestration engine into a distributed message broker, ingests it into a medallion-architecture lakehouse, and exposes curated datasets for analytics and AI services.

## 2. High-Level Data Flow

```
┌──────────────────────┐
│  Simulation Service  │  Deterministic IoT data generation
│  (Python / FastAPI)  │  9 correlated feeds, configurable seed
└──────────┬───────────┘
           │ HTTP POST (unified tick envelope)
           ▼
┌──────────────────────┐
│  ORCE Orchestration  │  Schema validation, feed splitting,
│  (Node-RED)          │  Kafka routing via rdkafka (mTLS)
└──────────┬───────────┘
           │ 9 Kafka topics (mTLS)
           ▼
┌──────────────────────┐
│  Apache Kafka        │  Distributed message broker
│  (Stackable K8s)     │  9 topics, mTLS authentication
└──────────┬───────────┘
           │ ConsumeKafka
           ▼
┌──────────────────────┐
│  Apache NiFi         │  Kafka → SQL → Trino ingestion
│  (Stackable K8s)     │  36 processors (4 per topic)
└──────────┬───────────┘
           │ INSERT INTO bronze.*
           ▼
┌──────────────────────┐
│  Trino Lakehouse     │  Medallion architecture on Iceberg/S3
│  (Stackable K8s)     │  Bronze → Silver → Gold
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Analytics Layer     │  Superset dashboards, AI services
└──────────────────────┘
```

## 3. Component Inventory

| Component | Technology | Version | Deployment |
|---|---|---|---|
| Simulation Service | Python 3.11, FastAPI, paho-mqtt, pymodbus, confluent-kafka | Custom | Docker Compose |
| ORCE | Node-RED (ecofacis/xfsc-orce) with rdkafka + mTLS patch | 2.0.3 | Docker Compose / K8s |
| Kafka | Apache Kafka (Stackable operator) | Managed | Kubernetes |
| NiFi | Apache NiFi (Stackable operator) | 2.6 | Kubernetes |
| Trino | Trino with Iceberg connector (Stackable operator) | Managed | Kubernetes |
| Object Storage | S3-compatible (IONOS) | — | External |
| Identity Provider | Keycloak | Managed | Kubernetes |
| Dashboarding | Apache Superset | Managed | Kubernetes |

## 4. Simulation Service Architecture

### 4.1 Source Layout

```
src/
├── main.py                 Entry point (uvicorn, port 8080)
├── config.py               Pydantic Settings (YAML + env vars)
├── core/
│   ├── engine.py           SimulationEngine state machine
│   ├── clock.py            SimulationClock (UTC, time acceleration)
│   ├── random_generator.py DeterministicRNG (seed-based)
│   └── time_series.py      BaseTimeSeriesGenerator framework
├── models/
│   ├── meter.py            Energy meter data model
│   ├── pv.py               PV generation data model
│   ├── weather.py          Weather data model
│   ├── price.py            Energy price data model
│   ├── consumer_load.py    Consumer load data model
│   ├── correlation.py      CorrelatedSnapshot, DerivedMetrics
│   └── smart_city/         Streetlight, traffic, event, visibility models
├── simulators/
│   ├── energy_meter/       3-phase Janitza UMG 96RM simulation
│   ├── pv_generation/      PV physics model (irradiance, temp derating)
│   ├── weather/            Atmospheric simulation (temp, wind, cloud, GHI)
│   ├── energy_price/       EPEX Spot day-ahead market model
│   ├── consumer_load/      Industrial device schedule and duty cycles
│   ├── smart_city/         Streetlight, traffic, events, visibility
│   └── correlation/        Cross-feed correlation engine
└── api/
    ├── rest/               FastAPI app, routes, dependencies
    ├── mqtt/               MQTT publisher (paho-mqtt)
    ├── kafka/              Kafka producer (confluent-kafka)
    └── orce/               ORCE HTTP client and tick envelope builder
```

### 4.2 Correlation Engines

**Smart Energy Correlation** — Enforces physical dependencies between feeds:

1. Weather generated first (ambient temperature, irradiance, wind, cloud cover)
2. PV generation uses weather irradiance and temperature for derating
3. Energy meters, consumer loads, and prices generated in parallel
4. Derived metrics calculated: total consumption, total generation, net grid power, self-consumption ratio, hourly cost (EUR)

**Smart City Correlation** — Enforces event-infrastructure dependencies:

1. City events generated first (accidents, emergencies, public events)
2. Streetlight simulator receives active events per zone
3. Streetlights apply dimming boost based on event severity (severity 2: +30%, severity 3: +50%)
4. Traffic and visibility generated independently

### 4.3 Publish Orchestrator

The central publishing loop runs as a background asyncio task:

```
Loop:
  1. Advance simulation clock by interval_minutes
  2. Generate energy correlation snapshot (weather → PV → meters → prices → loads)
  3. Generate smart city correlation snapshot (events → streetlights → traffic → visibility)
  4. Publish to all enabled channels:
     a. MQTT (per-topic, per-feed)
     b. Kafka (per-topic, per-feed) — disabled in cluster mode
     c. ORCE (single HTTP POST with unified tick envelope)
  5. Sleep for (interval_seconds / speed_factor)
```

With `speed_factor=60` and `interval_minutes=1`, the loop executes once per second, advancing simulation time by 1 minute each tick.

## 5. ORCE Orchestration

ORCE is a customized Node-RED instance with added Kafka support via `node-red-contrib-rdkafka` and a custom SSL/mTLS patch.

### 5.1 Flow Architecture

```
HTTP POST /api/sim/tick
    ↓
Validate Schema (type, schema_version, timestamp, site_id, smart_energy, smart_city)
    ↓
Split Feeds (extract individual messages from unified envelope)
    ↓
Route to Kafka Topic (9-output router)
    ↓
9× rdkafka Producers (mTLS to Kafka cluster)
    ↓
HTTP 200 OK (messages_queued count)
```

### 5.2 Feed Splitting

| Envelope Path | Kafka Topic | Message Key |
|---|---|---|
| `smart_energy.meters[]` | `sim.smart_energy.meter` | `meter_id` |
| `smart_energy.pv[]` | `sim.smart_energy.pv` | `pv_system_id` |
| `smart_energy.weather` | `sim.smart_energy.weather` | `site_id` |
| `smart_energy.price` | `sim.smart_energy.price` | `"price"` |
| `smart_energy.consumers[]` | `sim.smart_energy.consumer` | `device_id` |
| `smart_city.streetlights[]` | `sim.smart_city.light` | `light_id` |
| `smart_city.traffic_readings[]` | `sim.smart_city.traffic` | `zone_id` |
| `smart_city.events[]` | `sim.smart_city.event` | `zone_id` |
| `smart_city.visibility` | `sim.smart_city.weather` | `city_id` |

### 5.3 Custom rdkafka mTLS Patch

The stock `node-red-contrib-rdkafka` package does not support SSL/mTLS. The custom ORCE Docker image includes:

- `rdkafka-patch.js`: Extends the broker config node with `securityProtocol`, `sslCaLocation`, `sslCertLocation`, and `sslKeyLocation` properties
- `entrypoint.sh`: Applies the patch at container startup and delegates to the original ORCE entrypoint

## 6. NiFi Ingestion Pipeline

NiFi runs on Stackable Kubernetes and implements the Kafka-to-Bronze ingestion. The pipeline consists of 1 process group, 3 controller services, and 9 processor chains (4 processors each = 36 processors total).

### 6.1 Controller Services

| Service | Type | Purpose |
|---|---|---|
| Stackable TLS Context | StandardSSLContextService | Stackable-provisioned PKCS12 keystores for Kafka and Trino TLS |
| FACIS Kafka Connection | Kafka3ConnectionService | Bootstrap connection to Kafka cluster (headless service, SSL) |
| Trino JDBC Pool | DBCPConnectionPool | JDBC connection to Trino coordinator (headless service, HTTPS) |

### 6.2 Per-Topic Processor Chain

```
ConsumeKafka (consumer group: facis-nifi-lakehouse)
    ↓
ReplaceText — Escape single quotes in JSON ('  →  '')
    ↓
ReplaceText — Build INSERT SQL with Kafka metadata attributes
    ↓
PutSQL — Execute INSERT via Trino JDBC (autocommit=true)
```

### 6.3 Important: Stackable TLS SAN Configuration

Stackable generates TLS certificates with SANs matching the **headless** service FQDN only. All internal TLS connections must use the headless service name:

| Service | Valid SAN (headless) | Invalid (not in cert) |
|---|---|---|
| Kafka | `kafka-broker-default-headless.stackable.svc.cluster.local` | `kafka-broker-default-bootstrap` |
| Trino | `trino-coordinator-default-headless.stackable.svc.cluster.local` | `trino-coordinator.stackable.svc.cluster.local` |

Using the non-headless service name results in `SSLPeerUnverifiedException`.

## 7. Lakehouse Architecture

The Trino Lakehouse implements the Medallion architecture with three layers:

| Layer | Schema | Storage | Purpose |
|---|---|---|---|
| Bronze | `bronze` | Iceberg tables (Parquet on S3) | Raw JSON ingestion with Kafka metadata |
| Silver | `silver` | Trino views over Bronze | Typed field extraction, timestamp parsing |
| Gold | `gold` | Trino views over Silver | Aggregated KPIs, curated analytics |

See [Lakehouse Reference](../guides/lakehouse-reference.md) for full schema definitions.

## 8. Security Architecture

### 8.1 Transport Security

| Connection | Protocol | Authentication |
|---|---|---|
| Simulation → ORCE | HTTP (internal Docker network) | None (trusted network) |
| ORCE → Kafka | TLS/mTLS | Client certificate (X.509) |
| NiFi → Kafka | TLS/mTLS | Stackable-provisioned PKCS12 |
| NiFi → Trino | HTTPS | Basic auth (file-based) |
| External → Trino | HTTPS | Keycloak OIDC (JWT) |
| External → Kafka | TLS/mTLS | Client certificate (X.509) |

### 8.2 Identity Management

Keycloak serves as the central identity provider:
- Realm: `facis`
- OIDC client for Trino JWT authentication
- Role-based access for dashboard and API consumers

### 8.3 Certificate Management

TLS certificates are provisioned by Stackable's `secret-operator`:
- Self-signed cluster CA (per-cluster)
- Service-specific certificates with headless service FQDNs in SANs
- PKCS12 keystores and truststores for Java-based services (NiFi, Trino)
- PEM certificates for Kafka external access

## 9. Docker Compose Topology

### 9.1 Local Development (`docker-compose.yml`)

| Service | Image | Ports | Purpose |
|---|---|---|---|
| simulation | facis-simulation-service | 8080, 502 | Simulation service |
| mqtt | eclipse-mosquitto | 1883, 9001 | MQTT broker |
| kafka | confluentinc/cp-kafka:7.6.0 | 9092 | Local Kafka (KRaft) |
| orce | ecofacis/xfsc-orce:2.0.3 | 1880 | Orchestration engine |
| kafka-ui | provectuslabs/kafka-ui | 8090 | Kafka monitoring |

### 9.2 Cluster Mode Override (`docker-compose.cluster.yml`)

Overlays the local setup for remote cluster connectivity:
- Simulation: `CONFIG_OVERLAY=cluster`, disables direct Kafka, enables ORCE
- ORCE: Built from `./orce/` with rdkafka mTLS patch, mounts TLS certificates, uses cluster flow
- Speed factor: 60× (1 simulated minute per real second)

```bash
# Start in cluster mode
docker compose -f docker-compose.yml -f docker-compose.cluster.yml up --build
```

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
