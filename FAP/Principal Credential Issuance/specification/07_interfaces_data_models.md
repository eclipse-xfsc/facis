[← Functional Requirements](06_functional_requirements.md) · [↑ Table of Contents](README.md) · [Security & Trust →](08_security_trust.md)

---

## 7. Interfaces & Data Models
### 7.1 Tenant Administration UX


#### [FR-PCI-29] Confirmation/Deletion/List Section   
**Priority:** MUST   
**Description:** The administration page needs a protected section for the provider tenant administration, where tenants can be confirmed, listed, and deleted. This is used when a participant requests a tenant creation. Only one tenant per participant is allowed. This UX MUST be initially configured during the SaaS setup.   
**Acceptance criteria:**
- Demonstration of registration of a tenant with confirmation within the page,
- Demonstration of the registered tenant by using the tenant administration page for participants.


#### [FR-PCI-30] Participant Tenant Administration   
**Priority:** MUST   
**Description:** The tenant administration for participants is a part of the administration page where a participant can configure its issuer metadata, OIDC login information, styles, and other relevant tenant information. This functionality MUST be unlocked after confirmation by tenant administrator. The login for this page is created just for this registration page and will be sent via email. After first login the password MUST be changed and a 2FA registered.   
**Acceptance criteria:**
- Demonstration of tenant configuration and direct usage of it,
- Documentation of tenant configuration,
- Demonstration of tenant login.


### 7.2 Tenant Registration UX

#### [FR-PCI-31] Compliance   
**Priority:** SHOULD   
**Description:** The implementation of the UX SHOULD consider the fulfilment of ETSI EN 301 549 as it is referenced by IA 2025/2162.

#### [FR-PCI-32] Registration Data Form   
**Priority:** MUST   
**Description:** Under a given domain, the deployment MUST provide a registration data form which can be either private or public (per config). The form SHOULD contain the contact data of a participant who wants to create a tenant. The registration itself MUST be confirmed by tenant administrator before anything is created.   
**Acceptance criteria:**
- Demonstration of registration and confirmation,
- Demonstration of how resources are created in the cluster.


### 7.3 Issuer Administration UX

#### [FR-PCI-33] Compliance   
**Priority:** SHOULD   
**Description:** The implementation of the UX SHOULD consider the fulfilment of ETSI EN 301 549 as it is referenced by IA 2025/2162.
#### [FR-PCI-34] Credential Configuration Management   
**Priority:** MUST   
**Description:** UX MUST enable creation, modification, and deletion of credential configurations according to the given OID4VC specification. This includes card layouts, data repositories (e.g., participant backend), logos, texts, and other metadata. This also includes the connection to the data repository/backend and/or the issuing plugin configuration.   
**Acceptance criteria:**

- Demonstration of management by creating a configuration,
 - Demonstration of docking a data repository/backend.


#### [FR-PCI-35] Credential Issuance Permissioning   
**Priority:** MUST   
**Description:** UX MUST enable “docking” existing permissions like roles or groups to a credential configuration so that only a defined range of principals can request a credential. For instance, a group of directors only receive a director’s credential.   
**Acceptance criteria:**   
Demonstration of how two different credential requests can result in the issuance of two different kinds of credentials.
 
 #### [FR-PCI-36] Credential History and Revocation   
 **Priority:** MUST  
**Description:** UX MUST provide a feature to see the history of a credential configuration, e.g., how often it was issued, or which principal received which credential. Additionally, each history record SHALL have an option to revoke the credential via the Status List Service to block the credential for the principal and to block the re-issuance.   
**Acceptance criteria:**   
Demonstrate credential history and revocation.

#### [FR-PCI-37] Steps Configuration   
**Priority:** MUST   
**Description:** The issuer administration MUST be able to configure UI steps via ORCE for the issuance process, beginning with a landing page followed by other steps for issuance.     
**Acceptance criteria:**
- Steps can be configured and different kinds of flow can be produced,
- Tenant-specific layout is applied to the pages.


#### [FR-PCI-38] ORCE Utilization   
**Priority:** SHOULD   
**Description:** The issuer administration SHOULD utilize ORCE to define issuance flows on UX level. If this is not possible, another low-code design MUST be provided.   
**Acceptance criteria:**

- Custom flows can be configured for credential issuances,
- Two custom flows have been demonstrated.

### 7.4 Issuer Plugin (Participant Connection)


The issuer plugin connects itself to the participant data repository to get the credential data belonging to the subject. This interface MUST be therefore additionally protected to become enterprise ready. It is RECOMMENDED that the interface follows ETSI TS 119 478 as participant data repository.

#### [FR-PCI-39] mTLS Connection   
**Priority:** MUST   
**Description:** The connection to the participant data repository MUST be established by the issuer plugin via an mTLS connection. The certificates for this connection MUST be configured in the tenant administration of the participant.   
**Acceptance criteria:**
- Demonstration of mTLS configuration,
- Documentation of configuration.


#### [FR-PCI-40] Participant JWT Reusage   
**Priority:** MUST   
**Description:** During the call of the participant data repository service/backend, the issuer plugin MUST use the JWT issued by the participant backend to have access to participant backend resources, e.g., for accessing data repositories.   
**Acceptance criteria:**
- Code review,
- Data log.


#### [FR-PCI-41] Issuing Settings   
**Priority:** MUST   
**Description:** The tenant administration SHALL be able to limit the issuer plugin with parameters like rate limits.   **Acceptance criteria:**
- Code review,
- Data log.

---

[← Functional Requirements](06_functional_requirements.md) · [↑ Table of Contents](README.md) · [Security & Trust →](08_security_trust.md)

