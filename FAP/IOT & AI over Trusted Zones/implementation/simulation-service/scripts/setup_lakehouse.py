#!/usr/bin/env python3
"""
Lakehouse Setup: Create Bronze / Silver / Gold structure in Trino.

Creates Iceberg tables and views in the fap-iotai-stackable catalog:
  - Bronze:  9 raw-ingestion tables (one per Kafka topic)
  - Silver:  9 typed views (JSON extraction + casting + data quality + derived fields)
  - Gold:   12 aggregation views (hourly/daily analytics for Superset & AI)

WP3 Completion — Silver & Gold layers are production-ready with:
  - Data quality filters (null timestamps, invalid values)
  - Derived fields (total_active_power_w, capacity_factor, total_load_kw, etc.)
  - Schema evolution via COALESCE defaults
  - 6 new Gold views: energy_cost_daily, pv_self_consumption_daily,
    traffic_pattern_hourly, city_dashboard_summary, device_utilization_daily,
    anomaly_candidates

Usage:
    python scripts/setup_lakehouse.py --env-file .env.cluster
    python scripts/setup_lakehouse.py --env-file .env.cluster --teardown

Prerequisites:
    pip install -e ".[lakehouse]"
"""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import logging
import os
import sys
import urllib3

import requests
import trino
from tabulate import tabulate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("setup_lakehouse")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_KEYCLOAK_URL = "https://identity.facis.cloud/realms/facis"
DEFAULT_TRINO_HOST = "212.132.83.150"
DEFAULT_TRINO_PORT = 8443
DEFAULT_CATALOG = "fap-iotai-stackable"
DEFAULT_S3_BUCKET = "fap-iotai-stackable"

SCHEMAS = ("bronze", "silver", "gold")

# Kafka topic → Bronze table name
TOPIC_TABLE_MAP = {
    "sim.smart_energy.meter": "energy_meter",
    "sim.smart_energy.pv": "pv_generation",
    "sim.smart_energy.weather": "weather",
    "sim.smart_energy.price": "energy_price",
    "sim.smart_energy.consumer": "consumer_load",
    "sim.smart_city.light": "streetlight",
    "sim.smart_city.traffic": "traffic",
    "sim.smart_city.event": "city_event",
    "sim.smart_city.weather": "city_weather",
}

# ---------------------------------------------------------------------------
# Auth (reused from demo_lakehouse.py)
# ---------------------------------------------------------------------------


def get_oidc_token(keycloak_url: str, username: str, password: str, client_secret: str) -> str:
    resp = requests.post(
        f"{keycloak_url}/protocol/openid-connect/token",
        data={
            "client_id": "OIDC",
            "client_secret": client_secret,
            "username": username,
            "password": password,
            "grant_type": "password",
            "scope": "openid",
        },
        verify=False,
        timeout=15,
    )
    if not resp.ok:
        logger.error(f"OIDC token request failed ({resp.status_code}): {resp.text}")
        sys.exit(1)
    token = resp.json()["access_token"]
    payload = token.split(".")[1] + "=="
    claims = json.loads(base64.b64decode(payload))
    logger.info(f"Authenticated as: {claims.get('preferred_username', 'unknown')}")
    return token


def connect_trino(host: str, port: int, token: str, catalog: str) -> trino.dbapi.Connection:
    payload = token.split(".")[1] + "=="
    username = json.loads(base64.b64decode(payload)).get("preferred_username", "trino")
    conn = trino.dbapi.connect(
        host=host,
        port=port,
        user=username,
        catalog=catalog,
        auth=trino.auth.JWTAuthentication(token),
        http_scheme="https",
        verify=False,
    )
    logger.info(f"Connected to Trino at {host}:{port}")
    return conn


def execute(conn: trino.dbapi.Connection, sql: str) -> list:
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()


def execute_ddl(conn: trino.dbapi.Connection, sql: str, description: str) -> bool:
    """Execute a DDL statement with error handling. Returns True on success."""
    try:
        execute(conn, sql)
        logger.info(f"  OK: {description}")
        return True
    except Exception as e:
        logger.error(f"  FAIL: {description} — {e}")
        return False


# ---------------------------------------------------------------------------
# Bronze Tables
# ---------------------------------------------------------------------------

BRONZE_DDL = """
CREATE TABLE IF NOT EXISTS "{catalog}".bronze.{table} (
    ingestion_timestamp  TIMESTAMP(6) WITH TIME ZONE,
    kafka_topic          VARCHAR,
    kafka_partition      INTEGER,
    kafka_offset         BIGINT,
    message_key          VARCHAR,
    raw_value            VARCHAR
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['day(ingestion_timestamp)'],
    location = '{location}'
)
"""


def create_bronze_tables(conn: trino.dbapi.Connection, catalog: str, s3_bucket: str) -> int:
    logger.info("Creating Bronze tables...")
    ok = 0
    for topic, table in TOPIC_TABLE_MAP.items():
        location = f"s3a://{s3_bucket}/warehouse/bronze.db/{table}"
        sql = BRONZE_DDL.format(catalog=catalog, table=table, location=location)
        if execute_ddl(conn, sql, f"bronze.{table} (← {topic}) → {location}"):
            ok += 1
    return ok


# ---------------------------------------------------------------------------
# Silver Views
# ---------------------------------------------------------------------------

SILVER_VIEWS: dict[str, str] = {}

