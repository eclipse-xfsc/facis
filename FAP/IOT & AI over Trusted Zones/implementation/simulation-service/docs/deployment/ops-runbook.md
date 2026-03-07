# Operations Runbook

**Service:** FACIS FAP IoT & AI — Simulation Service
**Audience:** DevOps and platform team
**Version:** 1.0.0
**Date:** 07 March 2026

---

## 1. Service Overview

The simulation service generates deterministic, correlated IoT telemetry for the FACIS Smart Energy demonstrator. It publishes feeds via four channels: REST API (HTTP), MQTT, Kafka, and Modbus TCP.

### Ports and Protocols

| Port | Protocol | Purpose                  | Default Container Port |
|------|----------|--------------------------|------------------------|
| 8080 | HTTP/TCP | REST API, health checks, Swagger UI | 8080 |
| 502  | TCP      | Modbus TCP (Janitza UMG 96RM emulation) | 502 |
| 1883 | TCP      | MQTT publish (outbound to Mosquitto) | N/A (client) |
| 9092 | TCP      | Kafka produce (outbound to broker) | N/A (client) |

### Generated Feeds

The service produces 5 Smart Energy feeds per simulation tick (default: once per minute):

| Feed | MQTT Topic | Kafka Topic | Key |
|------|-----------|-------------|-----|
| Energy Meter | `facis/energy/meter/{id}` | `sim.smart_energy.meter` | meter_id |
| PV Generation | `facis/energy/pv/{id}` | `sim.smart_energy.pv` | system_id |
| Weather | `facis/weather/current` | `sim.smart_energy.weather` | site_id |
| Spot Price | `facis/prices/spot` | `sim.smart_energy.price` | — |
| Consumer Load | `facis/loads/{type}` | `sim.smart_energy.consumer` | device_id |

---

## 2. Kubernetes Deployment with Helm

### 2.1 Prerequisites

- Kubernetes 1.25+
- Helm 3.x installed
- `kubectl` configured with cluster access
- Container image pushed to registry
- MQTT broker and Kafka broker accessible from the cluster

### 2.2 Build and Push Image

```bash
# Build the production image
docker build -t ghcr.io/siemens-2/facis/simulation-service:1.0.0 .

# Push to container registry
docker push ghcr.io/siemens-2/facis/simulation-service:1.0.0
```

### 2.3 Install the Chart

```bash
cd simulation-service/helm

# Install with defaults (local dev)
helm install facis-sim ./facis-simulation -n facis --create-namespace

# Install with overrides for a production cluster
helm install facis-sim ./facis-simulation -n facis --create-namespace \
  --set image.tag=1.0.0 \
  --set simulation.seed=12345 \
  --set simulation.speedFactor=60 \
  --set mqtt.host=facis-mqtt.stackable.svc.cluster.local \
  --set kafka.bootstrapServers=kafka-broker-default-bootstrap.stackable.svc.cluster.local:9093 \
  --set kafka.securityProtocol=SSL

# Install with a values override file
helm install facis-sim ./facis-simulation -n facis -f values-cluster.yaml
```

### 2.4 Upgrade and Rollback

```bash
# Upgrade with new values
helm upgrade facis-sim ./facis-simulation -n facis --set simulation.speedFactor=120

# Rollback to previous revision
helm rollback facis-sim -n facis

# View release history
helm history facis-sim -n facis
```

### 2.5 Uninstall

```bash
helm uninstall facis-sim -n facis
```

### 2.6 Verify Deployment

```bash
# Check pod status
kubectl get pods -n facis -l app.kubernetes.io/name=facis-simulation

# View pod logs
kubectl logs -n facis -l app.kubernetes.io/name=facis-simulation -f

# Port-forward for local access
kubectl port-forward -n facis svc/facis-sim-facis-simulation 8080:8080

# Test health endpoint
curl http://localhost:8080/api/v1/health
```

### 2.7 Cluster Deployment Example with TLS

For the FACIS Stackable cluster, create a `values-cluster.yaml`:

