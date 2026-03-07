# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability in this project, please report it responsibly.

**Do not open a public issue for security vulnerabilities.**

Instead, please report vulnerabilities through the Eclipse Foundation's security process:

- **Email:** security@eclipse.org
- **Eclipse Security Page:** https://www.eclipse.org/security/

Include the following in your report:

- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (if available)

## Supported Versions

| Version | Supported |
|---|---|
| 1.0.x | Yes |

## Security Considerations

This project handles IoT simulation data. Key security measures include:

- **Transport Security:** All external communication uses TLS/mTLS
- **Authentication:** Keycloak OIDC for user authentication, mTLS for service-to-service
- **Credential Management:** Sensitive credentials stored in `.env.cluster` (excluded from version control)
- **Container Security:** Docker images run as non-root user (UID 1000)
- **Dependency Scanning:** Regular updates via `pip audit` and `ruff` security rules
