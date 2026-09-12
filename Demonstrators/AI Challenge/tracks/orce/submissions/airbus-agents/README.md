# airbus-agents — ORCE flow submission

Five-agent maintenance-triage pipeline (Diagnose → Judge/NFF → Plan → Execute → Learn),
ported from a Python reference implementation into a single Node-RED flow tab that runs
entirely inside the ORCE container: no Qdrant, no Python, no external services besides a
local Ollama for the LLM calls. Rules, thresholds and guards are embedded at build time
from `rules.yaml`; the closed loop (lessons feeding back into the next run's NFF risk) is
kept in Node-RED's global context.

## Architecture

```
                         POST /api/airbus-challenge/airbus-agents/run
                                          |
                                     [ http in ]
                                          |
                                    [ context ]  <- dossier, busy lock, model pick,
                                          |          deadline (26s) / wall (27.5s)
                                    [ Diagnosis ]        (agent 1)
                                          |
                                    [ NFF ]               (agent 2 — Judge / no-fault-found)
                                          |
                                    [ Plan ]              (agent 3)
                                          |
                                    [ Execution ]         (agent 4)
                                          |
                                    [ Learning ]          (agent 5 — writes lessons store)
                                          |
                                    [ assemble ]  -> [ http response ]
                                          |
                                     [ debug ]   (disabled sidebar node, wired
                                                   unconditionally; unrelated to
                                                   x-debug:1, which only adds a
                                                   `debug` key to the JSON body)

  catch (any node throws) -> [ degraded ] -> [ http response ]

  GET /api/airbus-challenge/airbus-agents/health -> [ health ] -> [ http response ]

  bootstrap inject (fires once at Deploy) -> [ bootstrap ] builds the in-memory tables
```

Each of the five agent nodes: builds its prompt from the shared dossier, calls Ollama
`/api/chat` (temperature 0, JSON-schema answer, at most one tool round, the same six
tools as the Python pipeline), runs a JS guard against the answer, retries with feedback
while the per-stage time budget allows (cap 3 retries), and falls back to the
deterministic computed output if the model or the guard doesn't cooperate in time. The
response's `trace[]` records `fallback`/`retries` per stage so a reviewer can see exactly
which stages were model-owned.

## Prerequisites

- Docker.
- Ollama running on the host with the model pulled: `ollama pull qwen2.5:3b-instruct`.
- This repo checked out, for the dataset under `Demonstrators/AI Challenge/data/`.

## Setup

All commands below are given with the directory they must be run from — copy them as
written and they work.

1. Start ORCE. Run from anywhere (this names the container `xfsc-orce`, matching step 2):
   ```bash
   docker run -d --name xfsc-orce \
     --platform linux/amd64 \
     -p 1880:1880 \
     -v orce_data:/data \
     --restart unless-stopped \
     ecofacis/xfsc-orce:2.0.13
   ```
   (image, platform, port and volume mirror `tracks/orce/docker-compose.yml`.)

   Alternative — `docker compose`, run from `Demonstrators/AI Challenge/tracks/orce/`:
   ```bash
   docker compose up -d
   ```
   This does **not** create a container named `xfsc-orce` — the default compose project
   name is `orce`, so the container is `orce-orce-1`. Substitute it in step 2, run from
   the same `tracks/orce/` directory:
   ```bash
   docker cp "../../data/." "$(docker compose ps -q orce)":/data/challenge/
   ```

2. Copy the dataset into the container so it lands at `/data/challenge/cases_seed.json`
   directly (note the trailing `/.` on the source and `/` on the destination). Run from
   `Demonstrators/AI Challenge/`:
   ```bash
   docker cp "./data/." xfsc-orce:/data/challenge/
   ```
   On the `docker compose` path, substitute the container name here too — the command
   already shown in step 1's alternative (`"$(docker compose ps -q orce)"` in place of
   `xfsc-orce`).

3. Open the ORCE editor at <http://localhost:1880> and sign in with the credentials from
   the top-level `Demonstrators/AI Challenge/README.md` (not repeated here). Then menu ≡
   → **Import** → select this folder's `flow.json` → Import → **Deploy** (top right). The
   bootstrap `inject` node fires once on Deploy and builds the in-memory lookup tables
   from `/data/challenge/*`; the health route reports `ready: true` once that has run.

   Alternative for scripted setups (not part of this submission, mentioned for
   completeness): the same flow JSON can be pushed with a plain `POST /flows` against the
   stock Node-RED admin API, header `Node-RED-Deployment-Type: full`.

4. Health check. Run from anywhere:
   ```bash
   curl -s http://localhost:1880/api/airbus-challenge/airbus-agents/health
   # {"ready":true,"version":"0.1","seats":48,"lessons":<n>}
   ```

## Endpoint