```yaml
simulation:
  seed: 12345
  speedFactor: 60.0

mqtt:
  host: facis-mqtt.stackable.svc.cluster.local

kafka:
  enabled: true
  bootstrapServers: kafka-broker-default-bootstrap.stackable.svc.cluster.local:9093
  securityProtocol: SSL
  ssl:
    caLocation: /certs/ca.crt
    certificateLocation: /certs/client.crt
    keyLocation: /certs/client.key

orce:
  enabled: true
  url: http://facis-orce.stackable.svc.cluster.local:1880

extraVolumes:
  - name: tls-certs
    secret:
      secretName: facis-kafka-tls

extraVolumeMounts:
  - name: tls-certs
    mountPath: /certs
    readOnly: true
```

```bash
helm install facis-sim ./facis-simulation -n facis -f values-cluster.yaml
```

---

## 3. Docker Compose for Dev/Demo

### 3.1 Local Development Stack

The `docker-compose.yml` runs the full local stack with 5 services:

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| simulation | Built from Dockerfile | 8080, 502 | Simulation service |
| mqtt | eclipse-mosquitto:2 | 1883, 9001 | MQTT broker |
| kafka | confluentinc/cp-kafka:7.6.0 | 9092 | Kafka broker (KRaft mode) |
| orce | ecofacis/xfsc-orce:2.0.3 | 1880 | ORCE orchestration engine |
| kafka-ui | provectuslabs/kafka-ui:latest | 8090 | Kafka topic browser |

```bash
# Start the full stack
docker compose up -d

# Start with rebuild
docker compose up -d --build

# View logs (all services)
docker compose logs -f

# View logs (simulation only)
docker compose logs -f simulation

# Stop the stack
docker compose down

# Stop and remove volumes
docker compose down -v
```

### 3.2 Cluster Publishing Mode

The `docker-compose.cluster.yml` override routes data through ORCE to a remote Kafka cluster with mTLS. This disables direct Kafka publishing from the simulator:

```bash
# Prerequisites: TLS certificates in ./certs/
cp /path/to/{ca.crt,client.crt,client.key} certs/

# Start with cluster override
docker compose -f docker-compose.yml -f docker-compose.cluster.yml up -d --build
```

Key differences from local mode: speed factor is 60x (1 simulated hour per real minute), direct Kafka is disabled, all data flows through ORCE with rdkafka+mTLS.

### 3.2.1 MQTT Flow Mode (No Plugins)

If `node-red-contrib-rdkafka` cannot be installed (e.g., ARM, minimal images), use the MQTT flow variant instead. This uses only built-in Node-RED MQTT nodes and relies on the NiFi ConsumeMQTT pipeline to bridge messages into Kafka:

```bash
# Use base ORCE image (no rdkafka build needed)
# Mount the MQTT flow as the active flow:
docker compose up -d \
  -e ORCE_FLOW_FILE=facis-simulation-mqtt.json

# Or mount manually:
# volumes:
#   - ./orce/flows/facis-simulation-mqtt.json:/data/flows.json:ro
```

Data path: Simulation → ORCE → MQTT Broker → NiFi ConsumeMQTT → Kafka Bronze topics.

The MQTT flow includes a health endpoint at `GET /api/orce/health` that reports MQTT connection status and publish statistics. Trade-off: one additional hop (MQTT → NiFi) adds slight latency but removes the rdkafka native dependency entirely.

### 3.3 Useful Docker Compose Commands

```bash
# Check service health
docker compose ps

# Restart a single service
docker compose restart simulation

# Scale (not recommended — simulation is stateful)
# docker compose up -d --scale simulation=1

# Execute command inside running container
docker compose exec simulation python -c "import src; print('OK')"

# View Kafka topics via Kafka UI
open http://localhost:8090
```

---

## 4. Helm Values Reference

### 4.1 Image Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image.repository` | string | `ghcr.io/siemens-2/facis/simulation-service` | Container registry/repo |
| `image.tag` | string | Chart appVersion (`1.0.0`) | Image tag |
| `image.pullPolicy` | string | `IfNotPresent` | `Always`, `IfNotPresent`, `Never` |
| `imagePullSecrets` | list | `[]` | Registry pull secrets |

### 4.2 Simulation Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `simulation.seed` | int | `12345` | Random seed for reproducible output |
| `simulation.intervalMinutes` | int | `1` | Minutes between generated readings |
| `simulation.speedFactor` | float | `1.0` | Time acceleration (60.0 = 1 sim hour per real minute) |
| `simulation.mode` | string | `normal` | `normal` or `event` (anomaly injection) |
| `simulation.siteId` | string | `site-berlin-001` | Site identifier for feed correlation |

