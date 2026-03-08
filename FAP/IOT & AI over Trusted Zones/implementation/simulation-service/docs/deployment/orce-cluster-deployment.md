# ORCE Cluster Deployment — Manual Registry-Free Guide

**Project:** FACIS FAP — IoT & AI Demonstrator
**Version:** 1.0
**Date:** 08 March 2026

---

## 1. Overview

This document describes the complete procedure for deploying ORCE (the XFSC Orchestration Engine) and the FACIS Simulation Service onto a Kubernetes cluster that has no managed container registry and no Docker daemon on its nodes. It covers building custom images with Kaniko, the ORCE customizations required for Kafka mTLS and the GUI Generator, the simulation service deployment, ORCE flow management via the admin API, and operational troubleshooting.

### 1.1 Scope Boundary

| In-Scope (this guide) | Out-of-Scope (pre-existing infrastructure) |
|---|---|
| In-cluster container registry provisioning | Kubernetes cluster provisioning |
| Containerd trust configuration for in-cluster registry | Stackable platform operator installation |
| Custom ORCE image build (rdkafka + JSON Forms) | Kafka / NiFi / Trino cluster deployment |
| ORCE deployment with Stackable auto-TLS | TLS root CA creation |
| Simulation service image build and deployment | Keycloak identity provider setup |
| ORCE flow import via admin API | S3 object storage provisioning |
| Start/stop controls via ORCE dashboard | NiFi pipeline configuration |

For platform infrastructure requirements, see [Infrastructure Prerequisites](infrastructure-prerequisites.md). For the standard deployment procedures (Docker Compose, Lakehouse setup, NiFi pipelines), see [Deployment & Operations Guide](deployment-operations.md).

### 1.2 Prerequisites

- `kubectl` configured with cluster access
- `tar` available locally (for creating build contexts)
- `curl` and `python3` available locally (for ORCE admin API calls)
- Source files checked out at `simulation-service/`
- All [infrastructure prerequisites](infrastructure-prerequisites.md) verified (Kafka topics, Stackable operators, Keycloak realm)

### 1.3 Architecture

The deployment creates two workloads in the `orce` namespace:

```
┌─────────────────┐     HTTP POST      ┌──────────────────┐    rdkafka/mTLS    ┌─────────────┐
│   Simulation    │ ──────────────────> │       ORCE       │ ─────────────────> │    Kafka     │
│  (0-1 replicas) │   /api/sim/tick    │  (Node-RED +     │   9 topics         │  (Stackable) │
│                 │                     │   rdkafka patch) │                    │              │
└─────────────────┘                     └──────────────────┘                    └─────────────┘
      ▲ scale up/down                          │
      └──────── K8s API (RBAC) ────────────────┘
                                    ORCE inject buttons
```

The simulation service starts at 0 replicas. ORCE inject buttons scale the deployment up (START) or down (STOP) by calling the Kubernetes API using the pod's service account token. When running, the simulation generates tick envelopes every simulated minute at 60× speed, posts them to ORCE, which validates, splits by feed type, and publishes each feed to its Kafka topic via rdkafka with mTLS.

## 2. ORCE Customizations

The upstream XFSC ORCE image (`ecofacis/xfsc-orce:2.0.3`) does not include Kafka support or the JSON Forms GUI generator. Three files in `orce/` customise it for the FACIS cluster deployment.

### 2.1 Dockerfile

**File:** `orce/Dockerfile`

The custom image extends the ORCE base with two plugin sets installed into staging directories (not `/data`, which is a runtime volume):

- **rdkafka plugin** (`node-red-contrib-rdkafka`): requires `librdkafka-dev` and native compilation tools (`python3`, `make`, `g++`). Built with `BUILD_LIBRDKAFKA=0` to use the system library rather than compiling from source.
- **JSON Forms GUI Generator** (`@jsonforms/core`, `@jsonforms/react`, `@jsonforms/material-renderers`, MUI, `node-red-contrib-uibuilder`): provides dynamic UI rendering from JSON Schema definitions for the DCM catalogue interface.

