# Thin Slice MVP - Open track

This submission is the first vertical slice: a local HTTP endpoint runs all five
ordered stages, shares typed state between them, returns the contract v1.1 shape,
and degrades safely for malformed or unknown cases.

It intentionally uses only the Python standard library so the walking skeleton
runs immediately. Each stage exposes a stable `run(state)` agent interface. In the
next slice, those stages can become LangGraph nodes backed by one shared LLM and
role-specific data tools.

## Run

From this directory:

```bash
python3 app.py
```

The endpoint is:

```text
POST http://localhost:8080/api/airbus-challenge/thin-slice-mvp/run
```

Example:

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"case_id":"CASE-2026-0002","seat_id":"D-AXFB-1K"}' \
  http://localhost:8080/api/airbus-challenge/thin-slice-mvp/run
```

Validate the live endpoint:

```bash
python3 ../../../../checker/validate_contract.py \
  http://localhost:8080/api/airbus-challenge/thin-slice-mvp/run \
  CASE-2026-0002 D-AXFB-1K
```

Run unit tests and validate the committed result:

```bash
python3 -m unittest discover -s tests -v
python3 ../../../../checker/validate_contract.py result.json CASE-2026-0002
```

## Current scope

- Real case lookup from `data/cases_seed.json`
- Five ordered agent boundaries and shared workflow state
- Contract-valid response and required integration flags
- Safe degraded response for malformed, mismatched, or unknown input
- Placeholder maintenance reasoning only

The `MONITOR` decision and subsequent outputs are safety-oriented placeholders,
not evidence-backed answers for known faulty cases. Thin Slice 2 will add the real
telemetry, BITE, manual, history, planning, and economics tools.