### 4.3 Entity Counts

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entities.meters` | int | `2` | Energy meters to simulate |
| `entities.pvSystems` | int | `2` | PV systems to simulate |
| `entities.consumers` | int | `4` | Consumer devices to simulate |

### 4.4 MQTT Connection

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mqtt.host` | string | `facis-mqtt` | Broker hostname |
| `mqtt.port` | int | `1883` | Broker port |
| `mqtt.clientId` | string | `facis-simulator` | MQTT client ID |
| `mqtt.qos` | int | `1` | Default QoS (0, 1, or 2) |

### 4.5 Kafka Connection

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `kafka.enabled` | bool | `true` | Enable Kafka publishing |
| `kafka.bootstrapServers` | string | `kafka:9092` | Bootstrap servers |
| `kafka.clientId` | string | `facis-simulator` | Producer client ID |
| `kafka.securityProtocol` | string | `PLAINTEXT` | `PLAINTEXT` or `SSL` |
| `kafka.ssl.caLocation` | string | `""` | CA certificate path |
| `kafka.ssl.certificateLocation` | string | `""` | Client certificate path |
| `kafka.ssl.keyLocation` | string | `""` | Client private key path |

### 4.6 ORCE Connection

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `orce.enabled` | bool | `false` | Enable ORCE webhook publishing |
| `orce.url` | string | `http://facis-orce:1880` | ORCE base URL |
| `orce.webhookPath` | string | `/api/sim/tick` | Webhook endpoint path |
| `orce.timeoutSeconds` | float | `10.0` | Request timeout |

### 4.7 Service and Ports

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `http.port` | int | `8080` | HTTP container port |
| `modbus.enabled` | bool | `true` | Enable Modbus TCP server |
| `modbus.port` | int | `502` | Modbus container port |
| `service.type` | string | `ClusterIP` | K8s Service type |
| `service.httpPort` | int | `8080` | Service HTTP port |
| `service.modbusPort` | int | `502` | Service Modbus port |

### 4.8 Resource Requests and Limits

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `resources.requests.cpu` | string | `100m` | CPU request |
| `resources.requests.memory` | string | `128Mi` | Memory request |
| `resources.limits.cpu` | string | `500m` | CPU limit |
| `resources.limits.memory` | string | `512Mi` | Memory limit |

### 4.9 Security Context

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `podSecurityContext.runAsNonRoot` | bool | `true` | Enforce non-root |
| `podSecurityContext.runAsUser` | int | `1000` | UID |
| `podSecurityContext.runAsGroup` | int | `1000` | GID |
| `podSecurityContext.fsGroup` | int | `1000` | Filesystem group |
| `securityContext.readOnlyRootFilesystem` | bool | `true` | Read-only root FS |
| `securityContext.allowPrivilegeEscalation` | bool | `false` | No escalation |
| `securityContext.capabilities.drop` | list | `[ALL]` | Dropped capabilities |

### 4.10 Additional Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `logging.level` | string | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `replicaCount` | int | `1` | Pod replicas (1 recommended) |
| `serviceAccount.create` | bool | `true` | Create ServiceAccount |
| `serviceAccount.automountServiceAccountToken` | bool | `false` | No API token mount |
| `ingress.enabled` | bool | `false` | Enable Ingress resource |
| `extraEnv` | list | `[]` | Additional environment variables |
| `extraVolumes` | list | `[]` | Additional volumes |
| `extraVolumeMounts` | list | `[]` | Additional volume mounts |
| `nodeSelector` | object | `{}` | Node selector labels |
| `tolerations` | list | `[]` | Pod tolerations |
| `affinity` | object | `{}` | Pod affinity rules |

---

## 5. Health and Monitoring Endpoints

### 5.1 Health Check

Used by Docker HEALTHCHECK, Kubernetes liveness/readiness probes, and load balancers.

```bash
curl http://localhost:8080/api/v1/health
```

Response (HTTP 200):

```json
{
  "status": "healthy",
  "service": "facis-simulation-service",
  "version": "1.0.0",
  "timestamp": "2026-03-07T14:30:00.123Z"
}
```

