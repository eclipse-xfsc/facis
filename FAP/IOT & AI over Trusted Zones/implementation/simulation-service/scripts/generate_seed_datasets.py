#!/usr/bin/env python3
"""
Seed Dataset Generator for FACIS Simulation Service.

Generates fixed, reproducible datasets for testing and demos.
Each scenario uses a specific seed to ensure consistent regeneration.

Usage:
    python scripts/generate_seed_datasets.py [--scenario SCENARIO] [--validate] [--output-dir DIR]

Scenarios:
    1. normal_operation (seed=12345, 24h) - Typical weekday
    2. high_consumption (seed=23456, 24h) - Peak load
    3. high_pv_generation (seed=34567, 24h) - Clear summer day
    4. price_volatility (seed=45678, 24h) - High price swings
    5. weekend_pattern (seed=56789, 48h) - Reduced activity
    6. edge_cases (seed=67890, 24h) - Boundary values
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes
from src.models.consumer_load import (
    ConsumerLoadConfig,
    ConsumerLoadReading,
    DeviceType,
    OperatingWindow,
)
from src.models.meter import MeterConfig, MeterReading
from src.models.price import PriceConfig, PriceReading
from src.models.pv import PVConfig, PVReading
from src.models.weather import WeatherConfig, WeatherReading
from src.simulators.consumer_load.simulator import ConsumerLoadSimulator
from src.simulators.energy_meter.simulator import EnergyMeterSimulator
from src.simulators.energy_price.simulator import EnergyPriceSimulator
from src.simulators.pv_generation.simulator import PVGenerationSimulator
from src.simulators.weather.simulator import WeatherSimulator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class ScenarioConfig:
    """Configuration for a test scenario."""

    name: str
    description: str
    seed: int
    duration_hours: int
    start_time: datetime
    interval_minutes: int = 15

    # Weather overrides
    weather_config: WeatherConfig | None = None

    # Meter overrides
    meter_config: MeterConfig | None = None

    # PV overrides
    pv_config: PVConfig | None = None

    # Price overrides
    price_config: PriceConfig | None = None

    # Consumer load overrides
    consumer_configs: list[ConsumerLoadConfig] = field(default_factory=list)


# =============================================================================
# Scenario Definitions
# =============================================================================


def get_normal_operation_scenario() -> ScenarioConfig:
    """Scenario 1: Normal weekday operation."""
    # Start on a Wednesday for typical weekday patterns
    return ScenarioConfig(
        name="normal_operation",
        description="Typical weekday with normal consumption, moderate PV generation, and standard pricing",
        seed=12345,
        duration_hours=24,
        start_time=datetime(2024, 6, 12, 0, 0, 0, tzinfo=UTC),  # Wednesday, June 12
        weather_config=WeatherConfig(
            base_temperature_summer_c=22.0,
            base_cloud_cover_percent=35.0,
        ),
        meter_config=MeterConfig(
            meter_id="meter-001",
            base_power_kw=10.0,
            peak_power_kw=25.0,
        ),
        pv_config=PVConfig(
            system_id="pv-system-001",
            nominal_capacity_kwp=10.0,
        ),
        price_config=PriceConfig(
            feed_id="epex-spot-de",
            volatility_pct=10.0,
        ),
        consumer_configs=[
            ConsumerLoadConfig(
                device_id="oven-001",
                device_type=DeviceType.INDUSTRIAL_OVEN,
                rated_power_kw=3.5,
                duty_cycle_pct=70.0,
            ),
            ConsumerLoadConfig(
                device_id="hvac-001",
                device_type=DeviceType.HVAC,
                rated_power_kw=2.0,
                duty_cycle_pct=60.0,
                operating_windows=[
                    OperatingWindow(start_hour=8, end_hour=18),
                ],
            ),
        ],
    )


def get_high_consumption_scenario() -> ScenarioConfig:
    """Scenario 2: High consumption / peak load."""
    return ScenarioConfig(
        name="high_consumption",
        description="Peak load scenario with high consumption across all devices",
        seed=23456,
        duration_hours=24,
        start_time=datetime(2024, 1, 15, 0, 0, 0, tzinfo=UTC),  # Winter Monday
        weather_config=WeatherConfig(
            base_temperature_winter_c=-5.0,  # Cold winter day
            base_temperature_summer_c=5.0,
            base_cloud_cover_percent=80.0,  # Overcast
        ),
        meter_config=MeterConfig(
            meter_id="meter-001",
            base_power_kw=18.0,  # Higher base load
            peak_power_kw=40.0,  # Higher peak
        ),
        pv_config=PVConfig(
            system_id="pv-system-001",
            nominal_capacity_kwp=10.0,
        ),
        price_config=PriceConfig(
            feed_id="epex-spot-de",
            morning_peak_price=0.45,  # Higher peak prices
            evening_peak_price=0.55,
        ),
        consumer_configs=[
            ConsumerLoadConfig(
                device_id="oven-001",
                device_type=DeviceType.INDUSTRIAL_OVEN,
                rated_power_kw=5.0,  # Larger oven
                duty_cycle_pct=85.0,  # Higher duty cycle
                operating_windows=[
                    OperatingWindow(start_hour=6, end_hour=20),  # Extended hours
                ],
            ),
            ConsumerLoadConfig(
                device_id="hvac-001",
                device_type=DeviceType.HVAC,
                rated_power_kw=4.0,  # Higher HVAC load (heating)
                duty_cycle_pct=90.0,  # Almost constant
                operating_windows=[
                    OperatingWindow(start_hour=0, end_hour=12),  # 24/7 heating (part 1)
                    OperatingWindow(start_hour=12, end_hour=23),  # 24/7 heating (part 2)
                ],
            ),
            ConsumerLoadConfig(
                device_id="compressor-001",
                device_type=DeviceType.COMPRESSOR,
                rated_power_kw=7.5,
                duty_cycle_pct=75.0,
                operating_windows=[
                    OperatingWindow(start_hour=7, end_hour=19),
                ],
            ),
        ],
    )


def get_high_pv_generation_scenario() -> ScenarioConfig:
    """Scenario 3: High PV generation - clear summer day."""
    return ScenarioConfig(
        name="high_pv_generation",
        description="Clear summer day with maximum PV generation and potential export",
        seed=34567,
        duration_hours=24,
        start_time=datetime(2024, 6, 21, 0, 0, 0, tzinfo=UTC),  # Summer solstice
        weather_config=WeatherConfig(
            base_temperature_summer_c=28.0,  # Warm summer day
            base_cloud_cover_percent=5.0,  # Almost clear sky
            cloud_variance_percent=5.0,  # Stable conditions
            max_clear_sky_ghi_w_m2=1100.0,  # High irradiance
        ),
        meter_config=MeterConfig(
            meter_id="meter-001",
            base_power_kw=8.0,  # Lower base (summer)
            peak_power_kw=20.0,
        ),
        pv_config=PVConfig(
            system_id="pv-system-001",
            nominal_capacity_kwp=15.0,  # Larger PV system
            system_losses_percent=12.0,  # Optimized system
        ),
        price_config=PriceConfig(
            feed_id="epex-spot-de",
            midday_price=0.15,  # Low midday prices (solar surplus)
        ),
        consumer_configs=[
            ConsumerLoadConfig(
                device_id="oven-001",
                device_type=DeviceType.INDUSTRIAL_OVEN,
                rated_power_kw=3.0,
                duty_cycle_pct=60.0,
            ),
        ],
    )


def get_price_volatility_scenario() -> ScenarioConfig:
    """Scenario 4: High price volatility."""
    return ScenarioConfig(
        name="price_volatility",
        description="High price volatility scenario with significant price swings",
        seed=45678,
        duration_hours=24,
        start_time=datetime(2024, 2, 5, 0, 0, 0, tzinfo=UTC),  # Winter Monday
        weather_config=WeatherConfig(
            base_temperature_winter_c=0.0,
            base_cloud_cover_percent=60.0,
            cloud_variance_percent=30.0,  # Variable weather
        ),
        meter_config=MeterConfig(
            meter_id="meter-001",
            base_power_kw=12.0,
            peak_power_kw=30.0,
        ),
        pv_config=PVConfig(
            system_id="pv-system-001",
            nominal_capacity_kwp=10.0,
        ),
        price_config=PriceConfig(
            feed_id="epex-spot-de",
            night_price=0.08,  # Very low night price
            morning_peak_price=0.50,  # Very high peak
            midday_price=0.20,
            evening_peak_price=0.65,  # Extreme evening peak
            evening_price=0.30,
            volatility_pct=35.0,  # High volatility
            weekend_discount_pct=15.0,
        ),
        consumer_configs=[
            ConsumerLoadConfig(
                device_id="oven-001",
                device_type=DeviceType.INDUSTRIAL_OVEN,
                rated_power_kw=3.5,
                duty_cycle_pct=70.0,
            ),
            ConsumerLoadConfig(
                device_id="hvac-001",
                device_type=DeviceType.HVAC,
                rated_power_kw=2.5,
                duty_cycle_pct=65.0,
            ),
        ],
    )


def get_weekend_pattern_scenario() -> ScenarioConfig:
    """Scenario 5: Weekend pattern - 48 hours covering Sat-Sun."""
    return ScenarioConfig(
        name="weekend_pattern",
        description="Weekend pattern with reduced industrial activity over 48 hours",
        seed=56789,
        duration_hours=48,  # Two days
        start_time=datetime(2024, 3, 16, 0, 0, 0, tzinfo=UTC),  # Saturday
        weather_config=WeatherConfig(
            base_temperature_summer_c=15.0,  # Spring weather
            base_temperature_winter_c=8.0,
            base_cloud_cover_percent=45.0,
        ),
        meter_config=MeterConfig(
            meter_id="meter-001",
            base_power_kw=5.0,  # Lower weekend base
            peak_power_kw=15.0,  # Lower peak
        ),
        pv_config=PVConfig(
            system_id="pv-system-001",
            nominal_capacity_kwp=10.0,
        ),
        price_config=PriceConfig(
            feed_id="epex-spot-de",
            weekend_discount_pct=12.0,  # Higher weekend discount
        ),
        consumer_configs=[
            ConsumerLoadConfig(
                device_id="oven-001",
                device_type=DeviceType.INDUSTRIAL_OVEN,
                rated_power_kw=3.0,
                duty_cycle_pct=0.0,  # Off on weekends
                operate_on_weekends=False,
            ),
            ConsumerLoadConfig(
                device_id="hvac-001",
                device_type=DeviceType.HVAC,
                rated_power_kw=1.5,
                duty_cycle_pct=30.0,  # Reduced HVAC
                operate_on_weekends=True,
                operating_windows=[
                    OperatingWindow(start_hour=8, end_hour=18),
                ],
            ),
        ],
    )


def get_edge_cases_scenario() -> ScenarioConfig:
    """Scenario 6: Edge cases - boundary values and extremes."""
    return ScenarioConfig(
        name="edge_cases",
        description="Edge cases with boundary values: zero PV at night, max load, price floor",
        seed=67890,
        duration_hours=24,
        start_time=datetime(2024, 12, 21, 0, 0, 0, tzinfo=UTC),  # Winter solstice
        weather_config=WeatherConfig(
            base_temperature_winter_c=-10.0,  # Very cold
            base_temperature_summer_c=-5.0,
            daily_temp_amplitude_c=3.0,  # Small variation
            base_cloud_cover_percent=95.0,  # Very cloudy
            cloud_variance_percent=5.0,
            max_clear_sky_ghi_w_m2=400.0,  # Low winter irradiance
        ),
        meter_config=MeterConfig(
            meter_id="meter-001",
            base_power_kw=20.0,  # High base (heating)
            peak_power_kw=50.0,  # Very high peak
            power_factor_min=0.85,  # Wider power factor range
            power_factor_max=0.99,
        ),
        pv_config=PVConfig(
            system_id="pv-system-001",
            nominal_capacity_kwp=10.0,
            system_losses_percent=20.0,  # Higher winter losses
        ),
        price_config=PriceConfig(
            feed_id="epex-spot-de",
            night_price=0.05,  # At price floor
            morning_peak_price=0.55,
            evening_peak_price=0.70,  # Very high peak
            volatility_pct=25.0,
            min_price=0.05,  # Explicit floor
        ),
        consumer_configs=[
            ConsumerLoadConfig(
                device_id="oven-001",
                device_type=DeviceType.INDUSTRIAL_OVEN,
                rated_power_kw=5.0,
                duty_cycle_pct=95.0,  # Near-constant operation
                power_variance_pct=2.0,  # Low variance
            ),
            ConsumerLoadConfig(
                device_id="hvac-001",
                device_type=DeviceType.HVAC,
                rated_power_kw=6.0,  # Large heating load
                duty_cycle_pct=100.0,  # Always on
                operate_on_weekends=True,
                operating_windows=[
                    OperatingWindow(start_hour=0, end_hour=12),  # 24/7 operation (part 1)
                    OperatingWindow(start_hour=12, end_hour=23),  # 24/7 operation (part 2)
                ],
            ),
            ConsumerLoadConfig(
                device_id="pump-001",
                device_type=DeviceType.PUMP,
                rated_power_kw=1.5,
                duty_cycle_pct=50.0,
                operating_windows=[
                    OperatingWindow(start_hour=6, end_hour=22),
                ],
            ),
        ],
    )


ALL_SCENARIOS = {
    "normal_operation": get_normal_operation_scenario,
    "high_consumption": get_high_consumption_scenario,
    "high_pv_generation": get_high_pv_generation_scenario,
    "price_volatility": get_price_volatility_scenario,
    "weekend_pattern": get_weekend_pattern_scenario,
    "edge_cases": get_edge_cases_scenario,
}


# =============================================================================
# Generator Functions
# =============================================================================


def generate_timestamps(
    start_time: datetime,
    duration_hours: int,
    interval_minutes: int,
) -> list[datetime]:
    """Generate a list of timestamps for the scenario."""
    timestamps = []
    current = start_time
    end_time = start_time + timedelta(hours=duration_hours)
    delta = timedelta(minutes=interval_minutes)

    while current < end_time:
        timestamps.append(current)
        current += delta

    return timestamps


def generate_weather_data(
    scenario: ScenarioConfig,
    timestamps: list[datetime],
) -> list[WeatherReading]:
    """Generate weather readings for the scenario."""
    rng = DeterministicRNG(scenario.seed)
    config = scenario.weather_config or WeatherConfig()
    simulator = WeatherSimulator(
        entity_id="weather-001",
        rng=rng,
        interval=IntervalMinutes(scenario.interval_minutes),
        config=config,
    )

    return [simulator.generate_value(ts) for ts in timestamps]


def generate_pv_data(
    scenario: ScenarioConfig,
    timestamps: list[datetime],
    weather_simulator: WeatherSimulator,
) -> list[PVReading]:
    """Generate PV readings for the scenario."""
    rng = DeterministicRNG(scenario.seed)
    config = scenario.pv_config or PVConfig()
    simulator = PVGenerationSimulator(
        entity_id=config.system_id,
        rng=rng,
        weather_simulator=weather_simulator,
        interval=IntervalMinutes(scenario.interval_minutes),
        config=config,
    )

    return [simulator.generate_value(ts) for ts in timestamps]


def generate_meter_data(
    scenario: ScenarioConfig,
    timestamps: list[datetime],
) -> list[MeterReading]:
    """Generate meter readings for the scenario."""
    rng = DeterministicRNG(scenario.seed)
    config = scenario.meter_config or MeterConfig(meter_id="meter-001")
    simulator = EnergyMeterSimulator(
        entity_id=config.meter_id,
        rng=rng,
        interval=IntervalMinutes(scenario.interval_minutes),
        config=config,
    )

    return [simulator.generate_value(ts) for ts in timestamps]


def generate_price_data(
    scenario: ScenarioConfig,
    timestamps: list[datetime],
) -> list[PriceReading]:
    """Generate price readings for the scenario."""
    rng = DeterministicRNG(scenario.seed)
    config = scenario.price_config or PriceConfig()
    simulator = EnergyPriceSimulator(
        entity_id=config.feed_id,
        rng=rng,
        interval=IntervalMinutes(scenario.interval_minutes),
        config=config,
    )

    return [simulator.generate_value(ts) for ts in timestamps]


def generate_consumer_data(
    scenario: ScenarioConfig,
    timestamps: list[datetime],
) -> dict[str, list[ConsumerLoadReading]]:
    """Generate consumer load readings for all devices."""
    rng = DeterministicRNG(scenario.seed)
    configs = scenario.consumer_configs or [
        ConsumerLoadConfig(device_id="oven-001"),
    ]

    results: dict[str, list[ConsumerLoadReading]] = {}

    for config in configs:
        simulator = ConsumerLoadSimulator(
            entity_id=config.device_id,
            rng=rng,
            interval=IntervalMinutes(scenario.interval_minutes),
            config=config,
        )
        results[config.device_id] = [simulator.generate_value(ts) for ts in timestamps]

    return results


# =============================================================================
# Output Functions
# =============================================================================


def write_jsonl(
    readings: list[Any],
    output_path: Path,
) -> int:
    """Write readings to a JSONL file. Returns record count."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for reading in readings:
            if hasattr(reading, "to_json_payload"):
                payload = reading.to_json_payload()
            else:
                payload = reading.model_dump(mode="json")
                # Convert datetime to ISO string
                if "timestamp" in payload and isinstance(payload["timestamp"], datetime):
                    payload["timestamp"] = payload["timestamp"].isoformat().replace("+00:00", "Z")
            f.write(json.dumps(payload) + "\n")

    return len(readings)


