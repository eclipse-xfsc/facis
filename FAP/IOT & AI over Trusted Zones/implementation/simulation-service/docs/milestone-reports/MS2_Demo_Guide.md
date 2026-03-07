# FACIS MS2 Demo Guide — IoT Simulation to Data Lakehouse

## What This Demo Shows

This demo presents a **complete IoT data pipeline** — from simulated smart energy and smart city sensors through a real-time orchestration layer, into a distributed Kafka message bus, through Apache NiFi ingestion, and finally into a queryable data lakehouse (Bronze/Silver/Gold) on Apache Iceberg + Trino.

The demo proves that the FACIS Trusted Zone architecture can handle **real-time, multi-domain IoT data** from edge to analytics, using open-source components deployed on Kubernetes.

---

## Architecture at a Glance

```
 LOCAL DOCKER                          REMOTE KUBERNETES CLUSTER (Stackable)
┌──────────────┐                      ┌───────────────────────────────────────────┐
│  Simulation   │───HTTP POST──────▶  │  ORCE (Node-RED)                          │
│  Service      │   /api/sim/tick     │    ↓ splits by feed type                  │
│  (9 feeds)    │                     │  Kafka (9 topics, mTLS)                   │
│               │                     │    ↓ consumed by                          │
│  FastAPI      │                     │  NiFi (36 processors)                     │
│  + Correlation│                     │    ↓ INSERT via JDBC                      │
│    Engine     │                     │  Trino + Iceberg (S3)                     │
└──────────────┘                     │    Bronze → Silver → Gold                 │
                                      │    ↓ queried by                           │
                                      │  Superset (dashboards)                    │
                                      └───────────────────────────────────────────┘
```

---

## The Data Domains

### Smart Energy (5 feeds)

| Feed | What It Simulates | Key Metrics |
|------|-------------------|-------------|
| **Energy Meters** (x2) | Janitza-class 3-phase meters | Active power (kW), voltage, current, power factor, cumulative energy (kWh) |
| **PV Generation** (x2) | Rooftop solar panels | Power output (kW), irradiance (W/m2), module temperature, efficiency |
| **Weather** | On-site weather station | Temperature, solar irradiance, humidity, wind, cloud cover |
| **Energy Price** | EPEX Spot day-ahead market | Price (EUR/kWh), tariff period (night, peak, midday) |
| **Consumer Loads** (x4) | Industrial devices (oven, HVAC, compressor, pump) | Device state (ON/OFF), power draw (kW), duty cycles |

### Smart City (4 feeds)

| Feed | What It Simulates | Key Metrics |
|------|-------------------|-------------|
| **Streetlights** (x6) | Adaptive LED streetlights across 2 zones | Dimming level (%), power (W), event-reactive boost |
| **Traffic** (x2 zones) | Urban traffic flow sensors | Vehicle count, average speed, congestion level |
| **City Events** | Incidents, weather alerts, festivals | Event type, severity (1-3), zone, active/inactive |
| **Visibility** | Atmospheric conditions | Fog index, visibility distance, sunrise/sunset |

---

## Key Correlations to Highlight

### 1. Weather Drives PV Output (Smart Energy)

The PV generation model uses real physics:

```
Power = Capacity x (Irradiance / 1000) x Temperature_Factor x (1 - Losses)
```

- **During the day:** Solar irradiance rises → PV output increases → net grid consumption drops
- **At night:** Zero irradiance → zero PV → full grid dependency
- **Cloud cover:** Higher clouds → reduced irradiance → reduced PV output

**Demo moment:** Show `gold.net_grid_hourly` — the net grid power swings negative during sunny midday hours (exporting to grid) and positive at night (importing from grid).

### 2. Price Impacts Cost (Smart Energy)

The energy price follows EPEX Spot tariff bands:

| Period | Hours | Typical Price |
|--------|-------|--------------|
| Night | 23:00-06:00 | ~0.08 EUR/kWh |
| Morning peak | 06:00-10:00 | ~0.14 EUR/kWh |
| Midday | 10:00-15:00 | ~0.10 EUR/kWh |
| Evening peak | 15:00-21:00 | ~0.18 EUR/kWh |
| Evening | 21:00-23:00 | ~0.12 EUR/kWh |

**Demo moment:** Show `gold.net_grid_hourly` with `estimated_hourly_cost_eur` — costs spike during evening peak even when consumption is similar, because the price per kWh is 2x higher.

### 3. Events Trigger Streetlight Dimming (Smart City)

When a city event occurs (accident, protest, severe weather), nearby streetlights react:

| Event Severity | Dimming Boost | Example |
|---------------|---------------|---------|
| 1 (minor) | No change | Minor congestion |
| 2 (moderate) | +30% brightness | Traffic accident |
| 3 (major) | +50% brightness | Emergency, severe weather |