Probe configuration (Kubernetes):

- **Liveness probe**: GET `/api/v1/health`, initial delay 10s, period 30s, timeout 3s, failure threshold 3
- **Readiness probe**: GET `/api/v1/health`, initial delay 5s, period 10s, timeout 3s, failure threshold 3

### 5.2 Simulation Status

Returns the current simulation engine state and timing:

```bash
curl http://localhost:8080/api/v1/simulation/status
```

Response:

```json
{
  "state": "running",
  "simulation_time": "2026-03-07T14:30:00.000Z",
  "seed": 12345,
  "acceleration": 1,
  "entities": {
    "meters": 2,
    "pv_systems": 2,
    "consumers": 4,
    "weather_stations": 1,
    "price_feeds": 1
  }
}
```

### 5.3 Configuration Inspection

Retrieve or update runtime configuration:

```bash
# Get current config
curl http://localhost:8080/api/v1/config

# Update seed (resets simulation)
curl -X PUT http://localhost:8080/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"seed": 42}'

# Update speed factor
curl -X PUT http://localhost:8080/api/v1/config \
  -H "Content-Type: application/json" \
  -d '{"time_acceleration": 60}'
```

### 5.4 Simulation Control

```bash
# Start or resume simulation
curl -X POST http://localhost:8080/api/v1/simulation/start

# Pause simulation
curl -X POST http://localhost:8080/api/v1/simulation/pause

# Reset simulation (optionally with new seed/start time)
curl -X POST http://localhost:8080/api/v1/simulation/reset \
  -H "Content-Type: application/json" \
  -d '{"seed": 99999, "start_time": "2025-06-01T00:00:00Z"}'
```

### 5.5 API Documentation

| Endpoint | Purpose |
|----------|---------|
| `GET /docs` | Swagger UI (interactive) |
| `GET /redoc` | ReDoc (readable) |
| `GET /api/openapi.json` | OpenAPI 3.0 specification |

### 5.6 Monitoring Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Service alive | `curl /api/v1/health` | `{"status": "healthy"}` |
| Simulation running | `curl /api/v1/simulation/status` | `"state": "running"` |
| MQTT connected | Service logs | `Connected to MQTT broker` |
| Kafka delivery | Kafka UI or `kafka-consumer-groups.sh` | Messages in all 5 topics |
| Modbus registers | `pymodbus.console tcp --host <ip> --port 502` | Register 19000+ readable |

---

## 6. Logging Configuration

### 6.1 Log Levels

The service uses Python's standard `logging` module. The level is set via configuration or environment variable:

| Level | Use Case | Environment Variable |
|-------|----------|---------------------|
| `DEBUG` | Development — full trace including tick details | `SIMULATOR_LOGGING__LEVEL=DEBUG` |
| `INFO` | Normal operations — startup, connections, errors (default) | `SIMULATOR_LOGGING__LEVEL=INFO` |
| `WARNING` | Production baseline — only unexpected conditions | `SIMULATOR_LOGGING__LEVEL=WARNING` |
| `ERROR` | Alerts — only failures requiring attention | `SIMULATOR_LOGGING__LEVEL=ERROR` |
| `CRITICAL` | Fatal — service cannot continue | `SIMULATOR_LOGGING__LEVEL=CRITICAL` |

### 6.2 Log Format

Default format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

Example output:
```
2026-03-07 14:30:00,123 - src.engine - INFO - Simulation started (seed=12345, speed=1.0x)
2026-03-07 14:30:01,456 - src.api.mqtt.publisher - INFO - Connected to MQTT broker at mqtt:1883
2026-03-07 14:30:01,789 - src.api.kafka.producer - INFO - Kafka producer initialized for kafka:9092
```

### 6.3 Configuration Methods

Configuration is applied with this priority (highest first):

1. **Environment variable**: `SIMULATOR_LOGGING__LEVEL=DEBUG`
2. **YAML file**: `logging.level: DEBUG` in `config/default.yaml`
3. **Helm values**: `logging.level: DEBUG` in `values.yaml`
4. **Built-in default**: `INFO`

### 6.4 Viewing Logs

