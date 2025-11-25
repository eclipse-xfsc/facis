# FACIS Reference FAP — Partner Onboarding



## 0. Conformance Language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in RFC 2119.



---



## 1. Executive Summary

The **Reference FAP** defines a **generic, reusable onboarding pattern** for federated ecosystems.  
It standardizes how an organization is admitted into a federation using **open W3C standards** (SSI, DIDs, VC/VP) through a **wizardized, lowcode flow** executed in **ORCE** (Orchestration Engine).  
The design is **not tied to any specific PoC or vendor**; **Gaia-X is treated only as one possible trust anchor/blueprint**.  
The outcome is an **executable, auditable, and portable** onboarding flow adaptable to any domain or trust framework.



---



## 2. Background & Context

**WP1** delivers **executable FAPs** as lowcode templates orchestrated by **ORCE**, including documentation and demo assets.  
Workshop1 covered ORCE fundamentals; Workshop2 focuses on **Reference FAP**, demonstrating deployment, execution, and customization of the reference onboarding flow.



---



## 3. Goals & Non-Goals



### 3.1 Goals

- Deliver a **generic reference onboarding flow** independent of PoC/domain.  
- Implement **open standards**: W3C DID/VC/VP, **OIDC4VCI** (issuance) and **OIDC4VP** (presentation), OAuth2/OIDC.  
- Ensure the flow **runs fully within ORCE** with **optional adapters** to Catalogue (CAT), OCM, PCM, TSA, NOT, AAS.  
- Provide **deployment & integration guidance** for Docker and Kubernetes via EasyStack Builder.



### 3.2 Non-Goals

- Binding the FAP to a specific trust framework or vendor.  
- Deep domainspecific approval processes or backoffice tasks.  
- Creating a monolithic implementation of federation services.



---



## 4. Scope



### 4.1 In-Scope

- **Onboarding Wizard** for organization data, DID, consent, and credential issuance.  
- **Credential verification**, **publication**, and **status tracking**.  
- **Local (Docker)** and **Kubernetes (Helm)** deployments (via **EasyStack Builder**).  
- Sample flows, JSON artifacts, and integration examples.



### 4.2 Out-of-Scope

- Nongeneric, sectorspecific logic.  
- Proprietary/manual workflow steps beyond reference scope.



---



## 5. Conceptual Model (Onboarding Steps)

1. **Data Gathering** — Organization identity, contacts, domain, keys.  
2. **Decentralized Identities & Trust Anchors** — Generate or ingest DIDs; select optional trust anchor.  
3. **Terms & Conditions** — Capture consent and timestamp.  
4. **Credential Issuance** — Sign claims using VC standards (OIDC4VCI).  
5. **Persistence** — Store credentials and SelfDescriptions (SDs) securely.  
6. **Verification** — Validate credentials locally or via trust anchors (OIDC4VP / resolver checks).  
7. **Publication** — Register/expose SDs for discovery (e.g., federated catalogue).  
8. **Audit & Logging** — Maintain traceability, timestamps, and evidences.



---



## 6. Functional Specification



| ID    | Function            | Description                                                 | Inputs               | Outputs                         |
|------:|---------------------|-------------------------------------------------------------|----------------------|---------------------------------|
| FR01 | Onboarding Wizard   | Collect org profile, ToC consent, and keys.                 | Forms                | Org SD (JSON), consent record   |
| FR02 | DID & Keys          | Create/import DID (default **did:web**) and JWK/keys.       | Domain, JWK          | DID Document, metadata          |
| FR03 | Credential Issuance | Issue Participant VC (OIDC4VCI); optional trustanchor flow | VC request           | Participant VC                  |
| FR04 | Verification        | Validate VC/VP (local resolver or anchor policy).           | VC/VP                | Verification result             |
| FR05 | Publication         | Publish SD (e.g., to CAT) and expose URL.                   | SD JSON              | Published URL                   |
| FR06 | Status & Audit      | Track states, evidences, timestamps.                        | State data           | Audit trail                     |



> Adapters for **CAT, OCM, PCM, TSA, AAS** are **OPTIONAL** and **pluggable**.



---



## 7. Technical Architecture



### 7.1 ORCE Orchestration

- ORCE executes modular fragments: `inject → validate → register → audit`.  
- A `msg` carries transient state; **context storage** persists participant data.  
- All nodes **MUST** emit normalized outputs `{url?, clientSecret?, status}` and structured logs.



### 7.2 Optional Components (Adapters)

- **CAT (Federated Catalogue):** SD indexing and discovery.  
- **AAS (Authentication/Authorisation Service):** OAuth2/OIDC realm & client mgmt.  
- **OCM/PCM:** Organization/Personal credential wallets.  
- **TSA:** Timestamping, signature, and policy evidence.  



> Reference architecture and toolbox roles are aligned with XFSC components. (Advisory)

  

---



## 8. Data Model & Interfaces



### 8.1 Core JSON Artifacts



