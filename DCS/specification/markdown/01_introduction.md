[↑ Table of Contents](../README.md) · [Product Overview →](02_product_overview.md)

---

## 1 Introduction

This document provides the technical specifications of the Digital Contracting Service (DCS), a component developed within the “Federation Architecture for Composed Infrastructure Services” (FACIS) project to support contract lifecycle management in federated cloud and edge service environments.

### 1.1 Document Purpose

This document specifies the requirements for version 1.0 of the Digital Contracting Service. It serves as a formal specification that outlines the system’s functional and non-functional requirements, as well as its technical constraints, architectural context, and verification methods. The primary objective of the DCS is to enable secure, structured, and standards-based digital contracting processes that are interoperable across decentralized infrastructure and compliant with relevant legal and regulatory frameworks.

This specification is prepared in the context of tendering. The intended audience is potential contractors able to deliver an open-source solution that combines an intuitive front-end user interface with back-end capabilities to support core scenarios such as contract creation, structured negotiation, secure digital signing, long-term archiving, and automated compliance monitoring, in alignment with relevant European legal and technical standards.

### 1.2 Product Scope

The product scope covers the functionalities of the DCS, a modular, standards-based platform for secure, auditable, and legally compliant digital contract lifecycle management in federated cloud and edge environments. The product supports both bilateral and multilateral contracting use cases and is developed to interoperate seamlessly with emerging European trust infrastructures. The DCS as a product will form the foundation for extending the Federation Architecture Pattern for Digital Contracting, as part of the FACIS strategy.

A contract is a legally binding agreement between two or more parties with resulting rights and obligations. Digital contracts are digital agreements between transacting parties that are written in computer code [Ref1], and a service for digital contracts consists of programs that implement and enforce the execution of a contract [Ref-2]. They rely on electronic signatures for authentication and verification. In legal terms, the conclusion of a contract occurs when two or more parties reach a binding agreement through mutual declarations of intent – specifically, an offer and a corresponding acceptance. An offer is a clear and definite proposal made with the intention of being legally bound if accepted, while acceptance is an unconditional agreement to the exact terms of the offer. Both declarations must be communicated and reflect a shared intention to create legal relations.

The scope of the specification initially targets business-to-business (B2B) contacting scenarios rather than business-to-consumer (B2C). To be more specific, in FACIS a work on SLA contracts is being carried out to define high-level legal requirements for both human-readable and machine-readable contract formats, along with their data processing and conversion mechanisms. B2C support might be considered as an optional functionality.

In the DCS context, a digital contract is a contract expressed, managed, and executed in digital form, existing in both machine-readable and human-readable formats. Each contract is represented as a contract object, a digital instance with a defined lifecycle, semantic conditions, and states such as offered, accepted, rejected, and withdrawal. The contract metadata contains structured information such as title, version, creation date, governing law, and unique identifiers, ensuring traceability. Contract parties include all entities involved in the agreement, with their roles, identifiers, and contact details explicitly defined. The agreement content is

organized into contract components, which may include the main contract text, annexes, and attachments, each with its own precedence rules. The scope of work is described under service scope, accompanied by acceptance criteria defining the evidence and conditions required for formal approval. Where applicable, licensing Information outlines the usage rights for software, data, or intellectual property. The contract also incorporates contract conditions, which are specific clauses, obligations, or regulatory requirements, and semantic conditions, which are machine-readable clauses enabling automated validation. Additional agreements & clauses, such as confidentiality or liability limitations, may also be included. Signature Information records the signatories, their signature types, timestamps, and legal evidence to ensure authenticity and enforceability.

A contract scenario in the DCS defines a legally binding agreement based on approved templates that embed usage policies and constraints. To give an example of such a scenario, a cultural institution could create a contract template to regulate access to its data API. The contract specifies geospatial and temporal restrictions (e.g., access limited to German organizations, with an expiry date). Usage policies are expressed as machine-readable semantic conditions that DCS validates at approval/signing and deploys to the Contract Target System (e.g., API gateway) for automated runtime enforcement. An interested organization negotiates and reviews the contract, and after mutual signing and verification of credentials, access to the API is granted under the agreed terms. Lifecycle management governs state transitions (offered → accepted → executed → active → terminated → archived), triggers renewal and expiry alerts, and revokes access if credentials are invalidated or terms are breached. Executed contracts, signatures, and validation artifacts are preserved with verifiable timestamps in a tamper-evident archive, ensuring auditability and legal traceability. A JSON-LD contract example is provided in the Appendix.

