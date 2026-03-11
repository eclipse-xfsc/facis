#!/usr/bin/env python3
"""
MS2 NiFi Setup: Configure Kafka → Bronze ingestion pipeline.

Creates NiFi 2.6 processor groups and flows that consume from 9 Kafka topics
and INSERT into the corresponding Trino Bronze tables via Trino REST API.

Architecture (all internal to Stackable K8s cluster):
    ConsumeKafka (Kafka3ConnectionService + Stackable TLS)
        → ReplaceText (escape SQL quotes)
        → ReplaceText (build INSERT SQL)
        → InvokeHTTP (POST to Trino REST /v1/statement, Basic auth)

Usage:
    python scripts/setup_nifi.py --env-file .env.cluster
    python scripts/setup_nifi.py --env-file .env.cluster --dry-run
    python scripts/setup_nifi.py --env-file .env.cluster --teardown

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
import time
import urllib3

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("setup_nifi")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_KEYCLOAK_URL = "https://identity.facis.cloud/realms/facis"
DEFAULT_NIFI_URL = "https://212.132.83.82:8443"
DEFAULT_CATALOG = "fap-iotai-stackable"

# Internal cluster endpoints (NiFi → Kafka/Trino within Stackable K8s)
KAFKA_BOOTSTRAP_INTERNAL = "kafka-broker-default-bootstrap.stackable.svc.cluster.local:9093"
TRINO_INTERNAL_URL = "https://trino-coordinator.stackable.svc.cluster.local:8443"

# Stackable TLS paths (on NiFi pod filesystem)
STACKABLE_KEYSTORE = "/stackable/server_tls/keystore.p12"
STACKABLE_TRUSTSTORE = "/stackable/server_tls/truststore.p12"
STACKABLE_STORE_PASSWORD = "secret"

# Trino password auth (from trino-users K8s secret)
# Override via FACIS_TRINO_USER / FACIS_TRINO_PASSWORD env vars or .env.cluster
TRINO_USER = os.getenv("FACIS_TRINO_USER", "admin")
TRINO_PASSWORD = os.getenv("FACIS_TRINO_PASSWORD", "sj3u82ka")

CONSUMER_GROUP = "facis-nifi-lakehouse"

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
# Auth
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


# ---------------------------------------------------------------------------
# NiFi REST API helpers
# ---------------------------------------------------------------------------


class NiFiClient:
    """Thin wrapper around the NiFi REST API."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/nifi-api"
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path: str) -> dict:
        resp = self.session.get(f"{self.api_url}{path}")
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, payload: dict) -> dict:
        resp = self.session.post(f"{self.api_url}{path}", json=payload)
        if not resp.ok:
            logger.error(f"POST {path} failed ({resp.status_code}): {resp.text[:500]}")
            resp.raise_for_status()
        return resp.json()

    def put(self, path: str, payload: dict) -> dict:
        resp = self.session.put(f"{self.api_url}{path}", json=payload)
        if not resp.ok:
            logger.error(f"PUT {path} failed ({resp.status_code}): {resp.text[:500]}")
            resp.raise_for_status()
        return resp.json()

    def delete(self, path: str, params: dict | None = None) -> dict:
        resp = self.session.delete(f"{self.api_url}{path}", params=params)
        resp.raise_for_status()
        return resp.json() if resp.text else {}

    # --- High-level helpers ---

    def get_root_pg_id(self) -> str:
        flow = self.get("/flow/process-groups/root")
        return flow["processGroupFlow"]["id"]

    def create_process_group(self, parent_id: str, name: str, x: int = 0, y: int = 0) -> dict:
        return self.post(f"/process-groups/{parent_id}/process-groups", {
            "revision": {"version": 0},
            "component": {
                "name": name,
                "position": {"x": x, "y": y},
            },
        })

    def create_processor(self, pg_id: str, proc_type: str, name: str,
                         properties: dict, x: int = 0, y: int = 0,
                         auto_terminate: list[str] | None = None,
                         scheduling_period: str = "0 sec") -> dict:
        config = {
            "properties": properties,
            "schedulingPeriod": scheduling_period,
        }
        if auto_terminate:
            config["autoTerminatedRelationships"] = auto_terminate
        return self.post(f"/process-groups/{pg_id}/processors", {
            "revision": {"version": 0},
            "component": {
                "type": proc_type,
                "name": name,
                "position": {"x": x, "y": y},
                "config": config,
            },
        })

    def create_connection(self, pg_id: str, source_id: str, dest_id: str,
                          relationships: list[str]) -> dict:
        return self.post(f"/process-groups/{pg_id}/connections", {
            "revision": {"version": 0},
            "component": {
                "source": {"id": source_id, "type": "PROCESSOR", "groupId": pg_id},
                "destination": {"id": dest_id, "type": "PROCESSOR", "groupId": pg_id},
                "selectedRelationships": relationships,
            },
        })

    def create_controller_service(self, pg_id: str, svc_type: str, name: str,
                                  properties: dict) -> dict:
        return self.post(f"/process-groups/{pg_id}/controller-services", {
            "revision": {"version": 0},
            "component": {
                "type": svc_type,
                "name": name,
                "properties": properties,
            },
        })

    def enable_controller_service(self, svc_id: str) -> dict:
        svc = self.get(f"/controller-services/{svc_id}")
        version = svc["revision"]["version"]
        return self.put(f"/controller-services/{svc_id}/run-status", {
            "revision": {"version": version},
            "state": "ENABLED",
        })

    def start_processor(self, proc_id: str) -> dict:
        proc = self.get(f"/processors/{proc_id}")
        version = proc["revision"]["version"]
        return self.put(f"/processors/{proc_id}/run-status", {
            "revision": {"version": version},
            "state": "RUNNING",
        })

    def find_process_group(self, parent_id: str, name: str) -> dict | None:
        flow = self.get(f"/flow/process-groups/{parent_id}")
        for pg in flow["processGroupFlow"]["flow"].get("processGroups", []):
            if pg["component"]["name"] == name:
                return pg
        return None