**Organization SelfDescription (SD) — Example**
```json
{
  "type": "Organization",
  "name": "Example Org GmbH",
  "domain": "example.org",
  "did": "did:web:example.org",
  "contacts": [
    { "type": "admin", "email": "admin@example.org" }
  ],
  "tocConsent": {
    "accepted": true,
    "timestamp": "2025-09-29T09:30:00Z"
  },
  "status": "requested"
}
```
**Participant VC — Example**
```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "type": ["VerifiableCredential", "ParticipantCredential"],
  "issuer": "did:web:issuer.example",
  "issuanceDate": "2025-09-29T09:35:00Z",
  "credentialSubject": {
    "id": "did:web:example.org",
    "orgName": "Example Org GmbH"
  },
  "proof": {
    "type": "JsonWebSignature2020",
    "jws": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```
**Verifiable Presentation (VP) — Example**
```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "type": ["VerifiablePresentation"],
  "verifiableCredential": [ /* Participant VC goes here */ ],
  "holder": "did:web:example.org",
  "proof": {
    "type": "JsonWebSignature2020",
    "created": "2025-09-29T10:00:00Z",
    "proofPurpose": "authentication",
    "verificationMethod": "did:web:example.org#keys-1",
    "jws": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```



### 8.2 Interfaces (Abstract)

  - OIDC4VCI: `POST /credential-offers` → `GET /credential` (Auth via OAuth2).

  - OIDC4VP: Presentation request → VP submission endpoint.

  - Catalogue (CAT): `POST /sd` (publish), `GET /sd/{id}` (retrieve).

  - OCM/PCM: `POST /wallet/vc`, `GET /wallet/vc/{id}`.

  - TSA/NOT: `POST /evidence/hash`, `GET /evidence/{id}`.

Implementations MAY vary by deployment and adapter.


---


## 9. Security & Trust

  - **W3Cfirst:** DID/VC/VP + JSON-LD

  - **Trust Anchors (OPTIONAL):** Gaia-X or others as policy providers.

  - **TLS Enforcement:** TLS 1.2+ for all endpoints.

  - **Auditability:** Timestamped logs; optional TSA/NOT evidence anchoring.

  - **Privacy:** Data minimization; secrets in external KMS; JWT expirations and revocation/status checks.


---


## 10. Deployment & Operations

### 10.1 Local (Docker)

  - Single-node ORCE + demo adapters; quickstart for PoC.

### 10.2 Kubernetes (Helm)

  - ORCE runtime and adapters as Helm release.

  - EasyStack Builder automates the management of kubeconfig, Secrets, TLS, and Ingress.

### 10.3 Integration Steps

1. Deploy ORCE runtime (Docker/K8s).

2. Configure domain, TLS, and realm.

3. Import the reference flow (orce-flow.json).

4. Test onboarding with a dummy SD/VC.

5. Monitor via ORCE dashboard; export audit logs.


---


## 11. Standards & Compliance Mapping

| Area         | Standard            | Usage                          |
|---------------|---------------------|--------------------------------|
| Identity      | W3C DID             | did:web (default), others      |
| Credentials   | W3C VC/VP           | Participant credentials        |
| Issuance      | OIDC4VCI / OAuth2   | Credential flow                |
| Presentation  | OIDC4VP             | VP verification                |
| Transport     | HTTPS/TLS           | Secure channels                |
| Trust         | Optional anchor     | Policy enforcement             |



---


## 12. Example Flow (Happy Path)

1. Admin enters org info and accepts ToC.

2. DID generated → VC issued → verified locally.

3. SD published in Catalogue (if enabled).

4. Status updated to published and visible in dashboard.


---


## 13. NonFunctional Requirements

  - **Portability:** Docker and K8s.

  - **Reliability:** Idempotent nodes; retry with backoff; compensating actions.

  - **Observability:** Structured logs, correlation IDs, debug nodes, health/readiness.

  - **Usability:** Clean UI, form validation, progressive disclosure.

  - **Extensibility:** New DID methods, anchors, adapters.


---


## 14. Validation & Acceptance Criteria

1. Endtoend onboarding runs in ORCE only (adapters optional).

2. VC/VP JSON-LD passes W3C validation (issuance & presentation).

3. Optional components (CAT, OCM/PCM, TSA, NOT, AAS) toggle on/off successfully.

4. Docker and K8s deployments run without errors (Helm lint & install succeed).

5. Outputs (SD, VC, VP) verifiable via Postman tests / resolver checks.


---


## 16. Roadmap (WP1)

| Sprint | Deliverable                                      |
|---------|--------------------------------------------------|
| A       | ORCE core flow, wizard UI, Docker PoC           |
| B       | K8s automation via EasyStack Builder            |
| C       | Integrations (CAT, AAS, OCM/PCM, TSA/NOT)       |



---


## 17. Positioning & Notes

  - **Reference FAP** is a generic pattern, not bound to any PoC.

  - **Gaia-X** is one possible trust anchor; not a dependency.

  - **Architecture** centers on open W3C standards for maximum interoperability.

  - **Licensing advisory:** consider CCBY4.0 for documents if aligning with broader XFSC practice.


---


## 18. Appendix

### A. Integration Variants

  - No-Catalogue mode (indexonly).

  - Alternative DID methods via resolvers.

  - Different trust anchors per environment.

  - Optional AI assisted flow generation.

### B. Example Gaia-X Adapter Path (Optional)

  - Transform inputs to Gaia-X JSON shapes;

  - Validate via GXDCH endpoints;

  - Store issued credential in OCM;

  - Publish SD to CAT;

  - Notarize hash in NOT;

  - Reverify via resolver/compliance API.



---
