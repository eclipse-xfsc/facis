#!/usr/bin/env bash
set -euo pipefail

#----------------------------------------
# Functions
#----------------------------------------
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

usage() {
  echo "Usage: $0 <kubeconfig> <private_key_path> <crt_path> <domain> <path> <keycloak_url> <realm> <admin_user> <admin_pass> <new_user> <new_pass> <client_role>"
  exit 1
}

#----------------------------------------
# Input validation
#----------------------------------------
[ "$#" -ne 12 ] && usage
export KUBECONFIG="$1"
KEY_FILE="$2"
CRT_FILE="$3"
DOMAIN="$4"
URL_PATH="$5"
KEYCLOAK_URL="$6"
REALM="$7"
ADMIN_USER="$8"
ADMIN_PASS="$9"
NEW_USER="${10}"
NEW_PASS="${11}"
CLIENT_ROLE="${12}"

# Check if kubeconfig file exists
if [[ ! -f "$KUBECONFIG" ]]; then
  log "❌ Kubeconfig file not found: $KUBECONFIG"
  exit 1
fi


#----------------------------------------
# Cleanup local helm artifacts
#----------------------------------------
if [ -f Chart.lock ]; then
  rm Chart.lock
  log "✅ Removed Chart.lock"
fi

if [ -d charts ]; then
  rm -rf charts
  log "✅ Removed charts/ directory"
fi

#----------------------------------------
# Check dependencies
#----------------------------------------
for cmd in kubectl helm jq curl sed trap; do
  if ! command -v "$cmd" &>/dev/null; then
    log "❌ '$cmd' is not installed. Please install it and retry."
    exit 1
  else
    log "✅ Found '$cmd'"
  fi
done

#----------------------------------------
# Verify ingress class traefik is installed
#----------------------------------------
log "ℹ Checking for ingressClass traefik..."
if ! kubectl get ingressclass traefik &>/dev/null; then
  log "❌ Ingress class traefik not found"
  exit 1
else
    log "✅ Ingress class traefik found"
fi