Key functional capabilities within the product scope are as follows:

- Multi-Contract Signing: Enables multi-party contract execution within a single integrated workflow.
- Automated Workflows: Automates contract generation, execution, and deployment to ensure legal consistency and efficiency.
- Lifecycle Management: Monitors contracts with alerts for renewals, expirations, or required actions.
- Signature Management: Links contract signatures to verifiable digital identities to maintain legal validity and trust.
- Secure Archiving: Stores signed contracts in a tamper-evident archive compliant with retention policies.
- Machine Signing: Supports automated signing for high-volume or routine transactions.


Digital contracts rely on electronic signatures for authentication and verification. Regarding signatures, it should be noted that digital signatures and seals must be qualified to sign legally valid contracts. Qualified electronic signatures (QES) must be traceable to a natural person. Qualified electronic seals are their equivalent for organizations. JAdES, PAdES, and XAdES are specifications that must be complied with when creating so-called advanced signatures on JSON, PDF, and XML documents.

The product scope focuses on the use of Advanced Electronic Signatures (AES) for authentication, allowing for the descope QES and the integration of remote signing services and Trust Service Providers (TSP). Should the product move to production, it will be the responsibility of the integrating party to connect to remote signing services and TSPs. Specifically, the company will sign DCS usage contract via OID4VP, with the user signing it using their AES PID. This contract is then stored and referenced through a role, along with the signed contracts.

The architecture SHOULD include an optional module to integrate a remote QES signing services of a Trust Service Provider (e.g., D-Trust) with the “Signature Management” Module of the functional architecture. This integration can be considered “optional.”

DCS provides both an intuitive web interface and back-end services, integrating with XFSC components. For this reason, the product extension must include interfaces (APIs) to integrate the DCS smoothly with XFSC

components and identity wallets. Building and operating these XFSC components are considered out of the product scope.

Regarding policies, DCS considers only two types of policies: namely DCS-to-DCS data exchange and access control for users to access DCS. In DCS-to-DCS data exchange, DCS is limited to offering the data information endpoint that provides the relevant contract information to be used for policy enforcement. For authorization and authentication of users to act with the defined roles in the system, the company or organization using DCS is expected to register employees or organization members with the user roles to the DCS over identity wallets.

### 1.3 Definitions, Acronyms and Abbreviations

Acronyms and abbreviations used in this document are defined in Table 1, while Table 2 contains the definitions of key terms essential for interpreting the requirements. Additional or supplementary definitions that provide extended context are collected in Appendix A: Glossary.

<p align="center"><em>Table 1 – List of acronyms and abbreviations</em></p>