```bash
# Docker Compose
docker compose logs -f simulation         # Simulation only
docker compose logs -f simulation mqtt     # Simulation + MQTT broker
docker compose logs --since 5m simulation  # Last 5 minutes
docker compose logs -f --tail 100         # Last 100 lines, follow

# Kubernetes
kubectl logs -n facis -l app.kubernetes.io/name=facis-simulation -f
kubectl logs -n facis -l app.kubernetes.io/name=facis-simulation --since=5m
kubectl logs -n facis -l app.kubernetes.io/name=facis-simulation --previous  # Crashed pod
```

### 6.5 Mosquitto Broker Logs

Mosquitto logs to stderr (captured by Docker/K8s). Configured in `config/mosquitto.conf`:

```bash
# View MQTT broker logs
docker compose logs -f mqtt

# Example output
2026-03-07T14:30:00 mosquitto[1]: New connection from 172.18.0.5:54321 on port 1883.
2026-03-07T14:30:00 mosquitto[1]: New client connected from 172.18.0.5:54321 as facis-simulator (p5, c1, k60).
```

---

## 7. Common Troubleshooting Scenarios

### 7.1 Service Fails to Start

**Symptom:** Pod in `CrashLoopBackOff` or Docker container exits immediately.

**Check logs:**
```bash
kubectl logs -n facis <pod-name> --previous
# or
docker compose logs simulation
```

**Common causes:**

| Cause | Log message | Fix |
|-------|-------------|-----|
| MQTT broker unreachable | `Failed to connect to MQTT broker` | Verify `mqtt.host` and `mqtt.port`. Check broker is running and network policy allows egress. |
| Kafka broker unreachable | `Failed to create Kafka producer` | Verify `kafka.bootstrapServers`. Check DNS resolution and network connectivity. |
| Invalid config YAML | `ValidationError` or `yaml.scanner.ScannerError` | Check ConfigMap or `config/default.yaml` syntax. |
| Port already in use | `Address already in use` | Check no other process binds 8080 or 502. Ensure only 1 replica. |
| Permission denied | `PermissionError: /app/...` | Verify `readOnlyRootFilesystem` has `/tmp` emptyDir mounted. |

### 7.2 No MQTT Messages Published

**Symptom:** MQTT broker receives no messages. Subscriber shows nothing.

**Diagnosis:**
```bash
# Subscribe to all FACIS topics (from host with mosquitto-clients)
mosquitto_sub -h localhost -p 1883 -t 'facis/#' -v

# Check simulation state
curl http://localhost:8080/api/v1/simulation/status
# If state is "initialized" or "paused", start it:
curl -X POST http://localhost:8080/api/v1/simulation/start
```

**Common causes:**

| Cause | Fix |
|-------|-----|
| Simulation not started | `POST /api/v1/simulation/start` |
| MQTT client ID conflict | Two instances with same `client_id` — one gets disconnected. Use unique `mqtt.clientId`. |
| Mosquitto `allow_anonymous false` | Set to `true` for dev, or configure username/password in `mqtt.username`/`mqtt.password`. |
| Network policy blocking egress | Allow pod egress to MQTT port 1883. |

### 7.3 No Kafka Messages

**Symptom:** Kafka topics are empty or consumer group shows no offsets.

**Diagnosis:**
```bash
# List topics
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Check consumer group lag
docker compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --all-groups

# Check for delivery errors in logs
docker compose logs simulation 2>&1 | grep -i "kafka\|delivery\|error"
```

**Common causes:**

| Cause | Fix |
|-------|-----|
| `kafka.enabled: false` | Set `--set kafka.enabled=true` or `SIMULATOR_KAFKA__ENABLED=true` |
| SSL cert mismatch | Verify `ssl.caLocation`, `ssl.certificateLocation`, `ssl.keyLocation` point to valid PEM files mounted in the pod. |
| Broker DNS not resolving | `kubectl exec <pod> -- nslookup kafka-broker-default-bootstrap.stackable.svc.cluster.local` |
| Topic auto-creation disabled | Create topics manually or enable `auto.create.topics.enable=true` on broker. |

### 7.4 Health Check Failing

**Symptom:** Kubernetes restarts the pod repeatedly. Docker shows `unhealthy`.

**Diagnosis:**
```bash
# Test from inside the container
kubectl exec -n facis <pod-name> -- python -c \
  "import urllib.request; print(urllib.request.urlopen('http://localhost:8080/api/v1/health').read())"

# Check readiness probe events
kubectl describe pod -n facis <pod-name> | grep -A5 "Conditions\|Events"
```

