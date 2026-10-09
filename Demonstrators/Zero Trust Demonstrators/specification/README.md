![Version](https://img.shields.io/badge/version-1.0-blue)
[![License](https://img.shields.io/badge/license-CC--BY--4.0-orange)](http://creativecommons.org/licenses/by/4.0/)
[![PDF Specification](https://img.shields.io/badge/specification-PDF-blue)](https://github.com/eclipse-xfsc/facis/blob/main/Demonstrators/Zero%20Trust%20Demonstrators/specification/ZTD_Software_Requirements_Specification.pdf)
# Federation Architecture for Composed Infrastructure Services (FACIS) Zero Trust Demonstrator Specification

The FACIS  Zero Trust Demonstrator will showcase the interaction between two trust zones as individual Federations, which a sharing digital services between entitled participants and principals, based on Policy Rules.

---

## Table of Contents

[1. Introduction](markdown/01_introduction.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[1.1 Document Purpose](markdown/01_introduction.md#11-document-purpose)  
&nbsp;&nbsp;&nbsp;&nbsp;[1.2 Conformance Language](markdown/01_introduction.md#12-conformance-language)  
&nbsp;&nbsp;&nbsp;&nbsp;[1.3 Product Scope](markdown/01_introduction.md#13-product-scope)  
&nbsp;&nbsp;&nbsp;&nbsp;[1.4 Definitions, Acronyms and Abbreviations](markdown/01_introduction.md#14-definitions-acronyms-and-abbreviations)  
&nbsp;&nbsp;&nbsp;&nbsp;[1.5 References](markdown/01_introduction.md#15-references)  
[2. Product Overview](markdown/02_product_overview.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[2.1 Product Perspective](markdown/02_product_overview.md#21-product-perspective)  
&nbsp;&nbsp;&nbsp;&nbsp;[2.2 Product Functions](markdown/02_product_overview.md#22-product-functions)  
&nbsp;&nbsp;&nbsp;&nbsp;[2.3 Product Constraints](markdown/02_product_overview.md#23-product-constraints)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.1 Component Dependencies](markdown/02_product_overview.md#231-component-dependencies)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.2 License](markdown/02_product_overview.md#232-license)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3.3 Technology Selection](markdown/02_product_overview.md#233-technology-selection)  
&nbsp;&nbsp;&nbsp;&nbsp;[2.4 Operating Environment](markdown/02_product_overview.md#24-operating-environment)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.4.1 General](markdown/02_product_overview.md#241-general)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.4.2 Requirements](markdown/02_product_overview.md#242-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.4.3 Connectivity Target Architecture](markdown/02_product_overview.md#243-connectivity-target-architecture)  
&nbsp;&nbsp;&nbsp;&nbsp;[2.5 User Documentation](markdown/02_product_overview.md#25-user-documentation)  
&nbsp;&nbsp;&nbsp;&nbsp;[2.6 Assumptions and Dependencies](markdown/02_product_overview.md#26-assumptions-and-dependencies)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.6.1 Attestation Code Basis](markdown/02_product_overview.md#261-attestation-code-basis)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.6.2 Visualization](markdown/02_product_overview.md#262-visualization)  
&nbsp;&nbsp;&nbsp;&nbsp;[2.7 Apportioning of Requirements](markdown/02_product_overview.md#27-apportioning-of-requirements)  
[3. Requirements](markdown/03_requirements.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[3.1 Functional Requirements](markdown/03_requirements.md#31-functional-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.1.1 Zero Trust Connector](markdown/03_requirements.md#311-zero-trust-connector)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.1.2 Zero-Trust Service Mesh](markdown/03_requirements.md#312-zero-trust-service-mesh)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.1.3 Inter-Cluster Communication Protocol](markdown/03_requirements.md#313-inter-cluster-communication-protocol)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.1.4 Zero Trust Execution Environment](markdown/03_requirements.md#314-zero-trust-execution-environment)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.1.5 Zero Trust Application Communication](markdown/03_requirements.md#315-zero-trust-application-communication)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.1.6 Zero Trust Communication Visualization](markdown/03_requirements.md#316-zero-trust-communication-visualization)  
&nbsp;&nbsp;&nbsp;&nbsp;[3.2 Non-Functional Requirements](markdown/03_requirements.md#32-non-functional-requirements)  
&nbsp;&nbsp;&nbsp;&nbsp;[3.3 General Security Requirements](markdown/03_requirements.md#33-general-security-requirements)  
[4. Design and Implementation](markdown/04_design_and_implementation.md)  
[5. System Features](markdown/05_system_features.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.1 Zero Trust-based Service Mesh](markdown/05_system_features.md#51-zero-trust-based-service-mesh)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.1.1 Description](markdown/05_system_features.md#511-description)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.1.2 Architecture](markdown/05_system_features.md#512-architecture)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.1.3 Definition of Done](markdown/05_system_features.md#513-definition-of-done)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.2 Bidirectional Remote Attestation](markdown/05_system_features.md#52-bidirectional-remote-attestation)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.2.1 Description](markdown/05_system_features.md#521-description)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.2.2 Architecture](markdown/05_system_features.md#522-architecture)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.2.3 Definition of Done](markdown/05_system_features.md#523-definition-of-done)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.3 Zero Trust Execution Environment](markdown/05_system_features.md#53-zero-trust-execution-environment)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.3.1 Description](markdown/05_system_features.md#531-description)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.3.2 Architecture](markdown/05_system_features.md#532-architecture)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.3.3 Definition of Done](markdown/05_system_features.md#533-definition-of-done)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.4 Zero Trust Application Communication](markdown/05_system_features.md#54-zero-trust-application-communication)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.4.1 Description](markdown/05_system_features.md#541-description)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.4.2 Architecture](markdown/05_system_features.md#542-architecture)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.4.3 Definition of Done](markdown/05_system_features.md#543-definition-of-done)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.5 Zero Trust Communication Visualization](markdown/05_system_features.md#55-zero-trust-communication-visualization)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.5.1 Description](markdown/05_system_features.md#551-description)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.5.2 Architecture](markdown/05_system_features.md#552-architecture)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.5.3 Definition of Done](markdown/05_system_features.md#553-definition-of-done)  
[6. Appendix](markdown/06_appendix.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[Example of an Attested TLS Protocol](markdown/06_appendix.md#example-of-an-attested-tls-protocol)  

---

## License

This work is licensed under the [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).

© eco – Association of the Internet Industry (eco – Verband der Internetwirtschaft e.V.)