**Demo moment:** Show `gold.streetlight_zone_hourly` alongside `gold.event_impact_daily` — during active events, the average dimming percentage jumps, and total power consumption increases as lights brighten for safety.

---

## How to Run SQL Queries

All Trino SQL queries in this guide can be run in three ways:

### Option A: Python (from your local machine)

Use the demo script which handles authentication automatically:

```bash
python scripts/demo_lakehouse.py --env-file .env.cluster
```

Or connect manually (requires `pip install trino`). Credentials are read from `.env.cluster`.

### Option B: Trino CLI (from the Kubernetes cluster)

```bash
kubectl exec -it -n stackable trino-coordinator-default-0 -- \
  /stackable/trino-cli --server https://localhost:8443 \
  --insecure --user <trino-user> --password
# Enter the Trino password when prompted (see .env.cluster)
# Then type SQL at the trino> prompt
```

### Option C: Superset SQL Lab (web browser)

1. Open the Superset URL (see infrastructure team for current endpoint)
2. Log in with Superset credentials (see `.env.cluster`)
3. Go to **SQL Lab** → paste and run any query

This is the recommended option during live demos — it provides a visual table output and can be projected on screen.

---

## How to Present the Demo

### Setup (Before the Demo)

1. **Start the simulation locally:**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.cluster.yml up --build
   ```
   This starts the simulation service + ORCE. Data begins flowing immediately.

2. **Verify the pipeline** (optional, takes 30 seconds):
   ```bash
   python scripts/demo_lakehouse.py --env-file .env.cluster
   ```

3. **Let it run for 5-10 minutes** before the demo to accumulate enough data in all layers.

### Demo Flow (Suggested 15-minute walkthrough)

#### Act 1: The Data Source (2 min)

Open the simulation REST API: `http://localhost:8080/api/v1/health`

> "This is a deterministic IoT simulation generating 9 synchronized data feeds — 5 smart energy, 4 smart city. Same seed always produces the same data, making it reproducible for testing and validation."

Show one meter reading: `http://localhost:8080/api/v1/meters/janitza-umg96rm-001/current`

> "Each meter produces Janitza-compatible 3-phase readings — voltage, current, power factor, frequency — exactly like a real industrial energy meter."

#### Act 2: The Orchestration Layer (3 min)

Open ORCE at `http://localhost:1880` (or the remote Node-RED if accessible).

> "Every second, the simulation POSTs a tick envelope containing all 9 feeds to ORCE — the Orchestration Engine. ORCE validates the schema, splits the envelope into individual messages, and publishes each to its own Kafka topic over mTLS."

Show the flow: `HTTP POST → Validate → Split → Route → 9 Kafka Producers`

> "The Kafka cluster runs on Kubernetes with TLS encryption. Every message is authenticated and encrypted in transit."

#### Act 3: The Ingestion Pipeline (3 min)

> "Apache NiFi consumes from all 9 Kafka topics and inserts each message into the Bronze layer of our data lakehouse — raw JSON with Kafka metadata, stored as Parquet files on S3 via Apache Iceberg."

Show Bronze table structure (via Trino or Superset):

```sql
SELECT COUNT(*) FROM "fap-iotai-stackable".bronze.energy_meter;
-- Grows in real-time as simulation runs
```

> "Data is partitioned by day and stored in Parquet format for efficient columnar queries. The row count increases every second as new data arrives."

#### Act 4: The Lakehouse Layers (5 min)

**Bronze → Silver transformation:**

```sql
SELECT event_timestamp, meter_id, active_power_kw, voltage_l1_v
FROM "fap-iotai-stackable".silver.energy_meter
ORDER BY event_timestamp DESC
LIMIT 5;
```

> "The Silver layer extracts and types every field from the raw JSON. This is where we get proper timestamps, doubles, and structured columns — ready for analytics."

**Silver → Gold aggregation:**

```sql
SELECT hour, avg_consumption_kw, avg_generation_kw, net_grid_kw,
       avg_price_eur_per_kwh, estimated_hourly_cost_eur
FROM "fap-iotai-stackable".gold.net_grid_hourly
ORDER BY hour DESC
LIMIT 10;
```

> "The Gold layer is the analytics layer. This view joins consumption, PV generation, and energy prices to calculate the estimated hourly cost of grid electricity. Notice how cost spikes during evening peak hours and drops when PV offsets consumption during the day."

**Smart City aggregation:**

```sql
SELECT hour, zone_id, avg_dimming_pct, total_power_w, light_count
FROM "fap-iotai-stackable".gold.streetlight_zone_hourly
ORDER BY hour DESC
LIMIT 10;
```

> "On the Smart City side, we aggregate streetlight behavior by zone and hour. You can see dimming levels increase at night and spike further during active events."

