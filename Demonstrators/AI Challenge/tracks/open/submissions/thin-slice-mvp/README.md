# Thin Slice 4 - Open track

This slice uses a LangGraph `StateGraph` to run five role-specific agents. Each
agent calls deterministic data tools, dynamically retrieves relevant manual
chunks, and asks the shared `qwen3.5:9b` Ollama model for structured analysis,
evidence selection, and a recommendation. A policy gate validates or overrides
the recommendation. The trace exposes every tool call and retrieved chunk.
Optional OpenTelemetry instrumentation sends the same execution hierarchy to a
self-hosted Arize Phoenix UI.

## Setup and run

Start Ollama in one terminal:

```bash
~/Applications/Ollama.app/Contents/Resources/ollama serve
```

From the repository root in another terminal:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r "Demonstrators/AI Challenge/tracks/open/submissions/thin-slice-mvp/requirements.txt"
cd "Demonstrators/AI Challenge/tracks/open/submissions/thin-slice-mvp"
python app.py
```

For the observable demo, ensure Docker is running and use:

```bash
./start-demo.sh
```

Then open `http://localhost:6006`, send a request to the challenge endpoint,
and select the `facis-thin-slice-mvp` project. Each request contains nested
agent, tool, retrieval, Ollama, and policy-guard spans.

The endpoint is:

```text
POST http://localhost:8080/api/airbus-challenge/thin-slice-mvp/run
```

Test the reference case:

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"case_id":"CASE-2026-0002","seat_id":"D-AXFB-1K"}' \
  http://localhost:8080/api/airbus-challenge/thin-slice-mvp/run
```

## Verify

```bash
python -m unittest discover -s tests -v
python ../../../../checker/validate_contract.py result.json CASE-2026-0002
```

Set `OLLAMA_ENABLED=0` for a fast deterministic run. Optional configuration:
`OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT_SECONDS`, and
`OLLAMA_TOTAL_BUDGET_SECONDS`. Phoenix tracing is off by default; configure it
with `PHOENIX_ENABLED`, `PHOENIX_COLLECTOR_ENDPOINT`, and
`PHOENIX_PROJECT_NAME`.

## Implemented tools

- Case, BITE, telemetry and flight-phase correlation
- Historical NFF-rate calculation and policy application
- Ground-slot, stock, skills and certification planning
- Simulated task-card execution result
- Configurable labour, part, removal and shop-test economics
- Fault-specific handling for all five seeded cases and healthy seats
- Generated agent analysis with identifier, evidence and contradiction guards

## Remaining work

- Commit Thin Slice 4.
- Live-test all five cases, a healthy seat, malformed input, repeated-run consistency, and the 30-second limit.
- Submit the branch through a pull request.

## Thin Slice 4: observability UI

Use self-hosted Arize Phoenix with OpenTelemetry/OpenInference tracing. Represent
each HTTP request as one trace, the five agents as child spans, and retrieval,
tool, policy-guard, and Ollama calls as nested spans. The UI should expose inputs,
outputs, evidence, recommendations, overrides, errors, and latency while keeping
all challenge data local.
