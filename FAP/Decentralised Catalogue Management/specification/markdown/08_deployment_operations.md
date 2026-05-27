[← Security & Trust](07_security_trust.md) · [↑ Table of Contents](../README.md) · [Standards & Protocols →](09_standards_protocols.md)

---

## 8. Deployment & Operations

### 8.1 Deployment Profiles (Exemplary)

Generally, it SHOULD be possible to define a set of default catalogues, which are pre-loaded into the Catalogue Registry of a new deployment of this FAP.

#### 8.1.1 Docker Compose (Development)   
Single-host deployment for local development and testing:

- Backend (FastAPI connector)
- Frontend (React UI)
- A graph database, e.g., Neo4j or an RDF triple store

#### 8.1.2 Kubernetes (Production)   
Multi-zone, highly available deployment:


- Helm charts for all services
- Separate namespaces per trust zone
- Horizontal Pod Autoscaling for connector and ingest services
- Ingress with TLS termination
- External Secrets Operator for KMS integration


### 8.2 Operational Requirements

#### 8.2.1 Availability

- Control plane: 99.9% uptime SLA
- Data plane: 99.95% uptime SLA
- Health checks at /health and /ready endpoints
- Circuit breakers for external dependencies


#### 8.2.2 Scalability

- Connector scales horizontally (stateless)
10 remote catalogues with 1,000 assets each can be harvested in parallel, including AI-driven schema mapping.


#### 8.2.3 Monitoring & Alerting

- Prometheus metrics for all services
- Grafana dashboards for operational visibility
- Alertmanager for SLA breach notifications
- Distributed tracing with Jaeger.

---

[← Security & Trust](07_security_trust.md) · [↑ Table of Contents](../README.md) · [Standards & Protocols →](09_standards_protocols.md)