def write_metadata(
    scenario: ScenarioConfig,
    output_dir: Path,
    record_counts: dict[str, int],
    generation_time: datetime,
) -> None:
    """Write metadata.json for the scenario."""
    metadata = {
        "scenario": {
            "name": scenario.name,
            "description": scenario.description,
            "seed": scenario.seed,
            "duration_hours": scenario.duration_hours,
            "interval_minutes": scenario.interval_minutes,
            "start_time": scenario.start_time.isoformat().replace("+00:00", "Z"),
            "end_time": (scenario.start_time + timedelta(hours=scenario.duration_hours))
            .isoformat()
            .replace("+00:00", "Z"),
        },
        "generation": {
            "timestamp": generation_time.isoformat().replace("+00:00", "Z"),
            "generator_version": "1.0.0",
        },
        "record_counts": record_counts,
        "total_records": sum(record_counts.values()),
        "configs": {
            "weather": (scenario.weather_config.model_dump() if scenario.weather_config else None),
            "meter": (scenario.meter_config.model_dump() if scenario.meter_config else None),
            "pv": scenario.pv_config.model_dump() if scenario.pv_config else None,
            "price": scenario.price_config.model_dump() if scenario.price_config else None,
            "consumers": [c.model_dump() for c in scenario.consumer_configs],
        },
    }

    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    logger.info(f"  Metadata written to {metadata_path}")


