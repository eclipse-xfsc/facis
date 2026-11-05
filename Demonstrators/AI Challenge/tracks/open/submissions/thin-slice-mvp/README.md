# Thin Slice MVP - Open track

This submission implements the complete five-stage challenge workflow with
LangGraph, a local Ollama model, deterministic data tools and policy guardrails.
Optional OpenTelemetry tracing exposes each request, agent and tool call in a
self-hosted Arize Phoenix UI.

All commands below run from the repository root.

## Prerequisites and binary installation

The tested setup is macOS with Python 3.9+, Docker Desktop and Ollama.

### 1. Python

Verify Python and `venv`:

```bash
python3 --version
python3 -m venv --help >/dev/null
```

If Python is unavailable, install Python 3 from
<https://www.python.org/downloads/macos/>.

### 2. Docker Desktop

Install Docker Desktop using
<https://docs.docker.com/desktop/setup/install/mac-install/>, launch it, then
verify the daemon:

```bash
docker --version
docker info >/dev/null
docker compose version
```

Docker runs the local Phoenix UI. No Phoenix Python server installation is
required.

### 3. Ollama and the model

Install Ollama from <https://ollama.com/download>, launch the application, then
verify the local API:

```bash
ollama --version
curl --fail http://localhost:11434/api/tags
```

Download the model only when it is not already listed:

```bash
ollama list
ollama pull qwen3.5:9b
```

If the desktop application is not running the server, start it manually in a
separate terminal:

```bash
ollama serve
```

## Python environment

Create the root virtual environment once and install the pinned dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r \
  "Demonstrators/AI Challenge/tracks/open/submissions/thin-slice-mvp/requirements.txt"
```

Re-running the `pip install` command is safe when `.venv` already exists.

## Start the complete setup

Ensure Docker and Ollama are running, then execute:

```bash
PORT=8080 \
  "./Demonstrators/AI Challenge/tracks/open/submissions/thin-slice-mvp/start-demo.sh"
```

This starts Phoenix and runs the challenge endpoint in the foreground:

- Endpoint: `http://localhost:8080/api/airbus-challenge/thin-slice-mvp/run`
- Phoenix: <http://localhost:6006>

If port 8080 is occupied, use another port consistently, for example:

```bash
PORT=8091 \
  "./Demonstrators/AI Challenge/tracks/open/submissions/thin-slice-mvp/start-demo.sh"
```

## Send a request

From a second root terminal:

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"case_id":"CASE-2026-0002","seat_id":"D-AXFB-1K"}' \
  http://localhost:8080/api/airbus-challenge/thin-slice-mvp/run
```

Use the selected alternate port in this and subsequent commands when needed.

## Validate

Run the 13 fast regression tests. These cover all five seeded faults, a healthy
seat, malformed requests, fallback behavior, guardrails and tracing:

```bash
OLLAMA_ENABLED=0 .venv/bin/python -m unittest discover \
  -s "Demonstrators/AI Challenge/tracks/open/submissions/thin-slice-mvp/tests" \
  -v
```

Validate the committed reference result:

```bash
.venv/bin/python "Demonstrators/AI Challenge/checker/validate_contract.py" \
  "Demonstrators/AI Challenge/tracks/open/submissions/thin-slice-mvp/result.json" \
  CASE-2026-0002
```

Validate the live endpoint:

```bash
.venv/bin/python "Demonstrators/AI Challenge/checker/validate_contract.py" \
  http://localhost:8080/api/airbus-challenge/thin-slice-mvp/run \
  CASE-2026-0002 D-AXFB-1K
```

Expected validator output starts with `VALID`.

Healthy-seat validation:

```bash
.venv/bin/python "Demonstrators/AI Challenge/checker/validate_contract.py" \
  http://localhost:8080/api/airbus-challenge/thin-slice-mvp/run \
  CASE-2026-0002 D-AXFB-1A