|Acronym or Abbreviation|Term|Definition|
|---|---|---|
|AES|Advanced Electronic Signature|A type of electronic signature that is uniquely linked to the signer and capable of identifying them, offering a higher level of assurance than simple electronic signatures.|
|API|Application Programming Interface|A set of rules and protocols for building and interacting with software applications, enabling communication between different systems.|
|B2B|Business-to-Business|Commercial transactions conducted directly between businesses.|
|B2C|Business-to-Consumer|Commercial transactions conducted directly between a business and end consumers.|
|BDD|Behavior-Driven Development|A development approach that defines software behavior in natural language for shared understanding.|
|C2PA|Coalition for Content Provenance and Authenticity|Standards for attaching provenance metadata and cryptographic assertions to digital content.|
|CAT|Federated Catalogue|A service for publishing, discovering, and requesting assets within the federation.|
|CRUD|Create, Read, Update, and Delete|Four basic operations performed on persistent data in databases or storage systems.|
|CSA|Contract Storage and Archive|Digital Contracting Service software component for archiving signed contracts in tamper-proof, long-term storage.|
|CWE|Contract Workflow Engine|Digital Contracting Service software component managing the life cycle and progression of contracts through defined steps.|
|DCS|Digital Contracting Service|A modular, standards-aligned platform for the secure, verifiable, and automated lifecycle management of digital contracts.|
|DSS|Digital Signature Service|An open-source library for creating and validating electronic signatures in compliance with European eIDAS regulations, usable in apps, standalone, or server solutions.|
|DID|Decentralized Identifier|A globally unique identifier enabling verifiable, self-sovereign digital identity.|
|ECO|ECO – Verband der Internetwirtschaft e.V|The German Association of the Internet Industry, representing companies involved in internet infrastructure, services, content, and applications.|
|ERP|Enterprise Resource Planning|An integrated business software suite for business operations.|
|ETSI|European Telecommunications Standards Institute|European standards organization for ICT|
|EUDI|European Digital Identity|An EU framework for a secure and interoperable digital identity wallet.|
|FACIS|Federated Architecture for Cloud and Edge Services|An initiative framework for secure and interoperable federation-based service delivery.|
|FR|Functional Requirement|A specification of a function or behavior the system must perform to meet business objectives.|
|IPCEI-CIS|Important Project of Common European Interest – Cloud Infrastructure and Services|An EU-driven initiative to foster large-scale, cross-border cloud and infrastructure projects of strategic importance.|
|JAdES|JSON Advanced Electronic Signatures|An ETSI standard specifying advanced electronic signatures in JSON-based documents.|
|JSON-LD|JavaScript Object Notation for Linked Data|A JSON-based format to serialize Linked Data, i.e., RDF, enabling integration with semantic web technologies.|
|NFR|Non-Functional Requirement|A specification of a quality attribute, constraint, or performance criterion that defines how a system must operate rather than what it should do|
|OCM W|Organizational Credential Manager – Wallet|A wallet component for managing organizational credentials in federated environments.|
|PACM|Process Audit & Compliance|DCS software component that maintains tamper-proof records and supports compliance and auditing functions.|
|PAdES|PDF Advanced Electronic Signatures|An ETSI standard for advanced electronic signatures embedded in PDF documents.|
|PCM|Personal Credential Manager|A wallet component for managing credentials of natural persons.|
|PoA|Power of Attorney|A credential granting the holder authority to act on behalf of another party.|
|PR|Participant|A legal entity officially onboarded to a Federation, capable of taking on roles such as Provider, Consumer, or Federator.|
|RBAC|Role-Based Access Control|A security model that restricts system access based on users’ roles and assigned permissions.|
|RDF|Resource Description Framework|W3C standard model for data interchange on the web.|
|QES|Qualified Electronic Signature|The highest standard of electronic signature under eIDAS, with the same legal standing as a handwritten signature.|
|REST|Representational State Transfer|An architectural style for distributed hypermedia systems, often used in web service APIs.|
|SES|Simple Electronic Signature|An electronic form of a signature, such as typing a name in an email, used to sign or associate with electronic data.|
|SLA|Service Level Agreement|A formal contract between a service provider and a customer defining performance and service standards.|
|SHACL|Shapes Constraint Language|A W3C standard for validating RDF data against a set of conditions (shapes).|
|SM|Signature Management|A component responsible for applying, verifying, and managing electronic signatures on contracts.|
|TR|Template Repository|DCS software component for storing and managing contract templates in both machine-readable and human-readable formats.|
|TSP|Trust Service Provider|An entity that provides and manages digital certificates and related trust services under eIDAS.|
|UI|User Interface|Visual and interactive elements through which a user interacts with the system.|
|UUID|Universally Unique Identifier|A 128-bit identifier used to uniquely identify information in computer systems.|
|VC|Verifiable Credential|A cryptographically verifiable statement issued about a subject, following the W3C standard.|
|W3C|World Wide Web Consortium|The main international standards organization for the World Wide Web.|
|XFSC|Cross Federation Services Components|A set of modular components enabling federation-level integration, orchestration, and interoperability.|


<p align="center"><em>Table 2 – List of terms and definitions</em></p>