#----------------------------------------
# Wait for ingress External-IP
#----------------------------------------
log "ℹ️ Waiting for ingress-nginx External-IP..."
while true; do
  EX_IP=$(kubectl get svc traefik -n kube-system \
    -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
  if [[ -n "$EX_IP" && "$EX_IP" != "<pending>" ]]; then
    log "✅ ingress External-IP: $EX_IP"
    break
  fi
  log "⏳ External-IP pending, retrying in 5s..."
  sleep 5
done

#----------------------------------------
# Generate and validate namespace from path
#----------------------------------------
NAMESPACE="digital-contracting-service-${URL_PATH}"
log "ℹ️ Using namespace: $NAMESPACE"

if kubectl get ns "$NAMESPACE" &>/dev/null; then
  log "⚠ Namespace '$NAMESPACE' already exists. Showing existing deployment info and exiting."

  # 1. External‐IP
  EX_IP=$(kubectl get svc traefik -n kube-system \
    -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
  echo "🔹 ingress External-IP: $EX_IP"

  # 2. URLs
  echo "🔹 DCS URL:             https://${DOMAIN}/${URL_PATH}"

  # 3. Try to get client secret from Keycloak (if permissions allow)
  TOKEN_URL="${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token"
  ACCESS_TOKEN=$(curl -k -s \
    -X POST "$TOKEN_URL" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "client_id=admin-cli" \
    -d "username=${ADMIN_USER}" \
    -d "password=${ADMIN_PASS}" \
    -d "grant_type=password" | jq -r .access_token)

  REALM_API="${KEYCLOAK_URL}/admin/realms/${REALM}"
  CLIENT_RESPONSE=$(curl -k -s \
    -X GET "${REALM_API}/clients?clientId=digital-contracting-service" \
    -H "Authorization: Bearer $ACCESS_TOKEN")
  
  if echo "$CLIENT_RESPONSE" | grep -q "error"; then
    log "⚠ Cannot retrieve client details (Keycloak Admin API not accessible with current credentials)"
    log "ℹ️ To fix: Ensure 'admin-cli' client has realm-admin role in Keycloak"
    exit 0
  fi
  
  if ! echo "$CLIENT_RESPONSE" | jq -e 'length > 0' > /dev/null 2>&1; then
    log "⚠ Client 'digital-contracting-service' not found in realm '$REALM' (may not be created yet)"
    exit 0
  fi

  CLIENT_ID=$(echo "$CLIENT_RESPONSE" | jq -r '.[0].id')
  EXISTING_SECRET=$(curl -k -s \
    -X GET "${REALM_API}/clients/${CLIENT_ID}/client-secret" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | jq -r '.value' | xargs)

  echo "🔹 Client Secret:       $EXISTING_SECRET"

  exit 0
fi

#----------------------------------------
# Prepare temporary values file
#----------------------------------------
TMP_VALUES="$(mktemp -t values.XXXXXX.yaml)" || TMP_VALUES="/tmp/values-$$.yaml"
cp values.yaml "$TMP_VALUES"

cp values.yaml "$TMP_VALUES"
log "ℹ️ Replacing placeholders in $TMP_VALUES"
sed -i \
  -e "s|\[domain-name\]|${DOMAIN}|g" \
  -e "s|\[path\]|${URL_PATH}|g" \
  -e "s|\[namespace\]|${NAMESPACE}|g" \
  -e "s|\[Admin_Username\]|${ADMIN_USER}|g" \
  -e "s|\[Admin_Password\]|${ADMIN_PASS}|g" \
  "$TMP_VALUES"
log "✅ Placeholders replaced in $TMP_VALUES"

#----------------------------------------
# Helm dependency build & install
#----------------------------------------

log "ℹ️ Running: helm dependency build"
helm dependency build . --kubeconfig "$KUBECONFIG"

log "ℹ️ Installing digital-contracting-service via Helm"
helm install digital-contracting-service . \
  --namespace "$NAMESPACE" \
  --create-namespace \
  --kubeconfig "$KUBECONFIG" \
  -f "$TMP_VALUES"
log "✅ digital-contracting-service Helm release deployed"

#----------------------------------------
# Create TLS secret
#----------------------------------------
log "ℹ️ Creating TLS secret 'certificates'"
kubectl create secret tls certificates \
  --namespace "$NAMESPACE" \
  --key "$KEY_FILE" \
  --cert "$CRT_FILE" \
  --kubeconfig "$KUBECONFIG"
log "✅ TLS secret created"

#----------------------------------------
# Keycloak API: Check if realm is ready
#----------------------------------------
if ! curl -k -s -o /dev/null -w "%{http_code}" "${KEYCLOAK_URL}/realms/${REALM}" | grep -q '^200$'; then
  log "❌ ${REALM} realm is not ready in Keycloak..."
  exit 1
fi
log "✅ ${REALM} realm is ready in Keycloak"

#----------------------------------------
# Keycloak API: client ID & secret
#----------------------------------------
TOKEN_URL="${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token"
ACCESS_TOKEN=$(curl -k -s \
  -X POST "$TOKEN_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=admin-cli" \
  -d "username=${ADMIN_USER}" \
  -d "password=${ADMIN_PASS}" \
  -d "grant_type=password" | jq -r .access_token)

REALM_API="${KEYCLOAK_URL}/admin/realms/${REALM}"
CLIENT_RESPONSE=$(curl -k -s -X GET \
  "${REALM_API}/clients?clientId=digital-contracting-service" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

# Check for errors in response
if echo "$CLIENT_RESPONSE" | grep -q "error"; then
  log "❌ Keycloak API Error: $CLIENT_RESPONSE"
  log "ℹ️ Ensure the 'admin-cli' client has proper admin roles in Keycloak"
  exit 1
fi

if ! echo "$CLIENT_RESPONSE" | jq -e 'length > 0' > /dev/null 2>&1; then
  log "❌ Client 'digital-contracting-service' not found in realm '$REALM'"
  exit 1
fi

CLIENT_ID=$(echo "$CLIENT_RESPONSE" | jq -r '.[0].id')
NEW_SECRET=$(curl -k -s -X POST \
  "${REALM_API}/clients/${CLIENT_ID}/client-secret" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq -r '.value' | xargs)
log "✅ New client secret generated"

#----------------------------------------
# Keycloak API: create user & assign role
#----------------------------------------
CREATE_STATUS=$(curl -k -s -o /dev/null -w "%{http_code}" -X POST \
  "${REALM_API}/users" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
        \"username\":\"${NEW_USER}\",
        \"enabled\":true,
        \"credentials\":[{\"type\":\"password\",\"value\":\"${NEW_PASS}\",\"temporary\":false}]
     }")
if [[ "$CREATE_STATUS" != "201" ]]; then
  log "❌ User creation failed (HTTP $CREATE_STATUS)"; exit 1
else
  log "✅ User '${NEW_USER}' created"
fi

USER_ID=$(curl -k -s -X GET \
  "${REALM_API}/users?username=${NEW_USER}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq -r '.[0].id')

if [[ -z "$USER_ID" || "$USER_ID" == "null" ]]; then
  log "❌ User '${NEW_USER}' not found"; exit 1
fi
log "ℹ️ User ID: $USER_ID"

ROLE_ID=$(curl -k -s -X GET \
  "${REALM_API}/clients/${CLIENT_ID}/roles" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq -r ".[]|select(.name==\"${CLIENT_ROLE}\")|.id")

log "ℹ️ Role ID: $ROLE_ID"

# Check if role exists
if [[ -z "$ROLE_ID" || "$ROLE_ID" == "null" ]]; then
  log "❌ Role '${CLIENT_ROLE}' not found in client"
  log "ℹ️ Available roles:"
  curl -k -s -X GET \
    "${REALM_API}/clients/${CLIENT_ID}/roles" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | jq -r '.[] | "\(.name) (ID: \(.id))"'
  exit 1
fi

# Assign role to user
ASSIGN_STATUS=$(curl -k -s -o /dev/null -w "%{http_code}" -X POST \
  "${REALM_API}/users/${USER_ID}/role-mappings/clients/${CLIENT_ID}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "[{\"id\":\"${ROLE_ID}\",\"name\":\"${CLIENT_ROLE}\"}]")

if [[ "$ASSIGN_STATUS" == "204" ]]; then
  log "✅ Role '${CLIENT_ROLE}' assigned to '${NEW_USER}'"
else
  log "❌ Failed to assign role (HTTP $ASSIGN_STATUS)"; exit 1
fi


#----------------------------------------
# Wait for digital-contracting-service Deployment to be ready (max 5m)
#----------------------------------------
log "ℹ️ Waiting for digital-contracting-service deployment to be ready (max 2m)..."
if ! kubectl rollout status deployment/digital-contracting-service \
     -n "$NAMESPACE" \
     --timeout=300s \
     --kubeconfig "$KUBECONFIG"; then
  log "❌ Timeout waiting for digital-contracting-service. Pod statuses:"
  kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=digital-contracting-service -o wide
  exit 1
fi
log "✅ digital-contracting-service deployment is ready"

#----------------------------------------
# Final output
#----------------------------------------
log "🎉 All operations completed successfully!"
echo
echo "🔹 ingress External-IP: ${EX_IP}"
echo "🔹 DCS URL:             https://${DOMAIN}/${URL_PATH}"
echo "🔹 Client Secret:       ${NEW_SECRET}"
