# Infrastructure Prerequisites

**Project:** FACIS FAP – IoT & AI Demonstrator
**Audience:** Platform / infrastructure team responsible for Stackable cluster provisioning
**Purpose:** Specifies exactly what the FACIS application layer requires from the underlying platform before deployment scripts can run

---

## 1. Overview

The FACIS IoT & AI Demonstrator runs on a Stackable-managed Kubernetes cluster. The application layer (simulation service, ORCE orchestration, NiFi pipeline configuration, and Trino Lakehouse schemas) is deployed by ATLAS IoT Lab using automated scripts.

This document defines the platform prerequisites that must be in place before the application layer can be deployed. All items listed here are **out of scope** for the ATLAS deployment scripts and must be provisioned by the infrastructure team.

## 2. Required Platform Components

| Component | Version | Purpose |
|---|---|---|
| Kubernetes | 1.25+ | Container orchestration |
| Stackable Platform | Latest stable | Operator-managed Kafka, NiFi, Trino |
| Apache Kafka | 3.x (Stackable-managed) | Message broker for 9 IoT data feeds |
| Apache NiFi | 2.x (Stackable-managed) | Data ingestion pipeline (Kafka → Trino) |
| Trino | Latest (Stackable-managed) | SQL query engine over Iceberg tables |
| S3-compatible storage | Any (IONOS, MinIO, AWS) | Persistent storage for Iceberg Parquet files |
| Keycloak | 20+ | OIDC identity provider for Trino authentication |
| MQTT Broker | Mosquitto 2.x | Message broker for ORCE MQTT flow variant (optional) |

## 3. Kafka Requirements

### 3.1 Cluster Configuration

The Kafka cluster must have mTLS enabled for external client access. Internal (pod-to-pod) communication uses Stackable's automatic TLS via `secret-operator`.

### 3.2 Required Topics

The following 9 Kafka topics must exist before the NiFi ingestion pipeline is configured. If `auto.create.topics.enable` is disabled on the broker (recommended for production), create them manually:

| Topic Name | Partition Count | Replication Factor | Content |
|---|---|---|---|
| `sim.smart_energy.meter` | 3 | 1 | 3-phase energy meter readings |
| `sim.smart_energy.pv` | 3 | 1 | PV solar generation data |
| `sim.smart_energy.weather` | 1 | 1 | Weather conditions (single source) |
| `sim.smart_energy.price` | 1 | 1 | Energy spot prices (single source) |
| `sim.smart_energy.consumer` | 3 | 1 | Consumer device load states |
| `sim.smart_city.light` | 3 | 1 | Streetlight telemetry per zone |
| `sim.smart_city.traffic` | 3 | 1 | Traffic zone indices |
| `sim.smart_city.event` | 3 | 1 | City event records |
| `sim.smart_city.weather` | 1 | 1 | City weather/visibility (single source) |

Partition counts above are recommendations. Single-source feeds (weather, price) need only 1 partition; multi-device feeds benefit from 3+ for parallelism.

**Topic creation example (via Kafka CLI inside the cluster):**

```bash
KAFKA_POD=$(kubectl get pod -n stackable -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

for TOPIC in \
  sim.smart_energy.meter \
  sim.smart_energy.pv \
  sim.smart_energy.weather \
  sim.smart_energy.price \
  sim.smart_energy.consumer \
  sim.smart_city.light \
  sim.smart_city.traffic \
  sim.smart_city.event \
  sim.smart_city.weather; do
  kubectl exec -n stackable "$KAFKA_POD" -- \
    /stackable/kafka/bin/kafka-topics.sh \
    --bootstrap-server localhost:9092 \
    --create --topic "$TOPIC" \
    --partitions 3 --replication-factor 1 \
    --if-not-exists
done
```

### 3.3 TLS Certificates for External Access

ATLAS deployment scripts require three PEM files for Kafka mTLS:

```
certs/
├── ca.crt        Stackable cluster CA certificate
├── client.crt    Client certificate signed by the CA
└── client.key    Client private key
```

