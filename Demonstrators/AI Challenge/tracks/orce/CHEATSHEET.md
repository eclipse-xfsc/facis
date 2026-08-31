# ORCE in 5 minutes - walkthrough cheat sheet
1. **Start it (local, no cloud):** `cd tracks/orce && docker compose up -d` -> editor at http://localhost:1880
2. **See a working flow:** menu ≡ -> Import -> paste `contracts/team-example-weak-flow.json` -> Import -> **Deploy** (top right).
3. **Read the wiring:** `http in` (your POST endpoint) -> five function nodes (one per agent, each pushes onto `msg.challenge.trace`) -> `http response`. The case arrives as `msg.payload.case_id`.
4. **Run it:** `curl -s -X POST -H 'Content-Type: application/json' -d '{"case_id":"CASE-2026-0002"}' http://localhost:1880/api/airbus-challenge/team-example-weak/run`
5. **Validate:** `python3 checker/validate_contract.py http://localhost:1880/api/airbus-challenge/team-example-weak/run CASE-2026-0002`
6. **Make it yours:** copy the tab, rename the endpoint to `/api/airbus-challenge/<your-name>/run`, replace each agent's canned output with real logic over `data/` (LLM calls via an `http request` node to your model API). Deploy after every change.
7. **Debug:** wire a `debug` node anywhere; watch the right-hand sidebar. Export your tab (not the workspace) for submission.
That is the whole loop: import -> deploy -> curl -> validate -> improve.