# =============================================================================
# Validation Functions
# =============================================================================


def validate_jsonl_file(
    file_path: Path,
    model_class: type,
) -> tuple[bool, int, list[str]]:
    """
    Validate all records in a JSONL file against a Pydantic model.

    Returns: (is_valid, record_count, errors)
    """
    errors = []
    count = 0

    with open(file_path) as f:
        for line_num, line in enumerate(f, 1):
            count += 1
            try:
                data = json.loads(line)
                # Handle nested structure for validation
                model_class.model_validate(data)
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: Invalid JSON - {e}")
            except Exception as e:
                errors.append(f"Line {line_num}: Validation error - {e}")

    return len(errors) == 0, count, errors


def validate_scenario(
    scenario_dir: Path,
) -> tuple[bool, dict[str, Any]]:
    """Validate all files in a scenario directory."""
    results: dict[str, Any] = {
        "valid": True,
        "files": {},
    }

    # Define file -> model mappings
    file_models: dict[str, type] = {
        "weather.jsonl": WeatherReading,
        "pv.jsonl": PVReading,
        "meter.jsonl": MeterReading,
        "price.jsonl": PriceReading,
    }

    # Check metadata exists
    metadata_path = scenario_dir / "metadata.json"
    if not metadata_path.exists():
        results["valid"] = False
        results["files"]["metadata.json"] = {
            "valid": False,
            "error": "File not found",
        }
    else:
        try:
            with open(metadata_path) as f:
                json.load(f)
            results["files"]["metadata.json"] = {"valid": True}
        except Exception as e:
            results["valid"] = False
            results["files"]["metadata.json"] = {
                "valid": False,
                "error": str(e),
            }

    # Validate feed files
    for filename, model_class in file_models.items():
        file_path = scenario_dir / filename
        if not file_path.exists():
            results["valid"] = False
            results["files"][filename] = {
                "valid": False,
                "error": "File not found",
            }
            continue

        is_valid, count, errors = validate_jsonl_file(file_path, model_class)
        results["files"][filename] = {
            "valid": is_valid,
            "record_count": count,
            "errors": errors[:5] if errors else [],  # Limit error output
        }
        if not is_valid:
            results["valid"] = False

    # Validate consumer files
    for consumer_file in scenario_dir.glob("consumer_*.jsonl"):
        is_valid, count, errors = validate_jsonl_file(consumer_file, ConsumerLoadReading)
        results["files"][consumer_file.name] = {
            "valid": is_valid,
            "record_count": count,
            "errors": errors[:5] if errors else [],
        }
        if not is_valid:
            results["valid"] = False

    return results["valid"], results


