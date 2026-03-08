# Deployment & Operations Guide

**Project:** FACIS FAP — IoT & AI Demonstrator
**Version:** 1.0
**Date:** 07 March 2026

---

## 1. Overview

This document describes the procedures to deploy and operate the FACIS IoT & AI end-to-end data pipeline. It covers local development, cluster deployment, the Lakehouse setup, and operational monitoring.

### 1.1 Scope Boundary

| In-Scope (this guide) | Out-of-Scope (pre-existing infrastructure) |
|---|---|
| Simulation service build and deployment | Kubernetes cluster provisioning |
| ORCE flow configuration and deployment | Stackable platform operator installation |
| NiFi pipeline configuration | Kafka / NiFi / Trino cluster deployment |
| Lakehouse schema creation (Bronze/Silver/Gold) | S3 object storage provisioning |
| End-to-end validation | Keycloak identity provider setup |
| Seed dataset generation | TLS root CA creation |

For platform infrastructure requirements (what must be in place before this guide can be followed), see [Infrastructure Prerequisites](infrastructure-prerequisites.md). That document specifies exact Kafka topics, Trino catalog settings, Keycloak realm configuration, and network requirements for the infrastructure team.

### 1.2 Prerequisites

- Docker and Docker Compose v2+
- Python 3.11+ with pip
- `kubectl` configured with cluster access
- TLS certificates for Kafka mTLS (CA cert, client cert, client key)
- Credentials file (`.env.cluster`) — see Section 2.1
- All infrastructure prerequisites verified — see [Infrastructure Prerequisites](infrastructure-prerequisites.md) § 9

## 2. Credential Management

### 2.1 Environment File

All sensitive credentials are stored in `.env.cluster` (excluded from version control via `.gitignore`). Copy the template and fill in values provided by the infrastructure team:

```bash
cp .env.cluster.example .env.cluster
# Edit .env.cluster with actual credentials
```

The file requires the following variables:

| Variable | Purpose |
|---|---|
| `FACIS_OIDC_USERNAME` | Keycloak OIDC test user |
| `FACIS_OIDC_PASSWORD` | Keycloak OIDC test password |
| `FACIS_OIDC_CLIENT_SECRET` | Keycloak OIDC client secret |
| `FACIS_KEYCLOAK_URL` | Keycloak realm URL |
| `FACIS_TRINO_HOST` | Trino coordinator external IP |
| `FACIS_TRINO_PORT` | Trino HTTPS port |
| `FACIS_TRINO_CATALOG` | Trino Iceberg catalog name |

### 2.2 TLS Certificates

Kafka requires mTLS for external access. Three PEM files are required:

```
certs/
├── ca.crt        Stackable cluster CA certificate
├── client.crt    Client certificate signed by the CA
└── client.key    Client private key
```

These certificates are extracted from Kubernetes secrets provisioned by Stackable's `secret-operator`. Obtain them from the infrastructure team or extract with:

```bash
# Extract from Kubernetes (requires cluster access)
kubectl get secret -n stackable <kafka-tls-secret> -o jsonpath='{.data.ca\.crt}' | base64 -d > certs/ca.crt
kubectl get secret -n stackable <kafka-tls-secret> -o jsonpath='{.data.tls\.crt}' | base64 -d > certs/client.crt
kubectl get secret -n stackable <kafka-tls-secret> -o jsonpath='{.data.tls\.key}' | base64 -d > certs/client.key
```

## 3. Building the Simulation Service

### 3.1 Docker Image

```bash
# Build the multi-stage Docker image
docker build -t facis-simulation-service:latest .

# Tag for a container registry (adjust registry URL)
docker tag facis-simulation-service:latest <registry>/facis-simulation-service:latest
docker push <registry>/facis-simulation-service:latest
```

The Dockerfile uses a two-stage build:
- **Builder stage**: Creates Python wheels from `pyproject.toml`
- **Runtime stage**: Installs wheels, copies source, runs as non-root user (`simulation`, UID 1000)

### 3.2 Python Dependencies

```bash
# Install for development
pip install -e ".[dev]"

# Install with lakehouse tooling (Trino, NiFi setup scripts)
pip install -e ".[lakehouse]"

# Install with demo tooling
pip install -e ".[demo]"
```

## 4. Local Development

