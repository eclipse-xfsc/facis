# How to Add New Simulators

**Project:** FACIS FAP — IoT & AI Demonstrator
**Version:** 1.0
**Date:** 07 March 2026

---

## 1. Overview

The simulation service is designed to be extended with new feed types. Each simulator is a self-contained module that implements the `BaseTimeSeriesGenerator` interface and plugs into the correlation engine. This guide walks through adding a new simulator end-to-end.

The process involves five steps: define the data model, implement the simulator, register it in the correlation engine, add a publish transport, and write tests.

---

## 2. Architecture Recap

Every simulator follows the same pattern:

```
Config (Pydantic)  →  Simulator (BaseTimeSeriesGenerator)  →  Reading (Pydantic model)
     ↑                        ↑                                      ↓
  config.py              generate_value(ts)                   PublishOrchestrator
```

The correlation engine calls `generate_value(timestamp)` once per tick and the reading is routed to all enabled transports (REST, MQTT, Kafka, ORCE, Modbus).

---

## 3. Step 1 — Define the Data Model

Create a new model file in `src/models/`. The model defines the JSON payload structure.

### 3.1 Example: Battery Storage Simulator

```python
# src/models/battery.py
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class BatteryMode(str, Enum):
    CHARGING = "charging"
    DISCHARGING = "discharging"
    IDLE = "idle"


class BatteryReading(BaseModel):
    """Battery energy storage system reading."""

    type: Literal["battery_storage"] = "battery_storage"
    schema_version: str = "1.0"
    site_id: str = ""
    timestamp: datetime
    battery_id: str
    mode: BatteryMode
    state_of_charge_pct: float = Field(ge=0.0, le=100.0)
    power_kw: float = Field(ge=0.0)
    capacity_kwh: float = Field(ge=0.0)

    @property
    def asset_id(self) -> str:
        return self.battery_id
```

### 3.2 Conventions

Follow these conventions to stay consistent with existing feeds:

- Include `type` as a `Literal` discriminator field with a default.
- Include `schema_version` defaulting to `"1.0"`.
- Include `site_id` for cross-feed correlation.
- Include `timestamp` as a required `datetime` field.
- Use an `asset_id` property (or computed field) for canonical identification.
- Use Pydantic `Field` constraints (`ge`, `le`) for value validation.
- Use `str` Enums for categorical fields.

---

## 4. Step 2 — Add Configuration

Add a config class in `src/config.py` within the `Settings` class.

### 4.1 Add the Config Class

```python
# In src/config.py, add alongside existing config classes:

class BatteryConfig(BaseModel):
    """Configuration for a battery storage simulator."""

    id: str = Field(min_length=1)
    capacity_kwh: float = Field(default=13.5, ge=0.1, le=10000.0)
    max_charge_kw: float = Field(default=5.0, ge=0.1)
    max_discharge_kw: float = Field(default=5.0, ge=0.1)
    initial_soc_pct: float = Field(default=50.0, ge=0.0, le=100.0)
    efficiency: float = Field(default=0.95, ge=0.5, le=1.0)
```

### 4.2 Register in Settings

Add the new config to the `Settings` class:

```python
class Settings(BaseSettings):
    # ... existing fields ...
    batteries: list[BatteryConfig] = Field(
        default_factory=lambda: [BatteryConfig(id="battery-001")]
    )
```

This automatically enables environment variable overrides (via YAML only for list types) and validation.

---

## 5. Step 3 — Implement the Simulator

Create a new package in `src/simulators/`:

```
src/simulators/battery_storage/
├── __init__.py
└── simulator.py
```

### 5.1 Implement the Simulator Class

