# NiFi Kubernetes Resources

Supplementary K8s manifests for the Stackable-managed NiFi cluster.

NiFi itself is deployed and managed by the **Stackable NiFi Operator**. These manifests handle FACIS-specific provisioning that the operator does not cover, namely the Trino JDBC driver required by the Kafka → Bronze ingestion pipeline.

## Files

| File | Purpose |
|---|---|
| `nifi-jdbc-provisioner.yaml` | Job that downloads the Trino JDBC driver and stores it in a PVC |
| `nifi-jdbc-pvc.yaml` | PersistentVolumeClaim for the JDBC driver (survives pod restarts) |
| `nifi-jdbc-volume-patch.yaml` | Stackable NiFi cluster patch to mount the PVC into NiFi pods |

## Usage

```bash
# 1. Create the PVC for JDBC driver storage
kubectl apply -f k8s/nifi/nifi-jdbc-pvc.yaml

# 2. Run the provisioner job (downloads trino-jdbc-467.jar)
kubectl apply -f k8s/nifi/nifi-jdbc-provisioner.yaml

# 3. Wait for completion
kubectl wait --for=condition=complete job/nifi-jdbc-provisioner -n stackable --timeout=120s

# 4. Patch the Stackable NiFi cluster to mount the JDBC volume
#    (See nifi-jdbc-volume-patch.yaml for instructions)

# 5. Configure the ingestion pipeline
python scripts/setup_nifi.py --env-file .env.cluster
```

## Automated Alternative

Use the provisioning script for a single-command setup:

```bash
scripts/provision_nifi_jdbc.sh
```