|Term|Definition|Link|
|---|---|---|
|Acceptance|An unconditional agreement to the exact terms of an offer, communicated between parties with the intent of creating legal relations.|See section 1.2|
|Additional Agreements & Clauses|Supplementary legal provisions included in a contract, such as confidentiality terms, liability limitations, and penalties for noncompliance.|See section 1.2|
|Audit-Proof Storage|Storage method ensuring contracts cannot be altered or deleted without detection, with verifiable proof of integrity over time.|See section 2.2.4|
|Audit Trail|An immutable record of significant actions taken during the contract lifecycle, including timestamps, user or system role, and action details.|See section 3.2.5|
|Compliance Check|Verification mechanism that a contract meets defined legal, regulatory, or policy requirements.|See section 3.2.5|
|Contract|A legally binding agreement between two or more parties with enforceable rights and obligations, containing an offer, acceptance, mutual intent, legal capacity, lawful purpose, and where applicable, consideration.|See section 1.2|
|Contract Adjustment|Adding, removing, and modification of specific clauses, terms, or data points in an existing contract during negotiation phase between the parties. When an adjustment is accepted by both parties, it creates a new version of the contract under the same contract ID, and the system re-renders the human-readable view to ensure consistency across formats.|See section 2.2.2|
|Contract Assembly|The process of combining selected metadata and components from the template with additional agreements & clauses into a complete contract document.|See section 3.2.2|
|Contract Change Request|A formal, version-controlled request to modify an already-created or active contract.|See section 2.2.2|
|Contract Conditions|Specific clauses, terms, or requirements that form part of a contract’s content and may be negotiated before signing.|See section 1.2|
|Contract Deployment|The release of a finalized, machine-readable contract to designated service endpoints for automated execution.|See section 2.2.2|
|Contract Identifier|A unique and persistent reference assigned to each contract for tracking and retrieval across systems.|See section 2.2.4|
|Contract Initiation|The process of starting contract creation by submitting a request, identifying the initiating and responding parties, and selecting a matching template.|See section 2.2.2|
|Contract Lifecycle|The complete set of stages from contract creation through negotiation, approval, signing, performance tracking, renewal or termination, and archival.|See section 2.1|
|Contract Negotiation|A collaborative process where involved parties propose, review, and agree on changes to a draft contract before finalization.|See section 3.2.2|
|Contract Object|A digital representation of a contractual agreement content with a defined lifecycle, semantic conditions, and states (e.g., offered, accepted, rejected, withdrawal).|See section 1.2|
|Contract Performance Monitoring|The tracking and assessment of contractual obligations against agreed metrics and deadlines throughout the contract lifecycle.|See section 4.6|
|Contract Renewal|The continuation of an existing contract’s validity through an agreed extension before its expiration date. Contract adjustments MAY be made during contract renewal phase.|See section 4.6|
|Contract Request|The submission that starts contract creation, identifying parties and the contract template to use.|See section 2.2.2.|
|Contract Target System|An external system that receives and executes deployed contracts.|See section 4.5|
|Contract Versioning|Contract versioning is the practice of creating and managing uniquely identified, immutable records of each draft, revision, and executed form of a contract, ensuring a clear history of changes, traceable authorship, and verifiable integrity over time.|See section 2.2.4|
|Contract Termination|The structured process of ending a contract, either by mutual or multi-party agreement or predefined conditions, including archival.|See section 4.6|
|Digital Contract|A contract expressed, managed, and executed in digital form, existing either in both machine-readable or human-readable formats, or both.|See section 1.2|
|Electronic Signature|Data in electronic form attached to or associated with a document to sign it.|See section 1.2|
|HumanReadable Contract|A natural language version of a contract intended for human interpretation.|See section 1.2|
|Identity Verification|The process of confirming the identity of contracting parties, possibly via digital wallets, DSS, or other secure methods.|See section 2.2.3|
|Initiator|The party that submits the initial contract request in a bilateral or multilateral workflow.|See section 2.2.2|
|Immutable Signing|The property that once a contract has been signed by all parties, its content cannot be altered without invalidating the signatures.|See section 3.2|
|Legal Capacity|The ability of a party to enter into a binding contract, typically requiring legal age and mental competence.|See section 1.2|
|Lifecycle States|The defined progression of a contract object, including at least the states: offered, accepted, rejected, and withdrawal.|See section 2.2.2|
|MachineReadable Contract|A structured, computer-processable representation of a contract.|See section 1.2|
|Multilateral Contract|A contract involving more than two parties.|See section 1.2|
|Offer|A clear, definite proposal to enter into a contract, made with intent to be legally bound if accepted.|See section 1.2|
|Policy|A formal, machine-enforceable set of rules and constraints that govern the behavior of the DCS. The scope of policies is limited to DCS-to-DCS connection and user access to DCS.|See section 1.2|
|Provenance Tracking|Recording the origin, history, and changes to a document or template to ensure authenticity and traceability.|See section 2.2.1|
|Responder|The party (or parties) that receive a contract request in a bilateral or multilateral workflow.|See section 2.2.2|
|Revocation|The process of invalidating credentials or signatures to prevent further use.|See section 4.15|
|Semantic Conditions|Machine-readable conditions or clauses within a contract that can be processed, validated, and tracked automatically.|See section 1.2|


