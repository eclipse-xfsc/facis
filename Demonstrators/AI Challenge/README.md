# The Airbus AI Challenge, powered by FACIS
**ContainerDays / AI Context Series - Hamburg, 3-4 September 2026 - Schuppen 52**

One aviation maintenance challenge, five open cases plus healthy seats. Two tool tracks. Every participant builds the **complete five-agent workflow** end to end with the tool of their choice - and the same flow must handle whichever case it is given (contract v1.1).

Teams assemble **on the day**: there is always at least one ORCE team, and the rest form
around whatever tool their members pick. No team heads are assigned - coaches are on the
floor for everyone.

| Track | Tool | Coach |
|---|---|---|
| **ORCE** | FACIS Low-Code Engine ORCE (Node-RED) - **local Docker on your laptop** | Daniel Pires |
| **Open** | Any platform / stack you like | Hossein Rafieekhah & Atoosa Eslami |

## Quick start
1. Read `CHALLENGE.md` - the scenario, the five agents, and the submission contract.
2. Pick your tool and open `tracks/<open|orce>/README.md`.
3. Explore `data/` - all synthetic input data (telemetry, BITE events, manuals, history, parts, crew).
4. Build your flow. Test it against the checker (`checker/README.md`).
5. Submit via Pull Request - see `CONTRIBUTING.md`. Day-1 PRs are the baselines that Day 2 extends.

## Working with ORCE
To work with **ORCE**, this is the repository you should use:
https://github.com/eclipse-xfsc/orchestration-engine

Bring ORCE up locally with Docker:
```bash
docker pull ecofacis/xfsc-orce:2.0.13

docker run -d \
  --name xfsc-orce \
  -p 1880:1880 \
  -p 8080:8080 \
  ecofacis/xfsc-orce:2.0.13
```

ORCE will then be available at:
```text
http://localhost:1880
```

Use the following credentials to sign in:
```text
Username: admin
Password: xfsc-orce
```
Use this local ORCE instance to develop and test your challenge solution.


## Repository layout
```
CHALLENGE.md        the challenge statement (read this first)
AGENDA.md           two-day schedule
CONTRIBUTING.md     how to submit (branches, PRs, folder layout)
contracts/          submission JSON contract + reference examples
checker/            how to run and validate your flow
data/               synthetic dataset (see data/README.md)
tracks/             one folder per track: guide + submissions/
```

License: Apache-2.0 (Eclipse XFSC standard) - see `LICENSE`. All data in this repository is **synthetic** and was generated for this exercise. Nothing here reproduces real Airbus, supplier, airline or MRO material, and nothing has any airworthiness validity.

This challenge lives inside the FACIS repository: **github.com/eclipse-xfsc/facis -> `Demonstrators/AI Challenge`**.
```
git clone --depth 1 https://github.com/eclipse-xfsc/facis
cd "facis/Demonstrators/AI Challenge"
```

## Why this challenge exists
FACIS wants working evidence, not slideware: the same maintenance decision built with
different tools, compared openly on speed, debuggability and robustness. Results will be
published through the FACIS dissemination channels - watch/star this repository to stay
in the loop, and see https://www.facis.eu/ for the wider programme.
