# FACIS Simulation Service — Helm Chart

Helm chart for deploying the FACIS FAP IoT & AI deterministic simulation
service on Kubernetes. Generates correlated Smart Energy and Smart City feeds
published via MQTT, Kafka, REST API, and Modbus TCP.

## Prerequisites

- Kubernetes 1.25+
- Helm 3.x
- An MQTT broker (e.g., Eclipse Mosquitto) accessible from the cluster
- A Kafka broker (e.g., Confluent or Strimzi) accessible from the cluster

## Quick Start

```bash
# Add the chart (from local directory)
cd simulation-service/helm

# Install with defaults
helm install facis-sim ./facis-simulation

# Install into a specific namespace
helm install facis-sim ./facis-simulation -n facis --create-namespace

# Install with custom values
helm install facis-sim ./facis-simulation \
  --set simulation.seed=42 \
  --set simulation.speedFactor=60 \
  --set mqtt.host=mosquitto.default.svc.cluster.local \
  --set kafka.bootstrapServers=kafka-bootstrap.kafka.svc.cluster.local:9093

# Install with a values file
helm install facis-sim ./facis-simulation -f my-values.yaml
```

## Uninstall

```bash
helm uninstall facis-sim -n facis
```

## Configuration

### Image

| Parameter          | Description              | Default                                         |
|--------------------|--------------------------|--------------------------------------------------|
| `image.repository` | Container image registry | `ghcr.io/siemens-2/facis/simulation-service`    |
| `image.tag`        | Image tag                | Chart `appVersion`                               |
| `image.pullPolicy` | Pull policy              | `IfNotPresent`                                   |

### Simulation

| Parameter                    | Description                            | Default            |
|------------------------------|----------------------------------------|--------------------|
| `simulation.seed`            | Random seed for reproducibility        | `12345`            |
| `simulation.intervalMinutes` | Reading generation interval (minutes)  | `1`                |
| `simulation.speedFactor`     | Time acceleration (1.0 = real-time)    | `1.0`              |
| `simulation.mode`            | `normal` or `event` (anomalies)        | `normal`           |
| `simulation.siteId`          | Site identifier for correlation        | `site-berlin-001`  |

### Entities

| Parameter            | Description                 | Default |
|----------------------|-----------------------------|---------|
| `entities.meters`    | Number of energy meters     | `2`     |
| `entities.pvSystems` | Number of PV systems        | `2`     |
| `entities.consumers` | Number of consumer devices  | `4`     |

### MQTT

| Parameter       | Description          | Default           |
|-----------------|----------------------|-------------------|
| `mqtt.host`     | Broker hostname      | `facis-mqtt`      |
| `mqtt.port`     | Broker port          | `1883`            |
| `mqtt.clientId` | Client identifier    | `facis-simulator` |
| `mqtt.qos`      | Default QoS level    | `1`               |

### Kafka

| Parameter                       | Description             | Default           |
|---------------------------------|-------------------------|--------------------|
| `kafka.enabled`                 | Enable Kafka publishing | `true`             |
| `kafka.bootstrapServers`        | Bootstrap servers       | `kafka:9092`       |
| `kafka.securityProtocol`        | `PLAINTEXT` or `SSL`   | `PLAINTEXT`        |
| `kafka.ssl.caLocation`          | CA cert path            | `""`               |
| `kafka.ssl.certificateLocation` | Client cert path        | `""`               |
| `kafka.ssl.keyLocation`         | Client key path         | `""`               |

### Resources

| Parameter              | Description    | Default  |
|------------------------|----------------|----------|
| `resources.requests.cpu`    | CPU request    | `100m`   |
| `resources.requests.memory` | Memory request | `128Mi`  |
| `resources.limits.cpu`      | CPU limit      | `500m`   |
| `resources.limits.memory`   | Memory limit   | `512Mi`  |

### Security

The chart enforces pod security best practices by default:

- `runAsNonRoot: true` (uid 1000, matching Dockerfile)
- `readOnlyRootFilesystem: true` (a `/tmp` emptyDir is mounted for writes)
- `capabilities.drop: [ALL]`
- `allowPrivilegeEscalation: false`
- `automountServiceAccountToken: false`

### Service

| Parameter             | Description         | Default     |
|-----------------------|---------------------|-------------|
| `service.type`        | Service type        | `ClusterIP` |
| `service.httpPort`    | HTTP port           | `8080`      |
| `service.modbusPort`  | Modbus TCP port     | `502`       |

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Deployment: facis-simulation                    │
│  ┌─────────────────────────────────────────────┐ │
│  │  Pod (uid 1000, readOnlyRootFilesystem)     │ │
│  │  ┌────────────────────────────────────────┐ │ │
│  │  │  Container: facis-simulation           │ │ │
│  │  │  Ports: 8080 (HTTP), 502 (Modbus)      │ │ │
│  │  │  Probes: /api/v1/health                │ │ │
│  │  │  Mounts:                               │ │ │
│  │  │    /app/config/default.yaml (ConfigMap) │ │ │
│  │  │    /tmp (emptyDir)                     │ │ │
│  │  └────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
        │                      │
   Service:http (8080)    Service:modbus (502)
```

## Cluster Deployment Example

For the FACIS Stackable cluster with SSL Kafka:

```yaml
# values-cluster.yaml
simulation:
  speedFactor: 60.0
  seed: 12345

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

## Development

```bash
# Lint the chart
helm lint ./facis-simulation

# Render templates locally (dry run)
helm template facis-sim ./facis-simulation

# Render with custom values
helm template facis-sim ./facis-simulation --set simulation.seed=42

# Debug template rendering
helm template facis-sim ./facis-simulation --debug
```

## License

Apache License 2.0 — see [LICENSE](../../LICENSE) in the project root.

ATLAS IoT Lab GmbH — Eclipse Foundation FACIS project.
