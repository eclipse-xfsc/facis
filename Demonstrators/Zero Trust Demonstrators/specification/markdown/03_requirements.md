[← Product Overview](02_product_overview.md) | [↑ Table of Contents](../README.md) | [Design and Implementation →](04_design_and_implementation.md)

---

## 3 Requirements

### 3.1 Functional Requirements

#### 3.1.1 Zero Trust Connector


#### [ZT-18] TRAIN Allow List
Priority: MUST

Description: The Connector MUST consume TRAIN lists to allow over policies in which counter-connector connections are allowed.

Acceptance Criteria: Connector reads TRAIN trust lists to allow counter-connector connections.

#### [ZT-19] Upstream / Downstream Proxy Functionality
Priority: MUST

Description: The connector MUST allow bidirectional communication to another connector by utilizing the attested TLS channel. This includes HTTPS headers and other relevant call information.

Acceptance Criteria: Connector uses and establishes the TLS channel.

#### [ZT-20] Guarding Functionality
Priority: MUST

Description: The connector MUST provide an application connection guard such as OAuth2 Provider, PIP, PEP or PAP. The enforcement MUST be based on Rego Policies and TSA Policy Engine. The guarding MUST be deployable for each protected resource on REST/GRPC basis. If any unauthorized access occurs, the guard SHOULD respond with OID4VP links.

Acceptance Criteria:

- Connector can guard a protected resource,
- No access without matching policies and authorizations.


#### [ZT-21] OAuth2 Server
Priority: MUST

Description: The OAuth2 Server of the connector MUST be able to dynamically register new participant backends via Dynamic Client Registrations to allow participant backends to use the connector. On the other hand, the server MUST also be able to issue access tokens based on OID4VP presentations to grant access for a counter connector. The server MUST utilize DPOP for access tokens.

Acceptance Criteria:

- Server issues access tokens based on OID4VP presentations,
- Server issues access tokens to participant backends for accessing the connector itself.


#### [ZT-22] Token Storage
Priority: MUST

Description: The Connector MUST store the issued access tokens of the counter connector after a credential presentation. If a participant backend call arrives, the used access token of the participant backend MUST be checked for DPOP headers, and if valid, the access token of the call MUST be upstreamed with the stored access token for the protected resource of the counter connector. The storage itself MUST keep caring about token renewal and OID4VP tasks.

Acceptance Criteria:

- Participant backend can call the protected resource over the connector,
- Upstream authorization is replaced via the token storage on DPOP basis.

#### 3.1.2 Zero-Trust Service Mesh


#### [ZT-23] Service Mesh Implementation
Priority: MUST

Description: A service mesh MUST be used for inter-service communication within each Kubernetes cluster. This service mesh MUST either be Istio- or Cilium-based.

Acceptance Criteria:

- A service mesh based on Istio or Cilium is implemented in each Kubernetes cluster,
- Communication between services is routed through the service mesh.


#### [ZT-24] SPIFFE/SPIRE Deployment
Priority: MUST