# ---------------------------------------------------------------------------
# Silver: energy_meter — 3-phase meter readings with derived total power
# Data quality: reject null timestamps, invalid power values
# Derived: total_active_power_w (L1+L2+L3), apparent_power_va
# ---------------------------------------------------------------------------
SILVER_VIEWS["energy_meter"] = """
CREATE OR REPLACE VIEW "{catalog}".silver.energy_meter AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    json_extract_scalar(raw_value, '$.site_id')                      AS site_id,
    json_extract_scalar(raw_value, '$.meter_id')                     AS meter_id,
    COALESCE(json_extract_scalar(raw_value, '$.asset_id'), json_extract_scalar(raw_value, '$.meter_id')) AS asset_id,
    COALESCE(json_extract_scalar(raw_value, '$.schema_version'), '1.0') AS schema_version,
    CAST(json_extract_scalar(raw_value, '$.active_power_kw') AS DOUBLE)           AS active_power_kw,
    CAST(json_extract_scalar(raw_value, '$.active_energy_kwh_total') AS DOUBLE)   AS active_energy_kwh_total,
    CAST(json_extract_scalar(raw_value, '$.readings.active_power_l1_w') AS DOUBLE) AS active_power_l1_w,
    CAST(json_extract_scalar(raw_value, '$.readings.active_power_l2_w') AS DOUBLE) AS active_power_l2_w,
    CAST(json_extract_scalar(raw_value, '$.readings.active_power_l3_w') AS DOUBLE) AS active_power_l3_w,
    -- Derived: total active power across all 3 phases
    COALESCE(CAST(json_extract_scalar(raw_value, '$.readings.active_power_l1_w') AS DOUBLE), 0)
      + COALESCE(CAST(json_extract_scalar(raw_value, '$.readings.active_power_l2_w') AS DOUBLE), 0)
      + COALESCE(CAST(json_extract_scalar(raw_value, '$.readings.active_power_l3_w') AS DOUBLE), 0)
        AS total_active_power_w,
    CAST(json_extract_scalar(raw_value, '$.readings.voltage_l1_v') AS DOUBLE)      AS voltage_l1_v,
    CAST(json_extract_scalar(raw_value, '$.readings.voltage_l2_v') AS DOUBLE)      AS voltage_l2_v,
    CAST(json_extract_scalar(raw_value, '$.readings.voltage_l3_v') AS DOUBLE)      AS voltage_l3_v,
    CAST(json_extract_scalar(raw_value, '$.readings.current_l1_a') AS DOUBLE)      AS current_l1_a,
    CAST(json_extract_scalar(raw_value, '$.readings.current_l2_a') AS DOUBLE)      AS current_l2_a,
    CAST(json_extract_scalar(raw_value, '$.readings.current_l3_a') AS DOUBLE)      AS current_l3_a,
    CAST(json_extract_scalar(raw_value, '$.readings.power_factor') AS DOUBLE)      AS power_factor,
    CAST(json_extract_scalar(raw_value, '$.readings.frequency_hz') AS DOUBLE)      AS frequency_hz,
    CAST(json_extract_scalar(raw_value, '$.readings.total_energy_kwh') AS DOUBLE)  AS total_energy_kwh,
    -- Derived: apparent power (V * I per phase, summed)
    COALESCE(CAST(json_extract_scalar(raw_value, '$.readings.voltage_l1_v') AS DOUBLE), 0)
      * COALESCE(CAST(json_extract_scalar(raw_value, '$.readings.current_l1_a') AS DOUBLE), 0)
    + COALESCE(CAST(json_extract_scalar(raw_value, '$.readings.voltage_l2_v') AS DOUBLE), 0)
      * COALESCE(CAST(json_extract_scalar(raw_value, '$.readings.current_l2_a') AS DOUBLE), 0)
    + COALESCE(CAST(json_extract_scalar(raw_value, '$.readings.voltage_l3_v') AS DOUBLE), 0)
      * COALESCE(CAST(json_extract_scalar(raw_value, '$.readings.current_l3_a') AS DOUBLE), 0)
        AS apparent_power_va,
    message_key
FROM "{catalog}".bronze.energy_meter
WHERE json_extract_scalar(raw_value, '$.timestamp') IS NOT NULL
  AND json_extract_scalar(raw_value, '$.meter_id') IS NOT NULL
  AND CAST(json_extract_scalar(raw_value, '$.active_power_kw') AS DOUBLE) >= 0
"""

# ---------------------------------------------------------------------------
# Silver: pv_generation — PV output with capacity factor
# Derived: capacity_factor (output_kw / nominal capacity)
# ---------------------------------------------------------------------------
SILVER_VIEWS["pv_generation"] = """
CREATE OR REPLACE VIEW "{catalog}".silver.pv_generation AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    json_extract_scalar(raw_value, '$.site_id')                      AS site_id,
    json_extract_scalar(raw_value, '$.pv_system_id')                 AS pv_system_id,
    COALESCE(json_extract_scalar(raw_value, '$.asset_id'), json_extract_scalar(raw_value, '$.pv_system_id')) AS asset_id,
    CAST(json_extract_scalar(raw_value, '$.pv_power_kw') AS DOUBLE)              AS pv_power_kw,
    CAST(json_extract_scalar(raw_value, '$.readings.power_output_kw') AS DOUBLE) AS power_output_kw,
    CAST(json_extract_scalar(raw_value, '$.readings.daily_energy_kwh') AS DOUBLE) AS daily_energy_kwh,
    CAST(json_extract_scalar(raw_value, '$.readings.irradiance_w_m2') AS DOUBLE)  AS irradiance_w_m2,
    CAST(json_extract_scalar(raw_value, '$.readings.module_temperature_c') AS DOUBLE) AS module_temperature_c,
    CAST(json_extract_scalar(raw_value, '$.readings.efficiency_percent') AS DOUBLE) AS efficiency_percent,
    -- Derived: capacity factor = output / nominal capacity (10 kWp default)
    CASE
        WHEN COALESCE(CAST(json_extract_scalar(raw_value, '$.nominal_capacity_kw') AS DOUBLE), 10.0) > 0
        THEN COALESCE(CAST(json_extract_scalar(raw_value, '$.pv_power_kw') AS DOUBLE), 0)
           / COALESCE(CAST(json_extract_scalar(raw_value, '$.nominal_capacity_kw') AS DOUBLE), 10.0)
        ELSE 0
    END AS capacity_factor,
    message_key
FROM "{catalog}".bronze.pv_generation
WHERE json_extract_scalar(raw_value, '$.timestamp') IS NOT NULL
  AND json_extract_scalar(raw_value, '$.pv_system_id') IS NOT NULL
  AND COALESCE(CAST(json_extract_scalar(raw_value, '$.pv_power_kw') AS DOUBLE), 0) >= 0
"""

