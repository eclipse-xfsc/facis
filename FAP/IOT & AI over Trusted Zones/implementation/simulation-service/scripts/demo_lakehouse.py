#!/usr/bin/env python3
"""
MS2 Lakehouse Demo: Query Bronze / Silver / Gold layers via Trino.

Authenticates via Keycloak OIDC, connects to the remote Trino cluster,
discovers lakehouse tables, and prints a formatted validation report.

Usage:
    # With env file (recommended)
    cp .env.cluster.example .env.cluster   # fill in credentials
    python scripts/demo_lakehouse.py --env-file .env.cluster

    # Interactive (prompts for credentials)
    python scripts/demo_lakehouse.py

    # Discover all tables in a catalog
    python scripts/demo_lakehouse.py --discover --catalog fap-iotai-stackable

    # Query specific schema
    python scripts/demo_lakehouse.py --catalog fap-iotai-stackable --schema default

Prerequisites:
    pip install -e ".[demo]"
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
from collections import defaultdict
from datetime import datetime

import requests
import trino
from tabulate import tabulate

# Suppress InsecureRequestWarning for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("demo_lakehouse")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_KEYCLOAK_URL = "https://identity.facis.cloud/realms/facis"
DEFAULT_TRINO_HOST = "212.132.83.150"
DEFAULT_TRINO_PORT = 8443
DEFAULT_CATALOG = "fap-iotai-stackable"

LAYER_KEYWORDS = {
    "bronze": "bronze",
    "silver": "silver",
    "gold": "gold",
}

# Kafka topic → expected table name fragments (for matching)
EXPECTED_FEEDS = [
    "meter",
    "pv",
    "weather",
    "price",
    "consumer",
    "light",
    "traffic",
    "event",
]


# ---------------------------------------------------------------------------
# OIDC Authentication
# ---------------------------------------------------------------------------


def get_oidc_token(
    keycloak_url: str,
    username: str,
    password: str,
    client_secret: str,
    client_id: str = "OIDC",
) -> str:
    """Obtain an OIDC access token from Keycloak."""
    token_url = f"{keycloak_url}/protocol/openid-connect/token"

    resp = requests.post(
        token_url,
        data={
            "client_id": client_id,
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
    # Decode username from token for Trino
    payload = token.split(".")[1] + "=="
    claims = json.loads(base64.b64decode(payload))
    logger.info(f"Authenticated as: {claims.get('preferred_username', 'unknown')}")
    return token


def extract_username(token: str) -> str:
    """Extract preferred_username from JWT payload."""
    payload = token.split(".")[1] + "=="
    claims = json.loads(base64.b64decode(payload))
    return claims.get("preferred_username", "trino")


# ---------------------------------------------------------------------------
# Trino Connection
# ---------------------------------------------------------------------------


def connect_trino(
    host: str,
    port: int,
    token: str,
    catalog: str | None = None,
    schema: str | None = None,
) -> trino.dbapi.Connection:
    """Create a Trino connection with JWT authentication."""
    username = extract_username(token)

    kwargs = {
        "host": host,
        "port": port,
        "user": username,
        "auth": trino.auth.JWTAuthentication(token),
        "http_scheme": "https",
        "verify": False,
    }
    if catalog:
        kwargs["catalog"] = catalog
    if schema:
        kwargs["schema"] = schema

    conn = trino.dbapi.connect(**kwargs)
    logger.info(f"Connected to Trino at {host}:{port}")
    return conn


def execute_query(conn: trino.dbapi.Connection, sql: str) -> list[list]:
    """Execute a SQL query and return all rows."""
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def discover_catalogs(conn: trino.dbapi.Connection) -> list[str]:
    """List all available Trino catalogs."""
    rows = execute_query(conn, "SHOW CATALOGS")
    return [r[0] for r in rows]


def discover_schemas(conn: trino.dbapi.Connection, catalog: str) -> list[str]:
    """List schemas in a catalog."""
    rows = execute_query(conn, f'SHOW SCHEMAS FROM "{catalog}"')
    return [r[0] for r in rows]


def discover_tables(conn: trino.dbapi.Connection, catalog: str, schema: str) -> list[str]:
    """List tables in a catalog.schema."""
    rows = execute_query(conn, f'SHOW TABLES FROM "{catalog}"."{schema}"')
    return [r[0] for r in rows]


def describe_table(
    conn: trino.dbapi.Connection, catalog: str, schema: str, table: str
) -> list[list]:
    """Get column info for a table."""
    return execute_query(conn, f'DESCRIBE "{catalog}"."{schema}"."{table}"')


def count_rows(conn: trino.dbapi.Connection, catalog: str, schema: str, table: str) -> int:
    """Count rows in a table."""
    rows = execute_query(conn, f'SELECT COUNT(*) FROM "{catalog}"."{schema}"."{table}"')
    return rows[0][0] if rows else 0


def sample_rows(
    conn: trino.dbapi.Connection, catalog: str, schema: str, table: str, limit: int = 3
) -> tuple[list[str], list[list]]:
    """Get sample rows from a table. Returns (column_names, rows)."""
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM "{catalog}"."{schema}"."{table}" LIMIT {limit}')
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description] if cur.description else []
    return columns, rows


def get_timestamp_range(
    conn: trino.dbapi.Connection,
    catalog: str,
    schema: str,
    table: str,
    ts_column: str = "timestamp",
) -> tuple[str | None, str | None]:
    """Get min/max of a timestamp column, or None if column doesn't exist."""
    try:
        rows = execute_query(
            conn,
            f'SELECT MIN("{ts_column}"), MAX("{ts_column}") '
            f'FROM "{catalog}"."{schema}"."{table}"',
        )
        if rows and rows[0][0] is not None:
            return str(rows[0][0]), str(rows[0][1])
    except Exception:
        pass
    return None, None


