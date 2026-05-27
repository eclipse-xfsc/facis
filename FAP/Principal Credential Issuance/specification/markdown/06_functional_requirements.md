[← Technical Architecture](05_technical_architecture.md) · [↑ Table of Contents](../README.md) · [Interfaces & Data Models →](07_interfaces_data_models.md)

---

## 6. Functional Requirements

### 6.1 Key Management

#### [FR-PCI-01] Key Creation over TSA Crypto Provider
        
**Priority:** MUST  
**Description:** The key creation and key usage MUST be handled over the [TSA](https://github.com/eclipse-xfsc/docs/tree/main/tsa) Crypto Provider. The crypto provider supports currently HashiCorp Vault, but it MUST be tested with OpenBao to ensure compatibility.  

**Acceptance criteria:**

 - Token signing key for Pre-Authorization Bridge can be configured in the issuer administration page,
 - Credential signing key for issuer can be configured in the issuer administration page.


#### [FR-PCI-02] DID Provisioning over TSA Crypto Provider 
 
**Priority:** MUST  
**Description:** For providing DID documents, the TSA Crypto Provider MUST be used to host DID web documents via [Ingress rules](https://github.com/eclipse-xfsc/deployment/blob/main/OCM%20W-Stack/Well%20Known%20Ingress%20Rules/templates/ingress.yaml#L18).  
**Acceptance criteria:** The issuer keys are represented over a public resolvable DID document (via the universal resolver).

### 6.2 Public Endpoints

#### [FR-PCI-03] Credential Endpoint   

**Priority:** MUST   
**Description:** The credential endpoint of the OCM W-Stack MUST be public per tenant in the deployment for the wallet to receive its credential. This MUST be configured in the ingress configuration/API gateway.   
**Acceptance criteria:** Demonstration via API request (e.g., Curl or Postman).

#### [FR-PCI-04] Pre-Authorization Bridge Endpoints   
**Priority:** MUST   
**Description:** The endpoints of the Pre-Authorization Bridge MUST be public per tenant to retrieve tokens for the issuance. This MUST be configured in the ingress configuration/API gateway.   
**Acceptance criteria:** Demonstration via API request (e.g., Curl or Postman).

#### [FR-PCI-05] TSA Endpoints   
**Priority:** MUST   
**Description:** The endpoints of the TSA MUST be public per tenant for the JWKS for the issuance. This MUST be configured in the ingress configuration/API gateway.   
**Acceptance criteria:** Demonstration via API request (e.g., Curl or Postman).

### 6.3 Participant Tenant Administration

#### [FR-PCI-06] Issuer Management Delegation   
**Priority:** MUST   
**Description:** The tenant administration MUST provide a feature where the participants in tenant administration can delegate credential creation and credential configuration management to several principals of the organization. This MAY be realized by defining a role which enables users to log in as a credential administrator and create credentials.   

**Acceptance criteria:**

 - Principals can be enabled to create, modify, and delete credential configuration definitions.
 - Principals can be enabled to manage the issuance flows.


#### [FR-PCI-07] OID4VCI Issuer Metadata Configuration   
**Priority:** MUST   
**Description:** The tenant administration MUST be able to configure the OID4VCI issuer metadata and distribute that metadata to the OCM W-Stack. The issuer administration MUST NOT have access to this information as this information is static.   

**Acceptance criteria:**

- Configured metadata are configurable and distributed over NATS,
- Editable by participant tenant administration only,
- Metadata is visible in the well-known configuration of the tenant.


### 6.4 Issuer Administration

#### [FR-PCI-08] Issuing Management   
**Priority:** MUST   
**Description:** The issuing management MUST provide a feature where the principals can manage issuance flows and details about credential configurations. This MAY be realized by defining a role which enables users to log in as a credential administrator and create credentials.   

**Acceptance criteria:**

- Principals can be enabled to create, modify, and delete credential configuration definitions.
- Principals can manage issuance flows


#### [FR-PCI-09] OID4VCI Credential Configuration Permissioning   
**Priority:** MUST   
**Description:** The issuer administration MUST consider defined roles which are able to create, modify, and delete credential configurations.   
**Acceptance criteria:** Standard principal cannot access the administration page.

#### [FR-PCI-10] Credential Logos   
**Priority:** MUST   
**Description:** The issuer administration MUST allow the uploading and storing of credential card logos for the credential configuration data. These logos MUST be resolvable over a tenant-specific URL from the storage for a wallet to download it via the well-known openID issuer configuration.   
**Acceptance criteria:** Wallet can load and display the credential card logo.

#### [FR-PCI-11] Issuance Flow Configuration  
**Priority:** MUST   
**Description:** The issuer administration MUST allow for a specific issuance flow with various steps to be configured per credential configuration. The steps MUST be configured via ORCE. Special UX frameworks MAY be used but ORCE is preferred.   
**Acceptance criteria:** For each credential configuration ID, a separate flow can be configured.

#### [FR-PCI-12] Credential History per Configuration   
**Priority:** MUST   
**Description:** The issuer administration MUST provide a credential history UI and backend which display the latest ID of the credential issuing, the status (“offered”, “expired”, “revoked”, “issued”) and the information on the principal (JWT format).   
**Acceptance criteria:** UI with overview of issuances per credential configuration which is only visible for credential configuration administrator.

#### [FR-PCI-13] Credential Revocation   
**Priority:** MUST   
**Description:** Within the issuer administration, there MUST be an option where an issued credential can be searched and revoked. The revocation MUST happen over the OCM W-Stack Status List Provider. An issued credential MUST be searchable over principal details, date or ID per credential configuration. UI history MAY be integrated.   
**Acceptance criteria:**   
For each credential configuration, a revocation option is available (the credential can be searched and revoked). Revocation links are embedded in the credential.

#### [FR-PCI-14] Credential Configuration Deletion   
**Priority:** MUST   
**Description:** A credential configuration MUST be deletable, but it MAY be archived if technically required.   
**Acceptance criteria:**  
Credential configuration can be deleted.
 
#### [FR-PCI-15] Credential Configuration Creation/Update   
**Priority:** MUST   
**Description:** A credential configuration MUST be creatable and modifiable according to the metadata credential configuration specification of OpenID4VCI.   
**Acceptance criteria:**  
Credential configuration can be deleted.

#### [FR-PCI-16] Participant Backend Connection    
**Priority:** MUST   
**Description:** A credential configuration setup MUST consist of participant backend connection settings which allow it to contact the participant backend for credential data. This requires all necessary settings for mTLS.

**Acceptance criteria:**  
mTLS can be configured per credential configuration.

### 6.5 Issuer Plugin

#### [FR-PCI-17] OCM W-Stack Integration   
**Priority:** MUST   
**Description:** The issuer plugin MUST be integrated into the OCM W-Stack issuance flow according to the current [architecture](https://github.com/eclipse-xfsc/oid4-vci-issuer-service?tab=readme-ov-file#introduction). This requires the setup of a structure which speaks NATS messages. The programming language SHOULD be golang, but for easier ORCE flow integration others MAY be used.   
**Acceptance criteria:**
- Code review and demonstration to crosscheck the integration pattern and functionality,
- Full-working issuance flow.


#### [FR-PCI-18] NATS Provisioning of Configured Metadata    
**Priority:** MUST   
**Description:** The issuer plugin MUST provide the configured metadata via NATS to the OCM W-Stack well-known service according to the [messaging library](https://github.com/eclipse-xfsc/nats-message-library/blob/main/wellknown.go).    
**Acceptance criteria:**   
Demonstration of an issuer configuration and credential configuration, crosscheck via well-known API of the tenant.

#### [FR-PCI-19] History Logging   
**Priority:** MUST   
**Description:** The issuer plugin MUST log all credential issuance requests in a GDPRcompliant way with status progress, e.g., “offered” or “accepted”. It MUST contain date, holder binding DID, revocation list address and other relevant data grouped by credential configuration.   
**Acceptance criteria:**  
Presentation of log entries.

#### [FR-PCI-20] Participant Backend Connection   
**Priority:** MUST    
**Description:** The issuer plugin MUST be able to either get data from the participant data repository to sign a credential via TSA, or to send a credential issuance request to the participant backend to get a signed credential back. An external issuer plugin MUST be configured per credential configuration for the purpose either for signing a credential or for providing the data for it. Communication MUST happen via TLSprotected GRPC calls.   
**Acceptance criteria:**
- Demonstration of data collection for TSA signing,
- Demonstration of credential signing via a participant backend mock.


#### [FR-PCI-21] ORCE Integration   
**Priority:** MUST  
**Description:** The issuer plugin MUST be triggerable via ORCE to request offering links from the OCM W-Stack. The integration MUST also provide a way to render the link as QR code.  
**Acceptance criteria:**
- Code review,
- ORCE flow demonstration.


### 6.6 Participant Data Repository

#### [FR-PCI-22] Golang Service   
**Priority:** MUST    
**Description:** The participant data repository MUST be implemented as golang microservice to reuse existing libraries, e.g., Crypto Provider Core. The service MUST be implemented with the Goa framework.    
**Acceptance criteria:**   
Code review.

#### [FR-PCI-23] Data Format Library    
**Priority:** SHOULD    
**Description:** Data format definitions for the used participant SD-JWT and W3C credentials SHOULD be collected in a go library and contributed to XFSC. It is RECOMMENDED to make use of W3CVCDM v2.0 or its profile in ETSI TS 119 4721 as the credential formats belong to EAA.    
**Acceptance criteria:**  
Code review.

#### [FR-PCI-24] Data Request   
**Priority:** MUST   
**Description:** The core data request for a credential MUST be abstracted via GRPC to allow a participant to dock various data pickup providers.   
**Acceptance criteria:**
- Demonstration of a simple data request via GRPC,
- Code review of the protobuf contract and demo review.


### 6.7 Provider Tenant Administration

#### [FR-PCI-25] Tenant Management   
**Priority: MUST**   
**Description:** The provider tenant administration MUST provide a functionality where the provider administrator can see, approve, and reject tenant registration requests made by participants.   
**Acceptance criteria:**  
Demonstration of the procedure.

#### [FR-PCI-26] Tenant Approved    
**Priority:** MUST   
**Description:** Once a tenant is approved, the Kubernetes resources, domains etc. can be provided, and the tenant can be unlocked to log in by participant tenant administration.  
**Acceptance criteria:**
- Demonstration of the procedure,
- Email verification for the participant tenant administration.


#### [FR-PCI-27] Tenant Deletion    
**Priority:** MUST   
**Description:** The tenant MUST be deletable by the provider tenant administration and the participant tenant administration. In both cases, confirmation MUST be triggered before all resources are deleted.   
**Acceptance criteria:**  
- Deletion after confirmation,
 - Deletion of resources (Kubernetes logs),
 - Tenant gone, no URLs reachable anymore, and issuer DIDs are not resolvable anymore.


#### [FR-PCI-28] Tenant Rejection   
**Priority:** MUST   
**Description:** The tenant MUST be rejectable by the provider tenant administration. An email MUST be sent out to communicate the decision. The decision is logged, and the registration request is stored.   
**Acceptance criteria:**

- Rejection is stored,
- Email is sent out.

---

[← Technical Architecture](05_technical_architecture.md) · [↑ Table of Contents](../README.md) · [Interfaces & Data Models →](07_interfaces_data_models.md)

