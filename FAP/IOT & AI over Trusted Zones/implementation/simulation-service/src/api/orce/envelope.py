"""
Tick envelope builder for ORCE.

Builds a unified JSON envelope that wraps all Smart Energy and Smart City
feeds for a single simulation tick.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.models.correlation import CorrelatedSnapshot
from src.simulators.smart_city.correlation import SmartCitySnapshot


def build_tick_envelope(
    timestamp: datetime,
    site_id: str,
    energy_snapshot: CorrelatedSnapshot,
    city_snapshot: SmartCitySnapshot,
    mode: str,
    seed: int,
    schema_version: str = "1.0",
) -> dict[str, Any]:
    """
    Build a unified tick envelope for ORCE.

    ORCE receives this envelope, validates schema, splits by feed type,
    and publishes each feed to its respective Kafka topic.

    Args:
        timestamp: Simulation timestamp for this tick.
        site_id: Site identifier for correlation.
        energy_snapshot: Correlated Smart Energy snapshot.
        city_snapshot: Correlated Smart City snapshot.
        mode: Simulation mode (normal, event).
        seed: Simulation seed for reproducibility.
        schema_version: Envelope schema version.

    Returns:
        Dict representing the tick envelope.
    """
    ts_iso = timestamp.isoformat().replace("+00:00", "Z")

    return {
        "type": "sim.tick",
        "schema_version": schema_version,
        "timestamp": ts_iso,
        "mode": mode,
        "seed": seed,
        "site_id": site_id,
        "smart_energy": {
            "meters": [m.to_json_payload() for m in energy_snapshot.meter_readings],
            "pv": [p.to_json_payload() for p in energy_snapshot.pv_readings],
            "weather": energy_snapshot.weather.to_json_payload()
            if energy_snapshot.weather
            else None,
            "price": energy_snapshot.price.to_json_payload() if energy_snapshot.price else None,
            "consumers": [c.to_json_payload() for c in energy_snapshot.consumer_loads],
            "metrics": energy_snapshot.metrics.to_json_payload(),
        },
        "smart_city": city_snapshot.to_json_payload(),
    }
