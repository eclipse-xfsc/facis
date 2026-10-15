# [open] Thin Slice MVP

## What we changed

- Added a complete five-stage LangGraph workflow for diagnosis, NFF assessment,
  repair planning, execution and outcome learning.
- Added data-backed handling for all five seeded cases and healthy seats.
- Added a shared local `qwen3.5:9b` Ollama client for structured analysis and
  evidence selection.
- Added dynamic retrieval from the supplied manual chunks.
- Added deterministic validation and policy guards so model output cannot
  override the supported maintenance decision.
- Added timeout, unavailable-model and malformed-request fallbacks.
- Added self-hosted Arize Phoenix tracing for requests, agents, tools,
  retrieval, Ollama calls and guardrails.
- Added a root-directory setup/run/cleanup guide and 13 regression tests.
- Included an honest `result.json` generated from the reference case.

## Why

- To generalize across the hidden case and healthy-seat reruns instead of
  returning a hard-coded reference answer.
- To keep diagnosis and planning grounded in the supplied evidence and expose
  where each value came from.
- To use the LLM for bounded analysis while retaining deterministic control of
  safety-relevant decisions.
- To keep the complete demo local and observable, including useful fallback
  behavior when Ollama or Phoenix is unavailable.

## Technical decisions

- **LangGraph for orchestration:** keeps the required five-stage order explicit
  while passing one typed state through the workflow.
- **One shared Ollama model:** the agents are separate roles and prompts, not
  separate model installations, which keeps the local setup small.
- **Deterministic tools own facts:** telemetry, history, planning and economics
  are calculated from repository data; the LLM only explains and selects from
  constrained evidence and recommendations.
- **Policy guard after every LLM call:** unsupported recommendations are exposed
  in the trace but cannot replace the deterministic decision.
- **Lexical retrieval over supplied chunks:** sufficient for this small offline
  corpus and reproducible without adding a vector database.
- **Fail-open integrations:** Ollama and Phoenix are optional dependencies;
  their failure does not break the response contract.
- **Honest infeasibility:** missing approved maintenance information produces a
  blocked plan instead of invented task data.

## Verification

- 13 automated tests pass, covering all seeded cases, a healthy seat,
  malformed/unknown requests, fallback behavior, guardrails and tracing.
- The committed result and live endpoint pass `checker/validate_contract.py`.
- A real local-Ollama reference run completed in approximately 18 seconds.
- The reference Phoenix trace contains 32 spans across the complete workflow.

## Notes

- Cases 4 and 5 intentionally return `feasible:false` because the supplied data
  lacks approved planning information. The flow does not invent task data.
- Execution outcomes are explicitly simulated or marked
  `PLANNED_NOT_EXECUTED`/`AWAITING_APPROVED_PLAN`.
- Supplied challenge data and contracts are unchanged.

## Potential improvements

The most useful next step is an evaluation harness. The checker verifies the
contract, but not whether a diagnosis, citation or recommendation is correct.
It should measure retrieval recall on `rag_eval_questions.json`, evidence
validity, decision consistency, latency, fallback rate and guardrail overrides.
Decision-accuracy scoring should be added only when organizers release the
withheld ground truth.

Other useful follow-ups:

- Add one live test-matrix command for all cases, a healthy seat, malformed
  input, repeated runs and the 30-second limit.
- Persist verified execution outcomes so the learning stage changes later
  decisions instead of only returning feedback text.
- Add an explicit human-approval/resolution path for blocked plans such as
  cases 4 and 5.
- Add CI for deterministic tests and contract validation.

An embedding/vector database, custom animated UI, full application
containerization and production authentication are intentionally deferred.
The current corpus is small, Phoenix already provides trace inspection, and
those additions would increase demo complexity without proving better challenge
outcomes.