A `npm install -g npm@latest` step is required to fix a `node-gyp` compatibility issue with Node 20.19 in the ORCE base image (the bundled `node-gyp` has a broken logger that causes `TypeError: Cannot read properties of undefined 'pause'`).

### 2.2 Entrypoint Script

**File:** `orce/entrypoint.sh`

The custom entrypoint runs before the original ORCE entrypoint and performs five steps:

1. **Bootstrap /data on first boot.** The ORCE image stores its defaults (settings.js, flows, branding CSS/JS, dark mode, AI button, zoom controls) in `/opt/maestro/MBE/.node-red/`. On first boot (empty PVC), the entrypoint copies everything except `node_modules/` into `/data/` so that the runtime presents as ORCE rather than plain Node-RED.

2. **Copy rdkafka modules.** Copies `node-red-contrib-rdkafka` and its native dependencies (`node-rdkafka`, `bindings`, `file-uri-to-path`, `nan`) from `/opt/rdkafka-staging/node_modules/` into `/data/node_modules/`.

3. **Apply the SSL patch.** Overwrites the stock `rdkafka.js` with the patched version that supports `security.protocol=ssl` and certificate path properties.

4. **Copy JSON Forms modules.** Copies `node-red-contrib-uibuilder` and all `@jsonforms`, `@mui`, `@emotion` scoped packages into `/data/node_modules/`.

5. **Register modules in package.json.** Adds `node-red-contrib-rdkafka` and `node-red-contrib-uibuilder` to `/data/package.json` so that Node-RED discovers them on startup.

### 2.3 rdkafka SSL/mTLS Patch

**File:** `orce/rdkafka-patch.js`

The upstream `node-red-contrib-rdkafka` plugin does not support SSL/TLS connections. The patch replaces the original `rdkafka.js` and adds four optional properties to the `kafka-broker` config node:

| Property | librdkafka equivalent | Purpose |
|---|---|---|
| `securityProtocol` | `security.protocol` | Set to `ssl` to enable TLS |
| `sslCaLocation` | `ssl.ca.location` | Path to CA certificate (PEM) |
| `sslCertLocation` | `ssl.certificate.location` | Path to client certificate (PEM) |
| `sslKeyLocation` | `ssl.key.location` | Path to client private key (PEM) |

When `securityProtocol` is set to `ssl`, the patch injects these into the librdkafka configuration object used by both producers and consumers. The certificate files are mounted from a Stackable CSI ephemeral volume (see Section 4.3).

## 3. In-Cluster Container Registry

Since the IONOS cluster has no managed container registry and Docker is not available on the nodes, the deployment provisions a temporary in-cluster registry and configures containerd to trust it.

### 3.1 Deploy the Registry

```bash
kubectl create namespace orce

kubectl apply -n orce -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: registry
  namespace: orce
spec:
  replicas: 1
  selector:
    matchLabels:
      app: registry
  template:
    metadata:
      labels:
        app: registry
    spec:
      containers:
        - name: registry
          image: registry:2
          ports:
            - containerPort: 5000
          volumeMounts:
            - name: data
              mountPath: /var/lib/registry
      volumes:
        - name: data
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: registry
  namespace: orce
spec:
  selector:
    app: registry
  ports:
    - port: 5000
      targetPort: 5000
EOF

kubectl -n orce wait --for=condition=ready pod -l app=registry --timeout=120s
```

The registry uses `emptyDir` storage, so images are lost if the pod is rescheduled. For persistent images, replace with a PVC.

### 3.2 Configure Containerd Trust

Each node's containerd runtime must be configured to pull from the in-cluster registry over HTTP (no TLS). A DaemonSet handles this automatically by writing a `hosts.toml` file and signalling containerd to reload:

```bash
kubectl apply -n orce -f - <<'EOF'
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: registry-config
  namespace: orce
spec:
  selector:
    matchLabels:
      app: registry-config
  template:
    metadata:
      labels:
        app: registry-config
    spec:
      hostPID: true
      initContainers:
        - name: configure
          image: alpine:3.19
          securityContext:
            privileged: true
          command:
            - sh
            - -c
            - |
              HOST_DIR="/host/etc/containerd/certs.d/registry.orce.svc.cluster.local:5000"
              mkdir -p "$HOST_DIR"
              cat > "$HOST_DIR/hosts.toml" <<TOML
              server = "http://registry.orce.svc.cluster.local:5000"
              [host."http://registry.orce.svc.cluster.local:5000"]
                capabilities = ["pull", "resolve"]
                skip_verify = true
              TOML
              nsenter -t 1 -m -- kill -s HUP $(nsenter -t 1 -m -- pidof containerd) 2>/dev/null || true
              echo "Done — containerd configured on $(hostname)"
          volumeMounts:
            - name: host-etc
              mountPath: /host/etc
      containers:
        - name: pause
          image: registry.k8s.io/pause:3.9
      volumes:
        - name: host-etc
          hostPath:
            path: /etc
      tolerations:
        - operator: Exists
EOF

kubectl -n orce rollout status daemonset/registry-config --timeout=120s
```

## 4. Building and Deploying ORCE

### 4.1 Build the Custom ORCE Image with Kaniko

Kaniko builds container images inside Kubernetes pods without requiring a Docker daemon. The build context is uploaded as a ConfigMap.

```bash
cd simulation-service/orce/

# Create a tarball of the build context
tar -czf /tmp/orce-context.tar.gz Dockerfile entrypoint.sh rdkafka-patch.js

# Upload as a ConfigMap
kubectl -n orce create configmap orce-build-context \
    --from-file=context.tar.gz=/tmp/orce-context.tar.gz \
    --dry-run=client -o yaml | kubectl apply -f -

# Run the Kaniko build job
kubectl apply -n orce -f - <<'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: orce-build
  namespace: orce
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      initContainers:
        - name: unpack
          image: alpine:3.19
          command: ["sh", "-c", "tar xzf /context-cm/context.tar.gz -C /workspace"]
          volumeMounts:
            - name: context-cm
              mountPath: /context-cm
            - name: workspace
              mountPath: /workspace
      containers:
        - name: kaniko
          image: gcr.io/kaniko-project/executor:latest
          args:
            - --context=dir:///workspace
            - --destination=registry.orce.svc.cluster.local:5000/facis/orce:2.0.3-facis
            - --insecure
            - --cache=false
          volumeMounts:
            - name: workspace
              mountPath: /workspace
          resources:
            requests:
              cpu: "2"
              memory: 4Gi
            limits:
              cpu: "4"
              memory: 8Gi
      volumes:
        - name: context-cm
          configMap:
            name: orce-build-context
        - name: workspace
          emptyDir: {}
EOF
```

Monitor the build (typically 5–10 minutes due to native compilation of `node-rdkafka`):

```bash
kubectl -n orce logs -f job/orce-build -c kaniko
kubectl -n orce wait --for=condition=complete job/orce-build --timeout=600s
```

### 4.2 Create Secrets

```bash
kubectl -n orce create secret generic orce-secrets \
    --from-literal=credential-secret='<RANDOM_32_CHAR_STRING>' \
    --from-literal=trino-user='admin' \
    --from-literal=trino-password='<TRINO_PASSWORD>' \
    --from-literal=oidc-client-secret='<KEYCLOAK_CLIENT_SECRET>' \
    --dry-run=client -o yaml | kubectl apply -f -
```

Replace `<placeholders>` with actual credentials provided by the infrastructure team.

### 4.3 Deploy ORCE

Apply the full deployment manifest:

```bash
kubectl apply -f k8s/orce/orce-deployment.yaml
```

This creates: PVC (`orce-data`, 1Gi), ConfigMaps (flows placeholder, DCM schemas placeholder), Deployment, Secret template, and LoadBalancer Service.

The manifest references `registry.facis.cloud/facis/orce:2.0.3-facis` as the image. Since we use the in-cluster registry, patch the image after applying:

