# Data catalog (all synthetic)

| File | What it is |
|---|---|
| `telemetry.jsonl` | 13,824 sensor records - 72 legs across 6 aircraft (12 each), 48 suites, 16 signals |
| `telemetry_highrate.csv` | 1 Hz / 15 min for one seat - signal-level work |
| `bite_events.jsonl` | discrete fault codes latched by the seat controller |
| `cabin_log_entries.csv` | free-text crew reports (deliberately vague) |
| `maintenance_history.csv` | 140 past work orders with NFF / confirmed-fault outcomes (21 rows carry no fault code - deliberate real-world noise; fleet-wide NFF share here is 0.21, per-fault rates differ, e.g. F-25-2140 = 0.47) |
| `cases_seed.json` | 5 open cases - the challenge case is `CASE-2026-0002` (D-AXFB-1K) |
| `economics.json` | the cost model (treat as configurable parameters) |
| `fleet.csv`, `flights.csv`, `seats.csv` | master data: aircraft, legs + ground times, seats/firmware |
| `stations.csv`, `technicians.csv` | who can fix what, where, on which shift |
| `parts_catalog.csv`, `parts_stock.csv` | prices, lead times, stock per station |
| `manuals/` | 11 synthetic AMM/TSM/MEL/SB/task-card documents |
| `rag_chunks.jsonl`, `rag_eval_questions.json` | pre-chunked manual passages + 20 Q/A regression pairs (optional RAG) |
| `kg/` | knowledge graph of seats, faults, work orders (CSV / Cypher / JSON-LD, optional) |

Note: `F-25-2166` (USB-PD) has no manual - for that case your evidence comes from telemetry, BITE and history. Hints: the signals worth attention include `actuator_current_a`, `can_error_count`, `scu_temp_c`, `usb_pd_current_a`, `divider_position_error_pct` - and `flight_phase`, which most people ignore. `ground_truth.json` is withheld until the retro.
