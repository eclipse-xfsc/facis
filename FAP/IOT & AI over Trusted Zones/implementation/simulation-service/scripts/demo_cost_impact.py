#!/usr/bin/env python3
"""
Smart Energy correlation demo: Cost impact of oven schedule vs price + PV.

Demonstrates that running the oven during peak-price evening hours (event mode)
costs significantly more than the normal schedule that runs during cheaper hours
with PV generation offset.

Usage:
    python scripts/demo_cost_impact.py
"""

from datetime import UTC, datetime, timedelta

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes
from src.models.consumer_load import ConsumerLoadConfig, DeviceType
from src.models.price import PriceConfig
from src.simulators.consumer_load import ConsumerLoadSimulator
from src.simulators.energy_price import EnergyPriceSimulator
from src.simulators.pv_generation import PVGenerationSimulator
from src.simulators.weather import WeatherSimulator

SEED = 12345
SITE_ID = "site-berlin-001"
INTERVAL = IntervalMinutes.FIFTEEN_MINUTES
DATE = datetime(2026, 6, 15, 0, 0, tzinfo=UTC)  # Summer day for good PV


def run_simulation(mode: str) -> dict:
    """Run a 24h simulation and calculate cost metrics."""
    rng = DeterministicRNG(SEED)

    # Create simulators
    weather = WeatherSimulator("weather-001", rng, INTERVAL, site_id=SITE_ID)
    pv = PVGenerationSimulator("pv-001", rng, weather, INTERVAL, site_id=SITE_ID)
    price = EnergyPriceSimulator("price-001", rng, INTERVAL, site_id=SITE_ID, mode=mode)
    oven = ConsumerLoadSimulator(
        "oven-001",
        rng,
        INTERVAL,
        config=ConsumerLoadConfig(
            device_id="oven-001",
            device_type=DeviceType.INDUSTRIAL_OVEN,
            rated_power_kw=3.0,
            duty_cycle_pct=70.0,
            power_variance_pct=5.0,
            operate_on_weekends=False,
        ),
        site_id=SITE_ID,
        mode=mode,
    )

    total_cost = 0.0
    total_oven_energy = 0.0
    total_pv_energy = 0.0
    oven_on_minutes = 0
    interval_hours = INTERVAL.value / 60.0

    current = DATE
    end = DATE + timedelta(days=1)

    while current < end:
        oven_reading = oven.generate_at(current).value
        price_reading = price.generate_at(current).value
        pv_reading = pv.generate_at(current).value

        oven_kw = oven_reading.device_power_kw
        pv_kw = pv_reading.readings.power_output_kw
        eur_per_kwh = price_reading.price_eur_per_kwh

        # Oven energy this interval
        oven_energy = oven_kw * interval_hours
        total_oven_energy += oven_energy

        # PV offset: if PV is generating, oven effectively costs less
        net_oven_kw = max(0.0, oven_kw - pv_kw)
        net_energy = net_oven_kw * interval_hours
        cost = net_energy * eur_per_kwh
        total_cost += cost

        total_pv_energy += pv_kw * interval_hours

        if oven_reading.device_state.value == "ON":
            oven_on_minutes += INTERVAL.value

        current += timedelta(minutes=INTERVAL.value)

    return {
        "mode": mode,
        "total_cost_eur": total_cost,
        "total_oven_energy_kwh": total_oven_energy,
        "total_pv_energy_kwh": total_pv_energy,
        "oven_on_minutes": oven_on_minutes,
    }


def main() -> None:
    print("=" * 65)
    print("SMART ENERGY CORRELATION DEMO: Cost Impact Analysis")
    print("=" * 65)
    print(f"Date: {DATE.strftime('%Y-%m-%d')} (summer, good PV day)")
    print(f"Seed: {SEED}")
    print()

    normal = run_simulation("normal")
    event = run_simulation("event")

    print("--- Normal Day (oven runs per regular schedule) ---")
    print(f"  Oven ON time:       {normal['oven_on_minutes']} min")
    print(f"  Oven energy:        {normal['total_oven_energy_kwh']:.2f} kWh")
    print(f"  PV generation:      {normal['total_pv_energy_kwh']:.2f} kWh")
    print(f"  Net oven cost:      EUR {normal['total_cost_eur']:.4f}")
    print()

    print("--- Event Day (oven forced ON during evening peak 17-19h) ---")
    print(f"  Oven ON time:       {event['oven_on_minutes']} min")
    print(f"  Oven energy:        {event['total_oven_energy_kwh']:.2f} kWh")
    print(f"  PV generation:      {event['total_pv_energy_kwh']:.2f} kWh")
    print(f"  Net oven cost:      EUR {event['total_cost_eur']:.4f}")
    print()

    diff = event["total_cost_eur"] - normal["total_cost_eur"]
    if normal["total_cost_eur"] > 0:
        pct = (diff / normal["total_cost_eur"]) * 100
    else:
        pct = 0.0

    print("--- Comparison ---")
    print(f"  Extra cost (event vs normal): EUR {diff:+.4f} ({pct:+.1f}%)")
    print()
    print("Conclusion: Running the oven during evening peak prices")
    print("(when PV generation is low) costs significantly more than")
    print("the normal schedule that overlaps with PV generation hours.")
    print("=" * 65)


if __name__ == "__main__":
    main()
