# Thin Slice 2 - Open track

This slice uses a LangGraph `StateGraph` to run five role-specific agents. Each
agent receives authoritative facts from local Python data tools, then asks the
shared `qwen3.5:9b` Ollama model for a short structured rationale. Calculations
and safety decisions remain deterministic. If Ollama is unavailable, a circuit
breaker returns grounded fallback text and preserves the response contract.

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
`OLLAMA_BASE_URL`, `OLLAMA_MODEL`, and `OLLAMA_TIMEOUT_SECONDS`.

## Implemented tools

- Case, BITE, telemetry and flight-phase correlation
- Historical NFF-rate calculation and policy application
- Ground-slot, stock, skills and certification planning
- Simulated task-card execution result
- Configurable labour, part, removal and shop-test economics
