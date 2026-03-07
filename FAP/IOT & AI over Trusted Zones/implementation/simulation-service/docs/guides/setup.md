# Development Environment Setup

**Project:** FACIS FAP — IoT & AI Demonstrator
**Version:** 1.0
**Date:** 07 March 2026

---

## 1. Prerequisites

| Requirement | Minimum Version | Verify Command |
|---|---|---|
| Python | 3.11 | `python3 --version` |
| pip | 23.0 | `pip --version` |
| Docker | 24.0 | `docker --version` |
| Docker Compose | 2.20 | `docker compose version` |
| Git | 2.40 | `git --version` |

Optional (for cluster deployment):

| Requirement | Minimum Version | Purpose |
|---|---|---|
| kubectl | 1.28 | Kubernetes cluster access |
| helm | 3.14 | Stackable operator installation |

---

## 2. Repository Setup

```bash
# Clone the repository
git clone <repo-url> facis
cd facis/FAP/IOT\ \&\ AI\ over\ Trusted\ Zones/implementation/simulation-service
```

All commands below assume you are in the `simulation-service/` directory.

---

## 3. Python Environment

### 3.1 Virtual Environment (Recommended)

```bash
python3.11 -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\Scripts\activate    # Windows
```

### 3.2 Install Dependencies

```bash
# Core dependencies only (run the simulation)
pip install -e .

# Development dependencies (tests, linting, type checking)
pip install -e ".[dev]"

# Lakehouse/demo scripts (Trino client, NiFi API)
pip install -e ".[lakehouse]"

# All extras
pip install -e ".[dev,lakehouse,demo]"
```

### 3.3 Dependency Summary

Core dependencies installed by `pip install -e .`:

| Package | Version | Purpose |
|---|---|---|
| fastapi | ≥ 0.109 | REST API framework |
| uvicorn | ≥ 0.27 | ASGI server |
| paho-mqtt | ≥ 2.0 | MQTT client |
| pymodbus | ≥ 3.6 | Modbus TCP server |
| numpy | ≥ 1.26 | Numerical computations |
| pydantic | ≥ 2.5 | Data validation and settings |
| pydantic-settings | ≥ 2.1 | Environment/YAML config loading |
| pyyaml | ≥ 6.0 | YAML config file parsing |
| confluent-kafka | ≥ 2.3 | Kafka producer (requires librdkafka) |
| httpx | ≥ 0.27 | HTTP client for ORCE webhook |

Dev dependencies installed by `pip install -e ".[dev]"`:

| Package | Purpose |
|---|---|
| pytest ≥ 8.0 | Test runner |
| pytest-bdd ≥ 7.0 | BDD scenario execution |
| pytest-asyncio ≥ 0.23 | Async test support |
| pytest-cov ≥ 4.1 | Coverage reporting |
| pytest-timeout ≥ 2.3 | Test timeout enforcement |
| ruff ≥ 0.2 | Linting (replaces flake8 + isort) |
| mypy ≥ 1.8 | Static type checking |
| black ≥ 24.1 | Code formatting |
| testcontainers ≥ 4.0 | Docker-based integration tests |

### 3.4 Verify Installation

```bash
# Verify the package is importable
python -c "from src.config import Settings; print('OK:', Settings().site_id)"
# OK: site-berlin-001

# Run the health check
python -m src.main &
sleep 2
curl -s http://localhost:8080/api/v1/health | python -m json.tool
kill %1
```

---

## 4. Docker Environment

### 4.1 Build the Simulation Image

```bash
docker build -t facis-simulation:latest .
```

### 4.2 Local Development Stack

The `docker-compose.yml` starts the full local stack (simulation + Mosquitto + Kafka + ORCE + Kafka UI):

```bash
docker compose up --build
```

Services and ports:

| Service | Port | URL |
|---|---|---|
| Simulation (REST) | 8080 | http://localhost:8080 |
| Simulation (Modbus) | 502 | tcp://localhost:502 |
| Mosquitto (MQTT) | 1883 | tcp://localhost:1883 |
| Kafka | 9092 | tcp://localhost:9092 |
| Kafka UI | 8090 | http://localhost:8090 |
| ORCE (Node-RED) | 1880 | http://localhost:1880 |

### 4.3 Cluster Overlay

For remote cluster deployment with mTLS Kafka:

```bash
# Ensure TLS certificates are in place
ls certs/  # ca.crt, client.crt, client.key

# Start with cluster overlay (ORCE publishes to remote Kafka via mTLS)
docker compose -f docker-compose.yml -f docker-compose.cluster.yml up --build
```

---

## 5. Running Tests

### 5.1 Full Test Suite

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term-missing

# Run with verbose output
pytest -v