# =============================================================================
# Main Generation Function
# =============================================================================


def generate_scenario(
    scenario: ScenarioConfig,
    output_dir: Path,
) -> dict[str, int]:
    """Generate all data for a scenario and write to output directory."""
    logger.info(f"Generating scenario: {scenario.name}")
    logger.info(f"  Seed: {scenario.seed}")
    logger.info(f"  Duration: {scenario.duration_hours}h")
    logger.info(f"  Start: {scenario.start_time.isoformat()}")

    scenario_dir = output_dir / scenario.name
    scenario_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamps
    timestamps = generate_timestamps(
        scenario.start_time,
        scenario.duration_hours,
        scenario.interval_minutes,
    )
    logger.info(f"  Timestamps: {len(timestamps)} readings")

    record_counts: dict[str, int] = {}

    # Generate weather data (needed for PV)
    rng = DeterministicRNG(scenario.seed)
    weather_config = scenario.weather_config or WeatherConfig()
    weather_simulator = WeatherSimulator(
        entity_id="weather-001",
        rng=rng,
        interval=IntervalMinutes(scenario.interval_minutes),
        config=weather_config,
    )
    weather_readings = [weather_simulator.generate_value(ts) for ts in timestamps]
    record_counts["weather"] = write_jsonl(
        weather_readings,
        scenario_dir / "weather.jsonl",
    )
    logger.info(f"  Weather: {record_counts['weather']} records")

    # Generate PV data (depends on weather)
    pv_readings = generate_pv_data(scenario, timestamps, weather_simulator)
    record_counts["pv"] = write_jsonl(
        pv_readings,
        scenario_dir / "pv.jsonl",
    )
    logger.info(f"  PV: {record_counts['pv']} records")

    # Generate meter data
    meter_readings = generate_meter_data(scenario, timestamps)
    record_counts["meter"] = write_jsonl(
        meter_readings,
        scenario_dir / "meter.jsonl",
    )
    logger.info(f"  Meter: {record_counts['meter']} records")

    # Generate price data
    price_readings = generate_price_data(scenario, timestamps)
    record_counts["price"] = write_jsonl(
        price_readings,
        scenario_dir / "price.jsonl",
    )
    logger.info(f"  Price: {record_counts['price']} records")

    # Generate consumer data
    consumer_data = generate_consumer_data(scenario, timestamps)
    for device_id, readings in consumer_data.items():
        key = f"consumer_{device_id}"
        record_counts[key] = write_jsonl(
            readings,
            scenario_dir / f"consumer_{device_id}.jsonl",
        )
        logger.info(f"  Consumer {device_id}: {record_counts[key]} records")

    # Write metadata
    write_metadata(
        scenario,
        scenario_dir,
        record_counts,
        datetime.now(UTC),
    )

    return record_counts


