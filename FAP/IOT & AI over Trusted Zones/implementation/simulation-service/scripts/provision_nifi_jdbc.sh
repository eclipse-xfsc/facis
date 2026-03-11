#!/usr/bin/env bash
# =============================================================================
# provision_nifi_jdbc.sh — Automated Trino JDBC Driver Provisioning for NiFi
# =============================================================================
#
# Downloads the Trino JDBC driver and makes it available to NiFi pods in the
# Stackable K8s cluster. Supports two modes:
#
#   1. PVC mode (default): Creates a PVC + provisioner Job. Driver survives
#      pod restarts. Requires Stackable NiFiCluster podOverrides or manual
#      volume mount.
#
#   2. Direct mode (--direct): kubectl exec into each NiFi pod and downloads
#      the JAR to /opt/nifi/jdbc/. Simpler but ephemeral (lost on restart).
#
# Usage:
#   scripts/provision_nifi_jdbc.sh              # PVC mode
#   scripts/provision_nifi_jdbc.sh --direct     # Direct kubectl exec mode
#   scripts/provision_nifi_jdbc.sh --verify     # Check if JAR exists on NiFi pods
#
# Prerequisites:
#   - kubectl configured with cluster access
#   - Stackable namespace: stackable (override with NIFI_NAMESPACE)
# =============================================================================

set -euo pipefail

NAMESPACE="${NIFI_NAMESPACE:-stackable}"
DRIVER_VERSION="${TRINO_JDBC_VERSION:-467}"
DRIVER_URL="https://repo1.maven.org/maven2/io/trino/trino-jdbc/${DRIVER_VERSION}/trino-jdbc-${DRIVER_VERSION}.jar"
JDBC_PATH="/opt/nifi/jdbc"
K8S_DIR="$(cd "$(dirname "$0")/../k8s/nifi" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

log()   { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

get_nifi_pods() {
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=nifi \
        --field-selector=status.phase=Running \
        -o jsonpath='{.items[*].metadata.name}' 2>/dev/null
}

verify_jdbc() {
    log "Checking JDBC driver on NiFi pods in namespace '$NAMESPACE'..."
    local pods
    pods=$(get_nifi_pods)

    if [ -z "$pods" ]; then
        warn "No running NiFi pods found in namespace '$NAMESPACE'"
        return 1
    fi

    local ok=0 fail=0
    for pod in $pods; do
        if kubectl exec -n "$NAMESPACE" "$pod" -- test -f "${JDBC_PATH}/trino-jdbc-${DRIVER_VERSION}.jar" 2>/dev/null; then
            log "  ✓ $pod — JDBC driver present"
            ok=$((ok + 1))
        else
            warn "  ✗ $pod — JDBC driver MISSING"
            fail=$((fail + 1))
        fi
    done

    if [ "$fail" -eq 0 ]; then
        log "All $ok NiFi pods have the Trino JDBC driver."
        return 0
    else
        error "$fail/$((ok + fail)) NiFi pods are missing the JDBC driver."
        return 1
    fi
}

provision_direct() {
    log "Provisioning JDBC driver via direct kubectl exec..."
    local pods
    pods=$(get_nifi_pods)

    if [ -z "$pods" ]; then
        error "No running NiFi pods found in namespace '$NAMESPACE'"
        exit 1
    fi

    for pod in $pods; do
        log "  Installing on $pod..."
        kubectl exec -n "$NAMESPACE" "$pod" -- \
            sh -c "mkdir -p ${JDBC_PATH} && curl -fSL -o ${JDBC_PATH}/trino-jdbc-${DRIVER_VERSION}.jar ${DRIVER_URL}" \
            && log "  ✓ $pod done" \
            || { error "  ✗ $pod failed"; continue; }
    done

    verify_jdbc
}

provision_pvc() {
    log "Provisioning JDBC driver via PVC + Job..."

    # Step 1: Create PVC
    log "Creating PersistentVolumeClaim..."
    kubectl apply -f "${K8S_DIR}/nifi-jdbc-pvc.yaml"

    # Step 2: Delete previous job if exists (idempotent)
    kubectl delete job nifi-jdbc-provisioner -n "$NAMESPACE" --ignore-not-found=true 2>/dev/null

    # Step 3: Run provisioner job
    log "Running provisioner job..."
    kubectl apply -f "${K8S_DIR}/nifi-jdbc-provisioner.yaml"

    # Step 4: Wait for completion
    log "Waiting for job to complete (timeout: 120s)..."
    if kubectl wait --for=condition=complete job/nifi-jdbc-provisioner -n "$NAMESPACE" --timeout=120s; then
        log "✓ JDBC driver provisioned to PVC successfully."
        echo ""
        log "Next steps:"
        log "  1. Patch the NiFi cluster to mount the PVC (see k8s/nifi/nifi-jdbc-volume-patch.yaml)"
        log "  2. Run: python scripts/setup_nifi.py --env-file .env.cluster"
    else
        error "Provisioner job did not complete within 120s."
        kubectl logs -n "$NAMESPACE" job/nifi-jdbc-provisioner --tail=20
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

case "${1:-pvc}" in
    --direct|-d)
        provision_direct
        ;;
    --verify|-v)
        verify_jdbc
        ;;
    --help|-h)
        echo "Usage: $0 [--direct|--verify|--help]"
        echo ""
        echo "Modes:"
        echo "  (default)   PVC mode — persistent storage via K8s Job"
        echo "  --direct    kubectl exec mode — downloads to each pod (ephemeral)"
        echo "  --verify    Check if JDBC driver exists on NiFi pods"
        echo ""
        echo "Environment:"
        echo "  NIFI_NAMESPACE      K8s namespace (default: stackable)"
        echo "  TRINO_JDBC_VERSION  Driver version (default: 467)"
        ;;
    *)
        provision_pvc
        ;;
esac