Extract from the Stackable secret-operator provisioned secret:

```bash
SECRET_NAME=<kafka-tls-secret>  # Typically: kafka-tls-<cluster-name>
kubectl get secret -n stackable "$SECRET_NAME" -o jsonpath='{.data.ca\.crt}' | base64 -d > certs/ca.crt
kubectl get secret -n stackable "$SECRET_NAME" -o jsonpath='{.data.tls\.crt}' | base64 -d > certs/client.crt
kubectl get secret -n stackable "$SECRET_NAME" -o jsonpath='{.data.tls\.key}' | base64 -d > certs/client.key
```

## 4. NiFi Requirements

### 4.1 Cluster Configuration

The NiFi cluster must be accessible via HTTPS and have network connectivity to:

- **Kafka brokers** (internal K8s DNS): `kafka-broker-default-bootstrap.stackable.svc.cluster.local:9093`
- **Trino coordinator** (internal K8s DNS): `trino-coordinator.stackable.svc.cluster.local:8443`
- **MQTT broker** (if using MQTT flow variant): `facis-mqtt.stackable.svc.cluster.local:1883`

### 4.2 NiFi REST API Access

ATLAS scripts configure NiFi programmatically via its REST API. The API must be accessible from the workstation running the scripts (external access or port-forward).

**Provide to ATLAS:**

| Item | Example |
|---|---|
| NiFi REST API URL | `https://212.132.83.82:8443` |
| Authentication method | Keycloak OIDC Bearer token |

### 4.3 Stackable TLS Context

NiFi pods must have Stackable TLS keystore/truststore available at the standard paths:

- Keystore: `/stackable/server_tls/keystore.p12`
- Truststore: `/stackable/server_tls/truststore.p12`
- Store password: `secret` (Stackable default)

These are used by the NiFi Kafka connection service for mTLS communication with brokers.

## 5. Trino Requirements

### 5.1 Cluster Configuration

Trino must be deployed with the **Iceberg connector** connected to S3 storage.

### 5.2 Catalog Configuration

ATLAS scripts expect a catalog named `fap-iotai-stackable` with the following properties:

| Property | Value |
|---|---|
| Connector | `iceberg` |
| Metastore type | `hive_metastore` or Iceberg REST catalog |
| S3 endpoint | Platform S3 endpoint |
| S3 bucket | `fap-iotai-stackable` (or as configured) |
| S3 path style | `true` (for non-AWS S3) |
| Authentication | Keycloak OIDC (JWT Bearer) |

### 5.3 Schema Permissions

The Keycloak user provided to ATLAS must have permissions to:

- `CREATE SCHEMA` in the catalog
- `CREATE TABLE` in schemas: `bronze`, `silver`, `gold`
- `CREATE VIEW` (or `CREATE OR REPLACE VIEW`) in schemas: `silver`, `gold`
- `INSERT INTO` tables in schema `bronze` (via NiFi)
- `SELECT` from all schemas

### 5.4 Trino Basic Auth (for NiFi)

NiFi's InvokeHTTP processor uses Trino Basic Auth (not OIDC) for INSERT queries. The infrastructure team must provide:

| Item | Example |
|---|---|
| Trino Basic Auth username | `admin` |
| Trino Basic Auth password | (from `trino-users` K8s secret) |

Extract with:

```bash
kubectl get secret trino-users -n stackable -o jsonpath='{.data.admin}' | base64 -d
```

## 6. S3 Object Storage Requirements

### 6.1 Bucket

A single S3 bucket is required for Iceberg table storage:

| Item | Value |
|---|---|
| Bucket name | `fap-iotai-stackable` |
| Purpose | Parquet files for Bronze Iceberg tables |
| Expected size | 1–10 GB for demo data (scales with simulation duration) |
| Retention | No special policy required |

### 6.2 Access Credentials

S3 credentials must be configured in the Trino catalog (not managed by ATLAS scripts).

## 7. Keycloak Requirements

### 7.1 Realm and Client

