# Component Design and Data Flow

**Project:** FACIS FAP — IoT & AI Demonstrator
**Version:** 1.0
**Date:** 07 March 2026

---

## 1. High-Level Architecture

The simulation service is structured in three layers: **Core** (engine, clock, RNG), **Simulators** (feed generators), and **API** (publish transports). The correlation engine orchestrates simulator execution order to maintain physical consistency across feeds.

```
┌─────────────────────────────────────────────────────────────────┐
│  API Layer (src/api/)                                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ REST     │ │ MQTT     │ │ Kafka    │ │ Modbus   │          │
│  │ FastAPI  │ │ paho     │ │ confluent│ │ pymodbus │          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       └─────────────┴────────────┴────────────┘                │
│                     │ PublishOrchestrator                       │
├─────────────────────┼──────────────────────────────────────────┤
│  Simulator Layer    │ (src/simulators/)                        │
│       ┌─────────────┴─────────────┐                            │
│       │   CorrelationEngine       │                            │
│       │   (ordered generation)    │                            │
│       └─────────────┬─────────────┘                            │
│  ┌──────┬──────┬────┴────┬──────┬──────────────────────┐      │
│  │Meter │ PV   │Weather │Price │Consumer │ SmartCity   │      │
│  └──────┴──────┴────────┴──────┴──────── ┴─────────────┘      │
├────────────────────────────────────────────────────────────────┤
│  Core Layer (src/core/)                                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐       │
│  │ Engine       │ │ Clock        │ │ DeterministicRNG │       │
│  │ (state mgmt) │ │ (time accel) │ │ (seeded random)  │       │
│  └──────────────┘ └──────────────┘ └──────────────────┘       │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Components

### 2.1 SimulationEngine (`src/core/engine.py`)

The engine is a state machine that manages the simulation lifecycle: IDLE → RUNNING → PAUSED → STOPPED. It owns the main simulation loop: on each tick it calls the correlation engine to generate all feeds, then hands the combined tick payload to the PublishOrchestrator.

### 2.2 SimulationClock (`src/core/clock.py`)

The clock manages simulated time independently of wall-clock time. The `speed_factor` setting controls time acceleration (1.0 = real-time, 60.0 = 1 hour per minute). Each tick advances the simulated clock by `interval_minutes` and aligns timestamps to the minute boundary.

### 2.3 DeterministicRNG (`src/core/random_generator.py`)

A seeded random number generator based on NumPy. Given the same `seed`, it produces identical sequences of random values. Each simulator receives its own RNG instance derived from the global seed, so adding or removing simulators does not affect other simulators' output streams.

---

## 3. Simulator Layer

### 3.1 Base Class (`src/simulators/base.py`)

All simulators inherit from `BaseTimeSeriesGenerator`, which defines three methods: `generate_value(timestamp)` returns a single reading for a given time, `iterate_range(time_range)` streams readings over a time range, and `generate_range(time_range)` collects all readings into a list.

Each concrete simulator overrides `generate_value` with its domain-specific model. The base class handles time alignment, iteration, and range slicing.

### 3.2 Correlation Engine (`src/simulators/correlation/engine.py`)

The correlation engine enforces generation order within each tick:

```
Step 1:  WeatherSimulator.generate_at(ts)           → WeatherReading
Step 2:  PVSimulator.generate_at(ts)                 → List[PVReading]
             ↑ reads weather.ghi_w_m2, weather.temperature_c
Step 3:  MeterSimulator.generate_at(ts)              → List[MeterReading]
         PriceSimulator.generate_at(ts)              → PriceReading
         ConsumerLoadSimulator.generate_at(ts)       → List[ConsumerLoadReading]