# Run with timeout enforcement (10s per test)
pytest --timeout=10
```

### 5.2 BDD Tests Only

```bash
pytest tests/bdd/ -v
```

### 5.3 Unit Tests Only

```bash
pytest tests/unit/ -v
```

### 5.4 Integration Tests

Integration tests require Docker (testcontainers):

```bash
pytest tests/integration/ -v
```

### 5.5 Coverage Report

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html   # macOS
# xdg-open htmlcov/index.html   # Linux
```

---

## 6. Code Quality Tools

### 6.1 Linting (Ruff)

```bash
# Check for issues
ruff check src/ tests/

# Auto-fix safe issues
ruff check --fix src/ tests/
```

Configuration is in `pyproject.toml`: line length 100, target Python 3.11, rules E/F/I/N/W/UP.

### 6.2 Formatting (Black)

```bash
# Check formatting
black --check src/ tests/

# Apply formatting
black src/ tests/
```

### 6.3 Type Checking (Mypy)

```bash
mypy src/
```

Configuration: non-strict mode, missing imports ignored.

### 6.4 Pre-commit Workflow

Run all checks before committing:

```bash
ruff check src/ tests/ && black --check src/ tests/ && mypy src/ && pytest
```

---

## 7. Project Structure

```
simulation-service/
├── src/
│   ├── main.py                    Entry point (uvicorn startup)
│   ├── config.py                  Pydantic Settings (all configuration)
│   ├── core/
│   │   ├── engine.py              SimulationEngine state machine
│   │   ├── clock.py               SimulationClock (time acceleration)
│   │   ├── random_generator.py    DeterministicRNG (seeded)
│   │   └── time_series.py         BaseTimeSeriesGenerator (ABC)
│   ├── models/
│   │   ├── meter.py               MeterReading, MeterReadings
│   │   ├── pv.py                  PVReading, PVReadings
│   │   ├── weather.py             WeatherReading, WeatherConditions
│   │   ├── price.py               PriceReading, TariffType
│   │   └── consumer_load.py       ConsumerLoadReading, DeviceType/State
│   ├── simulators/
│   │   ├── base.py                BaseTimeSeriesGenerator abstract class
│   │   ├── energy_meter/          Janitza UMG 96RM emulation
│   │   ├── pv_generation/         NOCT-based PV model
│   │   ├── weather/               Atmospheric simulation
│   │   ├── energy_price/          EPEX Spot tariff model
│   │   ├── consumer_load/         Industrial device scheduling
│   │   ├── smart_city/            Streetlight, traffic, events, visibility
│   │   └── correlation/           Cross-feed correlation engine
│   └── api/
│       ├── rest/                  FastAPI application and routes
│       ├── mqtt/                  MQTT publisher
│       ├── kafka/                 Kafka producer and topic definitions
│       └── modbus/                Modbus TCP server (pymodbus)
├── tests/
│   ├── unit/                      Unit tests
│   ├── bdd/                       BDD scenarios (pytest-bdd)
│   └── integration/               Integration tests (testcontainers)
├── config/
│   ├── default.yaml               Default configuration
│   └── development.yaml           Dev-specific overrides
├── scripts/
│   ├── setup_lakehouse.py         Create Bronze/Silver/Gold tables in Trino
│   ├── setup_nifi.py              Configure NiFi pipeline
│   ├── demo_e2e.py                End-to-end demo script
│   └── demo_lakehouse.py          Lakehouse query demo
├── orce/                          ORCE (Node-RED) configuration
│   ├── Dockerfile                 Custom ORCE image with rdkafka patch
│   ├── rdkafka-patch.js           mTLS patch for node-red-contrib-rdkafka
│   └── flows/                     Node-RED flow JSON files
├── schemas/avro/                  Avro schema definitions (Bronze/Silver)
├── certs/                         TLS certificates (not committed)
├── docs/                          Documentation tree
├── Dockerfile                     2-stage production image
├── docker-compose.yml             Local development stack
├── docker-compose.cluster.yml     Cluster deployment overlay
├── pyproject.toml                 Package metadata and tool config
├── LICENSE                        Apache 2.0
├── NOTICE.md                      Third-party notices
├── CONTRIBUTING.md                Contribution guidelines
└── SECURITY.md                    Vulnerability reporting
```

---

## 8. Troubleshooting

**`confluent-kafka` fails to install.** This package requires `librdkafka` system library. On macOS: `brew install librdkafka`. On Ubuntu: `apt install librdkafka-dev`. If you only need REST/MQTT/Modbus (no Kafka publishing), you can comment out `confluent-kafka` from `pyproject.toml` dependencies.

**Port 502 requires root.** Modbus default port 502 is a privileged port. Either run as root (not recommended), change the port via `SIMULATOR_MODBUS__PORT=5020`, or use Docker (which maps ports automatically).

**Docker compose "network not found".** Run `docker compose down` first to clean up stale networks, then `docker compose up --build`.

**ORCE connection refused.** ORCE publishing is disabled by default (`SIMULATOR_ORCE__ENABLED=false`). Enable it via environment variable or config YAML if you need the Kafka routing middleware.

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
