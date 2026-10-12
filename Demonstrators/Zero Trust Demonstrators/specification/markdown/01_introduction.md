[↑ Table of Contents](../README.md) | [Product Overview →](02_product_overview.md)

---

## 1 Introduction

### 1.1 Document Purpose

The purpose of this document is to specify the product perspective, functions, and constraints of the FACIS Zero Trust (ZT) Demonstrator in preparation for a Europe-wide public tender for its implementation. It also defines the system features and specifies the functional and non-functional requirements of the product. The primary audience of this document is prospective bidders participating in the public tender who can provide a software solution to be released as open-source software under the Apache License 2.0.

### 1.2 Conformance Language

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, and OPTIONAL in this document are to be interpreted as described in [RFC 2119] and are written in capital letters.

### 1.3 Product Scope

#### In Scope

A software solution which can be installed within a Kubernetes cloud environment MUST be provided. The solution MUST be provided with all REQUIRED deployment artifacts and other REQUIRED software components and operational environment setups:

-  Helm Charts
-  Docker images
-  CI/CD definitions on GitHub and ArgoCD
-  Usage and integration of existing Eclipse [XFSC](https://github.com/eclipse-xfsc) components, e.g., OCM W-Stack and PCM Cloud
-  Software repositories within Eclipse XFSC GitHub repository
-  Documentation for deployment instructions, user manual, and operation instructions
-  Provision of BDD tests and test reports.


In the scope is a final acceptance presentation of the fully operational software solution on the two mentioned cloud environments.

#### Out of Scope 
Out of scope is the provision of cloud environments and network connectivity.


### 1.4 Definitions, Acronyms and Abbreviations

<p align="center"><em>Table 1 - List of Acronyms and Abbreviations</em></p>

|Acronym or Abbreviation|Term|Definition|
|---|---|---|
|ABAC|Attribute-Based Access Control|An access control model that grants or denies access to resources based on attributes of the user, resource, action, and environment.|
|BDD|Behavior Driven Development|A design methodic to ensure that a system fulfills requirements on the level of “business requirements”, often implemented in Gherkin syntax in combination with Cucumber.|
|CrBAC|Credential Based Access Control|Credential based access control is a special version of attribute-based access control, where all attributes are derived from signed credentials.|
|DE-CIX|Deutscher Commercial Internet Exchange|A global operator of Internet Exchange Points (IXPs) that enables networks to directly exchange internet traffic.|
|ORCE|Orchestration Engine|XFSC orchestration engine based on Node-RED.|
|TEE|Trusted Execution Environment|Hardware-isolated secure area of a processor that protects sensitive code and data from unauthorized access or tampering, even if the main system is compromised.|
|TEEM|TEE Measurement|The launch digest of a trusted execution environment.|
|TRAIN|Trust Management Infrastructure|An XFSC component that enables Gaia-X participants to establish and verify trust using decentralized trust lists and DNS anchoring.|
|TRAIN TCR|Trust Management Infrastructure Trust Content Resolver|TRAIN feature is responsible for the Trust Discovery and Trust Validation functionalities based on the input from the Verifiable Credential / Verifiable Presentation.|


### 1.5 References

<p align="center"><em>Table 2 - List of References</em></p>


|Reference ID|Description|Link|
|---|---|---|
|[SHACL]|W3C Shapes Constraint Language|https://w3.org/TR/shacl/<br><br>|
|[SPARQL]|W3C SPARQL 1.2 Query Language|https://w3.org/TR/sparql12-query/<br><br>|
|[VC]|W3C Verifiable Credentials Data Model v2.0|https://w3.org/TR/vc-data-model-2.0/<br><br>|
|[RFC2119]|Key words for use in RFCs (MUST/SHOULD/MA Y)|https://rfc-editor.org/rfc/rfc2119<br><br>|
|[NIST.800207]|NIST SP 800-207 Zero Trust Architecture|https://doi.org/10.6028/NIST.SP.800-207<br><br>|
|[BSI.TR02102]|BSI TR-02102 Cryptographic Mechanisms|https://www.bsi.bund.de/EN/Themen/Unternehmen-undOrganisationen/Standards-und-Zertifizierung/TechnischeRichtlinien/TR-nach-Thema-sortiert/tr02102/tr02102_node.html<br><br>|
|[DO-326A]|RTCA DO-326A / EUROCAE ED-202A Airworthiness Security Process Specification|https://rtca.org/security/<br><br>|
|[RFC8915]|RFC 8915 Network Time Security (NTS)|https://rfc-editor.org/rfc/rfc8915<br><br>|

---

[↑ Table of Contents](../README.md) | [Product Overview →](02_product_overview.md)