def regenerate_and_verify(
    scenario_name: str,
    output_dir: Path,
) -> bool:
    """
    Regenerate a scenario and verify it matches the original.

    This tests that the seed produces identical output.
    """
    import hashlib
    import tempfile

    logger.info(f"Verifying regeneration for: {scenario_name}")

    scenario_func = ALL_SCENARIOS.get(scenario_name)
    if not scenario_func:
        logger.error(f"Unknown scenario: {scenario_name}")
        return False

    scenario = scenario_func()
    original_dir = output_dir / scenario_name

    if not original_dir.exists():
        logger.error(f"Original data not found at: {original_dir}")
        return False

    # Generate to temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        generate_scenario(scenario, temp_path)
        regen_dir = temp_path / scenario_name

        # Compare file hashes
        all_match = True
        for original_file in original_dir.glob("*.jsonl"):
            regen_file = regen_dir / original_file.name

            if not regen_file.exists():
                logger.error(f"  Missing regenerated file: {original_file.name}")
                all_match = False
                continue

            with open(original_file, "rb") as f:
                original_hash = hashlib.sha256(f.read()).hexdigest()
            with open(regen_file, "rb") as f:
                regen_hash = hashlib.sha256(f.read()).hexdigest()

            if original_hash == regen_hash:
                logger.info(f"  {original_file.name}: MATCH")
            else:
                logger.error(f"  {original_file.name}: MISMATCH")
                all_match = False

    return all_match