# ---------------------------------------------------------------------------
# Layer Classification
# ---------------------------------------------------------------------------


def classify_layer(schema: str, table: str) -> str | None:
    """Classify a table into bronze/silver/gold based on naming conventions."""
    combined = f"{schema}.{table}".lower()
    for layer, keyword in LAYER_KEYWORDS.items():
        if keyword in combined:
            return layer
    return None


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_header(title: str) -> None:
    width = 72
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_section(title: str) -> None:
    print(f"\n--- {title} ---")


def run_discovery(conn: trino.dbapi.Connection, catalog: str) -> None:
    """Discover and print all schemas and tables in a catalog."""
    print_header(f"Discovery: {catalog}")

    schemas = discover_schemas(conn, catalog)
    logger.info(f"Found {len(schemas)} schemas in {catalog}")

    for schema in schemas:
        if schema == "information_schema":
            continue
        tables = discover_tables(conn, catalog, schema)
        if not tables:
            continue

        print_section(f"Schema: {catalog}.{schema} ({len(tables)} tables)")
        table_info = []
        for table in tables:
            layer = classify_layer(schema, table) or "-"
            try:
                cnt = count_rows(conn, catalog, schema, table)
            except Exception as e:
                cnt = f"err: {e}"
            table_info.append([table, layer, cnt])

        print(tabulate(table_info, headers=["Table", "Layer", "Rows"], tablefmt="simple"))


def run_layer_report(
    conn: trino.dbapi.Connection,
    catalog: str,
    schemas: list[str],
) -> dict[str, list[dict]]:
    """Query all tables, classify by layer, and return structured results."""
    layers: dict[str, list[dict]] = defaultdict(list)

    for schema in schemas:
        if schema == "information_schema":
            continue
        tables = discover_tables(conn, catalog, schema)
        for table in tables:
            layer = classify_layer(schema, table) or "unclassified"
            fqn = f'"{catalog}"."{schema}"."{table}"'

            info: dict = {
                "catalog": catalog,
                "schema": schema,
                "table": table,
                "fqn": fqn,
                "layer": layer,
            }

            try:
                info["row_count"] = count_rows(conn, catalog, schema, table)
            except Exception as e:
                info["row_count"] = 0
                info["error"] = str(e)

            # Try to find a timestamp column for freshness
            try:
                cols = describe_table(conn, catalog, schema, table)
                info["columns"] = [(c[0], c[1]) for c in cols]
                ts_cols = [c[0] for c in cols if "timestamp" in c[0].lower() or "time" in c[0].lower()]
                if ts_cols:
                    ts_min, ts_max = get_timestamp_range(conn, catalog, schema, table, ts_cols[0])
                    info["ts_min"] = ts_min
                    info["ts_max"] = ts_max
            except Exception:
                pass

            layers[layer].append(info)

    return dict(layers)


