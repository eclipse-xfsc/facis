# Testing your flow - fully offline, no cloud involved

## Offline validator (ships in this repo)
```
python3 checker/validate_contract.py result.json CASE-2026-0002
python3 checker/validate_contract.py http://localhost:1880/api/airbus-challenge/<name>/run CASE-2026-0004 D-AXFD-4K
```
URL mode POSTs the case to your (local) endpoint - contract v1.1. Exit 0 = five ordered
stages, complete final_submission, non-empty grounded evidence_ids, correct case echo.

## curl
```
curl -s -X POST -H 'Content-Type: application/json' \
     -d '{"case_id":"CASE-2026-0001"}' http://localhost:1880/api/airbus-challenge/<name>/run
```

## What the checker checks
That your response is a valid contract: five stages, correct order, parseable outputs,
complete `final_submission`, non-empty grounded `evidence_ids`, and that your answer
echoes the requested `case_id`. It does **not** produce a score - this challenge has no
points and no leaderboard. Quality is discussed at the showcase against `CHALLENGE.md`.

## Showcase
You demo live from your own laptop: one validator run on the announced case, then one on
the case the organizers name on the spot. Keep a committed `result.json` as your fallback.