### 4.1 Run Locally (Default Configuration)

```bash
# Start simulation with default.yaml config
python -m src.main

# The service starts on http://localhost:8080
# Health check: GET /api/v1/health
```

### 4.2 Docker Compose (Local Stack)

Starts the simulation, MQTT broker, local Kafka, ORCE, and Kafka UI:

```bash
docker compose up -d

# Verify all services are healthy
docker compose ps

# View simulation logs
docker compose logs -f simulation
```

| Service | URL |
|---|---|
| Simulation API | `http://localhost:8080` |
| MQTT Broker | `localhost:1883` |
| Kafka | `localhost:9092` |
| ORCE (Node-RED) | `http://localhost:1880` |
| Kafka UI | `http://localhost:8090` |

### 4.3 Run Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires Docker services running)
pytest tests/integration/ -v

# BDD tests
pytest tests/bdd/ -v

# Full suite with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

## 5. Cluster Deployment

### 5.1 Start in Cluster Mode

Cluster mode routes all data through ORCE to the remote Kafka cluster (direct Kafka publishing from the simulation is disabled):

```bash
docker compose -f docker-compose.yml -f docker-compose.cluster.yml up --build
```

The cluster override:
- Sets `CONFIG_OVERLAY=cluster` (loads `config/cluster.yaml`)
- Enables ORCE with mTLS Kafka routing
- Disables simulation's direct Kafka publisher
- Sets speed factor to 60× (1 simulated minute per real second)
- Mounts TLS certificates into the ORCE container
- Uses `facis-simulation-cluster.json` flow

### 5.2 ORCE Kubernetes Deployment

For deploying ORCE directly on the cluster (without Docker Compose), follow the dedicated [ORCE Cluster Deployment Guide](orce-cluster-deployment.md). That document covers the complete manual procedure including in-cluster registry provisioning, Kaniko image builds, ORCE customizations (rdkafka SSL patch, JSON Forms GUI Generator), simulation service deployment, and ORCE flow management via the admin API.

Quick reference:

```bash
kubectl apply -f k8s/orce/orce-deployment.yaml

# Verify deployment
kubectl -n orce get pods -l app=orce
kubectl -n orce get svc orce
```

### 5.3 Simulation Kubernetes Deployment

The simulation service deploys alongside ORCE in the `orce` namespace. For the full procedure (including Kaniko builds and RBAC for ORCE-controlled scaling), see [ORCE Cluster Deployment Guide](orce-cluster-deployment.md) § 5.

```bash
kubectl apply -f k8s/simulation/simulation-deployment.yaml
```

The manifest creates a Deployment (0 replicas by default), ClusterIP Service, and RBAC resources that allow ORCE to scale the simulation up and down via its dashboard buttons. The simulation uses the `cluster` config overlay which routes data through ORCE instead of publishing directly to Kafka.

## 6. Lakehouse Setup

### 6.1 Create Bronze/Silver/Gold Schemas

The `setup_lakehouse.py` script authenticates via Keycloak OIDC and creates all Trino objects:

```bash
# Create all schemas, tables, and views (24 objects total)
python scripts/setup_lakehouse.py --env-file .env.cluster

# Preview without executing
python scripts/setup_lakehouse.py --env-file .env.cluster --dry-run

# Tear down everything (views, tables, schemas)
python scripts/setup_lakehouse.py --env-file .env.cluster --teardown
```

Expected output: `24/24 objects created` (9 Bronze tables + 9 Silver views + 12 Gold views).

### 6.2 Provision Trino JDBC Driver for NiFi

The NiFi ingestion pipeline requires the Trino JDBC driver to insert data into Bronze tables. The driver must be provisioned before configuring the pipeline.

**Option A: Automated provisioning (recommended)**

```bash
# Persistent: Creates a PVC and downloads the JAR via a K8s Job
scripts/provision_nifi_jdbc.sh

# Then patch the NiFi cluster to mount the PVC
# See k8s/nifi/nifi-jdbc-volume-patch.yaml for instructions
```

**Option B: Direct provisioning (ephemeral — for dev/testing)**

```bash
# Downloads JAR directly into each running NiFi pod (lost on restart)
scripts/provision_nifi_jdbc.sh --direct
```

**Option C: Manual kubectl exec**

