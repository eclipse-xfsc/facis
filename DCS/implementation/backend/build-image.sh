#!/bin/bash

# Parameters
# $1 - Optional tag for the Docker image (default: latest)

# Environment
# DOCKER_REGISTRY - Optional Docker registry URL
# DOCKER_REPO - Optional Docker repository name

set -euo pipefail

# Set defaults if arguments not provided
TAG=${1:-latest}

# Set registry and repo from environment variables if available
REGISTRY=${DOCKER_REGISTRY:-}
REPO=${DOCKER_REPO:-}

IMAGE_NAME="digital-contracting-service:$TAG"

if [[ -n "$REGISTRY" && -n "$REPO" ]]; then
  IMAGE_NAME="$REGISTRY/$REPO/digital-contracting-service:$TAG"
fi

echo "Building $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" .

if [[ -n "$REGISTRY" && -n "$REPO" ]]; then
  echo "Tagging as latest..."
  docker tag "$IMAGE_NAME" "$REGISTRY/$REPO/digital-contracting-service:latest"
  
  echo "Pushing to $REGISTRY..."
  docker push "$IMAGE_NAME"
  docker push "$REGISTRY/$REPO/digital-contracting-service:latest"
else
  echo "Skipping push (REGISTRY and REPO aren't set)"
fi