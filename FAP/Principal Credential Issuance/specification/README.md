![Version](https://img.shields.io/badge/version-1.0-blue)
[![License](https://img.shields.io/badge/license-CC--BY--4.0-orange)](http://creativecommons.org/licenses/by/4.0/)
[![PDF Specification](https://img.shields.io/badge/specification-PDF-blue)](https://github.com/eclipse-xfsc/facis/blob/main/FAP/Principal%20Credential%20Issuance/specification/FAP_PCI_Specifications.pdf)

# Principal Credential Issuance (PCI) Specification

---

**Version:** 1.0  
**Date:** February 2026  

---


## Conformance Language

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, and OPTIONAL in this document are to be interpreted as described in [RFC 2119](https://rfc-editor.org/rfc/rfc2119).

---


## Table of Contents

[1. Executive Summary](markdown/01_executive_summary.md)  
[2. Background & Context](markdown/02_background_context.md)  
[3. Scope](markdown/03_scope.md)  
[4. Conceptual Architecture](markdown/04_conceptual_architecture.md)  
[5. Technical Architecture](markdown/05_technical_architecture.md)  
[6. Functional Requirements](markdown/06_functional_requirements.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.1 Key Management](markdown/06_functional_requirements.md#61-key-management)   
&nbsp;&nbsp;&nbsp;&nbsp;[6.2 Public Endpoints](markdown/06_functional_requirements.md#62-public-endpoints)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.3 Participant Tenant Administration](markdown/06_functional_requirements.md#63-participant-tenant-administration)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.4 Issuer Administration](markdown/06_functional_requirements.md#64-issuer-administration)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.5 Issuer Plugin](markdown/06_functional_requirements.md#65-issuer-plugin)   
&nbsp;&nbsp;&nbsp;&nbsp;[6.6 Participant Data Repository](markdown/06_functional_requirements.md#66-participant-data-repository)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.7 Provider Tenant Administration](markdown/06_functional_requirements.md#67-provider-tenant-administration)  
[7. Interfaces & Data Models](markdown/07_interfaces_data_models.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[7.1 Tenant Administration UX](markdown/07_interfaces_data_models.md#71-tenant-administration-ux)  
&nbsp;&nbsp;&nbsp;&nbsp;[7.2 Tenant Registration UX](markdown/07_interfaces_data_models.md#72-tenant-registration-ux)  
&nbsp;&nbsp;&nbsp;&nbsp;[7.3 Issuer Administration UX](markdown/07_interfaces_data_models.md#73-issuer-administration-ux)   
&nbsp;&nbsp;&nbsp;&nbsp;[7.4 Issuer Plugin (Participant Connection)](markdown/07_interfaces_data_models.md#74-issuer-plugin-participant-connection)  
[8. Security & Trust](markdown/08_security_trust.md)   
&nbsp;&nbsp;&nbsp;&nbsp;[8.1 Transport Security](markdown/08_security_trust.md#81-transport-security)  
&nbsp;&nbsp;&nbsp;&nbsp;[8.2 Identity & Authentication](markdown/08_security_trust.md#82-identity-authentication)  
&nbsp;&nbsp;&nbsp;&nbsp;[8.3 Authorization & Policy Enforcement](markdown/08_security_trust.md#83-authorization-policy-enforcement)  
&nbsp;&nbsp;&nbsp;&nbsp;[8.4 Data Protection](markdown/08_security_trust.md#84-data-protection)  
[9. Deployment & Operations](markdown/09_deployment_operations.md)   
&nbsp;&nbsp;&nbsp;&nbsp;[9.1 Deployment](markdown/09_deployment_operations.md#91-deployment)  
&nbsp;&nbsp;&nbsp;&nbsp;[9.2 Operational Requirements](markdown/09_deployment_operations.md#92-operational-requirements)  
[10. Standards & Protocols](markdown/10_standards_protocols.md)   
&nbsp;&nbsp;&nbsp;&nbsp;[10.1 UX Framework](markdown/10_standards_protocols.md#101-ux-framework)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.2 Participant Data Protocol](markdown/10_standards_protocols.md#102-participant-data-protocol)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.3 GitHub Requirements](markdown/10_standards_protocols.md#103-github-requirements)  
[11. Validation & Acceptance Criteria](markdown/11_validation_acceptance_criteria.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.1 Tenant Management Milestone](markdown/11_validation_acceptance_criteria.md#111-tenant-management-milestone)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.2 Issuer Management Milestone](markdown/11_validation_acceptance_criteria.md#112-issuer-management-milestone)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.3 E2E Issuance Milestone](markdown/11_validation_acceptance_criteria.md#113-e2e-issuance-milestone)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.4 Second Cluster Deployment Milestone](markdown/11_validation_acceptance_criteria.md#114-second-cluster-deployment-milestone)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.5 GitHub Finalization Milestone](markdown/11_validation_acceptance_criteria.md#115-github-finalization-milestone)  
[12. Appendices](markdown/12_appendices.md)    
&nbsp;&nbsp;&nbsp;&nbsp;[Appendix A: Glossary](markdown/12_appendices.md#appendix-a-glossary)  
&nbsp;&nbsp;&nbsp;&nbsp;[Appendix B: Tenant-specific Ingress Rule](markdown/12_appendices.md#appendix-b-tenant-specific-ingress-rule)  



---

## License

This work is licensed under the [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).

© eco – Association of the Internet Industry (eco – Verband der Internetwirtschaft e.V.)
