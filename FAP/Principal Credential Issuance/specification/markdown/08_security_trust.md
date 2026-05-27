[← Interfaces & Data Models](07_interfaces_data_models.md) · [↑ Table of Contents](../README.md) · [Deployment & Operations →](09_deployment_operations.md)

---

## 8. Security & Trust
### 8.1 Transport Security

#### [FR-PCI-42] TLS Security   
**Priority:** MUST   
**Description:** The transport security for external connections MUST support TLS 1.3 following the „European Cybersecurity Certification Group, Sub-group on Cryptography: ‘Agreed Cryptographic Mechanisms’ published by the European Union Agency for [Cybersecurity](https://digital-strategy.ec.europa.eu/en/policies/cybersecurity-certification-group)”. All components which establish TLS connections MUST have pre-configuration.   
**Acceptance criteria:**   
Documentation of TLS settings of the network components in the code.

#### [FR-PCI-43] TLS Certificates   
**Priority:** MUST   
**Description:** The deployment setup MUST be configured so that either Let’s Encrypt can be activated per route, or a static TLS secret can be used.   
**Acceptance criteria:**
- Review of the configuration,
- Demonstration of TLS certificate.

### 8.2 Identity & Authentication
#### [FR-PCI-44] Authentication with Keycloak in Tenant   
**Priority:** MUST   
**Description:** The solution MUST be protected via an OIDC provider which identifies the principle and defines its roles for a certain scope. In general, it SHALL follow sections 7.4 ETSI TS 119 471 as well as 4.2.2.1 if applicable.   
**Acceptance criteria:** Demonstration of login with Keycloak and usage of the issuance process.

#### [FR-PCI-45] Authentication with Microsoft Entra in Tenant   
**Priority:** MUST  
**Description:** The solution MUST be able to use Microsoft Entra to start the issuance process. A process on how to connect an Entra Tenant MUST be documented.   
**Acceptance criteria:**
 - Demonstration of login with Microsoft Entra and usage of the issuance process,
 - Demonstration of Entra Tenant Connection.


#### [FR-PCI-46] Authentication in Tenant Administration/Registration   
**Priority:** MUST   
**Description:** The solution MUST use an authentication solution to reach tenant administration features and registration. This contains email verification flows, passkey registration and a confirmation flow by the cluster administrator.   
**Acceptance criteria:**   
Demonstration of Tenant Registration flow with email confirmation, cluster administrator confirmation and registration of passkey.

### 8.3 Authorization & Policy Enforcement

#### [FR-PCI-47] IDP Authorization Reusage  
**Priority:** MUST   
**Description:** The participant’s IDP will provide identity and optional authorizations like roles and permissions. The solution SHOULD re-use this kind of existing authorization. Documentation MUST be provided as well.   
**Acceptance criteria:**     
Solution is compatible with the participant’s login solution.

### 8.4 Data Protection


#### [FR-PCI-48] GDPR Compliance   
**Priority:** MUST   
**Description:** To have a GDPR-compliant system, the issuer flow SHALL never store data which was retrieved by the participant backend system.   
**Acceptance criteria:**
- Review of “fire and forget” logic during issuing: review of data deletion logic and documentation after issuance and review of the running system,
- Documentation of processes and preparation for auditing,
- Review of example implementation for participant data repository.

---

[← Interfaces & Data Models](07_interfaces_data_models.md) · [↑ Table of Contents](../README.md) · [Deployment & Operations →](09_deployment_operations.md)