# ---------------------------------------------------------------------------
# NiFi 2.6 processor types
# ---------------------------------------------------------------------------

PROC_CONSUME_KAFKA = "org.apache.nifi.kafka.processors.ConsumeKafka"
PROC_REPLACE_TEXT = "org.apache.nifi.processors.standard.ReplaceText"
PROC_INVOKE_HTTP = "org.apache.nifi.processors.standard.InvokeHTTP"

SVC_SSL_CONTEXT = "org.apache.nifi.ssl.StandardSSLContextService"
SVC_KAFKA_CONNECTION = "org.apache.nifi.kafka.service.Kafka3ConnectionService"

# ---------------------------------------------------------------------------
# Flow construction
# ---------------------------------------------------------------------------

PG_NAME = "FACIS Lakehouse Ingestion"


def build_insert_template(table: str, catalog: str) -> str:
    """Build INSERT SQL template for ReplaceText.

    Uses:
    - $1: regex capture of the escaped FlowFile content (JSON payload)
    - ${kafka.*}: NiFi Expression Language for Kafka metadata attributes
    """
    return (
        f"INSERT INTO \"{catalog}\".bronze.{table} "
        f"(ingestion_timestamp, kafka_topic, kafka_partition, kafka_offset, "
        f"message_key, raw_value) VALUES ("
        f"CURRENT_TIMESTAMP, "
        f"'${{kafka.topic}}', "
        f"CAST(${{kafka.partition}} AS INTEGER), "
        f"CAST(${{kafka.offset}} AS BIGINT), "
        f"'${{kafka.key}}', "
        f"'$1')"
    )