```python
# src/simulators/battery_storage/simulator.py
from datetime import datetime

from src.core.random_generator import DeterministicRNG
from src.core.time_series import BaseTimeSeriesGenerator
from src.config import BatteryConfig
from src.models.battery import BatteryMode, BatteryReading


class BatteryStorageSimulator(BaseTimeSeriesGenerator[BatteryReading]):
    """Simulates a battery energy storage system.

    The battery charges when PV generation exceeds consumption
    and discharges during peak tariff periods.
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        config: BatteryConfig | None = None,
        site_id: str = "",
    ):
        super().__init__(entity_id=entity_id, rng=rng)
        self._config = config or BatteryConfig(id=entity_id)
        self._site_id = site_id
        self._soc = self._config.initial_soc_pct

    def generate_value(self, timestamp: datetime) -> BatteryReading:
        """Generate a single battery reading for the given timestamp."""
        hour = timestamp.hour

        # Simple strategy: charge during midday (solar peak), discharge
        # during evening peak
        if 10 <= hour < 15 and self._soc < 95.0:
            mode = BatteryMode.CHARGING
            power = min(
                self._config.max_charge_kw,
                (100.0 - self._soc) / 100.0 * self._config.capacity_kwh,
            )
            # Add small variance
            power *= 1.0 + self._rng.uniform(-0.05, 0.05)
            self._soc += (power / self._config.capacity_kwh) * 100.0
            self._soc = min(self._soc, 100.0)

        elif 17 <= hour < 21 and self._soc > 10.0:
            mode = BatteryMode.DISCHARGING
            power = min(
                self._config.max_discharge_kw,
                self._soc / 100.0 * self._config.capacity_kwh,
            )
            power *= 1.0 + self._rng.uniform(-0.05, 0.05)
            self._soc -= (power / self._config.capacity_kwh) * 100.0
            self._soc = max(self._soc, 0.0)

        else:
            mode = BatteryMode.IDLE
            power = 0.0

        return BatteryReading(
            timestamp=timestamp,
            site_id=self._site_id,
            battery_id=self._config.id,
            mode=mode,
            state_of_charge_pct=round(self._soc, 1),
            power_kw=round(power, 3),
            capacity_kwh=self._config.capacity_kwh,
        )
```

### 5.2 Key Implementation Rules

Follow these rules to maintain simulation invariants:

- **Use the provided `DeterministicRNG`** for all random values. Never use `random.random()` or `numpy.random` directly — this would break determinism.
- **Accept `entity_id` and `rng` in the constructor** and pass them to `super().__init__()`.
- **Keep state minimal.** Any state that persists between ticks (like `self._soc` above) must be updated deterministically. If the same timestamp is generated twice, the result should be identical.
- **Round output values** to a consistent number of decimal places for clean JSON serialisation.
- **Return a Pydantic model instance.** The PublishOrchestrator calls `.model_dump()` to serialise it.

---

## 6. Step 4 — Register in the Correlation Engine

Edit `src/simulators/correlation/engine.py` to instantiate and call your simulator.

### 6.1 Add to Simulator Initialisation

```python
# In the CorrelationEngine.__init__() method:
from src.simulators.battery_storage.simulator import BatteryStorageSimulator

# After existing simulator setup:
self._battery_simulators = [
    BatteryStorageSimulator(
        entity_id=cfg.id,
        rng=self._create_sub_rng(f"battery-{cfg.id}"),
        config=cfg,
        site_id=settings.site_id,
    )
    for cfg in settings.batteries
]
```

### 6.2 Add to Tick Generation

In the `generate_tick()` method, decide where in the generation order your simulator should run. If it depends on another feed (e.g., PV surplus for battery charging), place it after that feed.

```python
# After Step 2 (PV generation) and Step 3 (meters, price, consumer):
# Step 3.5: Battery (depends on PV and meter for smart charging)
battery_readings = [
    sim.generate_value(aligned_ts)
    for sim in self._battery_simulators
]
```

### 6.3 Add to Tick Envelope

Add the readings to the tick envelope that the PublishOrchestrator serialises:

```python
tick_envelope["smart_energy"]["batteries"] = [
    r.model_dump(mode="json") for r in battery_readings
]
```

