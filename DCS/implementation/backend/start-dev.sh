#!/bin/bash

# Parameters
# $1 - Optional force build flag (default: false)
# $2 - Optional port for the container (default: 8991)
# $3 - Optional tag for the Docker image (default: latest)

# Environment
# DOCKER_REGISTRY - Optional Docker registry URL
# DOCKER_REPO - Optional Docker repository name

set -euo pipefail

# Set defaults if arguments not provided
FORCE_BUILD=${1:-"false"}
PORT=${2:-8991}
TAG=${3:-latest}

# Set registry and repo from environment variables if available
REGISTRY=${DOCKER_REGISTRY:-}
REPO=${DOCKER_REPO:-}

# Validate PORT is a number
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "Error: PORT must be a number (got: $PORT)"
  exit 1
fi

IMAGE_NAME="digital-contract-service:$TAG"

if [[ -n "$REGISTRY" && -n "$REPO" ]]; then
  IMAGE_NAME="$REGISTRY/$REPO/digital-contract-service:$TAG"
fi

echo "Using PORT=$PORT, IMAGE=$IMAGE_NAME and TAG=$TAG"

if ! docker image inspect "$IMAGE_NAME" &>/dev/null; then
  echo "Image not found, building $IMAGE_NAME..."
  ./build-image.sh "$TAG"
else
  echo "Image $IMAGE_NAME already exists, skipping build"

  if [[ "$FORCE_BUILD" == "true" ]]; then
    echo "Force build enabled, rebuilding $IMAGE_NAME..."
    ./build-image.sh "$TAG"
  fi

fi

echo "Starting $IMAGE_NAME container on port $PORT..."
docker run --rm -p $PORT:8991 --name digital-contract-service "$IMAGE_NAME"