# FACIS FAP IoT & AI Simulation Service

A deterministic simulation service for the FACIS IoT & AI demonstrator. Provides reproducible time-series and event data for Smart Energy Monitoring use cases.

## Quick Start

```bash
# Clone and navigate to the project
cd FAP/IOT\ \&\ AI\ over\ Trusted\ Zones/implementation/simulation-service

# Install dependencies
pip install -e .

# Run with default configuration
python -m src.main

# Or use Docker
docker-compose up
```

## Architecture

The simulation service consists of:

- **Core Engine**: Deterministic simulation clock with time acceleration
- **Simulators**: Energy meters, PV generation, weather, prices, consumer loads
- **API Layer**: REST (FastAPI), MQTT, Modbus TCP

## Configuration

Configure via environment variables or YAML files in `config/`.

| Variable | Default | Description |
|----------|---------|-------------|
| `SIMULATION_SEED` | `12345` | Random seed for reproducibility |
| `TIME_ACCELERATION` | `1` | Time acceleration factor |
| `MQTT_BROKER` | `localhost` | MQTT broker address |
| `HTTP_PORT` | `8080` | REST API port |
| `MODBUS_PORT` | `502` | Modbus TCP port |

## Documentation

- [Architecture](docs/architecture.md)
- [Configuration](docs/configuration.md)
- [API Usage](docs/api-usage.md)
- [Modbus Integration](docs/modbus-integration.md)
- [Deployment](docs/deployment.md)

## License

Apache 2.0
