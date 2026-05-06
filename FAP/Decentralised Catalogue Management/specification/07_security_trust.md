[← Technical Architecture](06_technical_architecture.md) · [↑ Table of Contents](README.md) · [Deployment & Operations →](08_deployment_operations.md)

---

## 7. Security & Trust  
**Transport Security**

- All endpoints MUST use TLS 1.2 or higher
- Certificates managed via cert-manager in Kubernetes deployments
- API calls to LLM service MUST use TLS 1.3.

**Identity & Authentication**

- Organizations identified by W3C DIDs (did:web or did:key methods)
- Single Sign On to access Graphical User Interfaces using OAuth/OIDC using did:webidentities. 

**Authorization & Policy Enforcement**  
User roles enforced (cf. FR-AC-01). Data Protection

- Data at rest MAY be encrypted
- Data in transit encrypted via TLS/SASL
- Secrets stored in external KMS (HashiCorp Vault or AWS Secrets Manager)
- PII handling per GDPR data minimization principles.


**Audit & Observability**

- Audit trail includes LLM prompts/responses and schema validation results for traceability
- Logs aggregated in ELK stack or Loki for querying
- Metrics exported to Prometheus (request rates, latencies, error rates).

---

[← Technical Architecture](06_technical_architecture.md) · [↑ Table of Contents](README.md) · [Deployment & Operations →](08_deployment_operations.md)