```bash
kubectl exec -n stackable <nifi-pod> -- \
  sh -c 'mkdir -p /opt/nifi/jdbc && curl -fSL -o /opt/nifi/jdbc/trino-jdbc-467.jar \
  https://repo1.maven.org/maven2/io/trino/trino-jdbc/467/trino-jdbc-467.jar'
```

**Verify** the driver is in place:

```bash
scripts/provision_nifi_jdbc.sh --verify
```

K8s manifests for the PVC and provisioner Job are in `k8s/nifi/`.

### 6.3 Configure NiFi Kafka → Bronze Pipeline

The `setup_nifi.py` script creates the ingestion pipeline (36 processors for 9 Kafka topics):

```bash
# Create NiFi process groups, processors, and connections
python scripts/setup_nifi.py --env-file .env.cluster

# Preview configuration without applying
python scripts/setup_nifi.py --env-file .env.cluster --dry-run

# Remove FACIS process group
python scripts/setup_nifi.py --env-file .env.cluster --teardown
```

### 6.4 Configure NiFi MQTT → Kafka Bridge (Optional)

When using the MQTT ORCE flow variant (no rdkafka plugin), data flows via MQTT instead of Kafka. The MQTT-to-Kafka bridge routes all 9 feeds (5 Smart Energy + 4 Smart City) to their corresponding Kafka topics:

```bash
# Create MQTT → Kafka pipeline (9 routes)
python scripts/setup_nifi_mqtt_to_kafka.py --env-file .env.cluster

# Preview without applying
python scripts/setup_nifi_mqtt_to_kafka.py --env-file .env.cluster --dry-run
```

**Data flow variants:**

| ORCE Flow | Smart Energy Path | Smart City Path | NiFi Scripts Needed |
|---|---|---|---|
| `facis-simulation-cluster.json` (rdkafka) | ORCE → Kafka directly | ORCE → Kafka directly | `setup_nifi.py` only |
| `facis-simulation-mqtt.json` (MQTT) | ORCE → MQTT → NiFi → Kafka | ORCE → MQTT → NiFi → Kafka | `setup_nifi_mqtt_to_kafka.py` + `setup_nifi.py` |
| Direct Kafka (no ORCE) | Simulation → Kafka | Simulation → Kafka | `setup_nifi.py` only |

## 7. Validation

### 7.1 End-to-End Pipeline Validation

```bash
python scripts/demo_e2e.py \
  --bootstrap <kafka-external-ip>:9093 \
  --tls \
  --ca-cert certs/ca.crt \
  --client-cert certs/client.crt \
  --client-key certs/client.key \
  --sim-url http://localhost:8080 \
  --orce-url http://localhost:1880
```

Validates: connectivity, Kafka message consumption (all 9 topics), JSON schema correctness, timestamp monotonicity, energy counter monotonicity, cost correlation, and event-dimming correlation.

### 7.2 Lakehouse Validation

```bash
python scripts/demo_lakehouse.py --env-file .env.cluster
```

Validates: Keycloak authentication, Bronze row counts, Silver view accessibility, Gold aggregation query results, data freshness, and feed coverage.

### 7.3 Seed Dataset Generation

For reproducible testing and demonstrations:

```bash
# Generate all 9 scenarios
python scripts/generate_seed_datasets.py

# Generate specific scenario with validation
python scripts/generate_seed_datasets.py --scenario normal_operation --validate
```

| Scenario | Seed | Duration | Purpose |
|---|---|---|---|
| `normal_operation` | 12345 | 24h | Typical weekday baseline |
| `high_consumption` | 23456 | 24h | Peak industrial load |
| `high_pv_generation` | 34567 | 24h | Clear summer day, high PV output |
| `price_volatility` | 45678 | 24h | High energy price swings |
| `weekend_pattern` | 56789 | 48h | Reduced weekend activity |
| `edge_cases` | 67890 | 24h | Boundary value testing |
| `smart_city_normal` | 77001 | 24h | Normal Smart City day |
| `smart_city_event` | 77002 | 24h | Smart City with active events |
| `correlation_demo` | 99001 | 24h | Combined Smart Energy + Smart City |

## 8. Configuration Reference

### 8.1 Configuration Loading

