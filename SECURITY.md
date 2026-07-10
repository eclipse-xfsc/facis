# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability in this monorepo, please report it responsibly.

**Do not open a public issue for security vulnerabilities.**

Instead, please report vulnerabilities through the Eclipse Foundation's security process:

- **Email:** security@eclipse.org
- **Eclipse Security Page:** https://www.eclipse.org/security/

Include the following in your report:

- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (if available)
- Affected service(s)

## Scope

This repository (`eclipse-xfsc/facis`) is a documentation and index hub for the FACIS project. It aggregates independently maintained components via git submodules — FAP, DCS, SLA, PoC, Demonstrators (see the component table in the [README](README.md)).

- If a vulnerability affects **this repository's own content** — documentation, GitHub Actions workflows (e.g. `daily-submodule-check.yml`), or submodule references — report it here using the process above.
- If a vulnerability affects a **specific component's code**, report it against that component's own repository. Several already maintain their own `SECURITY.md`, including:
  - [`FAP/Decentralised Catalogue Management/implementation/SECURITY.md`](FAP/Decentralised%20Catalogue%20Management/implementation/SECURITY.md)
  - [`FAP/IOT & AI over Trusted Zones/implementation/SECURITY.md`](FAP/IOT%20%26%20AI%20over%20Trusted%20Zones/implementation/SECURITY.md)
- When in doubt, report via the Eclipse Foundation central process above — it will be routed correctly.

## Supported Versions

This repository does not currently publish formal release branches. Security support applies to the active `main` branch only.

## Disclosure Handling

Security reports should remain private until a fix is available and maintainers have coordinated disclosure. Public issues, pull requests, or discussions should not include exploit details until disclosure is approved.

