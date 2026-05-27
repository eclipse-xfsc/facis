[← Background & Context](02_background_context.md) · [↑ Table of Contents](../README.md) · [Conceptual Architecture →](04_conceptual_architecture.md)

---

## 3. Scope

This section defines the scope of features of the requested solution. In Scope features must be implemented in accordance with this specification. Out of Scope features must not be implemented within this specification.

### In Scope 
The scope of the solution includes the following components and activities:

 - Setup of ready-to-use deployment on top of existing deployments,
 - Implementation of an issuer plugin(s),
 - Utilization of ORCE for web-based issuing flow, including potential implementation of new ORCE nodes and/or code extensions,
 - Provision of issuance flow,
 - Technical documentation for the architecture of the solution, components, and deployment,
 - Documentation describing the steps required to achieve EUDI and ETSI TS 119 471 compliance, including identification of components requiring modification and estimation of the effort needed to reach full compatibility (e.g., relying party registration processes, key management, and handling procedures),
 - Operations and SecDevOps documentation.


### Out of Scope 
The following items are explicitly out of scope for this specification:

 - Modification of existing XFSC components, unless explicitly agreed with the client through a formal alignment process,
 - Testing with external wallets (only PCM Mobile is required),
 - Development of XFSC deployments for TSA, OCM W-Stack, Status List Service (except for required modifications), and SD-JWT Service
 - Wallet implementation,
 - Full EUDI- and ETSI TS 119 471-compliant implementation across all components.

---

[← Background & Context](02_background_context.md) · [↑ Table of Contents](../README.md) · [Conceptual Architecture →](04_conceptual_architecture.md)