def create_controller_services(client: NiFiClient, pg_id: str) -> tuple[str, str]:
    """Create SSL Context and Kafka Connection controller services.

    Returns (ssl_svc_id, kafka_svc_id).
    """
    # 1. SSL Context Service (Stackable internal TLS — shared by Kafka and Trino)
    ssl_svc = client.create_controller_service(pg_id, SVC_SSL_CONTEXT,
        "Stackable TLS Context",
        {
            "Keystore Filename": STACKABLE_KEYSTORE,
            "Keystore Password": STACKABLE_STORE_PASSWORD,
            "Keystore Type": "PKCS12",
            "Truststore Filename": STACKABLE_TRUSTSTORE,
            "Truststore Password": STACKABLE_STORE_PASSWORD,
            "Truststore Type": "PKCS12",
        },
    )
    ssl_svc_id = ssl_svc["id"]
    logger.info(f"  Created SSL Context Service: {ssl_svc_id}")

    # 2. Kafka Connection Service (internal bootstrap + SSL)
    kafka_svc = client.create_controller_service(pg_id, SVC_KAFKA_CONNECTION,
        "FACIS Kafka Connection",
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_INTERNAL,
            "security.protocol": "SSL",
            "SSL Context Service": ssl_svc_id,
        },
    )
    kafka_svc_id = kafka_svc["id"]
    logger.info(f"  Created Kafka Connection Service: {kafka_svc_id}")

    return ssl_svc_id, kafka_svc_id