---

## 7. Step 5 — Add a Kafka Topic

Edit `src/api/kafka/topics.py` to register a new topic:

```python
TOPICS = {
    # ... existing topics ...
    "battery_storage": "sim.smart_energy.battery",
}
```

The PublishOrchestrator will route battery readings to this topic using `battery_id` as the partition key.

---

## 8. Step 6 — Write Tests

### 8.1 Unit Test

```python
# tests/unit/test_battery_simulator.py
from datetime import datetime, timezone

from src.core.random_generator import DeterministicRNG
from src.config import BatteryConfig
from src.simulators.battery_storage.simulator import BatteryStorageSimulator


def test_battery_charges_during_midday():
    rng = DeterministicRNG(seed=42)
    sim = BatteryStorageSimulator(
        entity_id="bat-001",
        rng=rng,
        config=BatteryConfig(id="bat-001", initial_soc_pct=50.0),
        site_id="test-site",
    )
    ts = datetime(2026, 3, 8, 12, 0, 0, tzinfo=timezone.utc)
    reading = sim.generate_value(ts)

    assert reading.mode.value == "charging"
    assert reading.power_kw > 0
    assert reading.state_of_charge_pct >= 50.0


def test_battery_discharges_during_evening_peak():
    rng = DeterministicRNG(seed=42)
    sim = BatteryStorageSimulator(
        entity_id="bat-001",
        rng=rng,
        config=BatteryConfig(id="bat-001", initial_soc_pct=80.0),
        site_id="test-site",
    )
    ts = datetime(2026, 3, 8, 18, 0, 0, tzinfo=timezone.utc)
    reading = sim.generate_value(ts)

    assert reading.mode.value == "discharging"
    assert reading.power_kw > 0


def test_battery_deterministic():
    """Same seed + timestamp produces identical output."""
    for _ in range(3):
        rng = DeterministicRNG(seed=99)
        sim = BatteryStorageSimulator(entity_id="bat-001", rng=rng)
        ts = datetime(2026, 3, 8, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_value(ts)
        assert reading.state_of_charge_pct == reading.state_of_charge_pct  # idempotent
```

### 8.2 BDD Scenario

```gherkin
# tests/bdd/features/battery_storage.feature
Feature: Battery Storage Simulation
  As an energy manager
  I want the battery to charge from PV surplus and discharge during peak hours
  So that I can reduce grid dependency

  Scenario: Battery charges during solar peak
    Given the simulation is configured with seed 42
    And the simulation time is 2026-03-08T12:00:00Z
    When I generate a battery reading
    Then the battery mode should be "charging"
    And the state of charge should increase

  Scenario: Battery idles outside operating windows
    Given the simulation is configured with seed 42
    And the simulation time is 2026-03-08T03:00:00Z
    When I generate a battery reading
    Then the battery mode should be "idle"
    And the power should be 0.0
```

---

## 9. Checklist for New Simulators

Use this checklist when adding a new simulator feed:

- [ ] Data model defined in `src/models/` with Pydantic validation
- [ ] Config class added to `src/config.py` with defaults and ranges
- [ ] Config registered in `Settings` class with default factory
- [ ] Simulator class in `src/simulators/<name>/simulator.py`
- [ ] Simulator extends `BaseTimeSeriesGenerator`
- [ ] Uses `DeterministicRNG` for all randomness
- [ ] Registered in correlation engine with correct generation order
- [ ] Readings added to tick envelope
- [ ] Kafka topic defined in `src/api/kafka/topics.py`
- [ ] Unit tests with determinism verification
- [ ] BDD scenario covering key behaviour
- [ ] JSON schema documented in `docs/data-model/schema-reference.md`
- [ ] Avro schemas added to `schemas/avro/bronze/` and `schemas/avro/silver/`
- [ ] Example JSON added to `schemas/avro/examples/`

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