```bash
kubectl -n orce set image deployment/orce \
    orce=registry.orce.svc.cluster.local:5000/facis/orce:2.0.3-facis
```

Wait for the pod to become ready:

```bash
kubectl -n orce rollout status deployment/orce --timeout=300s
```

**Kafka mTLS certificates** are provisioned automatically by Stackable's `secret-operator` via a CSI ephemeral volume. The deployment manifest declares:

```yaml
volumes:
  - name: kafka-certs
    ephemeral:
      volumeClaimTemplate:
        metadata:
          annotations:
            secrets.stackable.tech/class: tls
            secrets.stackable.tech/scope: pod
        spec:
          accessModes: ["ReadWriteOnce"]
          storageClassName: secrets.stackable.tech
          resources:
            requests:
              storage: 1
```

This auto-provisions `ca.crt`, `tls.crt`, and `tls.key` into `/etc/kafka-certs/` without requiring a pre-existing Kubernetes Secret.

### 4.4 Verify ORCE

```bash
# Check pod status
kubectl -n orce get pods -l app=orce

# Check logs — look for these lines:
#   [entrypoint] rdkafka modules ready
#   [entrypoint] JSON Forms + uibuilder modules ready
kubectl -n orce logs -l app=orce --tail=50

# Get the external IP
kubectl -n orce get svc orce -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

Access ORCE at `http://<EXTERNAL_IP>:1880`. It should show the ORCE-branded interface (dark mode, AI button, zoom controls), not plain Node-RED.

## 5. Building and Deploying the Simulation Service

### 5.1 Build the Simulation Image with Kaniko

The simulation service has a multi-stage Python Dockerfile. The build context must include `src/`, `config/`, `docs/` (contains `openapi.yaml`), `pyproject.toml`, and the Dockerfile.

When creating the tarball, anchor exclusions to the current directory (`--exclude='./orce'`) to avoid accidentally excluding `src/api/orce/`, which is the ORCE HTTP client used by the simulation.

```bash
cd simulation-service/

tar czf /tmp/sim-context.tar.gz \
    --exclude='./orce' --exclude='./k8s' --exclude='./tests' \
    --exclude='./schemas' --exclude='./demo' \
    --exclude='./features' --exclude='__pycache__' \
    Dockerfile pyproject.toml README.md LICENSE src/ config/ docs/

kubectl -n orce create configmap sim-build-context \
    --from-file=context.tar.gz=/tmp/sim-context.tar.gz \
    --dry-run=client -o yaml | kubectl apply -f -

kubectl delete job sim-build -n orce 2>/dev/null || true

kubectl apply -n orce -f - <<'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: sim-build
  namespace: orce
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      initContainers:
        - name: unpack
          image: alpine:3.19
          command: ["sh", "-c", "tar xzf /context-cm/context.tar.gz -C /workspace"]
          volumeMounts:
            - name: context-cm
              mountPath: /context-cm
            - name: workspace
              mountPath: /workspace
      containers:
        - name: kaniko
          image: gcr.io/kaniko-project/executor:latest
          args:
            - --context=dir:///workspace
            - --destination=registry.orce.svc.cluster.local:5000/facis/simulation:1.0.0
            - --insecure
            - --cache=false
          volumeMounts:
            - name: workspace
              mountPath: /workspace
          resources:
            requests:
              cpu: "2"
              memory: 4Gi
            limits:
              cpu: "4"
              memory: 8Gi
      volumes:
        - name: context-cm
          configMap:
            name: sim-build-context
        - name: workspace
          emptyDir: {}
EOF

kubectl -n orce wait --for=condition=complete job/sim-build --timeout=600s
```

### 5.2 Deploy the Simulation Service

```bash
kubectl apply -f k8s/simulation/simulation-deployment.yaml
```

This creates: Deployment (0 replicas), ClusterIP Service, ServiceAccount, Role (`simulation-scaler`), and RoleBinding (`orce-can-scale-simulation`).

