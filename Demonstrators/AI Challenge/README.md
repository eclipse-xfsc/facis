# The Airbus AI Challenge, powered by FACIS
**ContainerDays / AI Context Series - Hamburg, 3-4 September 2026 - Schuppen 52**

One aviation maintenance challenge, five open cases plus healthy seats. Three tool tracks. Every participant builds the **complete five-agent workflow** end to end with the tool of their choice - and the same flow must handle whichever case it is given (contract v1.1).

| Track | Tool | Lead |
|---|---|---|
| **Open** | Any platform / AI stack you like | Hossein Rafieekhah (support) |
| **ORCE** | FACIS Low-Code Engine ORCE (Node-RED) - **local Docker on your laptop** | Daniel Pires |
| **Neura** | Neura application builder (LEANEA) | Hossein Rafieekhah & Atoosa Eslami |

## Quick start
1. Read `CHALLENGE.md` - the scenario, the five agents, and the submission contract.
2. Pick your track and open `tracks/<track>/README.md`.
3. Explore `data/` - all synthetic input data (telemetry, BITE events, manuals, history, parts, crew).
4. Build your flow. Test it against the checker (`checker/README.md`).
5. Submit via Pull Request - see `CONTRIBUTING.md`. Day-1 PRs are the baselines that Day 2 extends.

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

Intended home of this repository: the FACIS space within the Eclipse XFSC organisation on GitHub.
