#!/usr/bin/env bash

set -euo pipefail

#----------------------------------------
# Functions
#----------------------------------------
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1";
}

usage() {
    echo "Usage: $0 <kubeconfig> <path>";
    exit 1;
}

#----------------------------------------
# Input validation
#----------------------------------------
[ "$#" -ne 2 ] && usage
export KUBECONFIG="$1"
URL_PATH="$2"

# Check if kubeconfig file exists
if [[ ! -f "$KUBECONFIG" ]]; then
  log "❌ Kubeconfig file not found: $KUBECONFIG"
  exit 1
fi
log "✅ Kubeconfig loaded: $KUBECONFIG"

NAMESPACE="digital-contracting-service-${URL_PATH}"
RELEASE="digital-contracting-service"

#----------------------------------------
# Uninstall Helm chart
#----------------------------------------
log "ℹ️  Uninstalling Helm release '$RELEASE' from namespace '$NAMESPACE'..."

if helm --kubeconfig="$KUBECONFIG" ls -n "$NAMESPACE" | grep -q "^$RELEASE"; then
  helm uninstall "$RELEASE" \
    --namespace "$NAMESPACE" \
    --kubeconfig "$KUBECONFIG"
  log "✅ Helm release '$RELEASE' uninstalled"
else
  log "⚠️  Release '$RELEASE' not found in '$NAMESPACE'"
fi

#----------------------------------------
# Delete namespace
#----------------------------------------
log "ℹ️ Delete namespace '$NAMESPACE'..."

if kubectl get ns "$NAMESPACE" &>/dev/null; then
  kubectl delete ns "$NAMESPACE" --kubeconfig "$KUBECONFIG"
  log "✅ Namespace '$NAMESPACE' deleted"
else
  log "⚠️  Namespace '$NAMESPACE' not found"
fi

log "🎉 Uninstall complete!"
