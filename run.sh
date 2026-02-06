#!/bin/bash
# Wrapper script to prevent duplicate notepm-mcp-server containers.
# Stops any existing container with the same name before starting a new one.
#
# Usage:
#   ./run.sh [container-name]
#
# The container name defaults to "notepm-mcp-server".
# Environment variables NOTEPM_TEAM and NOTEPM_API_TOKEN must be set.

set -euo pipefail

CONTAINER_NAME="${1:-notepm-mcp-server}"
IMAGE="ghcr.io/dynamis-jp/notepm-mcp-server"

# Stop and remove existing container with the same name (if any)
if docker container inspect "$CONTAINER_NAME" &>/dev/null; then
  docker rm -f "$CONTAINER_NAME" &>/dev/null || true
fi

# Start the container with a fixed name, passing stdio through
exec docker run -i --rm \
  --name "$CONTAINER_NAME" \
  -e NOTEPM_TEAM \
  -e NOTEPM_API_TOKEN \
  "$IMAGE"
