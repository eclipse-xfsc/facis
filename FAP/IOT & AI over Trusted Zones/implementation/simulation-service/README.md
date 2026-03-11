# FACIS FAP IoT & AI Simulation Service

A deterministic simulation service for the FACIS IoT & AI demonstrator. Generates 9 correlated time-series feeds (5 Smart Energy + 4 Smart City) with reproducible output for testing, BDD scenarios, and demonstration.

## Quick Start

```bash
# Navigate to the simulation service root
cd FAP/IOT\ \&\ AI\ over\ Trusted\ Zones/implementation/simulation-service

# Install in editable mode
pip install -e .

# Run with default configuration
python -m src.main

# Or use Docker (full stack with Mosquitto, Kafka, ORCE)
docker compose up --build
```

Verify the REST API: `curl http://localhost:8080/api/v1/health`

## Documentation

### Developer Guide (`docs/guides/`)

| Document | Description |
|---|---|
| [Overview & Quickstart](docs/guides/index.md) | Project overview, key concepts, and 60-second quickstart |
| [Development Setup](docs/guides/setup.md) | Environment setup, dependencies, running tests |
| [Component Architecture](docs/guides/architecture.md) | Component design, data flow, source layout |
| [Configuration Reference](docs/guides/configuration.md) | All config options with defaults and env vars |
| [Adding New Simulators](docs/guides/extending.md) | Step-by-step guide to implement a new feed type |

### Technical Reference (`docs/`)

| Document | Description |
|---|---|
| [System Architecture](docs/architecture/system-architecture.md) | High-level system design and data pipeline |
| [Deployment & Operations](docs/deployment/deployment-operations.md) | Production deployment procedures |
| [REST API](docs/api/rest-api.md) | Endpoint specification |
| [MQTT Reference](docs/api/mqtt-reference.md) | Topic structure and payloads |
| [Modbus Reference](docs/api/modbus-reference.md) | Janitza UMG 96RM register map |
| [Data Schema Reference](docs/data-model/schema-reference.md) | JSON payload structures for all 9 feeds |
| [Data Structures & Semantics](docs/data-model/data-structures-semantics.md) | Field semantics, value ranges, cross-feed relationships |
| [Avro Schema Reference](docs/data-model/avro-schema-reference.md) | Bronze/Silver Avro definitions and field mappings |
| [Lakehouse Reference](docs/guides/lakehouse-reference.md) | Bronze/Silver/Gold layer design |

## Configuration

Configure via environment variables (`SIMULATOR_` prefix) or YAML files in `config/`. See the [full configuration reference](docs/guides/configuration.md) for all options.

| Variable | Default | Description |
|---|---|---|
| `SIMULATOR_SIMULATION__SEED` | `12345` | Random seed for reproducibility |
| `SIMULATOR_SIMULATION__SPEED_FACTOR` | `1.0` | Time acceleration (60.0 = 1 hour/min) |
| `SIMULATOR_MQTT__HOST` | `localhost` | MQTT broker address |
| `SIMULATOR_HTTP__PORT` | `8080` | REST API port |
| `SIMULATOR_MODBUS__PORT` | `502` | Modbus TCP port |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, code standards, and the Eclipse Contributor Agreement.

## License

Apache 2.0 — see [LICENSE](LICENSE).

© ATLAS IoT Lab GmbH — Provided in the context of the FACIS project under the Eclipse Foundation.