Description: Each Kubernetes cluster MUST contain a deployment of [SPIRE](https://spiffe.io/docs/latest/spire-about/). The service mesh MUST use SPIRE deployment to provide service identities. Identity verification MUST be based on SPIRE as well.


Acceptance Criteria:

- SPIRE is deployed in each Kubernetes cluster,
- The service mesh is configured to use SPIRE-provided identities,
- Appropriate SPIRE node- and workload attestation is used,
- All services participating in the service mesh are registered as SPIRE workloads.


#### [ZT-25] Routing Policies
Priority: MUST

Description: Interactions between services in the service mesh MUST be governed by network policies. These policies MUST prevent interactions between unaffiliated services. These policies MUST NOT use insecure and unstable identifiers like an IP address.

Acceptance Criteria:

- The service mesh is configured to enforce network policies,
- Network policies are deployed to allow related services to communicate,
- A default deny policy is in place to prevent unaffiliated service communication.


#### [ZT-26] Ingress and Egress
Priority: MUST

Description: To ensure that the inter-cluster communication protocol is adhered to, appropriate ingress and egress rules MUST be configured to direct traffic to the ZT connector. Protocols (e.g. DNS) and endpoints not related to inter-connector communication (e.g. admin or observability APIs) MUST be able to bypass the ZT connector.

Acceptance Criteria:

- Ingress and egress for all inter-service communication is configured to use the ZT connector,
- Other APIs use a different appropriate ingress and egress configuration.


#### [ZT-27] Observability
Priority: MUST

Description: Observability MUST be considered when configuring the service mesh. Events MUST be exported from the cluster in a standard format such as Open Telemetry (Otel) traces and metrics:

- (1) OpenTelemetry Collector as the primary aggregation and export tool (OTEL standard),
- (2) Prometheus for metrics (retain),
- (3) OTEL-compatible tracing backend (e.g. Jaeger) 

Acceptance Criteria: 

OTEL logs available.

#### 3.1.3 Inter-Cluster Communication Protocol


#### [ZT-28] Attested TLS
Priority: MUST

Description: All communication between Kubernetes clusters MUST be performed over a mutually attested TLS channel. A high-level description of the desired protocol can be found in Section 5.2. The implementation of the TLS protocol MUST use TLSv1.3 or later and MUST be configured to reject any earlier version.

Acceptance Criteria:

- All inter-cluster communication uses the attested TLS protocol,
- An appropriate TLS version is used,
- TLS certificates are correctly checked against the cluster’s identities.


#### [ZT-29] Attestation Request
Priority: MUST

Description: The attestation request message MUST be transmitted in a machine-readable format (e.g. JSON, CBOR). It MUST include the attestation type for the connection REQUIRED by the sender. Additional information MAY be included in the message.

Acceptance Criteria:

- The attestation request message is sent in a machine-readable format,
- The information contained in the message includes the desired attestation type, including at least:
    - Server-Side Attestation: Only the server provides an attestation report,
    - Client-Side Attestation: Only the client provides an attestation report,
    - Mutual Attestation: Both server and client provide an attestation report.


- The size of any additional information contained in the message does not exceed the size of the attestation report.


#### [ZT-30] Attestation Response
Priority: MUST

Description: The attestation response MUST be transmitted in a machine-readable format. The message MUST contain at least the attestation report. If the peer did not request an attestation report, the attestation report part of the message SHOULD be empty or null.

Acceptance Criteria:

- The attestation response message is sent in a machine-readable format,
- The attestation response contains an attestation report,
- The size of any additional information contained in the message does not exceed the size of the attestation report.


#### [ZT-31] Attestation Report Format
Priority: MUST

Description: To ensure that the sender’s attestation report is valid, it MUST be cryptographically verifiable. A TEE format SHOULD be used for demo purposes. The report MUST contain the TLS-exporter channel binding specified in [RFC 9266](https://doi.org/10.17487/RFC9266).

Acceptance Criteria:

- All attestation report signatures can be verified using common cryptography libraries (e.g. OpenSSL),
- All attestation reports can be verified by the receiver without special knowledge; if additional information besides the attestation report is needed (e.g. an intermediary certificate), it is provided in TRAIN or as part of the attestation response message,
- All attestation reports contain the TLS-exporter channel binding for the TLS channel through which they are sent.


#### [ZT-32] Verification Result Message
Priority: MUST

Description: The verification result message MUST clearly communicate in a machinereadable format if the provided attestation report is acceptable. If the verification fails, the sender SHOULD provide a human-readable error message to assist in debugging.

Acceptance Criteria:

- The verification result message is sent in a machine-readable format,
- An affirmative verification result message is sent only if the attestation report sent by the peer could be verified successfully,
- The size of any additional information contained in the message does not exceed the size of the attestation report.


#### [ZT-33] Error Message
Priority: MUST

Description: If a peer encounters an error during the attestation protocol, it MUST terminate the protocol flow with a machine-readable error message. The error message MUST contain a human readable error message to assist in debugging. After sending or receiving an error message, either peer MUST close the TLS connection.

Acceptance Criteria:

- For any error case in each peer implementation, an error message is sent,
- The error message is machine-readable,
- The size of any additional information contained in the message does not exceed the size of the attestation report,
- Error messages are correctly received and lead to connection termination.


#### [ZT-34] Proxy Integration
Priority: SHALL

Description: The attested TLS protocol SHALL be integrated into a reverse proxy to accept attested upstream connections. The reverse proxy SHALL accept Kubernetes Ingress or Gateway API resources as configuration, possibly through an additional operator. It further MUST integrate with the service mesh to accept configuration and route inbound traffic to other members. The implementation SHOULD be implemented via the Go programming language.

#### [ZT-35] Hash Management/TRAIN Integration
Priority: MUST

Description: Any endpoint capable of establishing attested TLS connections (e.g. the Ingress gateway) MUST be able to resolve trusted hashes for its peers from TRAIN. This hash MUST reflect the launch digest value or equivalent of the endpoint’s attestation report. For each endpoint, its CI/CD pipeline MUST pre-generate its own hash and upload it to TRAIN on deployment.

Acceptance Criteria:

- Upon connection establishment, the attested TLS endpoint fetches the peer’s hash from TRAIN,
- Connection establishment proceeds only if the hash matches the value in the attestation report.

#### 3.1.4 Zero Trust Execution Environment


#### [ZT-36] OPA Gatekeeper
Priority: MUST

Description: The Environment(s) MUST install OPA Gatekeeper and combine it with [XFSC TSA Policy Service](https://github.com/eclipse-xfsc/smartdeployment/tree/main/Easy%20Stack%20Builder%20(ESB)/TSA) to load Rego policy packages for secure container admission.

Acceptance Criteria:  
Gatekeeper consumes the policies and enforces them.

#### [ZT-37] OPA Gatekeeper Policies
Priority: MUST

Description: The Rego policies MUST be distributed as Tarball packages within the XFSC Harbor over the OCI interface. To publish the package, a GitHub action MUST be provided.

Acceptance Criteria:

- Policies are available,
- GitHub push action is in place.


#### [ZT-38] Container Signing Pipeline
Priority: MUST

Description: To allow containers for OPA Gatekeeper, a signing pipeline MUST be provided over GitHub actions and custom runner setups to sign Docker images. The key material SHALL be integrated in the runner setup, but the public keys MUST be published for verification.

Acceptance Criteria:  
OPA Gatekeeper accepts Docker images which are signed by the client.

#### 3.1.5 Zero Trust Application Communication


#### [ZT-39] Participant Backend Mockup
Priority: MUST

Description: The participant backend mockup SHALL dynamically register itself via dynamic client registration against the OAuth2 server of the ZT connector to obtain access tokens for the usage of the trusted channel. All actions MUST be provided for the visualization.

Acceptance Criteria:

- Participant backend can register itself,
- Participant backend can obtain access tokens,
- Participant backend can successfully pass PEP proxy to connect Zero Trust connector and its channel,
- Participant backend gets an answer from protected resource mock,
- Visualization reflects this interaction.


#### [ZT-40] Credential-Based Access Control (CrBAC)
Priority: MUST

Description: The Zero Trust Connector MUST be able to get access tokens from another zero-trust connector over credentials from OCM W-Stack. Each of those access tokens belongs to a registered participant backend and can be used only over DPOP extensions. The Zero Trust Connector MUST take care of the expiration and renewal.

Acceptance Criteria:

- A participant backend can use the Zero Trust Channel of the Connector to call protected resource, and the Connector will add the obtained Access Tokens of the counter connector to each call,
- DPOP Verification of each participant backend call and matching it against internal JWT storage,
- OCM W-Stack Presentations can be triggered by using OID4VP Verifier requests from counter connector.


#### [ZT-41] Protected Resource Mockup
Priority: MUST

Description: The protected resource mock simulates various responses based on access token roles. All actions MUST be visualized.

Acceptance Criteria: Protected resource responds different results based on roles.

#### 3.1.6 Zero Trust Communication Visualization


#### [ZT-42] UX Concept
Priority: MUST

Description: A visualization concept which explains how the Demonstrator works MUST be created on GitHub. The concept MUST be aligned beforehand with the client and designed via Wireframes or similar tooling. Any UI Design has to be implemented with the ORCE UI Builder.

Acceptance Criteria:

- GitHub documentation and GitHub Page ready,
- Concept aligned with the client.


#### [ZT-43] ORCE Usage
Priority: MUST

Description: The ORCE MUST orchestrate the visualization demonstration.

Acceptance Criteria: ORCE is used.

#### [ZT-44] Value Visualization
Priority: MUST

Description: The Demonstrator MUST visualize important values like TEE measurements, credentials, TRAIN zones, communication decisions, messages etc.

Acceptance Criteria:

- Concept for value visualization aligned with the client,
- Values presented in Demonstrator.


#### [ZT-45] Demonstrator Configuration
Priority: MUST

Description: The Demonstrator MUST provide user interfaces for configuring TRAIN in the scope of the Zerto Trust Demonstrator (zones, policies).

Acceptance Criteria:

- Configuration documented,
- Configuration within the Demonstrator for certain parts can be demonstrated.


#### [ZT-46] User Journey Scenario
Priority: MUST

Description: The Demonstrator MUST demonstrate a scenario where an issuing process is providing a credential to OCM W-Stack to enable the protected resource access for a participant backend. This process can involve the user directly (e.g., by mobile app), or indirectly by providing user interfaces which unlock permissions. The scenario for this journey MUST be aligned with the client and MUST be described and documented on GitHub.

Acceptance Criteria:

- Scenario is aligned and documented on GitHub,
- Scenario is integrated into the Demonstrator and orchestrated by ORCE step-bystep,
- Scenario is illustrated with animations and images.

### 3.2 Non-Functional Requirements


#### [ZT-47] Continuous Authentication Enforcement
Priority: MUST

Description: The system SHALL continuously verify user and device identity for every access request to protected resources, regardless of network location.

Acceptance Criteria:

- All access requests require authentication and authorization,
- Session re-validation occurs at configurable intervals (≤ 15 minutes),
- Access is revoked automatically if session becomes non-compliant.


#### [ZT-48] Least Privilege Access Control
Priority: MUST

Description: The system SHALL enforce least-privilege access by granting users and services only the minimum permissions REQUIRED to perform their tasks.

Acceptance Criteria:

- RBAC or ABAC is implemented,
- Privileged access rights are time-bound and require explicit approval,


#### [ZT-49] Micro-Segmentation
Priority: MUST

Description: Network architecture SHALL implement logical micro-segmentation to prevent lateral movement between workloads and services.

Acceptance Criteria:

- Workloads are segmented by policy-defined trust zones,
- East-west traffic is inspected and authorized,
- Unauthorized lateral communication attempts are blocked and logged.

### 3.3 General Security Requirements


#### [ZT-50] Cryptographic Standards (BSI TR-02102)
Priority: MUST

Description: All cryptographic algorithms and key lengths used within the demonstrator MUST comply with BSI Technical Guideline TR-02102 (Cryptographic Mechanisms). Specifically: symmetric encryption MUST use AES-256 or equivalent, asymmetric encryption MUST use RSA-4096 or ECC P-256/P-384, hash functions MUST use SHA-256 or stronger, and TLS configurations MUST follow BSI TR-02102-2. Deprecated algorithms (MD5, SHA-1, RSA < 2048) MUST NOT be used. Reference: BSI TR-02102-1 and TR02102-2.

Acceptance Criteria:

- No deprecated algorithms present in any component.
- Key lengths documented and auditable.


#### [ZT-51] Credential Revocation
Priority: MUST

Description: The system MUST support credential revocation for Verifiable Credentials issued within the federation. Revocation MUST be implemented using a standardscompliant mechanism such as W3C Bitstring Status List v1.0 (W3C Recommendation, 15 May 2025) or IETF Token Status List (draft-ietf-oauth-status-list, active Internet Draft). Verifiers MUST check revocation status at credential verification time. Revoked credentials MUST NOT grant access to any protected resource. The revocation infrastructure MUST be available, as its unavailability MUST result in fail-closed behavior.

Acceptance Criteria:

- Revocation check performed at every credential verification.
- Revocation endpoint availability is monitored.


#### [ZT-52] Fail-Secure (Fail-Closed) Behavior
Priority: MUST

Description: In the event of unavailability of any Zero Trust control plane component (Policy Engine, TRAIN, SPIRE, OCM), the system MUST default to denying access rather than granting it (fail-closed). No access to protected resources SHALL be possible without a valid, verified policy decision. The system MUST detect control plane failures within 30 seconds and emit alerts via the observability stack. Partial degradation scenarios (e.g. one cluster unreachable) MUST be documented with defined behavior. Reference: NIST SP 800-207, Section 3.3.

Acceptance Criteria:

- Access denied when Policy Engine is unreachable (verified in test).
- Control plane failure detected and alerted within 30 seconds.
- Degradation scenarios documented with defined fail-closed behavior.


#### [ZT-53] Multi-Tenancy and Tenant Isolation
Priority: SHALL

Description: The system SHALL support logical multi-tenancy, allowing strict isolation between different organizational participants (tenants) within the same federation zone. Data, credentials, and policy configurations of one tenant SHALL NOT be accessible to another tenant under any circumstances. Tenant isolation SHALL be enforced at the Kubernetes namespace layer.

#### [ZT-54] Software Bill of Materials (SBOM)
Priority: MUST

Description: All software components of the demonstrator MUST have a documented Software Bill of Materials (SBOM) in CycloneDX or SPDX format. The SBOM MUST be generated automatically as part of the CI/CD pipeline and MUST be published alongside each release. The SBOM MUST include all direct and transitive dependencies, their versions, known vulnerabilities (CVE references), and license information. This is REQUIRED for NIS2 supply chain security compliance (Article 21) and enables rapid response to zero-day vulnerabilities across the dependency tree. The SBOM MUST be signed with the client's key material to ensure integrity.

Acceptance Criteria:

- SBOM generated in CycloneDX or SPDX format for every release.
- SBOM published in GitHub repository alongside release artefacts.


#### [ZT-55] Management Plane / Data Plane Separation
Priority: MUST

Description: The system MUST enforce strict separation between the management plane (Policy Engine, TRAIN, SPIRE control plane, OCM, observability stack) and the data plane (application traffic, participant backend communication, protected resource access). Management plane components MUST be accessible only via dedicated control channels and MUST NOT be reachable from the data plane network. This separation MUST be enforced at both the Kubernetes network policy layer and the service mesh layer. Compromise of the data plane MUST NOT grant any access to management plane components. Reference: NIST SP 800-207 Section 3 - Zero Trust Architecture Components.

Acceptance Criteria:

- Management plane components not reachable from data plane (verified in network test).
- Separation enforced at both network policy and service mesh layers.
- Architecture diagram clearly shows plane separation.


#### [ZT-56] CI/CD Pipeline Security (Zero Trust for the Pipeline)
Priority: MUST

Description: The CI/CD pipeline itself MUST be treated as a critical security boundary and MUST apply Zero Trust principles. This includes: (1) All GitHub Actions workflows MUST run with minimum necessary permissions (least privilege on repository secrets and tokens); (2) Third-party GitHub Actions MUST be pinned to exact commit SHAs, not mutable version tags; (3) Pipeline-generated artefacts (Docker images, policy packages, SBOMs) MUST be signed before use; (4) Secrets MUST never appear in pipeline logs; (5) All pipeline runs MUST be logged (6) Branch protection rules MUST enforce code review before merge to main.

Acceptance Criteria:

- All third-party GitHub Actions pinned to commit SHAs.
- Pipeline runs with minimum REQUIRED permissions (no wildcard write access).
- No secrets visible in any pipeline log output.

---

[← Product Overview](02_product_overview.md) | [↑ Table of Contents](../README.md) | [Design and Implementation →](04_design_and_implementation.md)