**Common causes:**

| Cause | Fix |
|-------|-----|
| Slow startup | Increase `livenessProbe.initialDelaySeconds` (default: 10s) |
| Port mismatch | Verify `http.port` matches probe target port. |
| Uvicorn not binding | Check `SIMULATOR_HTTP__HOST=0.0.0.0` (not 127.0.0.1). |

### 7.5 Modbus TCP Connection Refused

**Symptom:** Modbus client gets "connection refused" on port 502.

**Diagnosis:**
```bash
# Check if Modbus is enabled
curl http://localhost:8080/api/v1/config | python3 -m json.tool

# Test with pymodbus console
pip install pymodbus
pymodbus.console tcp --host localhost --port 502
# Then: client.read_holding_registers 19000 2
```

**Common causes:**

| Cause | Fix |
|-------|-----|
| Modbus disabled | Set `modbus.enabled: true` in values. |
| Port 502 requires root | In Docker/K8s, the container runs as uid 1000. Port 502 works because it's inside the container namespace. If running natively, use port >1024 and remap. |
| Service type not exposing Modbus | Verify Service template includes the modbus port. |

### 7.6 Configuration Not Taking Effect

**Symptom:** Changed values but simulation behaves the same.

**Diagnosis:**
```bash
# Check actual environment in the pod
kubectl exec -n facis <pod-name> -- env | grep SIMULATOR_

# Check mounted ConfigMap
kubectl exec -n facis <pod-name> -- cat /app/config/default.yaml

# Verify Helm values
helm get values facis-sim -n facis
```

**Common causes:**

| Cause | Fix |
|-------|-----|
| ConfigMap not updated | The Deployment has a `checksum/config` annotation that forces rollout on ConfigMap change. Run `helm upgrade`. |
| Env var overrides YAML | Environment variables take precedence. Check `extraEnv` and base env vars in Deployment. |
| Typo in env var name | Must use `SIMULATOR_` prefix with `__` (double underscore) for nesting: `SIMULATOR_SIMULATION__SEED`, not `SIMULATOR_SIMULATION_SEED`. |

### 7.7 ORCE Webhook Timeout

**Symptom:** Logs show `ORCE webhook timed out` or `Connection refused`.

**Diagnosis:**
```bash
# Test ORCE endpoint
curl -X POST http://facis-orce:1880/api/sim/tick \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Check ORCE logs
docker compose logs orce
```

**Common causes:**

| Cause | Fix |
|-------|-----|
| ORCE not running | `docker compose restart orce` or check K8s deployment. |
| Wrong URL | Verify `orce.url` includes correct hostname and port. |
| Flow not loaded | Check ORCE has the correct flow mounted at `/data/flows.json`. Variants: `facis-simulation.json` (validate only), `facis-simulation-mqtt.json` (MQTT, no plugins), `facis-simulation-cluster.json` (rdkafka). |
| Timeout too short | Increase `orce.timeoutSeconds` for large batches. |

---

## 8. Resource Recommendations

### 8.1 Baseline (Default Configuration)

With default settings (2 meters, 2 PV systems, 4 consumers, 1x speed):

| Resource | Request | Limit | Notes |
|----------|---------|-------|-------|
| CPU | 100m | 500m | ~50m steady state, spikes on tick |
| Memory | 128Mi | 512Mi | ~80Mi RSS at steady state |

### 8.2 High-Speed Simulation

At 60x speed factor (cluster mode), CPU usage increases proportionally because tick processing runs 60 times more frequently:

| Resource | Request | Limit | Notes |
|----------|---------|-------|-------|
| CPU | 250m | 1000m | Continuous tick processing |
| Memory | 128Mi | 512Mi | Memory usage unchanged |

### 8.3 Scaled Entity Count

If running with more entities (e.g., 10 meters, 5 PV, 10 consumers), memory increases for state tracking:

| Resource | Request | Limit | Notes |
|----------|---------|-------|-------|
| CPU | 200m | 750m | More per-tick computation |
| Memory | 256Mi | 768Mi | Additional entity state |

### 8.4 Supporting Services

