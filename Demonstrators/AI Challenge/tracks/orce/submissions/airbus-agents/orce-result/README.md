# Airbus Challenge ORCE result flow

This directory contains `airbus-challenge-flows.json`, an importable Node-RED/ORCE flow for the Airbus AI Challenge. It is a separate **day 2** variant of the five-agent submission in the [parent directory](../README.md). It exposes an operator console, a JSON run endpoint, and a health endpoint.

The five stages are:

1. **Diagnose** — use embedded BITE events, telemetry, and fault references to identify a supported cause.
2. **Assess NFF risk** — weigh reproducibility, fault history, trend, and safety relevance.
3. **Plan repair** — check task cards, ground time, station capability, stock, skills, authorization, and cost.
4. **Execute and verify** — report the planned or simulated action and its verification outcome.
5. **Learn** — record the outcome and economic assessment.

Case data and decisions are computed from a snapshot of the public `Airbus-Challenge-FINAL-2026-08-31` challenge data embedded in the first function node. The flow can also request a structured OpenAI review for each stage. If a review fails or is unavailable, the computed stage result remains in place and the failure appears in `model_runtime`. The economics are synthetic figures supplied for this exercise.

## Files

| File | Purpose |
| --- | --- |
| [`airbus-challenge-flows.json`](./airbus-challenge-flows.json) | Flow export containing the endpoints, five stages, embedded data, optional review calls, and console. |

The earlier [`flow.json`](../flow.json) and [`result.json`](../result.json) belong to the parent ORCE submission. They are **not** a captured response from this day 2 flow. Run the endpoint below to obtain a response from this export.

## Import and run

1. Start an ORCE/Node-RED instance. The [parent README](../README.md#setup) shows a local `ecofacis/xfsc-orce:2.0.13` setup on port 1880.
2. In the ORCE editor, choose **Menu → Import**, select `airbus-challenge-flows.json`, import the tab, and click **Deploy**.
3. Open the console at `http://localhost:1880/airbus-challenge/team-orce`, or call the API directly.

This export embeds the challenge data it uses, so its run path does not need the parent flow's dataset-copy or Ollama setup. No external model call is required for the computed result.

### OpenAI configuration

The exported tab defines `OPENAI_MODEL` as `gpt-5.4-mini` and `OPENAI_API_KEY` as the literal placeholder `API_KEY`. Before running it:

- For computed results **without** OpenAI reviews, clear the tab's `OPENAI_API_KEY` value and deploy again.
- For OpenAI reviews, configure a valid key in your local ORCE instance and select the model you intend to use. Keep the key out of committed flow exports and screenshots. The flow sends review requests to `https://api.openai.com/v1/responses` with an 8-second request timeout.

The health endpoint's `openai_configured` flag checks only whether the key value is nonempty. The shipped `API_KEY` placeholder can therefore make that flag `true` even though it is not a working credential. Check `final_submission.model_runtime.agents_reviewed` and `runs` in a response to see whether reviews succeeded.

## Endpoints

| Method | Path | Use |
| --- | --- | --- |
| `GET` | `/api/airbus-challenge/team-orce/health` | Reports the flow variant, contract, team ID, and model configuration. |
| `POST` | `/api/airbus-challenge/team-orce/run` | Runs the five-stage case analysis; returns contract v1.1 JSON. |
| `GET` | `/airbus-challenge/team-orce` | Opens the browser operator console. |

Example using a seeded case:

```bash
curl -sS -X POST http://localhost:1880/api/airbus-challenge/team-orce/run \
  -H 'Content-Type: application/json' \
  -d '{"case_id":"CASE-2026-0002"}'
```

The request also accepts `seat_id` and a nested form such as `{"case":{"id":"CASE-2026-0002","seat":"D-AXFB-1K"}}`. Omitting the case defaults to `CASE-2026-0002`. For the day 2 variant, an `incident` object can carry `part_out_of_stock_at`; the flat `part_out_of_stock_at` field is also accepted.

The response includes `team_id` (`TEAM-ORCE`), `run_id`, an ordered five-entry `trace`, `final_submission`, `request_shape`, `solution_variant`, and `data_lineage`. The final submission contains `model_runtime`, including each attempted review and the number that succeeded. Unknown or inconsistent input may produce `degraded: true`; inspect that field rather than assuming an HTTP 200 response means a fully supported case.

## Scope

This is a challenge demonstration built around the supplied public dataset and synthetic planning figures. The execution stage represents planned or simulated work; the flow does not control an aircraft or a maintenance system. For the original ORCE submission, its setup, measured runs, and limitations, see the [parent README](../README.md).