#### Act 5: The Business Value (2 min)

> "What we've demonstrated is a complete, end-to-end Trusted Zone pipeline:
>
> 1. **Edge simulation** with physically realistic, correlated IoT data
> 2. **Secure transport** via mTLS-encrypted Kafka
> 3. **Automated ingestion** through NiFi into a Bronze raw layer
> 4. **Progressive refinement** through Silver (typed) and Gold (aggregated) layers
> 5. **Real-time analytics** on a Trino data lakehouse backed by Iceberg + S3
>
> Every component is open-source, runs on Kubernetes, and can be replaced or extended independently. The same pipeline works for real sensors — just swap the simulation for actual MQTT/Modbus device feeds."

---

## Quick Queries for the Demo

### How much data is flowing?

```sql
-- Total rows across all Bronze tables
SELECT 'energy_meter' AS feed, COUNT(*) AS rows FROM "fap-iotai-stackable".bronze.energy_meter
UNION ALL SELECT 'pv_generation', COUNT(*) FROM "fap-iotai-stackable".bronze.pv_generation
UNION ALL SELECT 'weather', COUNT(*) FROM "fap-iotai-stackable".bronze.weather
UNION ALL SELECT 'energy_price', COUNT(*) FROM "fap-iotai-stackable".bronze.energy_price
UNION ALL SELECT 'consumer_load', COUNT(*) FROM "fap-iotai-stackable".bronze.consumer_load
UNION ALL SELECT 'streetlight', COUNT(*) FROM "fap-iotai-stackable".bronze.streetlight
UNION ALL SELECT 'traffic', COUNT(*) FROM "fap-iotai-stackable".bronze.traffic
UNION ALL SELECT 'city_event', COUNT(*) FROM "fap-iotai-stackable".bronze.city_event
UNION ALL SELECT 'city_weather', COUNT(*) FROM "fap-iotai-stackable".bronze.city_weather
ORDER BY feed;
```

### When did data start and what's the latest?

```sql
SELECT
    MIN(ingestion_timestamp) AS first_ingestion,
    MAX(ingestion_timestamp) AS last_ingestion,
    COUNT(*) AS total_rows,
    date_diff('second', MIN(ingestion_timestamp), MAX(ingestion_timestamp)) AS duration_seconds
FROM "fap-iotai-stackable".bronze.energy_meter;
```

### PV generation vs consumption over time

```sql
SELECT
    m.hour,
    m.avg_consumption_kw AS consumption,
    COALESCE(p.avg_power_kw, 0) AS pv_generation,
    m.avg_consumption_kw - COALESCE(p.avg_power_kw, 0) AS net_grid
FROM "fap-iotai-stackable".gold.energy_balance_hourly m
LEFT JOIN "fap-iotai-stackable".gold.pv_performance_hourly p ON m.hour = p.hour
ORDER BY m.hour;
```

### Event-driven streetlight response

```sql
SELECT
    e.event_date,
    e.zone_id,
    e.event_type,
    e.avg_severity,
    e.active_count AS active_events,
    s.avg_dimming_pct,
    s.total_power_w
FROM "fap-iotai-stackable".gold.event_impact_daily e
JOIN "fap-iotai-stackable".gold.streetlight_zone_hourly s
    ON e.zone_id = s.zone_id
    AND e.event_date = CAST(s.hour AS DATE)
ORDER BY e.event_date, e.zone_id;
```

---

## Troubleshooting During the Demo

| Symptom | Quick Fix |
|---------|-----------|
| Bronze tables show 0 rows | Check NiFi is running: NiFi bulletins for SSL errors |
| Gold views return errors | Run: `python scripts/setup_lakehouse.py --env-file .env.cluster` to recreate views |
| Simulation not sending ticks | Check `docker compose logs simulation` for ORCE connection errors |
| ORCE not publishing to Kafka | Check ORCE logs for rdkafka errors; verify certs in `certs/` directory |
| Trino connection refused | Verify OIDC token: `python scripts/demo_lakehouse.py --env-file .env.cluster` |
| Stale/slow Gold queries | Gold views scan all Silver data; give Trino 10-20 seconds for large datasets |

---

## Numbers to Expect

With the simulation running at **speed_factor=60** (1 simulated minute per real second):

| Metric | After 5 min | After 30 min | After 2 hours |
|--------|-------------|-------------|---------------|
| Bronze rows (total) | ~2,700 | ~16,200 | ~64,800 |
| Bronze rows per table | ~300 | ~1,800 | ~7,200 |
| Silver rows | Same as Bronze (views) | Same | Same |
| Gold hourly rows | ~50-100 | ~200-400 | ~800+ |
| Simulated time covered | ~5 hours | ~30 hours | ~5 days |
| Kafka messages delivered | ~2,700 | ~16,200 | ~64,800 |
