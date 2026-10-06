#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

repo_python="$(pwd)/../../../../../../.venv/bin/python"
if [[ -n "${PYTHON_BIN:-}" ]]; then
  python_bin="$PYTHON_BIN"
elif [[ -x "$repo_python" ]]; then
  python_bin="$repo_python"
else
  python_bin=python3
fi
demo_port="${PORT:-8080}"

docker compose -f docker-compose.phoenix.yml up -d

for attempt in {1..30}; do
  if curl --fail --silent http://127.0.0.1:6006/ >/dev/null; then
    break
  fi
  if [[ "$attempt" == "30" ]]; then
    echo "Phoenix did not become ready on http://localhost:6006"
    exit 1
  fi
  sleep 1
done

export PHOENIX_ENABLED=1
export PHOENIX_COLLECTOR_ENDPOINT=http://127.0.0.1:6006/v1/traces
export PHOENIX_PROJECT_NAME=facis-thin-slice-mvp
export PORT="$demo_port"

echo "Phoenix UI: http://localhost:6006"
echo "Challenge endpoint: http://localhost:${demo_port}/api/airbus-challenge/thin-slice-mvp/run"
if ! curl --fail --silent http://127.0.0.1:11434/api/tags >/dev/null; then
  echo "Warning: Ollama is unavailable; deterministic fallback reasoning will be used."
fi
exec "$python_bin" app.py