# =============================================================================
# CLI
# =============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate fixed seed datasets for FACIS simulation testing",
    )
    parser.add_argument(
        "--scenario",
        "-s",
        choices=list(ALL_SCENARIOS.keys()) + ["all"],
        default="all",
        help="Scenario to generate (default: all)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "seeds",
        help="Output directory for datasets",
    )
    parser.add_argument(
        "--validate",
        "-v",
        action="store_true",
        help="Validate generated datasets against Pydantic models",
    )
    parser.add_argument(
        "--verify-regeneration",
        "-r",
        action="store_true",
        help="Verify that regenerating produces identical output",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List available scenarios",
    )

    args = parser.parse_args()

    if args.list:
        print("\nAvailable scenarios:")
        print("-" * 60)
        for name, func in ALL_SCENARIOS.items():
            scenario = func()
            print(f"\n{name}:")
            print(f"  Seed: {scenario.seed}")
            print(f"  Duration: {scenario.duration_hours}h")
            print(f"  Description: {scenario.description}")
        return 0

    # Determine scenarios to generate
    if args.scenario == "all":
        scenarios_to_generate = list(ALL_SCENARIOS.keys())
    else:
        scenarios_to_generate = [args.scenario]

    output_dir = args.output_dir.resolve()
    logger.info(f"Output directory: {output_dir}")

    # Generate scenarios
    total_records = 0
    for scenario_name in scenarios_to_generate:
        scenario_func = ALL_SCENARIOS[scenario_name]
        scenario = scenario_func()
        counts = generate_scenario(scenario, output_dir)
        total_records += sum(counts.values())
        print()

    logger.info(f"Total records generated: {total_records}")

    # Calculate total size
    total_size = 0
    for scenario_name in scenarios_to_generate:
        scenario_dir = output_dir / scenario_name
        for file in scenario_dir.glob("*"):
            total_size += file.stat().st_size
    logger.info(f"Total dataset size: {total_size / 1024 / 1024:.2f} MB")

    # Validate if requested
    if args.validate:
        print("\n" + "=" * 60)
        print("Validating datasets...")
        print("=" * 60)

        all_valid = True
        for scenario_name in scenarios_to_generate:
            scenario_dir = output_dir / scenario_name
            is_valid, results = validate_scenario(scenario_dir)

            status = "PASS" if is_valid else "FAIL"
            print(f"\n{scenario_name}: {status}")

            for filename, file_result in results["files"].items():
                file_status = "OK" if file_result.get("valid", False) else "FAIL"
                count = file_result.get("record_count", "N/A")
                print(f"  {filename}: {file_status} ({count} records)")
                if file_result.get("errors"):
                    for error in file_result["errors"]:
                        print(f"    ERROR: {error}")

            if not is_valid:
                all_valid = False

        if not all_valid:
            logger.error("Validation failed!")
            return 1

    # Verify regeneration if requested
    if args.verify_regeneration:
        print("\n" + "=" * 60)
        print("Verifying regeneration produces identical output...")
        print("=" * 60)

        all_match = True
        for scenario_name in scenarios_to_generate:
            if not regenerate_and_verify(scenario_name, output_dir):
                all_match = False
                print(f"\n{scenario_name}: REGENERATION MISMATCH")
            else:
                print(f"\n{scenario_name}: REGENERATION VERIFIED")

        if not all_match:
            logger.error("Regeneration verification failed!")
            return 1

    logger.info("Done!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
