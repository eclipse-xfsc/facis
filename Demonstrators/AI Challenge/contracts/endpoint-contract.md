# Submission contract - v1.1 (case-parameterized)

Your flow is one **HTTP POST** endpoint, served from your own laptop. The reviewer (or the offline validator) calls it with a JSON body naming the case to solve:

```
POST /api/airbus-challenge/<your-name>/run
{ "case_id": "CASE-2026-0002", "seat_id": "D-AXFB-1K" }
```

An **empty body** means the warm-up reference case (CASE-2026-0002). Your flow must work for **any** case from `data/cases_seed.json` - and for a seat with no fault at all. At the showcase, endpoints are re-run on a case you have not been told in advance; a hard-coded answer dies there.

## Response
1. `team_id`, `run_id`
2. `trace` - exactly five ordered stage objects:
   `diagnosis` -> `nff_assessment` -> `repair_plan` -> `execution` -> `outcome_learning`
   Each: `{ "stage": "...", "agent": N, "status": "complete", "output": { ... } }`
   (The validator accepts equivalent names: `agent`/`name` for `stage`; `result`/`payload` for `output`.)
3. `final_submission` - the consolidated answer. It MUST:
   - echo the requested case: `final_submission.case_id == request.case_id`
   - contain a **non-empty `evidence_ids`** array referencing real artifacts: manual doc-ids
     (e.g. `TSM-25-21-55`), data files, or computed statistics (e.g. `history:nff_rate=0.47`).
     An answer without grounded evidence is treated as not submitted.

## Decisions
Use a clear decision string in `nff_assessment.decision`. Recommended vocabulary:
`CONNECTOR_TASK` | `REPLACE_COMPONENT` | `DEFER_PER_MEL` | `MONITOR` (healthy seat / no action justified).
"MONITOR" on a healthy seat is a *correct, winning* answer - a flow that always prescribes a repair is wrong.

## Robustness (part of the contract)
- Answer within **30 seconds**.
- A malformed or unknown request must still return valid JSON (`"degraded": true` is fine) - never an empty 200 and never a crash.
- Two runs on the same case should be substantially consistent.

## Endpoint naming & where it runs
Path convention: `/api/airbus-challenge/<team-or-name>/run` - lowercase, paths are case-sensitive.
- **ORCE track:** the flow runs LOCALLY in your own Docker Node-RED (`http://localhost:1880/...`). No cloud deployment is provided - test with the offline validator or curl, and demo live from your laptop.
- **Open (any other stack):** serve it from your own machine as well (`http://localhost:<port>/...`). Nothing is deployed to any cloud - the whole challenge runs offline; only model API calls (if you use a hosted LLM) leave your laptop.

## Reference examples
- `final_submission.sample.json` - a complete good response for the reference case.
- `team-example-weak-flow.json` - a running but deliberately weak ORCE flow: wrong cause, incomplete plan, minimal evidence, no learning. It reads and echoes the case correctly - study the wiring, not the answers.

## Integration flags (REQUIRED block)
`final_submission.integrations` must always be present with the three booleans `ai_iot`, `dcm`, `partner_onboarding` - **all false is perfectly fine**. Set one `true` only if your flow actually represents such a call (mocked is acceptable when visible in the returned data). No points attached - showcase talking points only.

## Healthy seat / MONITOR sentinels
When the decision is `MONITOR` (no action justified), keep the blocks present and use sentinels: `repair_plan.task_card_id: "NONE"`, `repair_plan.station: "N/A"`, `execution.outcome: "NO_ACTION"`, `execution.functional_test_passed: true` (meaning: no open defect).
