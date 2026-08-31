# Challenge Statement (v1.1)

## The story
A first-class suite that cannot be sold costs the airline about **EUR 10,000 per leg**. Pulling a cabin control unit costs about **EUR 3,800** plus **EUR 1,450** for a shop test - and far too many such removals come back *no fault found*: money spent, defect still on the aircraft. The planning assumption in `data/economics.json` is a **1-in-3** NFF share; in the shipped history the fleet-wide share is **0.21** and it differs strongly per fault family (the CAN fault: **0.47**) - part of your job is to use the number that is actually defensible for your case. *(All figures synthetic.)*

## Your mission
Build the complete **five-agent maintenance workflow** with the tool of your track - one working flow per participant (pairs are fine). Your endpoint receives a `case_id` + `seat_id` (contract v1.1) and must handle **any** of the open cases in `data/cases_seed.json`:

| Case | Seat | Fault code | Symptom family |
|---|---|---|---|
| CASE-2026-0001 | D-AXFA-2A | F-25-2101 | recline actuator degradation |
| CASE-2026-0002 | D-AXFB-1K | F-25-2140 | intermittent CAN fault (reference case, walk-through below) |
| CASE-2026-0003 | D-AXFC-3A | F-23-3401 | IFE seat-box thermal shutdown |
| CASE-2026-0004 | D-AXFD-4K | F-25-2166 | USB-PD overcurrent lockout |
| CASE-2026-0005 | D-AXFE-1A | F-25-2188 | privacy divider stall (safety-relevant) |

...and a seat that is **healthy**: the fleet contains suites with nothing wrong. For those, the correct answer is *monitor, no removal* - a flow that always prescribes a repair is a wrong flow. At the showcase your endpoint is re-run on a case you were not told in advance.

| # | Agent | It must... | Minimum output |
|---|---|---|---|
| 1 | **Diagnose** | Read fault/telemetry/manual data for the requested seat; name the likely cause | `fault_code`, `leading_cause`, `confidence`, `evidence` |
| 2 | **Assess NFF risk** | Apply the decision rules in `OPS-NFF-POLICY` - removal justified, or not? | `nff_risk`, `decision` |
| 3 | **Plan repair** | A feasible plan for THAT decision: task card, station, part, crew, window - or an honest `feasible: false` with alternatives | `task_card_id`, `station`, parts/crew/timing |
| 4 | **Execute & verify** | Record what was done and prove the result | `outcome`, `functional_test_passed`, measurement |
| 5 | **Learn** | Turn the outcome into reusable knowledge | `nff_avoided`, `saving_eur`, `feedback` |

Mocked data and mocked service calls are allowed - but the flow must actually run end to end, for whatever case it is given. A written answer or a hard-coded JSON is not a submission.

## Walk-through: the reference case (CASE-2026-0002)
Aircraft D-AXFB, suite 1K, intermittent CAN fault F-25-2140. Error bursts correlate with vibration phases (taxi, climb, descent) and almost never reproduce in a static ground test - a classic no-fault-found trap. The naive reaction replaces the seat control unit; the grounded answer follows `TSM-25-21-55` and inspects the CAN connector path (`DA-CON-3390`) first. Use this case to build; expect the others (and a healthy seat) at test time.

## Evidence is mandatory
Every diagnosis and every NFF decision must cite real artifacts in `evidence_ids`: manual doc-ids, data files, computed statistics. At the showcase you will be asked: *"where in the data does this number come from?"*

## What good looks like (showcase criteria - no points, no leaderboard)
- Generalisation: the same flow answers correctly across different cases, including the healthy seat
- Correct leading cause backed by evidence references - not just the fault code
- A defensible decision per `OPS-NFF-POLICY` (reproducibility, monotonic trend, safety relevance)
- A plan that respects ground time, parts stock and crew qualifications - `feasible: false` with alternatives is a success when true
- Verified execution with an honest outcome - "NFF" and "no action" are valid answers
- A learning step that would make the next case faster
- Robustness: answers in <=30 s, degrades gracefully, never crashes on odd input

## Day 2
Day 2 starts from your Day-1 baseline (your merged PR), adds new requirements, and - mid-morning - one **unexpected change** you must absorb. Bring your flow in a state you can modify quickly.

*Everything here is synthetic and for demonstration only - not confirmed Airbus operational data, not a certified process.*