Resource recommendations for co-deployed services:

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|------------|-----------|----------------|--------------|
| Mosquitto | 50m | 200m | 32Mi | 128Mi |
| Kafka (single broker) | 500m | 2000m | 1Gi | 2Gi |
| ORCE (Node-RED) | 100m | 500m | 128Mi | 512Mi |
| Kafka UI | 100m | 500m | 256Mi | 512Mi |

### 8.5 Storage

| Volume | Size | Purpose |
|--------|------|---------|
| Kafka data | 10Gi+ | Topic logs (24h retention default) |
| Mosquitto data | 100Mi | Retained messages and subscriptions |
| ORCE data | 100Mi | Node-RED flow state |
| /tmp emptyDir (simulation) | 64Mi | Temporary files (Python caches) |

---

## 9. Operational Scripts Reference

The `scripts/` directory contains automation for the full pipeline:

| Script | Purpose | Usage |
|--------|---------|-------|
| `provision_nifi_jdbc.sh` | Provision Trino JDBC driver for NiFi pods | `scripts/provision_nifi_jdbc.sh` (PVC) or `--direct` |
| `setup_nifi.py` | Deploy NiFi Kafka→Trino ingestion (9 topics, 36 processors) | `python scripts/setup_nifi.py --env-file .env.cluster` |
| `setup_nifi_mqtt_to_kafka.py` | Deploy NiFi MQTT→Kafka pipeline (9 routes: 5 energy + 4 city) | `python scripts/setup_nifi_mqtt_to_kafka.py --env-file .env.cluster` |
| `setup_lakehouse.py` | Create Trino Bronze/Silver/Gold schemas (30 objects) | `python scripts/setup_lakehouse.py --env-file .env.cluster` |
| `validate_lakehouse.py` | WP3 validation: 39 checks across all layers | `python scripts/validate_lakehouse.py --env-file .env.cluster` |
| `demo_e2e.py` | Validate end-to-end pipeline (Kafka, JSON schema, correlation) | `python scripts/demo_e2e.py --env-file .env.cluster` |
| `demo_lakehouse.py` | Validate lakehouse (auth, Bronze rows, Silver/Gold views) | `python scripts/demo_lakehouse.py --env-file .env.cluster` |
| `generate_seed_datasets.py` | Generate 9 reproducible test scenarios | `python scripts/generate_seed_datasets.py` |

All scripts support `--dry-run` for preview and `--teardown` where applicable. NiFi K8s manifests are in `k8s/nifi/`.

---

## 10. Quick Reference Card

```
SERVICE ENDPOINTS
  Health:       GET  /api/v1/health
  Status:       GET  /api/v1/simulation/status
  Config:       GET  /api/v1/config
  Start:        POST /api/v1/simulation/start
  Pause:        POST /api/v1/simulation/pause
  Reset:        POST /api/v1/simulation/reset
  Swagger:      GET  /docs
  OpenAPI:      GET  /api/openapi.json

ENVIRONMENT VARIABLES (SIMULATOR_ prefix, __ nesting)
  SIMULATOR_SIMULATION__SEED=12345
  SIMULATOR_SIMULATION__SPEED_FACTOR=1.0
  SIMULATOR_SIMULATION__INTERVAL_MINUTES=1
  SIMULATOR_MQTT__HOST=mqtt
  SIMULATOR_MQTT__PORT=1883
  SIMULATOR_KAFKA__ENABLED=true
  SIMULATOR_KAFKA__BOOTSTRAP_SERVERS=kafka:9092
  SIMULATOR_ORCE__ENABLED=false
  SIMULATOR_HTTP__PORT=8080
  SIMULATOR_MODBUS__PORT=502
  SIMULATOR_LOGGING__LEVEL=INFO

HELM INSTALL
  helm install facis-sim ./helm/facis-simulation -n facis --create-namespace

DOCKER COMPOSE
  docker compose up -d                    # Start local stack
  docker compose logs -f simulation       # Follow logs
  docker compose down -v                  # Stop and clean

TROUBLESHOOTING
  kubectl logs -n facis -l app.kubernetes.io/name=facis-simulation -f
  kubectl describe pod -n facis <pod>
  curl http://localhost:8080/api/v1/health
  mosquitto_sub -h localhost -t 'facis/#' -v
```