```
POST /api/airbus-challenge/airbus-agents/run
Content-Type: application/json
Body: {"case_id": "CASE-2026-0002"}   (empty body defaults to CASE-2026-0002)
```

Headers:
- `x-model: off` — deterministic mode, no LLM calls, guard-clean computed outputs only.
- `x-model: <name>` — use a different Ollama model for this request.
- `x-debug: 1` — also returns `debug.answers` / `debug.timings` / `debug.violations` (the
  raw model answers and per-call timings behind each stage); the plain contract document
  is unchanged without it.

Example:
```bash
curl -s -X POST http://localhost:1880/api/airbus-challenge/airbus-agents/run \
  -H 'content-type: application/json' \
  -d '{"case_id":"CASE-2026-0002"}'
```
returns a JSON document with `team_id`, `run_id`, `degraded`, `degraded_reasons`,
`timing_ms`, `trace` (5 ordered stage entries) and `final_submission` — see
`result.json` in this folder for a full real response.

## How the numbers are derived

Everything is computed in-flow, in JavaScript, from `/data/challenge/*` at bootstrap
time and per request — no Python, no external database at run time:

- per-leg statistics (means, maxima), rising-run trend detection with a per-signal
  minimum rise, breaches against the AMM limits, NFF history/rates, the "healthy seat"
  definition;
- repair-plan candidates (task-card matching, `opened_at` semantics, ground time ≥ task
  time + 30 min, capability/stock/crew-shift-overlap checks including certifier-before-
  departure), and the cost model;
- manual retrieval is a keyword BM25-lite scan over `rag_chunks.jsonl`, done in-flow —
  Qdrant is not used and is not required.

Rules, MEL items, task-card definitions and policy come from `rules.yaml`, embedded into
the flow at build time with their document ids, so the guards enforce the same truth
tables as the Python reference implementation.

## Results (model mode, `qwen2.5:3b-instruct`, 3 runs of 7 references + 2 traps)

| criterion | required | run 1 | run 2 | run 3 |
|---|---|---|---|---|
| checker VALID (7 references) | 7/7 each run | 7/7 | 7/7 | 7/7 |
| AI-owned stages (references, 35 = 7×5) | ≥ 30/35 | 30/35 | 30/35 | 31/35 |
| decisions vs. the expectation table | — | 9/9 | 9/9 | 9/9 |
| p95 seconds | < 30 s | 27.1 | 26.4 | 27.7 |
| median seconds | — | 26.0 | 24.4 | 24.9 |
| key fields identical across the 3 runs | all 9 requests | PASS | PASS | PASS |

Full per-request breakdown and the reasoning behind every divergence from the Python
pipeline: `airbus-agents/specs/003-orce-flow/acceptance.md` in the team repo.

The `result.json` in this folder is one additional real run of `CASE-2026-0002` against
the production container, all 5 stages model-owned (`fallback: false` throughout),
0 retries beyond 1 on `repair_plan`, 22.7 s total — checker VALID.

## Limitations

- Syntactically invalid JSON in the request body is rejected by Node-RED's own body
  parser with an HTTP 400 before the flow ever runs — the flow's own error handling
  (`catch` → degraded response) only sees errors raised after the body has parsed.
- The internal wall-clock budget is 26 s to start a stage / 27.5 s hard socket cut-off,
  chosen to stay under the organisers' 30 s contract limit. That margin is thin on a busy
  host: run the demo on a machine that won't sleep or throttle, and confirm
  `curl -s localhost:11434/api/ps` shows `qwen2.5:3b-instruct` alone and idle before each
  request.
- Concurrent requests are serialized by a single-run busy lock (`global` context,
  `seatlab.busy`); a second request arriving while one is in flight gets a deterministic
  "busy" response rather than running concurrently.
- The lessons store (`global` context, capped at 200 entries) accumulates across runs and
  is not reset by a redeploy (only by restarting the container). This can legitimately
  shift the NFF risk score and, in rare cases, the decision for borderline seats — see
  "Lessons drift" in `acceptance.md`.
- The model must be pulled locally (`ollama pull qwen2.5:3b-instruct`) and reachable from
  the container at `http://host.docker.internal:11434`.
- The Node-RED function-node sandbox has no `fetch`/`URL`/`process`; the flow uses the
  built-in `http` module for the Ollama calls instead.
- `x-debug-throw: 1` forces a mid-flow exception on purpose (it exercises the `catch` →
  degraded path; the response is still a valid degraded document). It is a test hook, not
  for production.

## Switching the model

Either set it once for all requests via the flow's `MODEL` context variable in the ORCE
editor, or override per request with the `x-model` header (`off` for deterministic mode,
or any other Ollama model name pulled on the host).

## Source

Build script, JS sources, unit tests and the full acceptance record live in the team
repository, `orce/` folder (`orce/build.py` generates this `flow.json` from
`orce/src/*.js` + `rules.yaml`; `orce/eval.py` is the acceptance runner).
