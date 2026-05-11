# Software Requirements Specification

## Federation Architecture Pattern Principal Credential Issuance (FAP PCI)

Version 1.0 (February 2026)

Published by eco – Association of the Internet Industry (eco – Verband der Internetwirtschaft e.V.) Lichtstrasse 43h 50825 Cologne, Germany

Copyright © eco Association of the Internet Industry (eco – Verband der Internetwirtschaft e.V.)


---

## Table of Contents

[1. Executive Summary](01_executive_summary.md)  
[2. Background & Context](02_background_context.md)  
[3. Scope](03_scope.md)  
[4. Conceptual Architecture](04_conceptual_architecture.md)  
[5. Technical Architecture](05_technical_architecture.md)  
[6. Functional Requirements](06_functional_requirements.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.1 Key Management](06_functional_requirements.md#61-key-management)   
&nbsp;&nbsp;&nbsp;&nbsp;[6.2 Public Endpoints](06_functional_requirements.md#62-public-endpoints)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.3 Participant Tenant Administration](06_functional_requirements.md#63-participant-tenant-administration)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.4 Issuer Administration](06_functional_requirements.md#64-issuer-administration)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.5 Issuer Plugin](06_functional_requirements.md#65-issuer-plugin)   
&nbsp;&nbsp;&nbsp;&nbsp;[6.6 Participant Data Repository](06_functional_requirements.md#66-participant-data-repository)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.7 Provider Tenant Administration](06_functional_requirements.md#67-provider-tenant-administration)  
[7. Interfaces & Data Models](07_interfaces_data_models.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[7.1 Tenant Administration UX](07_interfaces_data_models.md#71-tenant-administration-ux)  
&nbsp;&nbsp;&nbsp;&nbsp;[7.2 Tenant Registration UX](07_interfaces_data_models.md#72-tenant-registration-ux)  
&nbsp;&nbsp;&nbsp;&nbsp;[7.3 Issuer Administration UX](07_interfaces_data_models.md#73-issuer-administration-ux)   
&nbsp;&nbsp;&nbsp;&nbsp;[7.4 Issuer Plugin (Participant Connection)](07_interfaces_data_models.md#74-issuer-plugin-participant-connection)  
[8. Security & Trust](08_security_trust.md)   
&nbsp;&nbsp;&nbsp;&nbsp;[8.1 Transport Security](08_security_trust.md#81-transport-security)  
&nbsp;&nbsp;&nbsp;&nbsp;[8.2 Identity & Authentication](08_security_trust.md#82-identity-authentication)  
&nbsp;&nbsp;&nbsp;&nbsp;[8.3 Authorization & Policy Enforcement](08_security_trust.md#83-authorization-policy-enforcement)  
&nbsp;&nbsp;&nbsp;&nbsp;[8.4 Data Protection](08_security_trust.md#84-data-protection)  
[9. Deployment & Operations](09_deployment_operations.md)   
&nbsp;&nbsp;&nbsp;&nbsp;[9.1 Deployment](09_deployment_operations.md#91-deployment)  
&nbsp;&nbsp;&nbsp;&nbsp;[9.2 Operational Requirements](09_deployment_operations.md#92-operational-requirements)  
[10. Standards & Protocols](10_standards_protocols.md)   
&nbsp;&nbsp;&nbsp;&nbsp;[10.1 UX Framework](10_standards_protocols.md#101-ux-framework)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.2 Participant Data Protocol](10_standards_protocols.md#102-participant-data-protocol)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.3 GitHub Requirements](10_standards_protocols.md#103-github-requirements)  
[11. Validation & Acceptance Criteria](11_validation_acceptance_criteria.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.1 Tenant Management Milestone](11_validation_acceptance_criteria.md#111-tenant-management-milestone)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.2 Issuer Management Milestone](11_validation_acceptance_criteria.md#112-issuer-management-milestone)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.3 E2E Issuance Milestone](11_validation_acceptance_criteria.md#113-e2e-issuance-milestone)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.4 Second Cluster Deployment Milestone](11_validation_acceptance_criteria.md#114-second-cluster-deployment-milestone)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.5 GitHub Finalization Milestone](11_validation_acceptance_criteria.md#115-github-finalization-milestone)  
[12. Appendices](12_appendices.md)    
&nbsp;&nbsp;&nbsp;&nbsp;[Appendix A: Glossary](12_appendices.md#appendix-a-glossary)  
&nbsp;&nbsp;&nbsp;&nbsp;[Appendix B: Tenant-specific Ingress Rule](12_appendices.md#appendix-b-tenant-specific-ingress-rule)  

---

## Conformance Language

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, and OPTIONAL in this document are to be interpreted as described in [RFC 21191](https://rfc-editor.org/rfc/rfc2119).

---

## License

This work is licensed under the [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).

© eco – Association of the Internet Industry (eco – Verband der Internetwirtschaft e.V.)