# ---------------------------------------------------------------------------
# Silver: weather — atmospheric conditions
# ---------------------------------------------------------------------------
SILVER_VIEWS["weather"] = """
CREATE OR REPLACE VIEW "{catalog}".silver.weather AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    json_extract_scalar(raw_value, '$.site_id')                      AS site_id,
    CAST(json_extract_scalar(raw_value, '$.temperature_c') AS DOUBLE)            AS temperature_c,
    CAST(json_extract_scalar(raw_value, '$.solar_irradiance_w_m2') AS DOUBLE)    AS solar_irradiance_w_m2,
    CAST(json_extract_scalar(raw_value, '$.location.latitude') AS DOUBLE)        AS latitude,
    CAST(json_extract_scalar(raw_value, '$.location.longitude') AS DOUBLE)       AS longitude,
    CAST(json_extract_scalar(raw_value, '$.conditions.humidity_percent') AS DOUBLE) AS humidity_percent,
    CAST(json_extract_scalar(raw_value, '$.conditions.wind_speed_ms') AS DOUBLE)   AS wind_speed_ms,
    CAST(json_extract_scalar(raw_value, '$.conditions.wind_direction_deg') AS DOUBLE) AS wind_direction_deg,
    CAST(json_extract_scalar(raw_value, '$.conditions.cloud_cover_percent') AS DOUBLE) AS cloud_cover_percent,
    CAST(json_extract_scalar(raw_value, '$.conditions.ghi_w_m2') AS DOUBLE)      AS ghi_w_m2,
    CAST(json_extract_scalar(raw_value, '$.conditions.dni_w_m2') AS DOUBLE)      AS dni_w_m2,
    CAST(json_extract_scalar(raw_value, '$.conditions.dhi_w_m2') AS DOUBLE)      AS dhi_w_m2,
    message_key
FROM "{catalog}".bronze.weather
WHERE json_extract_scalar(raw_value, '$.timestamp') IS NOT NULL
  AND CAST(json_extract_scalar(raw_value, '$.temperature_c') AS DOUBLE) BETWEEN -50 AND 60
"""

# ---------------------------------------------------------------------------
# Silver: energy_price — spot pricing with peak classification
# Derived: is_peak_hour (boolean based on tariff type)
# ---------------------------------------------------------------------------
SILVER_VIEWS["energy_price"] = """
CREATE OR REPLACE VIEW "{catalog}".silver.energy_price AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    CAST(json_extract_scalar(raw_value, '$.price_eur_per_kwh') AS DOUBLE) AS price_eur_per_kwh,
    COALESCE(json_extract_scalar(raw_value, '$.tariff_type'), 'unknown')  AS tariff_type,
    COALESCE(json_extract_scalar(raw_value, '$.schema_version'), '1.0')   AS schema_version,
    -- Derived: peak classification
    CASE
        WHEN json_extract_scalar(raw_value, '$.tariff_type') IN ('morning_peak', 'evening_peak') THEN true
        ELSE false
    END AS is_peak_hour,
    message_key
FROM "{catalog}".bronze.energy_price
WHERE json_extract_scalar(raw_value, '$.timestamp') IS NOT NULL
  AND CAST(json_extract_scalar(raw_value, '$.price_eur_per_kwh') AS DOUBLE) >= 0
"""

# ---------------------------------------------------------------------------
# Silver: consumer_load — device state with ON/OFF boolean
# Derived: is_active (boolean from device_state)
# ---------------------------------------------------------------------------
SILVER_VIEWS["consumer_load"] = """
CREATE OR REPLACE VIEW "{catalog}".silver.consumer_load AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    json_extract_scalar(raw_value, '$.site_id')                      AS site_id,
    json_extract_scalar(raw_value, '$.device_id')                    AS device_id,
    COALESCE(json_extract_scalar(raw_value, '$.asset_id'), json_extract_scalar(raw_value, '$.device_id')) AS asset_id,
    json_extract_scalar(raw_value, '$.device_type')                  AS device_type,
    json_extract_scalar(raw_value, '$.device_state')                 AS device_state,
    CAST(json_extract_scalar(raw_value, '$.device_power_kw') AS DOUBLE) AS device_power_kw,
    -- Derived: boolean active flag
    CASE WHEN UPPER(json_extract_scalar(raw_value, '$.device_state')) = 'ON' THEN true ELSE false END AS is_active,
    message_key
FROM "{catalog}".bronze.consumer_load
WHERE json_extract_scalar(raw_value, '$.timestamp') IS NOT NULL
  AND json_extract_scalar(raw_value, '$.device_id') IS NOT NULL
  AND COALESCE(CAST(json_extract_scalar(raw_value, '$.device_power_kw') AS DOUBLE), 0) >= 0
"""

