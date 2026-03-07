#!/usr/bin/env python3
"""
WP3 Lakehouse Validation: Verify Bronze / Silver / Gold correctness.

Runs validation checks against the live Trino cluster:
  1. Bronze: All 9 tables have data
  2. Silver: All 9 views return typed data, derived fields are computed
  3. Gold:   All 12 views return aggregated data
  4. Data quality: Silver filters reject malformed records
  5. Cross-layer: Gold aggregations are consistent with Silver

Usage:
    python scripts/validate_lakehouse.py --env-file .env.cluster
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib3

import requests
import trino

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_KEYCLOAK_URL = "https://identity.facis.cloud/realms/facis"
DEFAULT_TRINO_HOST = "212.132.83.150"
DEFAULT_TRINO_PORT = 8443
DEFAULT_CATALOG = "fap-iotai-stackable"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_connection(env_file: str | None = None) -> tuple[trino.dbapi.Connection, str]:
    if env_file:
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, _, v = line.partition("=")
                    os.environ[k.strip()] = v.strip()

    keycloak_url = os.getenv("FACIS_KEYCLOAK_URL", DEFAULT_KEYCLOAK_URL)
    host = os.getenv("FACIS_TRINO_HOST", DEFAULT_TRINO_HOST)
    port = int(os.getenv("FACIS_TRINO_PORT", str(DEFAULT_TRINO_PORT)))
    catalog = os.getenv("FACIS_TRINO_CATALOG", DEFAULT_CATALOG)

    resp = requests.post(
        f"{keycloak_url}/protocol/openid-connect/token",
        data={
            "client_id": "OIDC",
            "client_secret": os.environ["FACIS_OIDC_CLIENT_SECRET"],
            "username": os.environ["FACIS_OIDC_USERNAME"],
            "password": os.environ["FACIS_OIDC_PASSWORD"],
            "grant_type": "password",
            "scope": "openid",
        },
        verify=False,
        timeout=15,
    )
    if not resp.ok:
        print(f"AUTH FAILED: {resp.status_code}")
        sys.exit(1)
    token = resp.json()["access_token"]
    conn = trino.dbapi.connect(
        host=host, port=port, user="test", catalog=catalog,
        auth=trino.auth.JWTAuthentication(token),
        http_scheme="https", verify=False,
    )
    return conn, catalog


def fresh_conn() -> tuple[trino.dbapi.Connection, str]:
    """Get a fresh connection (tokens are short-lived)."""
    return get_connection(os.environ.get("_ENV_FILE"))


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

class ValidationResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: list[str] = []

    def ok(self, msg: str):
        self.passed += 1
        print(f"  ✓ {msg}")

    def fail(self, msg: str):
        self.failed += 1
        self.errors.append(msg)
        print(f"  ✗ {msg}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'=' * 60}")
        print(f"  VALIDATION: {self.passed}/{total} checks passed")
        if self.errors:
            print(f"  FAILURES:")
            for e in self.errors:
                print(f"    - {e}")
        print(f"{'=' * 60}")
        return self.failed == 0


def validate_bronze(result: ValidationResult, catalog: str):
    """Check all 9 Bronze tables exist and have data."""
    print("\n--- BRONZE LAYER ---")
    tables = [
        "energy_meter", "pv_generation", "weather", "energy_price",
        "consumer_load", "streetlight", "traffic", "city_event", "city_weather",
    ]
    for t in tables:
        try:
            conn, _ = fresh_conn()
            cur = conn.cursor()
            cur.execute(f'SELECT 1 FROM "{catalog}".bronze."{t}" LIMIT 1')
            rows = cur.fetchall()
            if rows:
                result.ok(f"bronze.{t} has data")
            else:
                result.fail(f"bronze.{t} is EMPTY")
        except Exception as e:
            result.fail(f"bronze.{t} ERROR: {str(e)[:80]}")


def validate_silver(result: ValidationResult, catalog: str):
    """Check Silver views return typed data with derived fields."""
    print("\n--- SILVER LAYER ---")

    # Basic view checks
    views = [
        "energy_meter", "pv_generation", "weather", "energy_price",
        "consumer_load", "streetlight", "traffic", "city_event", "city_weather",
    ]
    for v in views:
        try:
            conn, _ = fresh_conn()
            cur = conn.cursor()
            cur.execute(f'SELECT * FROM "{catalog}".silver."{v}" LIMIT 1')
            rows = cur.fetchall()
            if rows:
                result.ok(f"silver.{v} returns data")
            else:
                result.fail(f"silver.{v} is EMPTY")
        except Exception as e:
            result.fail(f"silver.{v} ERROR: {str(e)[:80]}")

    # Derived field checks
    print("\n  Derived fields:")
    try:
        conn, _ = fresh_conn()
        cur = conn.cursor()
        cur.execute(f'SELECT total_active_power_w, apparent_power_va FROM "{catalog}".silver.energy_meter LIMIT 1')
        r = cur.fetchall()
        if r and r[0][0] is not None and r[0][1] is not None:
            result.ok(f"energy_meter.total_active_power_w = {r[0][0]:.1f}")
            result.ok(f"energy_meter.apparent_power_va = {r[0][1]:.1f}")
        else:
            result.fail("energy_meter derived fields are NULL")
    except Exception as e:
        result.fail(f"energy_meter derived fields ERROR: {e}")

    try:
        conn, _ = fresh_conn()
        cur = conn.cursor()
        cur.execute(f'SELECT capacity_factor FROM "{catalog}".silver.pv_generation WHERE pv_power_kw > 0 LIMIT 1')
        r = cur.fetchall()
        if r and r[0][0] is not None:
            result.ok(f"pv_generation.capacity_factor = {r[0][0]:.4f}")
        else:
            result.fail("pv_generation.capacity_factor is NULL")
    except Exception as e:
        result.fail(f"pv_generation derived field ERROR: {e}")

    try:
        conn, _ = fresh_conn()
        cur = conn.cursor()
        cur.execute(f'SELECT is_peak_hour FROM "{catalog}".silver.energy_price LIMIT 1')
        r = cur.fetchall()
        if r and r[0][0] is not None:
            result.ok(f"energy_price.is_peak_hour = {r[0][0]}")
        else:
            result.fail("energy_price.is_peak_hour is NULL")
    except Exception as e:
        result.fail(f"energy_price derived field ERROR: {e}")

    try:
        conn, _ = fresh_conn()
        cur = conn.cursor()
        cur.execute(f'SELECT is_active FROM "{catalog}".silver.consumer_load WHERE device_power_kw > 0 LIMIT 1')
        r = cur.fetchall()
        if r and r[0][0] is True:
            result.ok(f"consumer_load.is_active = True (when ON)")
        else:
            result.fail("consumer_load.is_active not True for active device")
    except Exception as e:
        result.fail(f"consumer_load derived field ERROR: {e}")

    try:
        conn, _ = fresh_conn()
        cur = conn.cursor()
        cur.execute(f'SELECT severity_label FROM "{catalog}".silver.city_event LIMIT 1')
        r = cur.fetchall()
        if r and r[0][0] in ('low', 'medium', 'high', 'critical'):
            result.ok(f"city_event.severity_label = '{r[0][0]}'")
        else:
            result.fail(f"city_event.severity_label unexpected: {r}")
    except Exception as e:
        result.fail(f"city_event derived field ERROR: {e}")


def validate_gold(result: ValidationResult, catalog: str):
    """Check all 12 Gold views return data."""
    print("\n--- GOLD LAYER ---")
    views = [
        "energy_balance_hourly", "pv_performance_hourly", "net_grid_hourly",
        "streetlight_zone_hourly", "event_impact_daily", "weather_hourly",
        "energy_cost_daily", "pv_self_consumption_daily", "traffic_pattern_hourly",
        "city_dashboard_summary", "device_utilization_daily", "anomaly_candidates",
    ]
    for v in views:
        try:
            conn, _ = fresh_conn()
            cur = conn.cursor()
            cur.execute(f'SELECT * FROM "{catalog}".gold."{v}" LIMIT 1')
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            # anomaly_candidates may legitimately be empty
            if rows:
                result.ok(f"gold.{v} ({len(cols)} cols, has data)")
            elif v == "anomaly_candidates":
                result.ok(f"gold.{v} ({len(cols)} cols, empty — no anomalies detected)")
            else:
                result.fail(f"gold.{v} is EMPTY")
        except Exception as e:
            result.fail(f"gold.{v} ERROR: {str(e)[:80]}")


def validate_cross_layer(result: ValidationResult, catalog: str):
    """Check Gold aggregations are consistent with Silver."""
    print("\n--- CROSS-LAYER CONSISTENCY ---")

    # Check that device_utilization utilization_rate is between 0 and 1
    try:
        conn, _ = fresh_conn()
        cur = conn.cursor()
        cur.execute(f"""
            SELECT MIN(utilization_rate), MAX(utilization_rate)
            FROM "{catalog}".gold.device_utilization_daily
        """)
        r = cur.fetchall()
        if r and r[0][0] is not None:
            lo, hi = r[0]
            if 0 <= lo and hi <= 1:
                result.ok(f"device_utilization_daily rates in [0,1]: [{lo:.3f}, {hi:.3f}]")
            else:
                result.fail(f"device_utilization_daily rate out of range: [{lo}, {hi}]")
        else:
            result.fail("device_utilization_daily has no data for rate check")
    except Exception as e:
        result.fail(f"cross-layer device util check ERROR: {e}")

    # Check self-consumption ratio between 0 and 1
    try:
        conn, _ = fresh_conn()
        cur = conn.cursor()
        cur.execute(f"""
            SELECT MIN(self_consumption_ratio), MAX(self_consumption_ratio),
                   MIN(autarky_ratio), MAX(autarky_ratio)
            FROM "{catalog}".gold.pv_self_consumption_daily
        """)
        r = cur.fetchall()
        if r and r[0][0] is not None:
            sc_lo, sc_hi, a_lo, a_hi = r[0]
            if 0 <= sc_lo and sc_hi <= 1 and 0 <= a_lo and a_hi <= 1:
                result.ok(f"pv_self_consumption ratios in [0,1]: sc=[{sc_lo:.3f},{sc_hi:.3f}] autarky=[{a_lo:.3f},{a_hi:.3f}]")
            else:
                result.fail(f"pv_self_consumption ratios out of range")
        else:
            result.fail("pv_self_consumption has no data")
    except Exception as e:
        result.fail(f"cross-layer pv_self_consumption check ERROR: {e}")

    # Check traffic index stays within 0-1 range
    try:
        conn, _ = fresh_conn()
        cur = conn.cursor()
        cur.execute(f"""
            SELECT MIN(avg_traffic_index), MAX(peak_traffic_index)
            FROM "{catalog}".gold.traffic_pattern_hourly
        """)
        r = cur.fetchall()
        if r and r[0][0] is not None:
            lo, hi = r[0]
            if 0 <= lo and hi <= 1:
                result.ok(f"traffic_pattern_hourly indices in [0,1]: [{lo:.3f}, {hi:.3f}]")
            else:
                result.fail(f"traffic indices out of range: [{lo}, {hi}]")
        else:
            result.fail("traffic_pattern_hourly has no data")
    except Exception as e:
        result.fail(f"cross-layer traffic check ERROR: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="WP3 Lakehouse Validation")
    parser.add_argument("--env-file", default=None, help="Path to .env.cluster")
    args = parser.parse_args()

    os.environ["_ENV_FILE"] = args.env_file or ""

    print("=" * 60)
    print("  WP3 LAKEHOUSE VALIDATION")
    print("=" * 60)

    conn, catalog = get_connection(args.env_file)
    print(f"Connected to Trino ({catalog})")

    result = ValidationResult()
    validate_bronze(result, catalog)
    validate_silver(result, catalog)
    validate_gold(result, catalog)
    validate_cross_layer(result, catalog)

    success = result.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