The simulation starts with 0 replicas by design — ORCE inject buttons control scaling. The RBAC resources grant ORCE's default ServiceAccount permission to `get` and `patch` the simulation deployment's scale sub-resource.

## 6. ORCE Flow Management

### 6.1 Flow Files

Two flow files define the ORCE behaviour:

| File | Tab Label | Purpose |
|---|---|---|
| `orce/flows/facis-simulation-cluster.json` | FACIS Simulation → Kafka | HTTP-in endpoint, schema validation, feed splitting, 9× rdkafka producers with mTLS |
| `orce/flows/facis-simulation-controls.json` | Simulation Controls | START/STOP/STATUS inject buttons that scale the simulation deployment via K8s API |

### 6.2 Import via the Admin API

Flows must be imported via the ORCE admin API rather than by copying files into the PVC. When Node-RED shuts down, it writes its in-memory flow state back to disk, overwriting any files that were copied via `kubectl cp`.

```bash
ORCE_IP=$(kubectl -n orce get svc orce -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Authenticate (default admin password: xfsc-orce)
TOKEN=$(curl -s -X POST http://${ORCE_IP}:1880/auth/token \
    -H "Content-Type: application/json" \
    -d '{"client_id":"node-red-admin","grant_type":"password","scope":"*","username":"admin","password":"xfsc-orce"}' \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Merge the two flow files into one
python3 -c "
import json
with open('orce/flows/facis-simulation-cluster.json') as f: kafka = json.load(f)
with open('orce/flows/facis-simulation-controls.json') as f: ctrl = json.load(f)
merged = kafka + ctrl
with open('/tmp/flows.json', 'w') as f: json.dump(merged, f)
"

# Deploy flows (full replace)
curl -s -X POST http://${ORCE_IP}:1880/flows \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Node-RED-Deployment-Type: full" \
    -d @/tmp/flows.json
```

After import, verify that the ORCE editor shows two flow tabs: "FACIS Simulation → Kafka" and "Simulation Controls". The debug sidebar should show 9 rdkafka producer nodes with green "connected" status.

### 6.3 Simulation Controls Flow

The "Simulation Controls" tab provides three inject buttons:

| Button | Action | Mechanism |
|---|---|---|
| **START Simulation** | Scales simulation to 1 replica | PATCHes K8s deployment scale endpoint |
| **STOP Simulation** | Scales simulation to 0 replicas | PATCHes K8s deployment scale endpoint |
| **Simulation STATUS** | Queries simulation state | GET request to simulation REST API |

The scale function node reads the Kubernetes service account token from `/var/run/secrets/kubernetes.io/serviceaccount/token` and uses the `fs` module via the Node-RED function node `libs` array (not `require()`, which is unavailable in function nodes):

```json
"libs": [{ "var": "fs", "module": "fs" }]
```

## 7. Kafka Broker Configuration

### 7.1 Broker Address

Stackable Kafka uses headless services for broker discovery. The correct DNS pattern is:

```
<pod-name>.<headless-service-name>.<namespace>.svc.cluster.local:<port>
```

For the FACIS cluster:

```
kafka-broker-default-0.kafka-broker-default-headless.stackable.svc.cluster.local:9093
```

The non-headless service name (`kafka-broker-default` without `-headless`) does not resolve individual broker pods and causes `ENOTFOUND` errors in the rdkafka client.

### 7.2 mTLS Certificate Paths

Inside the ORCE pod, Stackable CSI provisions certificates at:

| File | Mount Path | Usage |
|---|---|---|
| CA certificate | `/etc/kafka-certs/ca.crt` | Verify broker identity |
| Client certificate | `/etc/kafka-certs/tls.crt` | Client authentication |
| Client key | `/etc/kafka-certs/tls.key` | Client authentication |

These paths are configured in the `kafka-broker` config node within `facis-simulation-cluster.json`.

### 7.3 Kafka Topics

The simulation produces to 9 topics (auto-created by rdkafka if the broker allows, otherwise pre-create per [Infrastructure Prerequisites](infrastructure-prerequisites.md) § 3.2):