def print_layer_details(layer_name: str, tables: list[dict], conn: trino.dbapi.Connection) -> None:
    """Print details for a single lakehouse layer."""
    print_section(f"{layer_name.upper()} Layer ({len(tables)} tables)")

    if not tables:
        print("  (no tables found)")
        return

    summary = []
    for t in tables:
        row = [
            t["table"],
            t["schema"],
            t.get("row_count", "?"),
            t.get("ts_min", "-"),
            t.get("ts_max", "-"),
        ]
        summary.append(row)

    print(tabulate(summary, headers=["Table", "Schema", "Rows", "First Record", "Last Record"], tablefmt="simple"))

    # Show sample from first non-empty table
    for t in tables:
        if t.get("row_count", 0) > 0:
            print(f"\n  Sample from {t['table']}:")
            try:
                columns, rows = sample_rows(conn, t["catalog"], t["schema"], t["table"], limit=3)
                # Truncate wide columns for display
                display_cols = columns[:8]
                display_rows = [[str(v)[:40] for v in row[:8]] for row in rows]
                print(tabulate(display_rows, headers=display_cols, tablefmt="simple"))
            except Exception as e:
                print(f"  (error sampling: {e})")
            break


def print_summary_report(layers: dict[str, list[dict]]) -> None:
    """Print the final validation summary."""
    print_header("FACIS MS2 Lakehouse Validation Report")

    # Layer coverage
    print_section("Layer Coverage")
    checks = []
    for layer in ("bronze", "silver", "gold"):
        tables = layers.get(layer, [])
        total_rows = sum(t.get("row_count", 0) for t in tables)
        status = "OK" if tables and total_rows > 0 else "EMPTY" if tables else "MISSING"
        checks.append([layer.upper(), len(tables), total_rows, status])

    print(tabulate(checks, headers=["Layer", "Tables", "Total Rows", "Status"], tablefmt="simple"))

    # Unclassified tables
    unclassified = layers.get("unclassified", [])
    if unclassified:
        print(f"\n  + {len(unclassified)} unclassified table(s)")

    # Data freshness
    print_section("Data Freshness")
    for layer in ("bronze", "silver", "gold"):
        tables = layers.get(layer, [])
        for t in tables:
            ts_max = t.get("ts_max")
            if ts_max:
                print(f"  {layer.upper()} {t['table']}: latest = {ts_max}")

    # Feed coverage (check which simulation feeds appear in tables)
    print_section("Feed Coverage")
    all_table_names = []
    for tables in layers.values():
        all_table_names.extend(t["table"].lower() for t in tables)
    combined = " ".join(all_table_names)

    for feed in EXPECTED_FEEDS:
        found = feed in combined
        status = "FOUND" if found else "NOT FOUND"
        print(f"  {feed:20s} [{status}]")

    # Overall result
    bronze_ok = any(
        t.get("row_count", 0) > 0 for t in layers.get("bronze", [])
    )
    silver_ok = any(
        t.get("row_count", 0) > 0 for t in layers.get("silver", [])
    )
    gold_ok = any(
        t.get("row_count", 0) > 0 for t in layers.get("gold", [])
    )

    print()
    print("=" * 72)
    if bronze_ok and silver_ok and gold_ok:
        print("  RESULT: ALL LAKEHOUSE LAYERS POPULATED")
    elif bronze_ok:
        progress = []
        if silver_ok:
            progress.append("Silver")
        if gold_ok:
            progress.append("Gold")
        populated = ", ".join(["Bronze"] + progress)
        print(f"  RESULT: PARTIAL ({populated} populated)")
    else:
        print("  RESULT: NO DATA IN LAKEHOUSE")
    print("=" * 72)
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MS2 Lakehouse Demo - Query Bronze/Silver/Gold via Trino"
    )
    parser.add_argument("--env-file", default=None, help="Path to .env.cluster file with credentials")
    parser.add_argument(
        "--keycloak-url", default=None, help=f"Keycloak realm URL (default: {DEFAULT_KEYCLOAK_URL})"
    )
    parser.add_argument("--trino-host", default=None, help=f"Trino host (default: {DEFAULT_TRINO_HOST})")
    parser.add_argument(
        "--trino-port", type=int, default=None, help=f"Trino port (default: {DEFAULT_TRINO_PORT})"
    )
    parser.add_argument(
        "--catalog", default=None, help=f"Trino catalog (default: {DEFAULT_CATALOG})"
    )
    parser.add_argument("--schema", default=None, help="Specific schema to query (default: all)")
    parser.add_argument("--discover", action="store_true", help="Discovery mode: list all tables")
    parser.add_argument("--username", default=None, help="OIDC username (or set FACIS_OIDC_USERNAME)")
    parser.add_argument("--password", default=None, help="OIDC password (or set FACIS_OIDC_PASSWORD)")
    parser.add_argument(
        "--client-secret", default=None, help="OIDC client secret (or set FACIS_OIDC_CLIENT_SECRET)"
    )
    return parser.parse_args()


