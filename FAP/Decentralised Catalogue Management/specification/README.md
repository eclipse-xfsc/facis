# Software Requirements Specification

## Federation Architecture Pattern Decentralized Catalogue Management (FAP DCM)

## Table of Contents

[1. Executive Summary](01_executive_summary.md)  
[2. Background & Context](02_background_context.md)  
[3. Scope & Boundaries](03_scope_boundaries.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[3.1 In Scope](03_scope_boundaries.md#31-in-scope)  
&nbsp;&nbsp;&nbsp;&nbsp;[3.2 Out of Scope](03_scope_boundaries.md#32-out-of-scope)  
[4. Conceptual Architecture](04_conceptual_architecture.md)  
[5. Functional Requirements](05_functional_requirements.md)    
&nbsp;&nbsp;&nbsp;&nbsp;[5.1 Asset Crawler + Mapper](05_functional_requirements.md#51-asset-crawler-mapper)   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-ACM-01 Initiating a Harvest](05_functional_requirements.md#fr-acm-01-initiating-a-harvest)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-ACM-02 Harvest Scope](05_functional_requirements.md#fr-acm-02-Harvest-Scope)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-ACM-03 Lifecycle of Imported Assets](05_functional_requirements.md#fr-acm-03-lifecycle-of-imported-assets)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-ACM-04 Linked Assets](05_functional_requirements.md#fr-acm-04-linked-assets)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-ACM-05 Crawling References](05_functional_requirements.md#fr-acm-05-crawling-references)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.2 Schema Registry](05_functional_requirements.md#52-schema-registry)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-01 Storing Remote Schemas](05_functional_requirements.md#fr-sr-01-storing-remote-schemas)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-02 Transformation Strategy Selection](05_functional_requirements.md#fr-sr-02-transformation-strategy-selection)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-03 Prompt Storage as Versioned Assets](05_functional_requirements.md#fr-sr-03-prompt-storage-as-versioned-assets)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-04 Prompt Templates and Variables](05_functional_requirements.md#fr-sr-04-prompt-templates-and-variables)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-05 AI-Driven Transformation Execution](05_functional_requirements.md#fr-sr-05-ai-driven-transformation-execution)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-06 Deterministic Schema-selective RDF Mapping](05_functional_requirements.md#fr-sr-06-deterministic-schema-selective-rdf-mapping)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-07 Deterministic RDF Mapping Execution](05_functional_requirements.md#fr-sr-07-deterministic-rdf-mapping-execution)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-08 Hybrid Mapping Strategy with Automatic Fallback](05_functional_requirements.md#fr-sr-08-hybrid-mapping-strategy-with-automatic-fallback)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-09 Transformation Audit Trail](05_functional_requirements.md#fr-sr-09-transformation-audit-trail)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-10 Prompt Testing Interface](05_functional_requirements.md#fr-sr-10-prompt-testing-interface)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-11 LLM Configuration](05_functional_requirements.md#fr-sr-11-llm-configuration)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-12 Multi-Model Provider Support](05_functional_requirements.md#fr-sr-12-multi-model-provider-support)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-SR-13 Batch Re-transformation](05_functional_requirements.md#fr-sr-13-batch-re-transformation)   
&nbsp;&nbsp;&nbsp;&nbsp;[5.3 Catalogue Registry](05_functional_requirements.md#53-catalogue-registry)   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-CR-01 Configure Remote Catalogues](05_functional_requirements.md#fr-cr-01-configure-remote-catalogues)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-CR-02 Configure Asset Types](05_functional_requirements.md#fr-cr-02-configure-asset-types)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-CR-03 Catalogue API Mapping](05_functional_requirements.md#fr-cr-03-catalogue-api-mapping)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.4 Access Control](05_functional_requirements.md#54-access-control)   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FR-AC-01 User Roles](05_functional_requirements.md#fr-ac-01-user-roles)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.5 General Interoperability](05_functional_requirements.md#55-general-interoperability)  
[6. Technical Architecture](06_technical_architecture.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.1 Flows of Interaction with the Components](06_technical_architecture.md#61-flows-of-interaction-with-the-components)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.2 ORCE Integration Requirements](06_technical_architecture.md#62-orce-integration-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.2.1 UI Generation with ORCE UI Builder](06_technical_architecture.md#621-ui-generation-with-orce-ui-builder)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.2.2 Use of ORCE Standard Components](06_technical_architecture.md#622-use-of-orce-standard-components)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.2.3 UI Structures Without Available ORCE Components](06_technical_architecture.md#623-ui-structures-without-available-orce-components)   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.2.4 Workflow Orchestration Using ORCE](06_technical_architecture.md#624-workflow-orchestration-using-orce)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.2.5 Integration Requirements](06_technical_architecture.md#625-integration-requirements)  
[7. Security & Trust](07_security_trust.md)  
[8. Deployment & Operations](08_deployment_operations.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[8.1 Deployment Profiles (Exemplary)](08_deployment_operations.md#81-deployment-profiles-exemplary)  
&nbsp;&nbsp;&nbsp;&nbsp;[8.2 Operational Requirements](08_deployment_operations.md#82-operational-requirements)  
[9. Standards & Protocols](09_standards_protocols.md)  
[10. Validation & Acceptance Criteria](10_validation_acceptance_criteria.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.1 Protocol Conformance](10_validation_acceptance_criteria.md#101-protocol-conformance)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.2 Functional Tests](10_validation_acceptance_criteria.md#102-functional-tests)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.3 Security Tests](10_validation_acceptance_criteria.md#103-security-tests)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.4 Performance Tests](10_validation_acceptance_criteria.md#104-performance-tests)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.5 Operational Tests](10_validation_acceptance_criteria.md#105-operational-tests)  
[11. Requirements Traceability Matrix](11_requirements_traceability_matrix.md)  
[12. Appendices](12_appendices.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[Appendix A: Glossary](12_appendices.md#appendix-a-glossary)  
&nbsp;&nbsp;&nbsp;&nbsp;[Appendix B: References](12_appendices.md#appendix-b-references)  
&nbsp;&nbsp;&nbsp;&nbsp;[Appendix C: Possible Implementation of the Local Catalogue with the XFSC Federated Catalogue](12_appendices.md#appendix-c-possible-implementation-of-the-local-catalogue-with-the-xfsc-federated-catalogue)  
&nbsp;&nbsp;&nbsp;&nbsp;[Appendix D: Change Log Template](12_appendices.md#appendix-d-change-log-template)  

---

## Conformance Language

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, and OPTIONAL in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

---

## License

This work is licensed under the [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).

© eco – Association of the Internet Industry (eco – Verband der Internetwirtschaft e.V.)