def create_ingestion_flow(
    client: NiFiClient,
    pg_id: str,
    topic: str,
    table: str,
    kafka_svc_id: str,
    ssl_svc_id: str,
    catalog: str,
    x_offset: int = 0,
    y_offset: int = 0,
) -> list[str]:
    """Create one topic ingestion flow:
    ConsumeKafka → EscapeQuotes → BuildInsert → InvokeHTTP(Trino)

    Returns list of processor IDs.
    """
    proc_ids = []

    # 1. ConsumeKafka
    consume = client.create_processor(pg_id, PROC_CONSUME_KAFKA,
        f"Consume: {topic}",
        {
            "Kafka Connection Service": kafka_svc_id,
            "Group ID": CONSUMER_GROUP,
            "Topics": topic,
            "Topic Format": "names",
            "auto.offset.reset": "earliest",
            "Processing Strategy": "FLOW_FILE",
            "Output Strategy": "USE_VALUE",
            "Key Attribute Encoding": "utf-8",
        },
        x=x_offset, y=y_offset,
        scheduling_period="1 sec",
    )
    proc_ids.append(consume["id"])

    # 2. ReplaceText — escape single quotes for SQL safety
    escape = client.create_processor(pg_id, PROC_REPLACE_TEXT,
        f"Escape Quotes: {table}",
        {
            "Replacement Strategy": "Literal Replace",
            "Regular Expression": "'",
            "Replacement Value": "''",
            "Evaluation Mode": "Entire text",
        },
        x=x_offset + 400, y=y_offset,
        auto_terminate=["failure"],
    )
    proc_ids.append(escape["id"])

    # 3. ReplaceText — build INSERT SQL
    insert_sql = build_insert_template(table, catalog)
    build = client.create_processor(pg_id, PROC_REPLACE_TEXT,
        f"Build INSERT: {table}",
        {
            "Replacement Strategy": "Regex Replace",
            "Regular Expression": "(?s)(^.*$)",
            "Replacement Value": insert_sql,
            "Evaluation Mode": "Entire text",
        },
        x=x_offset + 800, y=y_offset,
        auto_terminate=["failure"],
    )
    proc_ids.append(build["id"])

    # 4. InvokeHTTP — POST to Trino REST API
    # Basic auth with Trino password user; dynamic properties become HTTP headers
    basic_auth = base64.b64encode(f"{TRINO_USER}:{TRINO_PASSWORD}".encode()).decode()
    invoke = client.create_processor(pg_id, PROC_INVOKE_HTTP,
        f"Trino INSERT: {table}",
        {
            "HTTP Method": "POST",
            "HTTP URL": f"{TRINO_INTERNAL_URL}/v1/statement",
            "Request Content-Type": "text/plain",
            "Request Body Enabled": "true",
            "SSL Context Service": ssl_svc_id,
            # Basic auth via Authorization header (dynamic property)
            "Authorization": f"Basic {basic_auth}",
            "X-Trino-User": TRINO_USER,
            "X-Trino-Catalog": catalog,
            "X-Trino-Schema": "bronze",
        },
        x=x_offset + 1200, y=y_offset,
        auto_terminate=["Original", "Response", "No Retry", "Failure", "Retry"],
    )
    proc_ids.append(invoke["id"])

    # Connect: Consume → Escape → Build → Invoke
    client.create_connection(pg_id, proc_ids[0], proc_ids[1], ["success"])
    client.create_connection(pg_id, proc_ids[1], proc_ids[2], ["success"])
    client.create_connection(pg_id, proc_ids[2], proc_ids[3], ["success"])

    logger.info(f"  Flow: {topic} → bronze.{table}")
    return proc_ids


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def setup_nifi(
    nifi_url: str,
    token: str,
    catalog: str,
    dry_run: bool = False,
) -> None:
    """Main NiFi setup flow."""
    client = NiFiClient(nifi_url, token)

    # Check connectivity
    try:
        root_id = client.get_root_pg_id()
        logger.info(f"NiFi root process group: {root_id}")
    except Exception as e:
        logger.error(f"Cannot connect to NiFi at {nifi_url}: {e}")
        sys.exit(1)

    # Check for existing process group
    existing = client.find_process_group(root_id, PG_NAME)
    if existing:
        logger.warning(f"Process group '{PG_NAME}' already exists (id={existing['id']})")
        logger.warning("Use --teardown to remove it first, or skip NiFi setup.")
        return

    if dry_run:
        logger.info("[DRY RUN] Would create:")
        logger.info(f"  Process group: {PG_NAME}")
        logger.info(f"  Kafka bootstrap: {KAFKA_BOOTSTRAP_INTERNAL}")
        logger.info(f"  Trino endpoint:  {TRINO_INTERNAL_URL}")
        logger.info(f"  Stackable TLS:   {STACKABLE_KEYSTORE}")
        for topic, table in TOPIC_TABLE_MAP.items():
            logger.info(f"  Flow: {topic} → bronze.{table}")
        return

    # Create process group
    pg = client.create_process_group(root_id, PG_NAME)
    pg_id = pg["id"]
    logger.info(f"Created process group: {PG_NAME} ({pg_id})")

    # Create controller services
    logger.info("Creating controller services...")
    ssl_svc_id, kafka_svc_id = create_controller_services(client, pg_id)

    # Enable controller services (SSL first, then Kafka which depends on SSL)
    logger.info("Enabling controller services...")
    try:
        client.enable_controller_service(ssl_svc_id)
        logger.info("  Enabled SSL Context Service")
        time.sleep(2)
        client.enable_controller_service(kafka_svc_id)
        logger.info("  Enabled Kafka Connection Service")
    except Exception as e:
        logger.warning(f"  Could not enable services: {e}")
        logger.warning("  Services may need manual enablement in NiFi UI")

    # Create ingestion flows
    logger.info("Creating ingestion flows...")
    all_proc_ids = []
    for i, (topic, table) in enumerate(TOPIC_TABLE_MAP.items()):
        proc_ids = create_ingestion_flow(
            client, pg_id, topic, table,
            kafka_svc_id, ssl_svc_id, catalog,
            x_offset=0, y_offset=i * 200,
        )
        all_proc_ids.extend(proc_ids)

    # Start all processors
    logger.info("Starting processors...")
    started = 0
    for proc_id in all_proc_ids:
        try:
            client.start_processor(proc_id)
            started += 1
        except Exception as e:
            logger.warning(f"  Could not start processor {proc_id}: {e}")

    logger.info(f"Started {started}/{len(all_proc_ids)} processors")

    # Summary
    print()
    print("=" * 72)
    print("  NiFi Setup Complete")
    print("=" * 72)
    print(f"  Process Group:    {PG_NAME}")
    print(f"  Kafka Bootstrap:  {KAFKA_BOOTSTRAP_INTERNAL}")
    print(f"  Consumer Group:   {CONSUMER_GROUP}")
    print(f"  Trino Endpoint:   {TRINO_INTERNAL_URL}")
    print(f"  Trino Auth:       Basic ({TRINO_USER})")
    print(f"  Flows Created:    {len(TOPIC_TABLE_MAP)}")
    print(f"  Processors:       {started}/{len(all_proc_ids)} running")
    print()
    print(f"  NiFi UI: {nifi_url}/nifi/")
    print("=" * 72)
    print()


