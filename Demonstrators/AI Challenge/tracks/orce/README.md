# Track: ORCE (FACIS Low-Code Engine) - runs LOCALLY via Docker
Coach: Daniel Pires.

**No cloud deployment is provided for this track.** You run ORCE / Node-RED yourself,
locally, in Docker - your flow lives and executes on your own laptop.

## Quickstart
```
cd tracks/orce
docker compose up -d          # Node-RED editor on http://localhost:1880
```
(Equivalent: `docker run -it -p 1880:1880 -v node_red_data:/data nodered/node-red`.
The ORCE building blocks / palette are introduced by the track lead at the session.)

## Build
- Pattern: `http in` (POST `/api/airbus-challenge/<name>/run`) -> five function/LLM nodes
  in sequence -> `http response`. Read the case from the POST body (`msg.payload.case_id`).
- Study `contracts/team-example-weak-flow.json` for the wiring (not the answers).
- Deploy before testing - the endpoint only exists after Deploy.

## Test (local endpoint)
Test with the offline validator or curl:
```
python3 ../../checker/validate_contract.py http://localhost:1880/api/airbus-challenge/<name>/run CASE-2026-0002
curl -s -X POST -H 'Content-Type: application/json' \
     -d '{"case_id":"CASE-2026-0001"}' http://localhost:1880/api/airbus-challenge/<name>/run
```
At the showcase you run live from your laptop (screen + validator output).

## Submit
Export your flow **tab** (not the whole workspace) into your submission folder, together
with a `result.json` from a real run. Endpoint URL in the README is your local path.