```

The healthy result should contain `MONITOR`, task `NONE`, and outcome
`NO_ACTION`.

## Monitor in Phoenix

1. Open <http://localhost:6006>.
2. Select project `facis-thin-slice-mvp`.
3. Open the latest `facis.workflow.request` trace.
4. Expand the five `agent.*` spans.
5. Inspect the nested tool, `manual_retriever.search`, `ollama.analyze`, and
   `policy_guard.validate` spans.

A reference request produces 32 spans. The endpoint response also contains
`observability.trace_id`, which identifies the corresponding Phoenix trace.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `8080` | Challenge HTTP port |
| `OLLAMA_ENABLED` | `1` | Set to `0` for deterministic fallback reasoning |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama API |
| `OLLAMA_MODEL` | `qwen3.5:9b` | Local model |
| `OLLAMA_TIMEOUT_SECONDS` | `8` | Maximum individual model-call time |
| `OLLAMA_TOTAL_BUDGET_SECONDS` | `25` | Model budget for the complete workflow |
| `PHOENIX_ENABLED` | `0` | `start-demo.sh` enables it automatically |
| `PHOENIX_COLLECTOR_ENDPOINT` | `http://127.0.0.1:6006/v1/traces` | Trace collector |

## Stop and clean up

Press `Ctrl-C` in the `start-demo.sh` terminal to stop the challenge endpoint.
The Phoenix container continues running so its traces remain available.

Stop Phoenix while preserving its trace volume:

```bash
docker compose \
  -f "Demonstrators/AI Challenge/tracks/open/submissions/thin-slice-mvp/docker-compose.phoenix.yml" \
  down
```

Stop a manually started Ollama server with `Ctrl-C`, or quit the Ollama desktop
application.

For a full cleanup, the following commands delete local generated state. They
do not delete project source files:

```bash
# Deletes Phoenix containers and stored trace history.
docker compose \
  -f "Demonstrators/AI Challenge/tracks/open/submissions/thin-slice-mvp/docker-compose.phoenix.yml" \
  down -v

# Deletes the downloaded model; omit this when other projects use it.
ollama rm qwen3.5:9b

# Deletes the disposable Python environment; run only from the repository root.
rm -rf .venv
```

The environment can be recreated using the installation steps above.

## Troubleshooting

- **Empty Phoenix project:** start through `start-demo.sh`, send one request and
  refresh Phoenix.
- **Ollama unavailable:** check `curl http://localhost:11434/api/tags`. The flow
  will still complete using deterministic fallback reasoning.
- **Model missing:** run `ollama list`, then pull `qwen3.5:9b` only if absent.
- **Port already used:** select another `PORT` and use it in validator URLs.
- **Fast non-LLM demo:** prefix the launcher with `OLLAMA_ENABLED=0`.

## Implementation map

| File | Responsibility |
|---|---|
| `app.py` | HTTP endpoint and last-resort degraded response |
| `workflow.py` | Five LangGraph agents and response assembly |
| `challenge_tools.py` | Data access and deterministic maintenance logic |
| `llm.py` | Structured Ollama analysis and validation |
| `observability.py` | OpenTelemetry/Phoenix tracing |
| `tests/test_workflow.py` | Regression suite |
| `result.json` | Real reference-case output |

## Potential improvements

| Priority | Improvement | Why |
|---|---|---|
| Next | Evaluation harness | The checker validates response shape, not diagnosis or evidence quality |
| Next | Live case-matrix runner | Re-check every case, healthy seat, malformed input, repeatability and latency with one command |
| Next | CI validation | Run deterministic tests and the saved-result checker on every change |
| Later | Persistent outcome store | Make the learning stage influence future runs using verified execution data |
| Later | Human approval path | Resolve plans blocked by missing approved task information |
| Conditional | Embedding retrieval | Consider only if the manual corpus grows beyond effective lexical search |
| Production only | Authentication and certified integrations | Not required for this local synthetic challenge |

Evaluation should begin with deterministic metrics:

- decision and plan invariants for all seeded cases and healthy seats;
- retrieval recall using `data/rag_eval_questions.json`;
- evidence identifiers that resolve to supplied artifacts;
- repeated-run decision consistency;
- per-stage and end-to-end latency;
- deterministic-fallback and guardrail-override rates.

Do not claim decision accuracy against a complete ground truth until the
organizers release it. A vector database or custom animated UI is also not
automatically an improvement for this small corpus; add either only when a
measured limitation justifies the extra moving parts.