| Topic | Feed Type | Key Field |
|---|---|---|
| `sim.smart_energy.meter` | 3-phase energy meter readings | `meter_id` |
| `sim.smart_energy.pv` | PV solar generation | `pv_system_id` |
| `sim.smart_energy.weather` | Temperature, humidity, irradiance | `site_id` |
| `sim.smart_energy.price` | Energy market price | `price` |
| `sim.smart_energy.consumer` | Device power consumption | `device_id` |
| `sim.smart_city.light` | Streetlight telemetry | `light_id` |
| `sim.smart_city.traffic` | Traffic/congestion data | `zone_id` |
| `sim.smart_city.event` | City incidents/alerts | `zone_id` |
| `sim.smart_city.weather` | Visibility conditions | `city_id` |

## 8. Rebuilding After Code Changes

### 8.1 ORCE Image

```bash
# Delete old build job
kubectl -n orce delete job orce-build

# Update build context
cd simulation-service/orce/
tar -czf /tmp/orce-context.tar.gz Dockerfile entrypoint.sh rdkafka-patch.js
kubectl -n orce create configmap orce-build-context \
    --from-file=context.tar.gz=/tmp/orce-context.tar.gz \
    --dry-run=client -o yaml | kubectl apply -f -

# Re-run Kaniko (re-apply the Job YAML from Section 4.1)

# Restart the deployment to pick up the new image
kubectl -n orce rollout restart deployment/orce
```

If the ORCE entrypoint or Dockerfile changed significantly, delete the PVC to force a clean first-boot seed:

```bash
kubectl -n orce delete pvc orce-data
kubectl -n orce rollout restart deployment/orce
```

Deleting the PVC wipes all ORCE data (flows, credentials, installed nodes). Re-import flows via the admin API (Section 6.2) after the pod restarts.

### 8.2 Simulation Image

```bash
kubectl -n orce delete job sim-build

cd simulation-service/
tar czf /tmp/sim-context.tar.gz \
    --exclude='./orce' --exclude='./k8s' --exclude='./tests' \
    --exclude='./schemas' --exclude='./demo' \
    --exclude='./features' --exclude='__pycache__' \
    Dockerfile pyproject.toml README.md LICENSE src/ config/ docs/
kubectl -n orce create configmap sim-build-context \
    --from-file=context.tar.gz=/tmp/sim-context.tar.gz \
    --dry-run=client -o yaml | kubectl apply -f -

# Re-run Kaniko (re-apply the Job YAML from Section 5.1)

# If the simulation is running, restart it
kubectl -n orce rollout restart deployment/simulation
```

## 9. Validation

### 9.1 ORCE Startup

```bash
# Confirm ORCE pod is running
kubectl -n orce get pods -l app=orce

# Check for plugin initialization
kubectl -n orce logs -l app=orce | grep '\[entrypoint\]'
# Expected:
#   [entrypoint] rdkafka modules ready
#   [entrypoint] JSON Forms + uibuilder modules ready

# Check rdkafka producer connections (all 9 should show "Producer ready")
kubectl -n orce logs -l app=orce | grep '\[rdkafka\] Producer ready'
```

### 9.2 End-to-End Data Flow

Start the simulation from the ORCE dashboard (click START Simulation), then verify messages arrive on Kafka:

```bash
# Verify simulation pod is running
kubectl -n orce get pods -l app=simulation

# Check simulation logs for successful tick delivery
kubectl -n orce logs -l app=simulation --tail=20

# Consume a message from Kafka inside the ORCE pod
kubectl -n orce exec deploy/orce -- node -e "
const Kafka = require('/data/node_modules/node-rdkafka');
const consumer = new Kafka.KafkaConsumer({
    'metadata.broker.list': 'kafka-broker-default-0.kafka-broker-default-headless.stackable.svc.cluster.local:9093',
    'group.id': 'test-verify',
    'security.protocol': 'ssl',
    'ssl.ca.location': '/etc/kafka-certs/ca.crt',
    'ssl.certificate.location': '/etc/kafka-certs/tls.crt',
    'ssl.key.location': '/etc/kafka-certs/tls.key',
    'auto.offset.reset': 'earliest'
}, {});
consumer.connect();
consumer.on('ready', () => {
    consumer.subscribe(['sim.smart_energy.meter']);
    consumer.consume();
    console.log('Subscribed — waiting for messages...');
});
consumer.on('data', (msg) => {
    console.log('Topic:', msg.topic, 'Key:', msg.key?.toString(), 'Size:', msg.size);
    consumer.disconnect();
    process.exit(0);
});
setTimeout(() => { console.log('No messages after 15s'); process.exit(1); }, 15000);
"
```