def load_env_file(path: str) -> None:
    """Load a .env file into os.environ."""
    try:
        from dotenv import load_dotenv

        load_dotenv(path, override=True)
        logger.info(f"Loaded credentials from {path}")
    except ImportError:
        # Fallback: simple key=value parser
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    os.environ[key.strip()] = value.strip()
        logger.info(f"Loaded credentials from {path} (fallback parser)")


def resolve_credentials(args: argparse.Namespace) -> tuple[str, str, str, str, str, int, str]:
    """Resolve credentials from args > env vars > interactive prompt."""
    if args.env_file:
        load_env_file(args.env_file)

    keycloak_url = args.keycloak_url or os.getenv("FACIS_KEYCLOAK_URL", DEFAULT_KEYCLOAK_URL)
    trino_host = args.trino_host or os.getenv("FACIS_TRINO_HOST", DEFAULT_TRINO_HOST)
    trino_port = args.trino_port or int(os.getenv("FACIS_TRINO_PORT", str(DEFAULT_TRINO_PORT)))
    catalog = args.catalog or os.getenv("FACIS_TRINO_CATALOG", DEFAULT_CATALOG)

    username = args.username or os.getenv("FACIS_OIDC_USERNAME")
    password = args.password or os.getenv("FACIS_OIDC_PASSWORD")
    client_secret = args.client_secret or os.getenv("FACIS_OIDC_CLIENT_SECRET")

    if not username:
        username = input("OIDC username: ")
    if not password:
        password = getpass.getpass("OIDC password: ")
    if not client_secret:
        client_secret = getpass.getpass("OIDC client secret: ")

    return username, password, client_secret, keycloak_url, trino_host, trino_port, catalog


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()

    print_header("FACIS MS2 Lakehouse Demo")
    print("  Keycloak OIDC -> Trino -> Bronze / Silver / Gold")

    # Step 1: Credentials
    logger.info("--- Step 1: Authentication ---")
    username, password, client_secret, keycloak_url, trino_host, trino_port, catalog = (
        resolve_credentials(args)
    )

    token = get_oidc_token(keycloak_url, username, password, client_secret)
    logger.info("OIDC token acquired")

    # Step 2: Connect to Trino
    logger.info("--- Step 2: Trino Connection ---")
    conn = connect_trino(trino_host, trino_port, token, catalog=catalog)

    # Step 3: Discovery
    logger.info("--- Step 3: Discovery ---")
    catalogs = discover_catalogs(conn)
    logger.info(f"Available catalogs: {catalogs}")

    if catalog not in catalogs:
        logger.warning(f"Catalog '{catalog}' not found. Available: {catalogs}")
        print(f"\nAvailable catalogs: {', '.join(catalogs)}")
        sys.exit(1)

    if args.schema:
        target_schemas = [args.schema]
    else:
        target_schemas = discover_schemas(conn, catalog)
        logger.info(f"Schemas in {catalog}: {target_schemas}")

    # Discovery mode: just list everything
    if args.discover:
        run_discovery(conn, catalog)
        return

    # Step 4: Query layers
    logger.info("--- Step 4: Querying Lakehouse Layers ---")
    layers = run_layer_report(conn, catalog, target_schemas)

    for layer_name in ("bronze", "silver", "gold", "unclassified"):
        if layer_name in layers:
            print_layer_details(layer_name, layers[layer_name], conn)

    # Step 5: Summary
    print_summary_report(layers)


if __name__ == "__main__":
    main()
