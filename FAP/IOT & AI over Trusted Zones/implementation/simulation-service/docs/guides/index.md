# FACIS IoT & AI Simulation Service — Developer Guide

**Project:** FACIS FAP — IoT & AI Demonstrator
**Version:** 1.0
**Date:** 07 March 2026

---

## What Is This?

The simulation service is a deterministic IoT data generator for the FACIS Federation Architecture Pattern (FAP) IoT & AI demonstrator. It produces 9 correlated time-series feeds (5 Smart Energy + 4 Smart City) that flow through a complete data pipeline: Simulation → ORCE → Kafka → NiFi → Trino Lakehouse → Superset Dashboards.

Deterministic means that for a given random seed and start time, the simulation produces byte-identical output across runs. This is essential for reproducible testing, BDD scenarios, and demonstration.

## Quickstart (60 seconds)

**Prerequisites:** Python 3.11+, pip.

```bash
# Navigate to the simulation service root
cd FAP/IOT\ \&\ AI\ over\ Trusted\ Zones/implementation/simulation-service

# Install the package in editable mode
pip install -e .

# Start the simulation with defaults
python -m src.main
```

The REST API is now running at `http://localhost:8080`. Verify with:

```bash
curl http://localhost:8080/api/v1/health
# {"status": "ok", "simulation_running": false}
```

Start the simulation:

```bash
curl -X POST http://localhost:8080/api/v1/simulation/start
```

View current meter reading:

```bash
curl http://localhost:8080/api/v1/meters
```

## Quickstart with Docker (full stack)

```bash
# Start simulation + Mosquitto + Kafka + ORCE + Kafka UI
docker compose up --build

# Endpoints:
#   REST API:   http://localhost:8080
#   MQTT:       localhost:1883
#   Kafka UI:   http://localhost:8090
#   ORCE:       http://localhost:1880
```

## Key Concepts

**Simulation tick.** Every `interval_minutes` (default 1 minute), the simulation generates one reading from each configured simulator. All readings share the same aligned timestamp and `site_id`.

**Correlation engine.** Weather is generated first, then PV (which depends on weather irradiance and temperature), then the remaining independent feeds. This ensures physically realistic cross-feed correlation.

**Publish orchestrator.** After generating a tick, the orchestrator publishes simultaneously to all enabled transports: REST state cache, MQTT topics, Kafka topics, ORCE webhook, and Modbus register bank.

**Seed and reproducibility.** The `seed` parameter (default 12345) initialises all random number generators. Identical seeds produce identical simulation output regardless of wall-clock timing.

## Developer Guide Contents

| Document | Description |
|---|---|
| [**setup.md**](setup.md) | Development environment setup, dependencies, tooling |
| [**architecture.md**](architecture.md) | Component design, data flow, source layout |
| [**configuration.md**](configuration.md) | All configuration options with defaults and env vars |
| [**extending.md**](extending.md) | How to add a new simulator feed type |

## Related Documentation

These documents live elsewhere in the `docs/` tree and cover specific technical domains:

| Document | Path | Description |
|---|---|---|
| System Architecture | `docs/architecture/system-architecture.md` | High-level system design and data flow |
| Deployment & Operations | `docs/deployment/deployment-operations.md` | Production deployment procedures |
| REST API Reference | `docs/api/rest-api.md` | Endpoint specification |
| MQTT Reference | `docs/api/mqtt-reference.md` | Topic structure and payloads |
| Modbus Reference | `docs/api/modbus-reference.md` | Register map and client example |
| Schema Reference | `docs/data-model/schema-reference.md` | JSON payload structures for all 9 feeds |
| Data Structures & Semantics | `docs/data-model/data-structures-semantics.md` | Field semantics, ranges, relationships |
| Avro Schema Reference | `docs/data-model/avro-schema-reference.md` | Bronze/Silver Avro definitions |
| Lakehouse Reference | `docs/guides/lakehouse-reference.md` | Bronze/Silver/Gold layer design |

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