## 10. Troubleshooting

| Symptom | Cause | Resolution |
|---|---|---|
| `ErrImagePull` on ORCE or simulation pod | Containerd does not trust the in-cluster registry | Re-apply the registry-config DaemonSet (Section 3.2) and verify with `kubectl -n orce rollout status daemonset/registry-config` |
| ORCE shows plain Node-RED (no branding) | `/data/` not seeded with ORCE files on first boot | Delete the PVC (`kubectl -n orce delete pvc orce-data`) and restart the pod to trigger the entrypoint bootstrap |
| `TypeError: Cannot read properties of undefined 'pause'` during build | `node-gyp` incompatibility with Node 20.19 | Ensure `RUN npm install -g npm@latest` is in the Dockerfile before any `npm install` |
| rdkafka producers show "disconnected" | Wrong broker DNS or mTLS cert issue | Verify broker address uses `-headless` service name; check that `kafka-certs` volume is mounted and contains `ca.crt`, `tls.crt`, `tls.key` |
| `ENOTFOUND kafka-broker-default-0.kafka-broker-default.stackable...` | Using non-headless service name | Change broker address to use `kafka-broker-default-headless` (with `-headless` suffix) |
| `require is not defined` in Node-RED function node | `require()` unavailable in function nodes | Use the `libs` array: `[{"var": "fs", "module": "fs"}]` and access the module directly |
| Flows disappear after ORCE pod restart | Flows were copied via `kubectl cp` and overwritten on shutdown | Import flows via the admin API (Section 6.2) instead of file copy |
| Kaniko build OOM killed | Insufficient memory for native compilation | Increase Kaniko job memory limits (4Gi request, 8Gi limit recommended) |
| `--exclude='orce'` excludes `src/api/orce/` | Unanchored tar exclude pattern | Use `--exclude='./orce'` (anchored to current directory) to exclude only the top-level `orce/` directory |
| `FileNotFoundError: docs/openapi.yaml` in simulation pod | `docs/` directory not copied in Dockerfile | Add `COPY docs/ ./docs/` to the simulation Dockerfile |
| PVC `storageClassName` immutable error on re-apply | Kubernetes does not allow changing PVC spec after creation | Non-blocking — the PVC already exists. Ignore the error or delete and recreate if the spec must change |

## 11. Key Files

| File | Purpose |
|---|---|
| `orce/Dockerfile` | Custom ORCE image: rdkafka + JSON Forms on Alpine |
| `orce/entrypoint.sh` | Runtime bootstrap: copies plugins, applies SSL patch, seeds /data |
| `orce/rdkafka-patch.js` | SSL/mTLS support for rdkafka broker config node |
| `orce/flows/facis-simulation-cluster.json` | ORCE flow: HTTP-in → validate → split → 9× rdkafka producers |
| `orce/flows/facis-simulation-controls.json` | ORCE flow: START/STOP/STATUS buttons via K8s API |
| `k8s/orce/orce-deployment.yaml` | ORCE K8s manifest (PVC, ConfigMaps, Deployment, Secret, Service) |
| `k8s/simulation/simulation-deployment.yaml` | Simulation K8s manifest (Deployment, Service, RBAC) |
| `Dockerfile` | Simulation service multi-stage Python image |
| `config/cluster.yaml` | Cluster config overlay: ORCE enabled, Kafka disabled, 60× speed |

---

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
Licensed under Apache License 2.0
