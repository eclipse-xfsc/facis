#!/usr/bin/env python3
"""
NiFi MQTT-to-Kafka Bronze Pipeline Setup.

Creates an Apache NiFi 2.x pipeline that:
    1. Consumes MQTT messages from the Mosquitto broker
    2. Routes messages by MQTT topic to the correct Kafka Bronze topic
    3. Enriches each message with ingestion metadata
    4. Publishes to Kafka Bronze topics
    5. Routes failures to a dead-letter queue

Architecture:
    ConsumeMQTT (9 subscriptions with MQTT wildcards)
        → RouteOnAttribute (match MQTT topic → Kafka destination)
        → JoltTransformJSON (enrich with ingest_timestamp, source_system, source_topic)
        → PublishKafka (produce to Bronze Kafka topic)
        → dead-letter-queue (on failure)

MQTT → Kafka Topic Mapping (Smart Energy):
    facis/energy/meter/+       → energy.bronze.meter-readings
    facis/prices/spot          → energy.bronze.prices
    facis/weather/current      → energy.bronze.weather
    facis/energy/pv/+          → energy.bronze.pv-generation
    facis/loads/+              → energy.bronze.consumer-states

MQTT → Kafka Topic Mapping (Smart City):
    facis/city/light/+         → sim.smart_city.light
    facis/city/traffic/+       → sim.smart_city.traffic
    facis/city/event/+         → sim.smart_city.event
    facis/city/weather         → sim.smart_city.weather

Usage:
    python scripts/setup_nifi_mqtt_to_kafka.py --env-file .env.cluster
    python scripts/setup_nifi_mqtt_to_kafka.py --env-file .env.cluster --dry-run
    python scripts/setup_nifi_mqtt_to_kafka.py --env-file .env.cluster --teardown

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
logger = logging.getLogger("setup_nifi_mqtt_to_kafka")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_KEYCLOAK_URL = "https://identity.facis.cloud/realms/facis"
DEFAULT_NIFI_URL = "https://212.132.83.82:8443"

# MQTT Broker — internal to Docker Compose / K8s cluster
MQTT_BROKER_HOST_LOCAL = "mqtt"
MQTT_BROKER_HOST_CLUSTER = "facis-mqtt.stackable.svc.cluster.local"
MQTT_BROKER_PORT = 1883

# Kafka — internal to Docker Compose / K8s cluster
KAFKA_BOOTSTRAP_LOCAL = "kafka:9092"
KAFKA_BOOTSTRAP_CLUSTER = "kafka-broker-default-bootstrap.stackable.svc.cluster.local:9093"

# Stackable TLS paths (on NiFi pod filesystem — cluster mode only)
STACKABLE_KEYSTORE = "/stackable/server_tls/keystore.p12"
STACKABLE_TRUSTSTORE = "/stackable/server_tls/truststore.p12"
STACKABLE_STORE_PASSWORD = "secret"

# Consumer / Producer identifiers
NIFI_MQTT_CLIENT_ID = "facis-nifi-mqtt-consumer"
NIFI_KAFKA_CLIENT_ID = "facis-nifi-mqtt-to-kafka"
CONSUMER_GROUP = "facis-nifi-mqtt-ingest"

# ---------------------------------------------------------------------------
# MQTT → Kafka topic mapping
# ---------------------------------------------------------------------------

# Each entry: (mqtt_subscription, mqtt_routing_regex, kafka_topic, description)
MQTT_KAFKA_ROUTES: list[dict] = [
    {
        "mqtt_subscription": "facis/energy/meter/+",
        "route_regex": r"facis/energy/meter/.+",
        "route_name": "meter-readings",
        "kafka_topic": "energy.bronze.meter-readings",
        "description": "Energy meter readings (3-phase power, voltage, current)",
        "qos": 1,
    },
    {
        "mqtt_subscription": "facis/prices/spot",
        "route_regex": r"facis/prices/spot",
        "route_name": "prices",
        "kafka_topic": "energy.bronze.prices",
        "description": "Spot electricity prices",
        "qos": 1,
    },
    {
        "mqtt_subscription": "facis/weather/current",
        "route_regex": r"facis/weather/current",
        "route_name": "weather",
        "kafka_topic": "energy.bronze.weather",
        "description": "Weather conditions (temperature, irradiance, wind)",
        "qos": 0,
    },
    {
        "mqtt_subscription": "facis/energy/pv/+",
        "route_regex": r"facis/energy/pv/.+",
        "route_name": "pv-generation",
        "kafka_topic": "energy.bronze.pv-generation",
        "description": "PV generation data (power output, efficiency)",
        "qos": 1,
    },
    {
        "mqtt_subscription": "facis/loads/+",
        "route_regex": r"facis/loads/.+",
        "route_name": "consumer-states",
        "kafka_topic": "energy.bronze.consumer-states",
        "description": "Consumer device load states",
        "qos": 0,
    },
    # --- Smart City routes (used with MQTT ORCE flow variant) ---
    {
        "mqtt_subscription": "facis/city/light/+",
        "route_regex": r"facis/city/light/.+",
        "route_name": "streetlight",
        "kafka_topic": "sim.smart_city.light",
        "description": "Streetlight telemetry (dimming, power per zone)",
        "qos": 0,
    },
    {
        "mqtt_subscription": "facis/city/traffic/+",
        "route_regex": r"facis/city/traffic/.+",
        "route_name": "traffic",
        "kafka_topic": "sim.smart_city.traffic",
        "description": "Traffic zone indices (congestion data)",
        "qos": 0,
    },
    {
        "mqtt_subscription": "facis/city/event/+",
        "route_regex": r"facis/city/event/.+",
        "route_name": "city-event",
        "kafka_topic": "sim.smart_city.event",
        "description": "City events (accidents, emergencies, public events)",
        "qos": 1,
    },
    {
        "mqtt_subscription": "facis/city/weather",
        "route_regex": r"facis/city/weather",
        "route_name": "city-weather",
        "kafka_topic": "sim.smart_city.weather",
        "description": "City weather/visibility (fog index, sunrise/sunset)",
        "qos": 0,
    },
]

# Dead-letter topic for unroutable / failed messages
DEAD_LETTER_TOPIC = "energy.bronze.dead-letter"

# ---------------------------------------------------------------------------
# NiFi 2.x processor types
# ---------------------------------------------------------------------------

PROC_CONSUME_MQTT = "org.apache.nifi.processors.mqtt.ConsumeMQTT"
PROC_ROUTE_ON_ATTRIBUTE = "org.apache.nifi.processors.standard.RouteOnAttribute"
PROC_JOLT_TRANSFORM = "org.apache.nifi.processors.standard.JoltTransformJSON"
PROC_REPLACE_TEXT = "org.apache.nifi.processors.standard.ReplaceText"
PROC_UPDATE_ATTRIBUTE = "org.apache.nifi.processors.attributes.UpdateAttribute"
PROC_PUBLISH_KAFKA = "org.apache.nifi.kafka.processors.PublishKafka"
PROC_FUNNEL = "org.apache.nifi.processors.standard.Funnel"

SVC_SSL_CONTEXT = "org.apache.nifi.ssl.StandardSSLContextService"
SVC_KAFKA_CONNECTION = "org.apache.nifi.kafka.service.Kafka3ConnectionService"


# ---------------------------------------------------------------------------
# Auth (reused from setup_nifi.py)
# ---------------------------------------------------------------------------


def get_oidc_token(keycloak_url: str, username: str, password: str, client_secret: str) -> str:
    """Obtain OIDC access token from Keycloak."""
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
# NiFi REST API client
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

    def create_process_group(self, parent_id: str, name: str,
                             x: int = 0, y: int = 0) -> dict:
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
        config: dict = {
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
                          relationships: list[str],
                          back_pressure_count: str = "10000",
                          back_pressure_size: str = "1 GB") -> dict:
        return self.post(f"/process-groups/{pg_id}/connections", {
            "revision": {"version": 0},
            "component": {
                "source": {"id": source_id, "type": "PROCESSOR", "groupId": pg_id},
                "destination": {"id": dest_id, "type": "PROCESSOR", "groupId": pg_id},
                "selectedRelationships": relationships,
                "backPressureObjectThreshold": back_pressure_count,
                "backPressureDataSizeThreshold": back_pressure_size,
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
# JOLT transform spec for metadata enrichment
# ---------------------------------------------------------------------------


def build_jolt_enrich_spec(kafka_topic: str) -> str:
    """Build a JOLT shift+default spec that wraps the original payload
    and adds ingestion metadata.

    Output structure:
    {
        "ingest_timestamp": "<ISO-8601 from NiFi>",
        "source_system": "facis-simulation-service",
        "source_topic": "<original MQTT topic>",
        "kafka_destination": "<target Kafka topic>",
        "payload": { <original JSON> }
    }
    """
    spec = [
        {
            "operation": "shift",
            "spec": {
                "*": "payload.&",
            },
        },
        {
            "operation": "default",
            "spec": {
                "source_system": "facis-simulation-service",
                "kafka_destination": kafka_topic,
            },
        },
    ]
    return json.dumps(spec)


def build_metadata_enrichment_expression() -> str:
    """Build a ReplaceText expression that wraps the original JSON with
    ingestion metadata using NiFi Expression Language.

    This approach is more reliable than JOLT for adding dynamic timestamps
    because it uses NiFi's ${now():format()} expression language.
    """
    return (
        '{"ingest_timestamp":"${now():format(\'yyyy-MM-dd\'\'T\'\'HH:mm:ss.SSS\'\'Z\'\'\',' +
        "'UTC')}\",\"source_system\":\"facis-simulation-service\"," +
        "\"source_topic\":\"${mqtt.topic}\"," +
        "\"payload\":$1}"
    )


# ---------------------------------------------------------------------------
# Flow construction
# ---------------------------------------------------------------------------

PG_NAME = "FACIS MQTT → Kafka Bronze Pipeline"


def create_controller_services(
    client: NiFiClient,
    pg_id: str,
    cluster_mode: bool,
    kafka_bootstrap: str,
) -> tuple[str | None, str]:
    """Create SSL Context (cluster only) and Kafka Connection controller services.

    Returns (ssl_svc_id | None, kafka_svc_id).
    """
    ssl_svc_id = None

    if cluster_mode:
        # SSL Context Service (Stackable internal TLS)
        ssl_svc = client.create_controller_service(
            pg_id, SVC_SSL_CONTEXT,
            "MQTT-Kafka Stackable TLS",
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

    # Kafka Connection Service
    kafka_props: dict = {
        "bootstrap.servers": kafka_bootstrap,
    }
    if cluster_mode and ssl_svc_id:
        kafka_props["security.protocol"] = "SSL"
        kafka_props["SSL Context Service"] = ssl_svc_id
    else:
        kafka_props["security.protocol"] = "PLAINTEXT"

    kafka_svc = client.create_controller_service(
        pg_id, SVC_KAFKA_CONNECTION,
        "MQTT-Kafka Bronze Connection",
        kafka_props,
    )
    kafka_svc_id = kafka_svc["id"]
    logger.info(f"  Created Kafka Connection Service: {kafka_svc_id}")

    return ssl_svc_id, kafka_svc_id


def create_mqtt_consumer(
    client: NiFiClient,
    pg_id: str,
    route: dict,
    mqtt_host: str,
    x: int,
    y: int,
) -> str:
    """Create a ConsumeMQTT processor for one MQTT subscription.

    Returns the processor ID.
    """
    proc = client.create_processor(
        pg_id, PROC_CONSUME_MQTT,
        f"MQTT: {route['mqtt_subscription']}",
        {
            "Broker URI": f"tcp://{mqtt_host}:{MQTT_BROKER_PORT}",
            "Client ID": f"{NIFI_MQTT_CLIENT_ID}-{route['route_name']}",
            "Topic Filter": route["mqtt_subscription"],
            "Quality of Service(QoS)": str(route["qos"]),
            "Max Queue Size": "10000",
        },
        x=x, y=y,
        scheduling_period="0 sec",
    )
    logger.info(f"  ConsumeMQTT: {route['mqtt_subscription']}")
    return proc["id"]


def create_metadata_enricher(
    client: NiFiClient,
    pg_id: str,
    route: dict,
    x: int,
    y: int,
) -> str:
    """Create a ReplaceText processor that wraps the payload with ingestion metadata.

    Uses NiFi Expression Language for dynamic timestamps and MQTT topic attributes.
    Returns the processor ID.
    """
    # Step 1: UpdateAttribute — set kafka.destination for downstream routing
    update_attr = client.create_processor(
        pg_id, PROC_UPDATE_ATTRIBUTE,
        f"Set Kafka Dest: {route['route_name']}",
        {
            "kafka.destination": route["kafka_topic"],
        },
        x=x, y=y,
        auto_terminate=["failure"],
    )
    return update_attr["id"]


def create_envelope_builder(
    client: NiFiClient,
    pg_id: str,
    route: dict,
    x: int,
    y: int,
) -> str:
    """Create a ReplaceText processor that builds the Bronze envelope.

    Wraps original JSON payload with:
      - ingest_timestamp (ISO-8601 UTC)
      - source_system ("facis-simulation-service")
      - source_topic (original MQTT topic from FlowFile attribute)

    Returns the processor ID.
    """
    # Build envelope using regex capture of entire FlowFile content
    # (?s)(^.*$) captures all content including newlines
    replacement = (
        '{"ingest_timestamp":"${now():format(\'yyyy-MM-dd\'\'T\'\'HH:mm:ss.SSS\'\'Z\''
        "','UTC')}\"," +
        '"source_system":"facis-simulation-service",' +
        '"source_topic":"${mqtt.topic}",' +
        '"payload":$1}'
    )
    proc = client.create_processor(
        pg_id, PROC_REPLACE_TEXT,
        f"Enrich: {route['route_name']}",
        {
            "Replacement Strategy": "Regex Replace",
            "Regular Expression": "(?s)(^.*$)",
            "Replacement Value": replacement,
            "Evaluation Mode": "Entire text",
        },
        x=x, y=y,
        auto_terminate=["failure"],
    )
    logger.info(f"  Enrich metadata: {route['route_name']}")
    return proc["id"]


def create_kafka_publisher(
    client: NiFiClient,
    pg_id: str,
    route: dict,
    kafka_svc_id: str,
    x: int,
    y: int,
) -> str:
    """Create a PublishKafka processor for one Bronze topic.

    Returns the processor ID.
    """
    proc = client.create_processor(
        pg_id, PROC_PUBLISH_KAFKA,
        f"Kafka: {route['kafka_topic']}",
        {
            "Kafka Connection Service": kafka_svc_id,
            "Topic Name": route["kafka_topic"],
            "Use Transactions": "false",
            "Delivery Guarantee": "DELIVERY_REPLICATED",
            "Attributes to Send as Headers (Regex)": "mqtt\\..*",
            "Message Key Field": "${mqtt.topic}",
            "Compression Type": "lz4",
            "Max Request Size": "1 MB",
        },
        x=x, y=y,
        auto_terminate=["success"],
        scheduling_period="0 sec",
    )
    logger.info(f"  PublishKafka: {route['kafka_topic']}")
    return proc["id"]


def create_dead_letter_publisher(
    client: NiFiClient,
    pg_id: str,
    kafka_svc_id: str,
    x: int,
    y: int,
) -> str:
    """Create a PublishKafka processor for the dead-letter queue.

    Handles messages that fail enrichment or publishing.
    Returns the processor ID.
    """
    proc = client.create_processor(
        pg_id, PROC_PUBLISH_KAFKA,
        f"DLQ: {DEAD_LETTER_TOPIC}",
        {
            "Kafka Connection Service": kafka_svc_id,
            "Topic Name": DEAD_LETTER_TOPIC,
            "Use Transactions": "false",
            "Delivery Guarantee": "DELIVERY_REPLICATED",
            "Attributes to Send as Headers (Regex)": ".*",
            "Message Key Field": "${mqtt.topic}",
            "Compression Type": "lz4",
        },
        x=x, y=y,
        auto_terminate=["success", "failure"],
        scheduling_period="0 sec",
    )
    logger.info(f"  Dead-letter queue: {DEAD_LETTER_TOPIC}")
    return proc["id"]


def build_pipeline(
    client: NiFiClient,
    pg_id: str,
    kafka_svc_id: str,
    mqtt_host: str,
) -> list[str]:
    """Build the complete MQTT → Kafka Bronze pipeline.

    For each of the 5 MQTT subscriptions, creates:
        ConsumeMQTT → UpdateAttribute → ReplaceText (enrich) → PublishKafka
        Failures from PublishKafka → DLQ

    Returns list of all processor IDs.
    """
    all_proc_ids = []
    y_spacing = 200
    x_positions = {
        "consume": 0,
        "set_attr": 400,
        "enrich": 800,
        "publish": 1200,
    }

    # Create DLQ publisher (shared by all routes)
    dlq_id = create_dead_letter_publisher(
        client, pg_id, kafka_svc_id,
        x=1600, y=len(MQTT_KAFKA_ROUTES) * y_spacing // 2,
    )
    all_proc_ids.append(dlq_id)

    for i, route in enumerate(MQTT_KAFKA_ROUTES):
        y = i * y_spacing
        logger.info(f"  --- Route {i + 1}/{len(MQTT_KAFKA_ROUTES)}: "
                     f"{route['mqtt_subscription']} → {route['kafka_topic']} ---")

        # 1. ConsumeMQTT
        consume_id = create_mqtt_consumer(
            client, pg_id, route, mqtt_host,
            x=x_positions["consume"], y=y,
        )
        all_proc_ids.append(consume_id)

        # 2. UpdateAttribute — set kafka.destination
        attr_id = create_metadata_enricher(
            client, pg_id, route,
            x=x_positions["set_attr"], y=y,
        )
        all_proc_ids.append(attr_id)

        # 3. ReplaceText — build Bronze envelope with metadata
        enrich_id = create_envelope_builder(
            client, pg_id, route,
            x=x_positions["enrich"], y=y,
        )
        all_proc_ids.append(enrich_id)

        # 4. PublishKafka — produce to Bronze topic
        publish_id = create_kafka_publisher(
            client, pg_id, route, kafka_svc_id,
            x=x_positions["publish"], y=y,
        )
        all_proc_ids.append(publish_id)

        # Wire: Consume → SetAttr → Enrich → Publish
        client.create_connection(pg_id, consume_id, attr_id, ["Message"])
        client.create_connection(pg_id, attr_id, enrich_id, ["success"])
        client.create_connection(pg_id, enrich_id, publish_id, ["success"])

        # Wire: PublishKafka failure → DLQ
        client.create_connection(pg_id, publish_id, dlq_id, ["failure"])

    return all_proc_ids


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def setup_pipeline(
    nifi_url: str,
    token: str,
    cluster_mode: bool,
    dry_run: bool = False,
) -> None:
    """Main setup flow: create the MQTT → Kafka Bronze pipeline in NiFi."""
    client = NiFiClient(nifi_url, token)

    # Resolve environment-specific endpoints
    mqtt_host = MQTT_BROKER_HOST_CLUSTER if cluster_mode else MQTT_BROKER_HOST_LOCAL
    kafka_bootstrap = KAFKA_BOOTSTRAP_CLUSTER if cluster_mode else KAFKA_BOOTSTRAP_LOCAL

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
        logger.warning("Use --teardown to remove it first.")
        return

    if dry_run:
        logger.info("[DRY RUN] Would create:")
        logger.info(f"  Process Group:     {PG_NAME}")
        logger.info(f"  MQTT Broker:       tcp://{mqtt_host}:{MQTT_BROKER_PORT}")
        logger.info(f"  Kafka Bootstrap:   {kafka_bootstrap}")
        logger.info(f"  Cluster Mode:      {cluster_mode}")
        logger.info(f"  Dead-letter Topic: {DEAD_LETTER_TOPIC}")
        logger.info("")
        logger.info("  MQTT → Kafka Routes:")
        for route in MQTT_KAFKA_ROUTES:
            logger.info(f"    {route['mqtt_subscription']:30s} → {route['kafka_topic']}")
        logger.info("")
        logger.info("  Pipeline per route:")
        logger.info("    ConsumeMQTT → UpdateAttribute → ReplaceText(Enrich) → PublishKafka")
        logger.info("    PublishKafka[failure] → DLQ")
        return

    # Create process group
    pg = client.create_process_group(root_id, PG_NAME)
    pg_id = pg["id"]
    logger.info(f"Created process group: {PG_NAME} ({pg_id})")

    # Create controller services
    logger.info("Creating controller services...")
    ssl_svc_id, kafka_svc_id = create_controller_services(
        client, pg_id, cluster_mode, kafka_bootstrap,
    )

    # Enable controller services
    logger.info("Enabling controller services...")
    try:
        if ssl_svc_id:
            client.enable_controller_service(ssl_svc_id)
            logger.info("  Enabled SSL Context Service")
            time.sleep(2)
        client.enable_controller_service(kafka_svc_id)
        logger.info("  Enabled Kafka Connection Service")
    except Exception as e:
        logger.warning(f"  Could not enable services: {e}")
        logger.warning("  Services may need manual enablement in NiFi UI")

    # Build the pipeline
    logger.info("Building MQTT → Kafka Bronze pipeline...")
    all_proc_ids = build_pipeline(client, pg_id, kafka_svc_id, mqtt_host)

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
    print("  FACIS MQTT → Kafka Bronze Pipeline — Setup Complete")
    print("=" * 72)
    print(f"  Process Group:     {PG_NAME}")
    print(f"  MQTT Broker:       tcp://{mqtt_host}:{MQTT_BROKER_PORT}")
    print(f"  Kafka Bootstrap:   {kafka_bootstrap}")
    print(f"  Cluster Mode:      {cluster_mode}")
    print(f"  Dead-letter Topic: {DEAD_LETTER_TOPIC}")
    print(f"  Routes:            {len(MQTT_KAFKA_ROUTES)}")
    print(f"  Processors:        {started}/{len(all_proc_ids)} running")
    print()
    for route in MQTT_KAFKA_ROUTES:
        print(f"    {route['mqtt_subscription']:30s} → {route['kafka_topic']}")
    print()
    print(f"  NiFi UI: {nifi_url}/nifi/")
    print("=" * 72)
    print()


def teardown_pipeline(nifi_url: str, token: str) -> None:
    """Remove the MQTT → Kafka Bronze pipeline process group."""
    client = NiFiClient(nifi_url, token)
    root_id = client.get_root_pg_id()
    existing = client.find_process_group(root_id, PG_NAME)

    if not existing:
        logger.info(f"Process group '{PG_NAME}' not found. Nothing to teardown.")
        return

    pg_id = existing["id"]

    # Stop all processors
    try:
        client.put(f"/flow/process-groups/{pg_id}", {
            "id": pg_id,
            "state": "STOPPED",
        })
        logger.info("Stopped all processors")
        time.sleep(3)
    except Exception as e:
        logger.warning(f"Could not stop processors: {e}")

    # Empty connection queues
    try:
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
    """Load environment variables from a .env file."""
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
    parser = argparse.ArgumentParser(
        description="FACIS NiFi MQTT → Kafka Bronze Pipeline Setup",
    )
    parser.add_argument(
        "--env-file", default=None,
        help="Path to .env.cluster credentials file",
    )
    parser.add_argument(
        "--nifi-url", default=None,
        help=f"NiFi URL (default: {DEFAULT_NIFI_URL})",
    )
    parser.add_argument(
        "--cluster", action="store_true",
        help="Use cluster-mode endpoints (Stackable K8s internal DNS)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print configuration without applying",
    )
    parser.add_argument(
        "--teardown", action="store_true",
        help="Remove the MQTT → Kafka Bronze process group",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.env_file:
        load_env_file(args.env_file)

    keycloak_url = os.getenv("FACIS_KEYCLOAK_URL", DEFAULT_KEYCLOAK_URL)
    nifi_url = args.nifi_url or os.getenv("FACIS_NIFI_URL", DEFAULT_NIFI_URL)

    username = os.getenv("FACIS_OIDC_USERNAME") or input("OIDC username: ")
    password = os.getenv("FACIS_OIDC_PASSWORD") or getpass.getpass("OIDC password: ")
    client_secret = os.getenv("FACIS_OIDC_CLIENT_SECRET") or getpass.getpass("OIDC client secret: ")

    print()
    print("=" * 72)
    print("  FACIS NiFi MQTT → Kafka Bronze Pipeline Setup")
    print("=" * 72)

    token = get_oidc_token(keycloak_url, username, password, client_secret)

    if args.teardown:
        teardown_pipeline(nifi_url, token)
        return

    setup_pipeline(
        nifi_url=nifi_url,
        token=token,
        cluster_mode=args.cluster,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
