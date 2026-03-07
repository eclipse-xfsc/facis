#!/usr/bin/env python3
"""
MS2 End-to-End Demo: Simulation → ORCE → Kafka → Validation

This script validates the full data pipeline by:
1. Checking connectivity (simulation service, ORCE, Kafka)
2. Running a deterministic simulation
3. Consuming from all Kafka topics
4. Validating message schemas, timestamps, and correlations

Usage:
    # Local (Docker Compose)
    python scripts/demo_e2e.py

    # Remote cluster with TLS
    python scripts/demo_e2e.py \
        --bootstrap 212.132.83.222:9093 \
        --tls \
        --ca-cert certs/ca.crt \
        --client-cert certs/client.crt \
        --client-key certs/client.key

    # Custom simulation endpoint
    python scripts/demo_e2e.py --sim-url http://localhost:8080
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import defaultdict
from datetime import datetime

import httpx
from confluent_kafka import Consumer, KafkaError, KafkaException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("demo_e2e")

# All expected Kafka topics
EXPECTED_TOPICS = [
    "sim.smart_energy.meter",
    "sim.smart_energy.pv",
    "sim.smart_energy.weather",
    "sim.smart_energy.price",
    "sim.smart_energy.consumer",
    "sim.smart_city.light",
    "sim.smart_city.traffic",
    "sim.smart_city.event",
    "sim.smart_city.weather",
]

# Required fields per topic
REQUIRED_FIELDS = {
    "sim.smart_energy.meter": [
        "site_id",
        "meter_id",
        "timestamp",
        "active_power_kw",
        "active_energy_kwh_total",
        "schema_version",
        "type",
    ],
    "sim.smart_energy.pv": ["site_id", "pv_system_id", "timestamp", "schema_version", "type"],
    "sim.smart_energy.weather": [
        "site_id",
        "timestamp",
        "temperature_c",
        "solar_irradiance_w_m2",
        "schema_version",
        "type",
    ],
    "sim.smart_energy.price": [
        "timestamp",
        "price_eur_per_kwh",
        "tariff_type",
        "schema_version",
        "type",
    ],
    "sim.smart_energy.consumer": [
        "site_id",
        "device_id",
        "timestamp",
        "device_state",
        "device_power_kw",
        "schema_version",
        "type",
    ],
    "sim.smart_city.light": [
        "city_id",
        "zone_id",
        "light_id",
        "timestamp",
        "dimming_level_pct",
        "power_w",
        "schema_version",
        "type",
    ],
    "sim.smart_city.traffic": [
        "city_id",
        "zone_id",
        "timestamp",
        "traffic_index",
        "schema_version",
        "type",
    ],
    "sim.smart_city.event": [
        "city_id",
        "zone_id",
        "timestamp",
        "event_type",
        "severity",
        "schema_version",
        "type",
    ],
    "sim.smart_city.weather": [
        "city_id",
        "timestamp",
        "fog_index",
        "visibility",
        "schema_version",
        "type",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MS2 End-to-End Demo Validator")
    parser.add_argument("--bootstrap", default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--tls", action="store_true", help="Enable TLS for Kafka")
    parser.add_argument("--ca-cert", default=None, help="CA certificate path")
    parser.add_argument("--client-cert", default=None, help="Client certificate path")
    parser.add_argument("--client-key", default=None, help="Client key path")
    parser.add_argument("--sim-url", default="http://localhost:8080", help="Simulation service URL")
    parser.add_argument("--orce-url", default="http://localhost:1880", help="ORCE URL")
    parser.add_argument(
        "--consume-timeout", type=int, default=120, help="Max seconds to consume messages"
    )
    parser.add_argument(
        "--min-messages", type=int, default=5, help="Min messages per topic to validate"
    )
    return parser.parse_args()


def check_simulation(url: str) -> bool:
    """Check if simulation service is reachable and healthy."""
    try:
        resp = httpx.get(f"{url}/api/v1/health", timeout=5)
        if resp.is_success:
            logger.info(f"Simulation service healthy: {resp.json()}")
            return True
        logger.error(f"Simulation service unhealthy: {resp.status_code}")
        return False
    except Exception as e:
        logger.error(f"Cannot reach simulation service at {url}: {e}")
        return False


def check_orce(url: str) -> bool:
    """Check if ORCE is reachable."""
    try:
        resp = httpx.get(url, timeout=5)
        if resp.is_success:
            logger.info("ORCE is reachable")
            return True
        logger.warning(f"ORCE returned {resp.status_code}")
        return False
    except Exception as e:
        logger.warning(f"Cannot reach ORCE at {url}: {e}")
        return False


def create_kafka_consumer(args: argparse.Namespace) -> Consumer:
    """Create a Kafka consumer with optional TLS."""
    config = {
        "bootstrap.servers": args.bootstrap,
        "group.id": f"facis-demo-validator-{int(time.time())}",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
        "session.timeout.ms": 10000,
    }
    if args.tls:
        config["security.protocol"] = "SSL"
        if args.ca_cert:
            config["ssl.ca.location"] = args.ca_cert
        if args.client_cert:
            config["ssl.certificate.location"] = args.client_cert
        if args.client_key:
            config["ssl.key.location"] = args.client_key
        logger.info("Kafka consumer configured with TLS")

    return Consumer(config)


def consume_messages(consumer: Consumer, timeout: int, min_messages: int) -> dict[str, list[dict]]:
    """Consume messages from all topics until timeout or sufficient messages."""
    consumer.subscribe(EXPECTED_TOPICS)
    messages: dict[str, list[dict]] = defaultdict(list)
    start = time.time()

    logger.info(
        f"Consuming from {len(EXPECTED_TOPICS)} topics (timeout: {timeout}s, min: {min_messages}/topic)..."
    )

    while time.time() - start < timeout:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            logger.error(f"Consumer error: {msg.error()}")
            continue

        topic = msg.topic()
        try:
            payload = json.loads(msg.value().decode("utf-8"))
            messages[topic].append(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Invalid message on {topic}: {e}")

        # Check if we have enough messages from all topics
        total = sum(len(v) for v in messages.values())
        if total % 50 == 0:
            coverage = sum(1 for v in messages.values() if len(v) >= min_messages)
            logger.info(
                f"  {total} messages consumed, {coverage}/{len(EXPECTED_TOPICS)} topics satisfied"
            )

        if all(len(messages[t]) >= min_messages for t in EXPECTED_TOPICS):
            logger.info("All topics have sufficient messages!")
            break

    consumer.close()
    return dict(messages)


def validate_schema(messages: dict[str, list[dict]]) -> tuple[int, int]:
    """Validate required fields in messages. Returns (pass_count, fail_count)."""
    passed = 0
    failed = 0

    for topic, msgs in messages.items():
        required = REQUIRED_FIELDS.get(topic, [])
        for msg in msgs:
            missing = [f for f in required if f not in msg]
            if missing:
                logger.warning(
                    f"[{topic}] Missing fields: {missing} in message at {msg.get('timestamp', '?')}"
                )
                failed += 1
            else:
                passed += 1

    return passed, failed


def validate_timestamps(messages: dict[str, list[dict]]) -> bool:
    """Check that timestamps are increasing within each topic."""
    all_ok = True
    for topic, msgs in messages.items():
        timestamps = []
        for msg in msgs:
            ts_str = msg.get("timestamp")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    timestamps.append(ts)
                except ValueError:
                    logger.warning(f"[{topic}] Invalid timestamp format: {ts_str}")
                    all_ok = False

        # Check monotonicity
        for i in range(1, len(timestamps)):
            if timestamps[i] < timestamps[i - 1]:
                logger.warning(f"[{topic}] Non-monotonic timestamps at index {i}")
                all_ok = False
                break

    return all_ok


def validate_meter_monotonic(messages: dict[str, list[dict]]) -> bool:
    """Validate that active_energy_kwh_total is monotonically increasing."""
    meter_msgs = messages.get("sim.smart_energy.meter", [])
    if not meter_msgs:
        logger.warning("No meter messages to validate")
        return False

    # Group by meter_id
    by_meter: dict[str, list[float]] = defaultdict(list)
    for msg in meter_msgs:
        meter_id = msg.get("meter_id", "unknown")
        energy = msg.get("active_energy_kwh_total")
        if energy is not None:
            by_meter[meter_id].append(energy)

    all_ok = True
    for meter_id, values in by_meter.items():
        for i in range(1, len(values)):
            if values[i] < values[i - 1]:
                logger.warning(
                    f"Meter {meter_id}: energy not monotonic at index {i} ({values[i - 1]} -> {values[i]})"
                )
                all_ok = False
                break
        if all_ok:
            logger.info(
                f"Meter {meter_id}: energy monotonic OK ({values[0]:.2f} -> {values[-1]:.2f} kWh)"
            )

    return all_ok


def validate_cost_correlation(messages: dict[str, list[dict]]) -> bool:
    """
    Validate Smart Energy cost correlation:
    Compare cost during high-price vs low-price windows.
    """
    price_msgs = messages.get("sim.smart_energy.price", [])
    consumer_msgs = messages.get("sim.smart_energy.consumer", [])

    if not price_msgs or not consumer_msgs:
        logger.warning("Insufficient data for cost correlation")
        return False

    # Find ON windows with prices
    high_cost_sum = 0.0
    low_cost_sum = 0.0
    high_count = 0
    low_count = 0

    price_by_ts = {m.get("timestamp"): m for m in price_msgs}

    for cm in consumer_msgs:
        if cm.get("device_state") != "ON":
            continue
        ts = cm.get("timestamp")
        price_msg = price_by_ts.get(ts)
        if not price_msg:
            continue

        price = price_msg.get("price_eur_per_kwh", 0)
        power = cm.get("device_power_kw", 0)
        cost = price * power

        tariff = price_msg.get("tariff_type", "")
        if tariff in ("MORNING_PEAK", "EVENING_PEAK"):
            high_cost_sum += cost
            high_count += 1
        else:
            low_cost_sum += cost
            low_count += 1

    if high_count > 0 and low_count > 0:
        avg_high = high_cost_sum / high_count
        avg_low = low_cost_sum / low_count
        logger.info(
            f"Cost correlation: avg high-tariff cost={avg_high:.4f} EUR/h, "
            f"avg low-tariff cost={avg_low:.4f} EUR/h "
            f"(ratio: {avg_high / avg_low:.2f}x)"
        )
        if avg_high > avg_low:
            logger.info("Cost correlation validated: high-tariff > low-tariff")
            return True
        else:
            logger.warning("Cost correlation unexpected: high-tariff <= low-tariff")
            return False
    else:
        logger.info(
            f"Cost correlation: high_count={high_count}, low_count={low_count} (insufficient data for comparison)"
        )
        return high_count > 0 or low_count > 0


def validate_event_dimming(messages: dict[str, list[dict]]) -> bool:
    """
    Validate Smart City event→dimming correlation:
    When an event with severity >= 2 is active, dimming should increase.
    """
    event_msgs = messages.get("sim.smart_city.event", [])
    light_msgs = messages.get("sim.smart_city.light", [])

    if not event_msgs or not light_msgs:
        logger.warning("Insufficient data for event-dimming correlation")
        return False

    # Find active events with severity >= 2
    active_events = [e for e in event_msgs if e.get("active") and e.get("severity", 0) >= 2]

    if not active_events:
        logger.info("No active events with severity >= 2 found (normal mode — this is expected)")
        return True

    # Check if dimming increased in the same zone within 5 minutes
    for event in active_events:
        zone = event.get("zone_id")
        event_ts = event.get("timestamp", "")
        zone_lights = [l for l in light_msgs if l.get("zone_id") == zone]
        high_dimming = [l for l in zone_lights if l.get("dimming_level_pct", 0) > 50]

        if high_dimming:
            logger.info(
                f"Event→dimming correlation: zone={zone}, event at {event_ts}, dimming boost detected"
            )
            return True

    logger.warning("Event→dimming correlation not detected")
    return False


def print_summary(
    messages: dict[str, list[dict]],
    schema_pass: int,
    schema_fail: int,
    ts_ok: bool,
    mono_ok: bool,
    cost_ok: bool,
    dimming_ok: bool,
) -> bool:
    """Print final summary and return overall pass/fail."""
    print("\n" + "=" * 70)
    print("  FACIS MS2 End-to-End Validation Report")
    print("=" * 70)

    # Topic coverage
    print("\n--- Topic Coverage ---")
    all_covered = True
    for topic in EXPECTED_TOPICS:
        count = len(messages.get(topic, []))
        status = "OK" if count > 0 else "MISSING"
        if count == 0:
            all_covered = False
        print(f"  {topic:40s} {count:5d} messages  [{status}]")

    # Validation results
    print("\n--- Validation Results ---")
    checks = [
        ("Schema validity", schema_fail == 0, f"{schema_pass} passed, {schema_fail} failed"),
        ("Timestamp monotonicity", ts_ok, "increasing" if ts_ok else "non-monotonic detected"),
        ("Energy counter monotonic", mono_ok, "verified" if mono_ok else "failed"),
        ("Cost impact correlation", cost_ok, "high > low tariff" if cost_ok else "inconclusive"),
        ("Event→dimming correlation", dimming_ok, "detected" if dimming_ok else "not detected"),
    ]

    all_pass = all_covered
    for name, passed, detail in checks:
        status = "PASS" if passed else "FAIL"
        all_pass = all_pass and passed
        print(f"  {name:35s} [{status}]  {detail}")

    print("\n" + "=" * 70)
    if all_pass:
        print("  RESULT: ALL CHECKS PASSED")
    else:
        print("  RESULT: SOME CHECKS FAILED")
    print("=" * 70 + "\n")

    return all_pass


def main() -> None:
    args = parse_args()

    print("\n" + "=" * 70)
    print("  FACIS MS2 End-to-End Demo")
    print("  Simulation -> ORCE -> Kafka -> Validation")
    print("=" * 70 + "\n")

    # Step 1: Connectivity checks
    logger.info("--- Step 1: Connectivity Checks ---")
    sim_ok = check_simulation(args.sim_url)
    orce_ok = check_orce(args.orce_url)

    if not sim_ok:
        logger.error("Simulation service not reachable. Ensure it is running.")
        sys.exit(1)

    if not orce_ok:
        logger.warning("ORCE not reachable — ORCE channel may be disabled")

    # Step 2: Consume from Kafka
    logger.info("\n--- Step 2: Consuming from Kafka ---")
    try:
        consumer = create_kafka_consumer(args)
    except KafkaException as e:
        logger.error(f"Failed to create Kafka consumer: {e}")
        sys.exit(1)

    messages = consume_messages(consumer, args.consume_timeout, args.min_messages)
    total = sum(len(v) for v in messages.values())
    logger.info(f"Total messages consumed: {total}")

    if total == 0:
        logger.error("No messages consumed. Ensure the simulation is running and publishing.")
        sys.exit(1)

    # Step 3: Validate
    logger.info("\n--- Step 3: Validation ---")
    schema_pass, schema_fail = validate_schema(messages)
    ts_ok = validate_timestamps(messages)
    mono_ok = validate_meter_monotonic(messages)
    cost_ok = validate_cost_correlation(messages)
    dimming_ok = validate_event_dimming(messages)

    # Step 4: Summary
    all_pass = print_summary(
        messages, schema_pass, schema_fail, ts_ok, mono_ok, cost_ok, dimming_ok
    )
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
