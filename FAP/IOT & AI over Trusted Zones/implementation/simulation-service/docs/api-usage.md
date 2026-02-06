# API Usage Guide

## REST API

Base URL: `http://localhost:8080/api/v1`

### Health Check
```bash
curl http://localhost:8080/api/v1/health
```

## MQTT Topics

Subscribe to topics:
```bash
mosquitto_sub -t "facis/energy/meter/#"
```

| Topic | Description |
|-------|-------------|
| `facis/energy/meter/{id}` | Meter readings |
| `facis/energy/pv/{id}` | PV generation |
| `facis/weather/current` | Weather data |
| `facis/prices/spot` | Spot prices |