def teardown_nifi(nifi_url: str, token: str) -> None:
    """Remove the FACIS Lakehouse Ingestion process group."""
    client = NiFiClient(nifi_url, token)
    root_id = client.get_root_pg_id()
    existing = client.find_process_group(root_id, PG_NAME)

    if not existing:
        logger.info(f"Process group '{PG_NAME}' not found. Nothing to teardown.")
        return

    pg_id = existing["id"]

    # Stop all processors first
    try:
        client.put(f"/flow/process-groups/{pg_id}", {
            "id": pg_id,
            "state": "STOPPED",
        })
        logger.info("Stopped all processors")
        time.sleep(3)
    except Exception as e:
        logger.warning(f"Could not stop processors: {e}")

    # Drop all connections (must be empty — wait for queues to drain)
    try:
        flow = client.get(f"/process-groups/{pg_id}")
        # Empty connection queues
        pg_flow = client.get(f"/flow/process-groups/{pg_id}")
        for conn in pg_flow["processGroupFlow"]["flow"].get("connections", []):
            conn_id = conn["id"]
            try:
                client.post(f"/flowfile-queues/{conn_id}/drop-requests", {})
                time.sleep(0.5)
            except Exception:
                pass
        time.sleep(2)
    except Exception as e:
        logger.warning(f"Could not empty queues: {e}")

    # Disable controller services
    try:
        services = client.get(f"/flow/process-groups/{pg_id}/controller-services")
        for svc in services.get("controllerServices", []):
            svc_id = svc["id"]
            svc_version = svc["revision"]["version"]
            try:
                client.put(f"/controller-services/{svc_id}/run-status", {
                    "revision": {"version": svc_version},
                    "state": "DISABLED",
                })
            except Exception:
                pass
        logger.info("Disabled controller services")
        time.sleep(3)
    except Exception as e:
        logger.warning(f"Could not disable services: {e}")

    # Delete process group
    try:
        pg_info = client.get(f"/process-groups/{pg_id}")
        version = pg_info["revision"]["version"]
        client.delete(f"/process-groups/{pg_id}", {"version": version})
        logger.info(f"Deleted process group '{PG_NAME}'")
    except Exception as e:
        logger.error(f"Could not delete process group: {e}")


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MS2 NiFi Setup — Kafka → Bronze Ingestion")
    parser.add_argument("--env-file", default=None, help="Path to .env.cluster credentials file")
    parser.add_argument("--nifi-url", default=None, help=f"NiFi URL (default: {DEFAULT_NIFI_URL})")
    parser.add_argument("--catalog", default=None, help=f"Trino catalog (default: {DEFAULT_CATALOG})")
    parser.add_argument("--dry-run", action="store_true", help="Print config without applying")
    parser.add_argument("--teardown", action="store_true", help="Remove FACIS process group")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.env_file:
        load_env_file(args.env_file)

    keycloak_url = os.getenv("FACIS_KEYCLOAK_URL", DEFAULT_KEYCLOAK_URL)
    nifi_url = args.nifi_url or os.getenv("FACIS_NIFI_URL", DEFAULT_NIFI_URL)
    catalog = args.catalog or os.getenv("FACIS_TRINO_CATALOG", DEFAULT_CATALOG)

    username = os.getenv("FACIS_OIDC_USERNAME") or input("OIDC username: ")
    password = os.getenv("FACIS_OIDC_PASSWORD") or getpass.getpass("OIDC password: ")
    client_secret = os.getenv("FACIS_OIDC_CLIENT_SECRET") or getpass.getpass("OIDC client secret: ")

    print()
    print("=" * 72)
    print("  FACIS MS2 NiFi Setup")
    print("  Kafka → Bronze Ingestion Pipeline (NiFi 2.6 / Stackable)")
    print("=" * 72)

    token = get_oidc_token(keycloak_url, username, password, client_secret)

    if args.teardown:
        teardown_nifi(nifi_url, token)
        return

    setup_nifi(
        nifi_url=nifi_url,
        token=token,
        catalog=catalog,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
