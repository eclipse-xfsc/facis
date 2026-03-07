#!/usr/bin/env python3
"""
Smart City correlation demo: Event triggers higher dimming in zone.

Demonstrates that when a high-severity emergency event occurs in a zone,
the streetlights in that zone boost their dimming level, consuming more power.

Usage:
    python scripts/demo_event_dimming.py
"""

from datetime import UTC, datetime, timedelta

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes
from src.models.smart_city.streetlight import StreetlightConfig
from src.simulators.smart_city import (
    CityEventSimulator,
    SmartCityCorrelationEngine,
    StreetlightSimulator,
    TrafficSimulator,
    VisibilitySimulator,
)

SEED = 12345
CITY_ID = "city-berlin"
INTERVAL = IntervalMinutes.FIFTEEN_MINUTES
DATE = datetime(2026, 2, 10, 0, 0, tzinfo=UTC)


def main() -> None:
    print("=" * 65)
    print("SMART CITY CORRELATION DEMO: Event -> Dimming Response")
    print("=" * 65)
    print(f"Date: {DATE.strftime('%Y-%m-%d')}")
    print(f"Seed: {SEED}")
    print()

    rng = DeterministicRNG(SEED)

    # Zone 1: has events in event mode
    event_sim = CityEventSimulator(
        "event-z1", rng, INTERVAL, city_id=CITY_ID, zone_id="zone-001", mode="event"
    )
    light1 = StreetlightSimulator(
        "light-001",
        rng,
        INTERVAL,
        config=StreetlightConfig(light_id="light-001", zone_id="zone-001"),
        city_id=CITY_ID,
    )
    light2 = StreetlightSimulator(
        "light-002",
        rng,
        INTERVAL,
        config=StreetlightConfig(light_id="light-002", zone_id="zone-001"),
        city_id=CITY_ID,
    )
    traffic_sim = TrafficSimulator("traffic-z1", rng, INTERVAL, city_id=CITY_ID, zone_id="zone-001")
    vis_sim = VisibilitySimulator("vis-001", rng, INTERVAL, city_id=CITY_ID)

    engine = SmartCityCorrelationEngine(
        event_simulators=[event_sim],
        streetlight_simulators=[light1, light2],
        traffic_simulators=[traffic_sim],
        visibility_simulator=vis_sim,
        city_id=CITY_ID,
        interval_minutes=INTERVAL.value,
    )

    print("Scanning 24h for event impact on streetlights...")
    print()
    print(
        f"{'Time':>5}  {'Event':>12}  {'Sev':>3}  {'Active':>6}  "
        f"{'Light-001':>10}  {'Light-002':>10}  {'Traffic':>7}"
    )
    print("-" * 65)

    current = DATE
    end = DATE + timedelta(days=1)
    last_event_active = False

    while current < end:
        snap = engine.generate_snapshot(current)

        event = snap.events[0] if snap.events else None
        is_active = event.active if event else False

        # Print every hour, plus transitions around events
        hour_boundary = current.minute == 0
        transition = is_active != last_event_active

        if hour_boundary or transition:
            event_type = event.event_type.value if event and is_active else "-"
            severity = str(event.severity.value) if event and is_active else "-"
            active_str = "YES" if is_active else "no"

            l1 = snap.streetlights[0] if snap.streetlights else None
            l2 = snap.streetlights[1] if len(snap.streetlights) > 1 else None
            l1_str = f"{l1.dimming_level_pct:.1f}%" if l1 else "-"
            l2_str = f"{l2.dimming_level_pct:.1f}%" if l2 else "-"

            traffic = snap.traffic_readings[0] if snap.traffic_readings else None
            t_str = f"{traffic.traffic_index:.0f}" if traffic else "-"

            print(
                f"{current.strftime('%H:%M'):>5}  {event_type:>12}  {severity:>3}  "
                f"{active_str:>6}  {l1_str:>10}  {l2_str:>10}  {t_str:>7}"
            )

        last_event_active = is_active
        current += timedelta(minutes=INTERVAL.value)

    print()
    print("Key observations:")
    print("  - During the emergency (sev=3), streetlight dimming increases by +50%")
    print("  - During the accident (sev=2), streetlight dimming increases by +30%")
    print("  - Low-severity events (sev=1) do not trigger dimming boost")
    print("  - At night, lights are already at ~100%, so boost is less visible")
    print("=" * 65)


if __name__ == "__main__":
    main()