Step 4:  Compute derived metrics (net_grid, self_consumption, cost)
```

After Step 4, all readings are bundled into a tick envelope and handed to the PublishOrchestrator.

### 3.3 Smart Energy Simulators

**EnergyMeterSimulator** emulates a Janitza UMG 96RM three-phase meter. It generates per-phase voltage, current, and power readings with realistic industrial load curves (weekday ramp-up, lunchtime dip, evening decline). A monotonically increasing energy counter tracks cumulative consumption.

**PVGenerationSimulator** models a rooftop PV system using the NOCT (Nominal Operating Cell Temperature) formula. It reads weather irradiance and temperature to compute panel output with temperature-dependent efficiency derating.

**WeatherSimulator** generates atmospheric conditions using a sinusoidal diurnal temperature model with seasonal offset. Solar radiation (GHI, DNI, DHI) follows a solar-position model attenuated by stochastic cloud cover.

**EnergyPriceSimulator** produces EPEX Spot day-ahead prices following a five-band tariff schedule with configurable volatility and weekend discount.

**ConsumerLoadSimulator** models individual industrial devices (oven, HVAC, compressor, pump) with operating-window schedules and probabilistic duty cycles.

### 3.4 Smart City Simulators

Four additional simulators cover streetlight dimming (event-reactive), traffic congestion (rush-hour patterns), city events (deterministic occurrence schedule), and atmospheric visibility (fog index with dawn peak).

---

## 4. API Layer

### 4.1 PublishOrchestrator (`src/api/rest/app.py`)

The orchestrator receives a tick envelope and publishes to all enabled transports concurrently. It manages connection state for each transport and handles failures gracefully (a Kafka outage does not block MQTT publishing).

### 4.2 REST API (FastAPI)

The REST API serves two purposes: simulation control (start, stop, pause, configure) and data access (current readings from the latest tick). Endpoints are defined in `src/api/rest/routes/`. An auto-generated OpenAPI spec is available at `/docs` when the server is running.

### 4.3 MQTT Publisher

Publishes each feed to its own MQTT topic (e.g., `sim/smart_energy/meter/{meter_id}`). QoS is configurable (default 1). Supports optional username/password authentication.

### 4.4 Kafka Producer

Publishes to 9 Kafka topics (one per feed type). Supports PLAINTEXT and SSL security protocols. Disabled by default when ORCE is enabled (ORCE handles Kafka routing in cluster mode).

### 4.5 ORCE Webhook

Posts the complete tick envelope as a single HTTP POST to the ORCE (Node-RED) webhook endpoint. ORCE then splits the envelope and routes each feed to its corresponding Kafka topic with mTLS authentication. This is the primary publishing path in cluster deployments.

### 4.6 Modbus TCP Server

Exposes meter readings as Modbus holding registers compatible with the Janitza UMG 96RM register map (addresses 19000–19065). The register bank is updated on each tick. See `docs/api/modbus-reference.md` for the complete register map.

---

## 5. Data Flow

### 5.1 Local Development

```
Simulation → REST (state cache)
           → MQTT (per-feed topics)
           → Kafka (per-feed topics, local broker)
           → Modbus (register bank)
```

### 5.2 Cluster Deployment

```
Simulation → ORCE webhook (HTTP POST, single envelope)
               → ORCE splits envelope into 9 feeds
               → ORCE publishes to remote Kafka (mTLS, 9 topics)
                    → NiFi consumes Kafka topics
                    → NiFi writes to S3 (Iceberg/Parquet)
                    → Trino reads Iceberg tables (Bronze)
                    → Trino views (Silver → Gold)
                    → Superset queries Gold views
```

### 5.3 Configuration Loading Flow

```
Pydantic defaults → default.yaml → {env}.yaml → Environment variables → Init params
                     (lowest priority)                        (highest priority)
```

---

## 6. Key Design Decisions

**Deterministic simulation over stochastic.** Every random value is derived from a seeded RNG. This makes BDD testing possible (expected outputs are predictable) and enables reproducible demos.

**Correlation engine over independent generators.** PV output must physically correlate with weather irradiance. The correlation engine enforces generation order so that PV always reads the current tick's weather data.

**ORCE middleware over direct Kafka.** In cluster mode, the simulation publishes a single HTTP POST to ORCE rather than connecting directly to Kafka with mTLS. This separates Kafka TLS complexity from the simulation service and uses ORCE's battle-tested rdkafka library for production-grade Kafka publishing.

**Pydantic Settings for configuration.** Using `pydantic-settings` provides type validation, environment variable overrides, YAML loading, and nested configuration — all with a single class definition.

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