### 1.4 References

<p align="center"><em>Table 3 – List of references</em></p>

|Reference ID|Description|Link|
|---|---|---|
|[AES]|Advanced Electronic Signature (eIDAS).|https://eur-lex.europa.eu/eli/reg/2014/910/oj<br><br>|
|[Animo]|Animo Solutions framework for SSI wallet and credential integration.|https://animo.id<br><br>|
|[ARF]|EU Digital Identity Wallet Architecture and Reference Framework (ARF).|https://digital-strategy.ec.europa.eu/en/library/europeandigital-identity-wallet-architecture-and-referenceframework<br><br>|
|[ArgoCD]|GitOps continuous delivery for Kubernetes.|https://argo-cd.readthedocs.io/en/stable/<br><br>|
|[BDD Executor]|XFSC bdd-executor – Framework to define and run executable Behavior-driven development scenarios|https://github.com/eclipse-xfsc/bdd-executor<br><br>|
|[BSI]|German Federal Office for Information Security (crypto guidance).|https://www.bsi.bund.de/EN<br><br>|
|[CAdES]|CMS Advanced Electronic Signatures.|https://en.wikipedia.org/wiki/CAdES_(computing)<br><br>|
|[CAT.AD]|Architecture of XFSC Catalogue.|https://gaia-x.eu https://gaia-x.gitlab.io/data-infrastructure-federationservices/cat/architecturedocument/architecture/catalogue-architecture.html<br><br>|
|[DID]|W3C Decentralized Identifiers v1.0.|https://www.w3.org/TR/did-1.0/<br><br>|
|[DIDcomm]|DIDComm Messaging v2.|https://identity.foundation/didcomm-messaging/spec/v2/<br><br>|
|[Docker]|Container runtime / tooling.|https://www.docker.com<br><br>|
|[EUDI]|European Digital Identity Wallet framework.|https://digital-strategy.ec.europa.eu/en/policies/eudiwallet<br><br>|
|[Gaia X]|Federation / data space initiative.|https://gaia-x.eu<br><br>|
|[GDPR]|EU General Data Protection Regulation.|https://eur-lex.europa.eu/eli/reg/2016/679/oj<br><br>|
|[GitHub Actions]|CI/CD service.|https://docs.github.com/actions<br><br>|
|[Helm]|Kubernetes package manager.|https://helm.sh<br><br>|
|[IPCEI CIS]|Important Project of Common European Interest – Cloud Infrastructure & Services.|https://digital-strategy.ec.europa.eu/en/policies/ipceicloud<br><br>|
|[ISO/IEC 27001]|Information security management.|https://www.iso.org/standard/27001.html<br><br>|
|[JAdES]|ETSI JSON Advanced Electronic Signatures.|https://www.etsi.org/committee/esi<br><br>|
|[JSON LD]|JSON for Linked Data 1.1.|https://www.w3.org/TR/json-ld11/<br><br>|
|[Kubernetes]|Container orchestration.|https://kubernetes.io<br><br>|
|[NATS]|High performance messaging.|https://nats.io<br><br>|
|[NodeRED]|Flow-based development tool for visual programming.|https://nodered.org<br><br>|
|[OAuth2]|OAuth 2.0 authorization framework.|https://www.rfc-editor.org/rfc/rfc6749<br><br>|
|[OIDC]|OpenID Connect Core 1.0.|https://openid.net/specs/openid-connect-core-1_0.html<br><br>|
|[OpenID4VC]|OpenID for Verifiable Credential Issuance (OID4VCI) 1.0.|https://openid.net/specs/openid-4-verifiable-credentialissuance-1_0.html<br><br>|
|[OpenID4VP]|OpenID for Verifiable Presentations (OID4VP) 1.0.|https://openid.net/specs/openid-4-verifiablepresentations-1_0.html<br><br>|
|[Ory/Hydra]|Open source OAuth2/OIDC server used for secure access and authentication.|https://www.ory.sh/hydra/docs/<br><br>|
|[PAdES]|PDF Advanced Electronic Signatures.|https://en.wikipedia.org/wiki/PAdES<br><br>|
|[PDF/A-3]|Archival PDF (ISO 19005 3).|https://www.iso.org/standard/54534.html<br><br>|
|[PoA]|Power of Attorney credential chain.|https://en.wikipedia.org/wiki/Power_of_attorney<br><br>|
|[PostgreSQL]|Relational database (Postgres compatible).|https://www.postgresql.org<br><br>|
|[QES]|Qualified Electronic Signature (eIDAS).|https://eur-lex.europa.eu/eli/reg/2014/910/oj<br><br>|
|[REST]|Representational State Transfer (architectural style).|https://www.ics.uci.edu/~fielding/pubs/dissertation/fielding_dissertation.pdf<br><br>|
|[RFC 2119]|Keywords to state requirement levels.|https://www.rfc-editor.org/rfc/rfc2119<br><br>|
|[SCS]|Sovereign Cloud Stack.|https://sovereigncloudstack.org<br><br>|
|[SDE.DCS]|Gaia-X Federation Services Sovereign Data Exchange Data Contract Service.|https://www.gxfs.eu/data-contract-service/<br><br>|
|[SHACL]|Shapes Constraint Language.|https://www.w3.org/TR/shacl/<br><br>|
|[SOG-IS]|Senior Officials Group – Information Systems Security (crypto guidance).|https://www.sogis.eu<br><br>|
|[SSI]|Self-Sovereign Identity concept.|https://en.wikipedia.org/wiki/Self-sovereign_identity<br><br>|
|[TLS 1.3]|Transport Layer Security v1.3.|https://www.rfc-editor.org/rfc/rfc8446<br><br>|
|[TSP]|Trust Service Provider (eIDAS/ETSI).|https://www.etsi.org/technologies/trust-service-providers<br><br>|
|[UUID]|Universally Unique Identifier.|https://www.rfc-editor.org/rfc/rfc4122<br><br>|
|[VC]|W3C Verifiable Credentials Data Model v2.0.|https://www.w3.org/TR/vc-data-model-2.0/<br><br>|
|[WACI]|Wallet & Credential Interaction – Presentation Exchange.|https://identity.foundation/waci-presentation-exchange/<br><br>|
|[WCAG]|Web Content Accessibility Guidelines.|https://www.w3.org/TR/WCAG21/<br><br>|
|[XFSC]|Eclipse Cross Federation Services Components.|https://projects.eclipse.org/projects/technology.xfsc<br><br>|
|[Ref-1]|Law, A. Smart contracts and their application in supply chain management|https://dspace.mit.edu/handle/1721.1/114082|
|[Ref-2]|Das, A. et al. ResourceAware Session Types for Digital Contracts|https://doi.org/10.1109/CSF51468.2021.00004|



### 1.5 Document Overview

This document describes the product perspective, functions, and constraints of the Digital Contracting Service. It defines the system features in detail, including both functional and non-functional requirements, and specifies binding requirements for the development and operation of the system. All functional requirements are identified by a unique ID in square brackets following the format [DCS-FR-<Component Code>-<Number>], and all non-functional requirements follow the format [DCS-NFR-<Number>]. Component codes (e.g., TR for Template Repository, CWE for Contract Workflow Engine, SM for Signature Management, CSA for Contract Storage and Archive, PACM for Process Audit & Compliance) correspond to the major subsystems described in this document. Requirements use the keywords MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY as defined in RFC 2119 [RFC 2119].

---

[↑ Table of Contents](../README.md) · [Product Overview →](02_product_overview.md)

