# REST API Reference

**Project:** FACIS FAP — IoT & AI Demonstrator
**Base URL:** `http://<host>:8080/api/v1`
**Framework:** FastAPI (auto-generated OpenAPI at `/docs`)

---

## Endpoints

### Health & Configuration

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `GET` | `/config` | Current simulation configuration |
| `PUT` | `/config` | Update simulation configuration |

### Simulation Control

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/simulation/status` | Current simulation state (running, paused, speed factor, simulated time) |
| `POST` | `/simulation/start` | Start or resume simulation |
| `POST` | `/simulation/pause` | Pause simulation (no new data generated) |
| `POST` | `/simulation/reset` | Reset simulation to initial state |

### Data Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/meters` | List all configured meters |
| `GET` | `/meters/{id}/current` | Current meter reading |
| `GET` | `/meters/{id}/history` | Historical meter readings (supports pagination) |
| `GET` | `/pv/{id}/current` | Current PV generation reading |
| `GET` | `/weather/current` | Current weather conditions |
| `GET` | `/prices/current` | Current energy spot price |
| `GET` | `/prices/forecast` | 24-hour price forecast |

### Event Injection

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/events/inject` | Inject a simulation event (city event, price spike, weather event) |

## Response Models

### Health Response

```json
{
  "status": "healthy",
  "service": "facis-simulation-service",
  "version": "1.0.0",
  "timestamp": "2026-03-08T14:00:00Z"
}
```

### Simulation Status Response

```json
{
  "state": "running",
  "simulated_time": "2026-03-08T14:00:00Z",
  "speed_factor": 60.0,
  "seed": 12345,
  "ticks_generated": 840,
  "uptime_seconds": 840
}
```

## Notes

- All endpoints respond within 100ms under normal load
- History endpoints support `?from=` and `?to=` ISO 8601 timestamp parameters
- OpenAPI documentation is auto-generated and available at `GET /docs`

---

© ATLAS IoT Lab GmbH — Licensed under Apache License 2.0
