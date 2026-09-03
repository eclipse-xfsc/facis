# Track: ORCE (FACIS Low-Code Engine) - runs locally via Docker

Coach: Daniel Pires.

**No cloud deployment is provided for this track.** You run ORCE / Node-RED yourself,
locally, in Docker—your flow lives and executes on your own laptop.

This track uses the published `ecofacis/xfsc-orce:2.0.13` image directly. It does
not build ORCE from source and does not start SQLite, Qdrant, or any other
companion container.

## Quickstart

Run these commands from the repository root:

```bash
cd tracks/orce
docker compose pull
docker compose up -d
docker compose ps
```

Open the ORCE editor at <http://localhost:1880>. The named volume `orce_data`
keeps flows and settings across container restarts.

Equivalent command without Compose:

```bash
docker run -d --name xfsc-orce \
  --platform linux/amd64 \
  -p 1880:1880 \
  -v orce_data:/data \
  --restart unless-stopped \
  ecofacis/xfsc-orce:2.0.13
```

The ORCE building blocks and palette are introduced by the track lead during
the session.

To stop ORCE without deleting your saved work:

```bash
docker compose down
```

## Build

- Pattern: `http in` (POST `/api/airbus-challenge/<name>/run`) -> five function/LLM nodes
  in sequence -> `http response`. Read the case from the POST body (`msg.payload.case_id`).
- Study `../../contracts/team-example-weak-flow.json` for the wiring (not the answers).
- Deploy before testing—the endpoint only exists after you select **Deploy**.

## Test (local endpoint)

Test with the offline validator or curl:

```bash
python3 ../../checker/validate_contract.py http://localhost:1880/api/airbus-challenge/<name>/run CASE-2026-0002
curl -s -X POST -H 'Content-Type: application/json' \
     -d '{"case_id":"CASE-2026-0001"}' http://localhost:1880/api/airbus-challenge/<name>/run
```

At the showcase you run live from your laptop (screen + validator output).

## Submit

Export your flow **tab** (not the whole workspace) into your submission folder, together
with a `result.json` from a real run. Endpoint URL in the README is your local path.