Configuration files are merged in priority order:
1. `config/default.yaml` — base defaults
2. `config/{CONFIG_OVERLAY}.yaml` — environment-specific overrides (deep merge)
3. Environment variables `SIMULATOR_*` — individual value overrides
4. Pydantic validation

### 8.2 Key Configuration Parameters

| Parameter | YAML Path | Environment Variable | Default | Description |
|---|---|---|---|---|
| Seed | `simulation.seed` | `SIMULATOR_SIMULATION__SEED` | `12345` | Deterministic RNG seed |
| Speed Factor | `simulation.speed_factor` | `SIMULATOR_SIMULATION__SPEED_FACTOR` | `1.0` | Time acceleration (60.0 = 60×) |
| Interval | `simulation.interval_minutes` | — | `1` | Simulated time per tick |
| Mode | `simulation.mode` | — | `normal` | Simulation mode |
| MQTT Host | `mqtt.host` | `SIMULATOR_MQTT__HOST` | `mqtt` | MQTT broker hostname |
| MQTT Port | `mqtt.port` | `SIMULATOR_MQTT__PORT` | `1883` | MQTT broker port |
| Kafka Enabled | `kafka.enabled` | `SIMULATOR_KAFKA__ENABLED` | `true` | Direct Kafka publishing |
| ORCE Enabled | `orce.enabled` | `SIMULATOR_ORCE__ENABLED` | `false` | ORCE webhook publishing |
| ORCE URL | `orce.url` | `SIMULATOR_ORCE__URL` | `http://orce:1880` | ORCE service URL |
| HTTP Port | `http.port` | `SIMULATOR_HTTP__PORT` | `8080` | REST API port |
| Modbus Port | `modbus.port` | `SIMULATOR_MODBUS__PORT` | `5020` | Modbus TCP port |
| Log Level | `logging.level` | `SIMULATOR_LOGGING__LEVEL` | `INFO` | Log verbosity |

### 8.3 Environment-Specific Configurations

| File | Speed | Kafka | ORCE | Log Level |
|---|---|---|---|---|
| `default.yaml` | 1.0× | Enabled | Disabled | INFO |
| `cluster.yaml` | 60.0× | Disabled | Enabled | INFO |
| `production.yaml` | 1.0× | (inherit) | (inherit) | WARNING |

## 9. Monitoring & Troubleshooting

### 9.1 Health Checks

```bash
# Simulation service
curl http://localhost:8080/api/v1/health

# Simulation status
curl http://localhost:8080/api/v1/simulation/status
```

### 9.2 Log Monitoring

```bash
# Simulation and ORCE logs
docker compose logs -f simulation orce

# Kafka consumer group status (from inside cluster)
kubectl exec -n stackable <kafka-pod> -- \
  /stackable/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9093 \
  --command-config /tmp/client.properties \
  --group facis-nifi-lakehouse --describe
```

### 9.3 Common Issues

| Issue | Cause | Resolution |
|---|---|---|
| ORCE: `SSL handshake failed` | Certificate mismatch or expiry | Regenerate certificates from Kubernetes secrets |
| NiFi: `SSLPeerUnverifiedException` | Using non-headless K8s service name | Use `*-headless` service FQDN for all TLS connections |
| NiFi: `AUTOCOMMIT_WRITE_CONFLICT` | Iceberg concurrent write conflict | Expected transient error; PutSQL retry handles it |
| Trino: `Value cannot be cast to timestamp` | Silver view using wrong cast | Use `from_iso8601_timestamp()` for ISO 8601 strings |
| Trino: `View is stale` | Underlying schema changed | Re-run `setup_lakehouse.py` to recreate views |
| Bronze: 0 rows | NiFi not consuming or PutSQL failing | Check NiFi bulletins and JDBC connection status |
| OIDC: `invalid_client` | Wrong client ID in `.env.cluster` | Verify Keycloak OIDC client configuration |

## 10. Stopping and Cleanup

```bash
# Stop simulation (data in Lakehouse persists)
docker compose -f docker-compose.yml -f docker-compose.cluster.yml down

# Full Lakehouse teardown (drops all schemas, tables, views)
python scripts/setup_lakehouse.py --env-file .env.cluster --teardown

# NiFi pipeline teardown (removes FACIS process group)
python scripts/setup_nifi.py --env-file .env.cluster --teardown
```

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
