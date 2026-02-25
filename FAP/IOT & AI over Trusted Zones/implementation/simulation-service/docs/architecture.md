# Architecture Documentation

## Overview

The FACIS Simulation Service is a deterministic simulation engine for IoT & AI demonstrators. It provides reproducible time-series and event data for Smart Energy Monitoring use cases.

## Components

### Core Engine (`src/core/`)
- **engine.py** - Main simulation orchestrator
- **clock.py** - Simulation clock with time acceleration
- **random_generator.py** - Seeded deterministic RNG
- **time_series.py** - Base time-series generator

### Simulators (`src/simulators/`)
- **energy_meter/** - Janitza-compatible Modbus TCP meter
- **pv_generation/** - PV power output simulation
- **weather/** - Correlated weather data
- **energy_price/** - EPEX Spot market prices
- **consumer_load/** - Appliance load profiles

### API Layer (`src/api/`)
- **rest/** - FastAPI HTTP endpoints
- **mqtt/** - Paho MQTT publisher
- **modbus/** - pymodbus TCP server

## Data Flow

```
Simulators → Data Router → API Layer → Downstream Systems
```

## Configuration

See `config/` for YAML configuration files per environment.
