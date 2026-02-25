# Configuration Guide

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SIMULATION_SEED` | `12345` | Random seed for reproducibility |
| `TIME_ACCELERATION` | `1` | Time acceleration factor (1-1000) |
| `HTTP_PORT` | `8080` | REST API port |
| `MODBUS_PORT` | `502` | Modbus TCP port |
| `MQTT_BROKER` | `localhost` | MQTT broker address |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `LOG_LEVEL` | `INFO` | Logging level |

## YAML Configuration

Configuration files are in `config/`:
- `default.yaml` - Base configuration
- `development.yaml` - Development overrides
- `production.yaml` - Production overrides
- `test.yaml` - Test environment

## Configuration Precedence

1. Environment variables (highest)
2. Environment-specific YAML
3. default.yaml (lowest)