# ---------------------------------------------------------------------------
# Silver: streetlight — per-light readings with energy estimate
# Derived: energy_wh_estimate (power * 1 min interval / 60)
# ---------------------------------------------------------------------------
SILVER_VIEWS["streetlight"] = """
CREATE OR REPLACE VIEW "{catalog}".silver.streetlight AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    json_extract_scalar(raw_value, '$.city_id')                      AS city_id,
    json_extract_scalar(raw_value, '$.zone_id')                      AS zone_id,
    json_extract_scalar(raw_value, '$.light_id')                     AS light_id,
    COALESCE(json_extract_scalar(raw_value, '$.asset_id'), json_extract_scalar(raw_value, '$.light_id')) AS asset_id,
    CAST(json_extract_scalar(raw_value, '$.dimming_level_pct') AS DOUBLE) AS dimming_level_pct,
    CAST(json_extract_scalar(raw_value, '$.power_w') AS DOUBLE)           AS power_w,
    -- Derived: estimated energy for 1-min interval (Wh)
    COALESCE(CAST(json_extract_scalar(raw_value, '$.power_w') AS DOUBLE), 0) / 60.0 AS energy_wh_estimate,
    message_key
FROM "{catalog}".bronze.streetlight
WHERE json_extract_scalar(raw_value, '$.timestamp') IS NOT NULL
  AND json_extract_scalar(raw_value, '$.zone_id') IS NOT NULL
"""

# ---------------------------------------------------------------------------
# Silver: traffic — zone traffic index with congestion flag
# Derived: is_congested (traffic_index > 0.7)
# ---------------------------------------------------------------------------
SILVER_VIEWS["traffic"] = """
CREATE OR REPLACE VIEW "{catalog}".silver.traffic AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    json_extract_scalar(raw_value, '$.city_id')                      AS city_id,
    json_extract_scalar(raw_value, '$.zone_id')                      AS zone_id,
    CAST(json_extract_scalar(raw_value, '$.traffic_index') AS DOUBLE) AS traffic_index,
    -- Derived: congestion flag
    CASE WHEN CAST(json_extract_scalar(raw_value, '$.traffic_index') AS DOUBLE) > 0.7 THEN true ELSE false END AS is_congested,
    message_key
FROM "{catalog}".bronze.traffic
WHERE json_extract_scalar(raw_value, '$.timestamp') IS NOT NULL
  AND json_extract_scalar(raw_value, '$.zone_id') IS NOT NULL
  AND CAST(json_extract_scalar(raw_value, '$.traffic_index') AS DOUBLE) BETWEEN 0 AND 1
"""

# ---------------------------------------------------------------------------
# Silver: city_event — zone events with severity label
# Derived: severity_label (low/medium/high/critical)
# ---------------------------------------------------------------------------
SILVER_VIEWS["city_event"] = """
CREATE OR REPLACE VIEW "{catalog}".silver.city_event AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    json_extract_scalar(raw_value, '$.city_id')                      AS city_id,
    json_extract_scalar(raw_value, '$.zone_id')                      AS zone_id,
    COALESCE(json_extract_scalar(raw_value, '$.event_type'), 'unknown') AS event_type,
    CAST(json_extract_scalar(raw_value, '$.severity') AS INTEGER)    AS severity,
    COALESCE(CAST(json_extract_scalar(raw_value, '$.active') AS BOOLEAN), false) AS active,
    -- Derived: severity label
    CASE
        WHEN CAST(json_extract_scalar(raw_value, '$.severity') AS INTEGER) >= 4 THEN 'critical'
        WHEN CAST(json_extract_scalar(raw_value, '$.severity') AS INTEGER) >= 3 THEN 'high'
        WHEN CAST(json_extract_scalar(raw_value, '$.severity') AS INTEGER) >= 2 THEN 'medium'
        ELSE 'low'
    END AS severity_label,
    message_key
FROM "{catalog}".bronze.city_event
WHERE json_extract_scalar(raw_value, '$.timestamp') IS NOT NULL
  AND json_extract_scalar(raw_value, '$.zone_id') IS NOT NULL
"""

# ---------------------------------------------------------------------------
# Silver: city_weather — visibility conditions with alert flag
# Derived: is_fog_alert (fog_index > 0.6)
# ---------------------------------------------------------------------------
SILVER_VIEWS["city_weather"] = """
CREATE OR REPLACE VIEW "{catalog}".silver.city_weather AS
SELECT
    ingestion_timestamp,
    from_iso8601_timestamp(json_extract_scalar(raw_value, '$.timestamp')) AS event_timestamp,
    json_extract_scalar(raw_value, '$.city_id')                      AS city_id,
    CAST(json_extract_scalar(raw_value, '$.fog_index') AS DOUBLE)    AS fog_index,
    COALESCE(json_extract_scalar(raw_value, '$.visibility'), 'unknown') AS visibility,
    json_extract_scalar(raw_value, '$.sunrise_time')                 AS sunrise_time,
    json_extract_scalar(raw_value, '$.sunset_time')                  AS sunset_time,
    -- Derived: fog alert flag
    CASE WHEN CAST(json_extract_scalar(raw_value, '$.fog_index') AS DOUBLE) > 0.6 THEN true ELSE false END AS is_fog_alert,
    message_key
FROM "{catalog}".bronze.city_weather
WHERE json_extract_scalar(raw_value, '$.timestamp') IS NOT NULL
"""


def create_silver_views(conn: trino.dbapi.Connection, catalog: str) -> int:
    logger.info("Creating Silver views...")
    ok = 0
    for name, sql_template in SILVER_VIEWS.items():
        sql = sql_template.format(catalog=catalog)
        if execute_ddl(conn, sql, f"silver.{name}"):
            ok += 1
    return ok