| Item | Value |
|---|---|
| Realm name | `facis` |
| Client ID | `OIDC` |
| Client type | Confidential |
| Grant types | `password` (Resource Owner Password Credentials) |
| Token endpoint | `https://<keycloak-host>/realms/facis/protocol/openid-connect/token` |

### 7.2 User Account

Provide at least one user with Trino access:

| Item | Value |
|---|---|
| Username | (e.g., `test`) |
| Password | (e.g., `TestUser#12345`) |
| Realm roles | Must allow Trino query execution |

### 7.3 Items to Provide to ATLAS

| Credential | Environment Variable |
|---|---|
| Username | `FACIS_OIDC_USERNAME` |
| Password | `FACIS_OIDC_PASSWORD` |
| Client secret | `FACIS_OIDC_CLIENT_SECRET` |
| Keycloak URL | `FACIS_KEYCLOAK_URL` |

## 8. Network Requirements

### 8.1 External Access (from ATLAS workstation)

| Service | Protocol | Port | Purpose |
|---|---|---|---|
| Trino coordinator | HTTPS | 8443 | Lakehouse setup and validation |
| NiFi REST API | HTTPS | 8443 | Pipeline configuration |
| Kafka bootstrap | TLS | 9093 | E2E validation (mTLS) |
| Keycloak | HTTPS | 443 | OIDC token generation |

### 8.2 Internal Access (pod-to-pod within K8s)

| From | To | Port | Purpose |
|---|---|---|---|
| NiFi → Kafka | `kafka-broker-default-bootstrap.stackable.svc.cluster.local` | 9093 | ConsumeKafka (mTLS) |
| NiFi → Trino | `trino-coordinator.stackable.svc.cluster.local` | 8443 | InvokeHTTP INSERT (Basic Auth) |
| Simulation → Kafka | Kafka bootstrap | 9092/9093 | Direct Kafka publishing |
| Simulation → MQTT | MQTT broker | 1883 | MQTT publishing (optional) |
| ORCE → Kafka | Kafka bootstrap | 9093 | rdkafka publishing (mTLS) |

## 9. Verification Checklist

Before handing off to ATLAS for application deployment, verify:

- [ ] Kafka cluster is running: `kubectl get pods -n stackable -l app.kubernetes.io/name=kafka`
- [ ] NiFi cluster is running: `kubectl get pods -n stackable -l app.kubernetes.io/name=nifi`
- [ ] Trino cluster is running: `kubectl get pods -n stackable -l app.kubernetes.io/name=trino`
- [ ] 9 Kafka topics exist: `kafka-topics.sh --list --bootstrap-server localhost:9092`
- [ ] Keycloak realm `facis` accessible: `curl https://<keycloak>/realms/facis/.well-known/openid-configuration`
- [ ] OIDC token obtainable: `curl -X POST .../token -d 'grant_type=password&...'`
- [ ] Trino query works: `SELECT 1` via Trino CLI with OIDC token
- [ ] S3 bucket accessible from Trino: `SHOW SCHEMAS FROM "fap-iotai-stackable"`
- [ ] TLS certificates extracted to `certs/` directory
- [ ] `.env.cluster` populated with all credentials

---

## 10. Handover Summary

Once all prerequisites are verified, ATLAS deployment proceeds with:

```bash
# 1. Install Python dependencies
pip install -e ".[lakehouse]"

# 2. Create Bronze/Silver/Gold schemas (30 objects)
python scripts/setup_lakehouse.py --env-file .env.cluster

# 3. Provision Trino JDBC driver on NiFi pods
scripts/provision_nifi_jdbc.sh --direct

# 4. Configure NiFi Kafka→Bronze pipeline (36 processors)
python scripts/setup_nifi.py --env-file .env.cluster

# 5. Deploy simulation service (Helm or Docker Compose)
helm install facis-sim ./helm/facis-simulation -n facis --create-namespace

# 6. Validate end-to-end
python scripts/validate_lakehouse.py --env-file .env.cluster
```

Full deployment procedures: see [Deployment & Operations Guide](deployment-operations.md).

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