# ---------------------------------------------------------------------------
# Gold Views
# ---------------------------------------------------------------------------

GOLD_VIEWS: dict[str, str] = {}

GOLD_VIEWS["energy_balance_hourly"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.energy_balance_hourly AS
SELECT
    date_trunc('hour', m.event_timestamp)           AS hour,
    m.meter_id,
    AVG(m.active_power_kw)                          AS avg_consumption_kw,
    MAX(m.active_power_kw)                          AS peak_consumption_kw,
    MAX(m.active_energy_kwh_total)
      - MIN(m.active_energy_kwh_total)              AS energy_consumed_kwh,
    COUNT(*)                                        AS reading_count
FROM "{catalog}".silver.energy_meter m
GROUP BY date_trunc('hour', m.event_timestamp), m.meter_id
"""

GOLD_VIEWS["pv_performance_hourly"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.pv_performance_hourly AS
SELECT
    date_trunc('hour', p.event_timestamp)           AS hour,
    p.pv_system_id,
    AVG(p.pv_power_kw)                              AS avg_power_kw,
    MAX(p.pv_power_kw)                              AS peak_power_kw,
    AVG(p.irradiance_w_m2)                          AS avg_irradiance,
    AVG(p.efficiency_percent)                       AS avg_efficiency,
    MAX(p.daily_energy_kwh)                         AS daily_energy_kwh
FROM "{catalog}".silver.pv_generation p
GROUP BY date_trunc('hour', p.event_timestamp), p.pv_system_id
"""

GOLD_VIEWS["net_grid_hourly"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.net_grid_hourly AS
SELECT
    m.hour,
    m.avg_consumption_kw,
    COALESCE(p.avg_power_kw, 0)                                     AS avg_generation_kw,
    m.avg_consumption_kw - COALESCE(p.avg_power_kw, 0)              AS net_grid_kw,
    pr.avg_price_eur_per_kwh,
    (m.avg_consumption_kw - COALESCE(p.avg_power_kw, 0))
        * COALESCE(pr.avg_price_eur_per_kwh, 0)                     AS estimated_hourly_cost_eur
FROM "{catalog}".gold.energy_balance_hourly m
LEFT JOIN (
    SELECT date_trunc('hour', event_timestamp) AS hour,
           AVG(pv_power_kw) AS avg_power_kw
    FROM "{catalog}".silver.pv_generation
    GROUP BY date_trunc('hour', event_timestamp)
) p ON m.hour = p.hour
LEFT JOIN (
    SELECT date_trunc('hour', event_timestamp) AS hour,
           AVG(price_eur_per_kwh) AS avg_price_eur_per_kwh
    FROM "{catalog}".silver.energy_price
    GROUP BY date_trunc('hour', event_timestamp)
) pr ON m.hour = pr.hour
"""

GOLD_VIEWS["streetlight_zone_hourly"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.streetlight_zone_hourly AS
SELECT
    date_trunc('hour', event_timestamp)             AS hour,
    zone_id,
    AVG(dimming_level_pct)                          AS avg_dimming_pct,
    SUM(power_w)                                    AS total_power_w,
    COUNT(DISTINCT light_id)                        AS light_count
FROM "{catalog}".silver.streetlight
GROUP BY date_trunc('hour', event_timestamp), zone_id
"""

GOLD_VIEWS["event_impact_daily"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.event_impact_daily AS
SELECT
    CAST(event_timestamp AS DATE)                   AS event_date,
    zone_id,
    event_type,
    COUNT(*)                                        AS event_count,
    AVG(severity)                                   AS avg_severity,
    SUM(CASE WHEN active THEN 1 ELSE 0 END)        AS active_count
FROM "{catalog}".silver.city_event
GROUP BY CAST(event_timestamp AS DATE), zone_id, event_type
"""

GOLD_VIEWS["weather_hourly"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.weather_hourly AS
SELECT
    date_trunc('hour', event_timestamp)             AS hour,
    AVG(temperature_c)                              AS avg_temperature_c,
    AVG(solar_irradiance_w_m2)                      AS avg_irradiance_w_m2,
    AVG(humidity_percent)                           AS avg_humidity_pct,
    AVG(wind_speed_ms)                              AS avg_wind_speed_ms,
    AVG(cloud_cover_percent)                        AS avg_cloud_cover_pct
FROM "{catalog}".silver.weather
GROUP BY date_trunc('hour', event_timestamp)
"""

# ---------------------------------------------------------------------------
# NEW Gold Views (WP3 completion — W9-02)
# ---------------------------------------------------------------------------

GOLD_VIEWS["energy_cost_daily"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.energy_cost_daily AS
SELECT
    CAST(m.event_timestamp AS DATE)                         AS cost_date,
    SUM(m.active_power_kw)                                  AS total_consumption_kw,
    SUM(m.active_power_kw * COALESCE(pr.price_eur_per_kwh, 0)) / NULLIF(COUNT(*), 0)
                                                             AS avg_cost_per_reading_eur,
    SUM(CASE WHEN COALESCE(pr.is_peak_hour, false)
             THEN m.active_power_kw ELSE 0 END)             AS peak_consumption_kw,
    SUM(CASE WHEN NOT COALESCE(pr.is_peak_hour, false)
             THEN m.active_power_kw ELSE 0 END)             AS offpeak_consumption_kw,
    AVG(CASE WHEN COALESCE(pr.is_peak_hour, false)
             THEN pr.price_eur_per_kwh END)                  AS avg_peak_price_eur,
    AVG(CASE WHEN NOT COALESCE(pr.is_peak_hour, false)
             THEN pr.price_eur_per_kwh END)                  AS avg_offpeak_price_eur,
    COUNT(*)                                                 AS reading_count
FROM "{catalog}".silver.energy_meter m
LEFT JOIN "{catalog}".silver.energy_price pr
    ON date_trunc('hour', m.event_timestamp) = date_trunc('hour', pr.event_timestamp)
GROUP BY CAST(m.event_timestamp AS DATE)
"""

GOLD_VIEWS["pv_self_consumption_daily"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.pv_self_consumption_daily AS
SELECT
    CAST(sub.hour AS DATE)                                       AS sc_date,
    SUM(sub.hourly_consumption_kw)                               AS total_consumption_kw,
    SUM(sub.hourly_generation_kw)                                AS total_generation_kw,
    SUM(LEAST(sub.hourly_consumption_kw, sub.hourly_generation_kw)) AS self_consumed_kw,
    SUM(GREATEST(sub.hourly_generation_kw - sub.hourly_consumption_kw, 0)) AS exported_kw,
    SUM(GREATEST(sub.hourly_consumption_kw - sub.hourly_generation_kw, 0)) AS imported_kw,
    CASE WHEN SUM(sub.hourly_generation_kw) > 0
         THEN SUM(LEAST(sub.hourly_consumption_kw, sub.hourly_generation_kw))
            / SUM(sub.hourly_generation_kw)
         ELSE 0 END                                               AS self_consumption_ratio,
    CASE WHEN SUM(sub.hourly_consumption_kw) > 0
         THEN 1.0 - SUM(GREATEST(sub.hourly_consumption_kw - sub.hourly_generation_kw, 0))
                   / SUM(sub.hourly_consumption_kw)
         ELSE 0 END                                               AS autarky_ratio
FROM (
    SELECT
        m_agg.hour,
        m_agg.hourly_consumption_kw,
        COALESCE(p_agg.hourly_generation_kw, 0)                  AS hourly_generation_kw
    FROM (
        SELECT date_trunc('hour', event_timestamp) AS hour,
               AVG(active_power_kw) AS hourly_consumption_kw
        FROM "{catalog}".silver.energy_meter
        GROUP BY date_trunc('hour', event_timestamp)
    ) m_agg
    LEFT JOIN (
        SELECT date_trunc('hour', event_timestamp) AS hour,
               AVG(pv_power_kw) AS hourly_generation_kw
        FROM "{catalog}".silver.pv_generation
        GROUP BY date_trunc('hour', event_timestamp)
    ) p_agg ON m_agg.hour = p_agg.hour
) sub
GROUP BY CAST(sub.hour AS DATE)
"""

GOLD_VIEWS["traffic_pattern_hourly"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.traffic_pattern_hourly AS
SELECT
    date_trunc('hour', event_timestamp)                     AS hour,
    zone_id,
    AVG(traffic_index)                                      AS avg_traffic_index,
    MAX(traffic_index)                                      AS peak_traffic_index,
    SUM(CASE WHEN is_congested THEN 1 ELSE 0 END)          AS congested_readings,
    COUNT(*)                                                AS reading_count,
    -- Rush-hour classification (Berlin local: 7-9 morning, 16-18 evening)
    CASE
        WHEN HOUR(date_trunc('hour', event_timestamp)) BETWEEN 7 AND 8 THEN 'morning_rush'
        WHEN HOUR(date_trunc('hour', event_timestamp)) BETWEEN 16 AND 17 THEN 'evening_rush'
        WHEN HOUR(date_trunc('hour', event_timestamp)) BETWEEN 22 AND 5 THEN 'night'
        ELSE 'normal'
    END AS period_type
FROM "{catalog}".silver.traffic
GROUP BY date_trunc('hour', event_timestamp), zone_id
"""

GOLD_VIEWS["city_dashboard_summary"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.city_dashboard_summary AS
SELECT
    CAST(e.event_timestamp AS DATE)                         AS summary_date,
    e.zone_id,
    COUNT(DISTINCT e.event_type)                            AS event_types,
    COUNT(*)                                                AS total_events,
    SUM(CASE WHEN e.active THEN 1 ELSE 0 END)              AS active_events,
    AVG(e.severity)                                         AS avg_severity,
    COALESCE(t.avg_traffic_index, 0)                        AS avg_traffic_index,
    COALESCE(t.congested_hours, 0)                          AS congested_hours,
    COALESCE(sl.avg_dimming_pct, 0)                         AS avg_dimming_pct,
    COALESCE(sl.total_energy_wh, 0)                         AS streetlight_energy_wh,
    COALESCE(sl.light_count, 0)                             AS active_lights
FROM "{catalog}".silver.city_event e
LEFT JOIN (
    SELECT CAST(event_timestamp AS DATE) AS d, zone_id,
           AVG(traffic_index) AS avg_traffic_index,
           SUM(CASE WHEN is_congested THEN 1 ELSE 0 END) AS congested_hours
    FROM "{catalog}".silver.traffic
    GROUP BY CAST(event_timestamp AS DATE), zone_id
) t ON CAST(e.event_timestamp AS DATE) = t.d AND e.zone_id = t.zone_id
LEFT JOIN (
    SELECT CAST(event_timestamp AS DATE) AS d, zone_id,
           AVG(dimming_level_pct) AS avg_dimming_pct,
           SUM(energy_wh_estimate) AS total_energy_wh,
           COUNT(DISTINCT light_id) AS light_count
    FROM "{catalog}".silver.streetlight
    GROUP BY CAST(event_timestamp AS DATE), zone_id
) sl ON CAST(e.event_timestamp AS DATE) = sl.d AND e.zone_id = sl.zone_id
GROUP BY CAST(e.event_timestamp AS DATE), e.zone_id,
         t.avg_traffic_index, t.congested_hours,
         sl.avg_dimming_pct, sl.total_energy_wh, sl.light_count
"""

GOLD_VIEWS["device_utilization_daily"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.device_utilization_daily AS
SELECT
    CAST(event_timestamp AS DATE)                           AS util_date,
    device_id,
    device_type,
    COUNT(*)                                                AS total_readings,
    SUM(CASE WHEN is_active THEN 1 ELSE 0 END)             AS active_readings,
    CAST(SUM(CASE WHEN is_active THEN 1 ELSE 0 END) AS DOUBLE)
      / NULLIF(COUNT(*), 0)                                 AS utilization_rate,
    AVG(CASE WHEN is_active THEN device_power_kw END)       AS avg_active_power_kw,
    MAX(device_power_kw)                                    AS peak_power_kw,
    SUM(device_power_kw) / 60.0                             AS estimated_energy_kwh
FROM "{catalog}".silver.consumer_load
GROUP BY CAST(event_timestamp AS DATE), device_id, device_type
"""

GOLD_VIEWS["anomaly_candidates"] = """
CREATE OR REPLACE VIEW "{catalog}".gold.anomaly_candidates AS
SELECT * FROM (
    -- Energy anomalies: consumption > 2 stddev from hourly mean
    SELECT
        'energy_spike' AS anomaly_type,
        m.event_timestamp,
        m.meter_id AS entity_id,
        m.active_power_kw AS observed_value,
        stats.avg_kw AS expected_value,
        stats.stddev_kw AS stddev,
        (m.active_power_kw - stats.avg_kw) / NULLIF(stats.stddev_kw, 0) AS z_score,
        'Energy consumption spike detected' AS description
    FROM "{catalog}".silver.energy_meter m
    CROSS JOIN (
        SELECT AVG(active_power_kw) AS avg_kw,
               STDDEV(active_power_kw) AS stddev_kw
        FROM "{catalog}".silver.energy_meter
    ) stats
    WHERE m.active_power_kw > stats.avg_kw + 2 * stats.stddev_kw

    UNION ALL

    -- PV anomalies: generation during daytime much below expected
    SELECT
        'pv_underperformance' AS anomaly_type,
        p.event_timestamp,
        p.pv_system_id AS entity_id,
        p.pv_power_kw AS observed_value,
        stats.avg_kw AS expected_value,
        stats.stddev_kw AS stddev,
        (stats.avg_kw - p.pv_power_kw) / NULLIF(stats.stddev_kw, 0) AS z_score,
        'PV generation below expected during daylight' AS description
    FROM "{catalog}".silver.pv_generation p
    CROSS JOIN (
        SELECT AVG(pv_power_kw) AS avg_kw,
               STDDEV(pv_power_kw) AS stddev_kw
        FROM "{catalog}".silver.pv_generation
        WHERE pv_power_kw > 0
    ) stats
    WHERE p.irradiance_w_m2 > 100
      AND p.pv_power_kw < stats.avg_kw - 2 * stats.stddev_kw

    UNION ALL

    -- Voltage anomalies: voltage outside ±10% of 230V nominal
    SELECT
        'voltage_deviation' AS anomaly_type,
        m.event_timestamp,
        m.meter_id AS entity_id,
        m.voltage_l1_v AS observed_value,
        230.0 AS expected_value,
        CAST(0 AS DOUBLE) AS stddev,
        ABS(m.voltage_l1_v - 230.0) / 230.0 * 100 AS z_score,
        'Voltage deviation beyond 10%% of nominal' AS description
    FROM "{catalog}".silver.energy_meter m
    WHERE m.voltage_l1_v < 207 OR m.voltage_l1_v > 253
) anomalies
"""


def create_gold_views(conn: trino.dbapi.Connection, catalog: str) -> int:
    logger.info("Creating Gold views...")
    ok = 0
    for name, sql_template in GOLD_VIEWS.items():
        sql = sql_template.format(catalog=catalog)
        if execute_ddl(conn, sql, f"gold.{name}"):
            ok += 1
    return ok


# ---------------------------------------------------------------------------
# Schema creation with fallback
# ---------------------------------------------------------------------------


def create_schemas(conn: trino.dbapi.Connection, catalog: str, s3_bucket: str) -> bool:
    """Create bronze/silver/gold schemas with explicit S3 locations.

    Drops and recreates schemas if they already exist (to fix file:/ locations).
    Returns True if all schemas are created successfully.
    """
    logger.info("Creating schemas with S3 locations...")
    base = f"s3a://{s3_bucket}/warehouse"

    for schema in SCHEMAS:
        location = f"{base}/{schema}.db"

        # Drop existing schema (safe — fails if non-empty, which is fine)
        execute_ddl(
            conn,
            f'DROP SCHEMA IF EXISTS "{catalog}".{schema}',
            f"drop schema {schema} (cleanup)",
        )

        sql = f"CREATE SCHEMA \"{catalog}\".{schema} WITH (location = '{location}')"
        if not execute_ddl(conn, sql, f"schema {schema} → {location}"):
            logger.error(
                f"Schema {schema} creation failed. If tables exist, run with --teardown first."
            )
            return False
    return True


# ---------------------------------------------------------------------------
# Teardown
# ---------------------------------------------------------------------------


def teardown(conn: trino.dbapi.Connection, catalog: str) -> None:
    """Drop all views, tables, and schemas (Gold → Silver → Bronze order)."""
    logger.info("Tearing down lakehouse structure...")

    # Gold views
    for name in GOLD_VIEWS:
        execute_ddl(conn, f'DROP VIEW IF EXISTS "{catalog}".gold.{name}', f"drop gold.{name}")

    # Silver views
    for name in SILVER_VIEWS:
        execute_ddl(conn, f'DROP VIEW IF EXISTS "{catalog}".silver.{name}', f"drop silver.{name}")

    # Bronze tables
    for table in TOPIC_TABLE_MAP.values():
        execute_ddl(
            conn, f'DROP TABLE IF EXISTS "{catalog}".bronze.{table}', f"drop bronze.{table}"
        )

    # Schemas (reverse order)
    for schema in reversed(SCHEMAS):
        execute_ddl(conn, f'DROP SCHEMA IF EXISTS "{catalog}".{schema}', f"drop schema {schema}")

    logger.info("Teardown complete.")


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def verify(conn: trino.dbapi.Connection, catalog: str) -> None:
    """Verify all tables/views exist and print summary."""
    print()
    print("=" * 72)
    print("  Lakehouse Structure Verification")
    print("=" * 72)

    for schema in SCHEMAS:
        try:
            rows = execute(conn, f'SHOW TABLES FROM "{catalog}".{schema}')
            tables = [r[0] for r in rows]
        except Exception as e:
            print(f"\n  {schema.upper()}: ERROR — {e}")
            continue

        print(f"\n  {schema.upper()} ({len(tables)} objects)")
        for table in tables:
            try:
                cols = execute(conn, f'DESCRIBE "{catalog}".{schema}."{table}"')
                col_names = [c[0] for c in cols]
                print(f"    {table:30s} {len(cols)} columns  ({', '.join(col_names[:4])}...)")
            except Exception as e:
                print(f"    {table:30s} ERROR: {e}")

    print()
    print("=" * 72)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def load_env_file(path: str) -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(path, override=True)
    except ImportError:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    os.environ[key.strip()] = value.strip()
    logger.info(f"Loaded credentials from {path}")


def resolve_credentials(args: argparse.Namespace) -> tuple[str, str, str, str, str, int, str, str]:
    if args.env_file:
        load_env_file(args.env_file)

    keycloak_url = os.getenv("FACIS_KEYCLOAK_URL", DEFAULT_KEYCLOAK_URL)
    trino_host = os.getenv("FACIS_TRINO_HOST", DEFAULT_TRINO_HOST)
    trino_port = int(os.getenv("FACIS_TRINO_PORT", str(DEFAULT_TRINO_PORT)))
    catalog = args.catalog or os.getenv("FACIS_TRINO_CATALOG", DEFAULT_CATALOG)
    s3_bucket = args.s3_bucket or os.getenv("FACIS_S3_BUCKET", DEFAULT_S3_BUCKET)

    username = os.getenv("FACIS_OIDC_USERNAME") or input("OIDC username: ")
    password = os.getenv("FACIS_OIDC_PASSWORD") or getpass.getpass("OIDC password: ")
    client_secret = os.getenv("FACIS_OIDC_CLIENT_SECRET") or getpass.getpass("OIDC client secret: ")

    return username, password, client_secret, keycloak_url, trino_host, trino_port, catalog, s3_bucket


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MS2 Lakehouse Setup — Trino DDL")
    parser.add_argument("--env-file", default=None, help="Path to .env.cluster credentials file")
    parser.add_argument("--catalog", default=None, help=f"Trino catalog (default: {DEFAULT_CATALOG})")
    parser.add_argument("--s3-bucket", default=None, help=f"S3 bucket for Iceberg data (default: {DEFAULT_S3_BUCKET})")
    parser.add_argument("--teardown", action="store_true", help="Drop all tables/views/schemas")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print()
    print("=" * 72)
    print("  FACIS MS2 Lakehouse Setup")
    print("  Bronze tables + Silver views + Gold views")
    print("=" * 72)

    username, password, client_secret, keycloak_url, trino_host, trino_port, catalog, s3_bucket = (
        resolve_credentials(args)
    )

    token = get_oidc_token(keycloak_url, username, password, client_secret)
    conn = connect_trino(trino_host, trino_port, token, catalog)

    if args.teardown:
        teardown(conn, catalog)
        return

    logger.info(f"S3 bucket: {s3_bucket} (warehouse base: s3a://{s3_bucket}/warehouse)")

    # Step 1: Create schemas with S3 locations
    logger.info("--- Step 1: Schemas ---")
    schemas_ok = create_schemas(conn, catalog, s3_bucket)
    if not schemas_ok:
        logger.error("Cannot create schemas. Check Trino/Iceberg catalog configuration.")
        sys.exit(1)

    # Step 2: Bronze tables
    logger.info("--- Step 2: Bronze Tables ---")
    bronze_count = create_bronze_tables(conn, catalog, s3_bucket)

    # Step 3: Silver views
    logger.info("--- Step 3: Silver Views ---")
    silver_count = create_silver_views(conn, catalog)

    # Step 4: Gold views
    logger.info("--- Step 4: Gold Views ---")
    gold_count = create_gold_views(conn, catalog)

    # Step 5: Verify
    logger.info("--- Step 5: Verification ---")
    verify(conn, catalog)

    # Summary
    total = bronze_count + silver_count + gold_count
    expected = len(TOPIC_TABLE_MAP) + len(SILVER_VIEWS) + len(GOLD_VIEWS)
    print(f"\n  Created {total}/{expected} objects "
          f"(Bronze: {bronze_count}/{len(TOPIC_TABLE_MAP)}, "
          f"Silver: {silver_count}/{len(SILVER_VIEWS)}, "
          f"Gold: {gold_count}/{len(GOLD_VIEWS)})")

    if total == expected:
        print("  STATUS: ALL OBJECTS CREATED SUCCESSFULLY")
    else:
        print("  STATUS: SOME OBJECTS FAILED (check logs above)")
    print()


if __name__ == "__main__":
    main()
