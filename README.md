# FACIS Project (Federation Architecture for Composed Infrastructure Services)

## Introduction  
**FACIS** stands for *Federation Architecture for Composed Infrastructure Services*.  
It pioneers the future of digital ecosystems in Europe by addressing fundamental challenges such as **interoperability**, **governance frameworks**, and the increasing demand for distributed and flexible infrastructures.  

FACIS combines innovative technologies such as **Federation Architecture Patterns (FAPs)**, **machine-readable Service Level Agreements (SLAs)**, and **low-code orchestration engines**, together with strong governance frameworks, to build a multi-provider cloud-edge continuum.  

This approach improves scalability, security, and compliance with regulations, while enabling organizations to retain control of their data. FACIS is an **open-source and collaborative project** that promotes transparency, inclusiveness, and innovation across the European digital ecosystem.  

---

## Key Objectives and Features  

- **SLA Governance Framework**  
  FACIS introduces a framework for governing **Service Level Agreements (SLAs)** across federated ecosystems.  
  Instead of static, text-heavy documents, FACIS promotes **machine-readable SLAs** that can be enforced and monitored automatically.  
  This ensures quality of service, reliability, and compliance across multiple providers and borders.  
  It also reduces operational complexity by enabling automated SLA negotiation, violation detection, and adaptation in real time.  

- **Digital Contracting Service (DCS)**  
  The **Digital Contracting Service** provides an **open-source platform** for creating, signing, and managing contracts digitally.  
  Integrated with the **European Digital Identity Wallet (EUDI)**, it guarantees that all digital transactions are secure, legally binding, and interoperable.  
  DCS allows organizations to streamline business processes, reduce paperwork, and ensure **compliance with eIDAS 2.0 regulations**, while fostering trust across federated partners.  

- **Federation Architecture Patterns (FAPs)**  
  At the core of FACIS are **Federation Architecture Patterns (FAPs)** – reusable, pre-defined technical blueprints.  
  These patterns provide structured templates for designing interoperable digital ecosystems.  
  With FAPs, companies can integrate diverse IT systems, cloud services, and data-sharing platforms **without losing autonomy**.  
  By offering modular, open-source designs, FAPs simplify federation-building, lower integration costs, and accelerate adoption across industries.  

---

## What is a FAP?  

A **Federation Architecture Pattern (FAP)** is a **modular, reusable blueprint** that provides ready-made templates for building collaborative digital ecosystems.  

- **The Problem:** Every vendor and company uses different technologies, standards, and infrastructures. Connecting them securely and efficiently is often costly and complex.  
- **The Solution:** FAPs deliver **pre-built, open-source technical patterns** that act like **construction plans** for your digital infrastructure. They help integrate different systems seamlessly, reducing complexity and ensuring interoperability from the start.  
- **Benefits for Industry:**  
  - Pre-built templates for faster integration  
  - Free, open-source blueprints adaptable to many industries  
  - Reduced complexity in multi-company collaboration  
  - Boosted innovation in Industry 4.0 (real-time monitoring, efficiency optimization, reduced downtime)  
- **How It Works:**  
  Each FAP defines **governance, identity management, credential handling, SLA monitoring, and orchestration flows**, ensuring that partners can connect their systems quickly and securely. Organizations retain **full control of their own data and services** while adhering to a **shared governance model**.  
- **Availability:**  
  The first FAPs will be made available in **Q3 2025**, with more released gradually through the official [FACIS website](https://www.facis.eu) and the [Eclipse XFSC GitHub repository](https://github.com/eclipse-xfsc).  

In essence, **FAPs are the building blocks of digital federation**, enabling independent organizations to collaborate while safeguarding sovereignty, compliance, and trust.  

---

## About FAPs & FRAME  
FACIS leverages **Federation Architecture Patterns (FAPs)** as the **core blueprint** for interoperability in federated ecosystems.  
- **Feature-FAPs**: modular building blocks addressing major domains (e.g., Storage, Authentication).  
- **Micro-FAPs**: executable units handling small, focused tasks (e.g., install CAT service, validate credential).  
- **FRAME** (FAP Readiness & Architecture Model for Ecosystems) provides the **scalable backbone** of FAPs – ensuring they are modular, reusable, and compliant across diverse providers.  
- FAPs are aligned with open-source ecosystems such as **Gaia-X, XFSC, IDS, FIWARE, Tractus-X**, ensuring broad adoption and reusability.  

**Core Functions of FACIS & FRAME:**  
- Low-code orchestration with the **XFSC Orchestrator**  
- Establishment of an **OSS repository** for FAPs under Eclipse Foundation  
- Delivery of **executable FAPs as templates**  
- Provision of **demo environments** for validation and PoC  

---

## FRAME Methodology & Lifecycle  
The **FRAME methodology** defines a systematic lifecycle for developing FAPs:  
1. **Use Case Identification** – Define the goals and challenges.  
2. **Stakeholder Engagement** – Collect requirements via workshops.  
3. **Scenario Specification** – Define Base FAPs and Vertical FAPs.  
4. **Low-Code Orchestration** – Develop executable templates with XFSC Orchestrator.  
5. **Integration with OSS** – Leverage Gaia-X, XFSC, IDS, Tractus-X, FIWARE.  
6. **Prototyping & Testing** – Build demo environments and validate functionality.  
7. **Quality Assurance** – Conduct compliance and interoperability validation.  
8. **Technical Provisioning** – Provide repositories, testbeds, registries.  
9. **Implementation & Integration** – Deploy FAPs into federated environments.  
10. **Dissemination & Community Building** – Publish results, workshops, open repos.  
11. **Final Validation & Approval** – Formal review and sign-off.  

This lifecycle ensures that each FAP is **standardized, tested, and reusable** across federated ecosystems.  

---

## FACIS FAP1 Breakdown  
The first Federation Architecture Pattern (**FAP1**) is structured into **five Feature-FAPs**, each containing several Micro-FAPs that handle specific functions:  

1. **Storage**  
   - CAT (Catalog): Registers participants and services  
   - OCM (Organization Credential Manager): Stores and manages organizational credentials  
   - PCM Cloud (Personal Credential Manager): Handles personal user credentials  
   - Integration with ORCE for orchestration, scaling, and resource allocation  

2. **Onboarding Wizard**  
   - Multi-step user interface for onboarding new participants  
   - Wizard orchestration logic to guide flows  
   - Basic integration with authentication and backend services  

3. **Credential Management & Validation**  
   - Credential issuance based on onboarding/authentication data  
   - Validation engine (signature, JSON format, revocation list)  
   - Lifecycle management: renewals and revocations  

4. **Authentication**  
   - Supports OAuth2, SAML, and OIDC  
   - Role/Policy service (RBAC/ABAC)  
   - Session management and security hooks  

5. **GXDCH Connect**  
   - Integration with Gaia-X Digital Clearing House  
   - Credential issuance and validation against Gaia-X standards  
   - Auditing and notification for compliance events  

---

## Example Use Cases (FAPs)  
Beyond FAP1, FACIS defines additional **base and vertical FAPs**:  
- **Partner Registration** (reference FAP for onboarding)  
- **Digital Contract Creation** (secure, compliant digital contracting)  
- **Validation of Distributed Information Objects** (e.g., Product Passport)  
- **AI Training Framework** (collaborative AI pipelines)  
- **Collaborative Condition Monitoring** (federated monitoring across providers)  

---

## Planned Deliverables (WP1)  
According to the WP1 FAP Plan:  
- **5 Base FAPs** (Partner Registration, Digital Contract Creation, Validation of Distributed Information Objects, AI Training Framework, Collaborative Condition Monitoring)  
- **3–5 Vertical FAPs (V-FAPs)** developed for domain-specific use cases  
- **OSS Repository for FAPs** hosted under Eclipse Foundation  
- **FAPs Testbed** for operational testing and validation  

---

## Synergies with PoC  
FAPs are closely linked to **Proof of Concepts (PoCs)**, ensuring smooth transition from design to real-world validation:  
- Use case identification in FAPs ↔ business problem definition in PoC  
- Scenario specifications in FAPs ↔ technical requirements in PoC  
- Low-code orchestration in FAPs informs tool selection in PoC  
- QA in FAPs ↔ risk assessment & validation in PoC  

This alignment accelerates adoption by ensuring architectural patterns are validated through **industry-grade pilots**.  

---

## Roadmap (High-Level)  
The development of FAP1 follows a phased approach:  
- **Phase 1**: Core infrastructure and Storage services (CAT, OCM, PCM)  
- **Phase 2**: Authentication services  
- **Phase 3**: Onboarding Wizard front-end & orchestration  
- **Phase 4**: Credential Management & Validation flows  
- **Phase 5**: Full Gaia-X compliance via GXDCH Connect  

---

## Roles & Responsibilities  
- **Technical Lead (Project Architect)** – Oversees overall FAP architecture and compliance  
- **Implementation Team (Dev & DevOps)** – Develops Micro-FAPs, integration scripts, and containers  
- **Infrastructure Team (K8s, Networking, Security)** – Manages server, cluster, and scaling operations  
- **Compliance & QA Team** – Validates compliance (Gaia-X, eIDAS) and conducts acceptance testing  
- **Stakeholders / eco PMO / WP1** – Align with FACIS goals, review progress, and approve deliverables  

---

## Requirements for New Use Cases  
To be transformed into FAPs, new use cases must meet key requirements:  
- Alignment with **IPCEI-CIS goals** and federated ecosystem principles  
- Clearly defined **use case scenario** and expected outcomes  
- Integration with **federated systems** (Gaia-X, XFSC, IDS, etc.)  
- Compliance with **open-source principles**  
- Consideration of **data sovereignty, privacy, GDPR**  
- Adaptability to **low-code orchestration with XFSC Orchestrator**  
- Integration of **security and trust frameworks**  
- Potential use of **AI & automation**  
- Scalability, flexibility, and performance metrics  
- Comprehensive **documentation, testing, and validation**  
- Contribution to **open-source community** via Eclipse Foundation  

---

## Potential Extensions  
Future enhancements and extensions include:  
- SLA Governance (latency, uptime tracking, SLA violation detection)  
- Analytics & AI integration for anomaly detection and dashboards  
- Multi-region and edge deployments for compliance and data residency  
- Open-source release of Micro-FAPs with Docker images and adapters  

---

## Installation and Usage  
All outcomes of the FACIS project will be provided as **open-source**. Organizations and developers can access these tools through the **official FACIS website** and the related GitHub repositories.  

FAPs are expected to be available starting from **Q3 2025** on GitHub under the `eclipse-xfsc` organization. Each pattern will include code, documentation, and a deployable low-code orchestration engine.  

---

## Contributing  
FACIS is part of the **Eclipse XFSC Project (Cross Federation Services Components)**.  
Contributors are welcome to collaborate via GitHub under the organization [`eclipse-xfsc`](https://github.com/eclipse-xfsc).  

To contribute, you need to sign the **Eclipse Contributor Agreement (ECA)** and then fork and submit pull requests to the corresponding repository.  

This repository serve as the central-entry point for all the FACIS components. 
| Component | Primary Goal | Repository Link |
|-----------|--------------|-----------------|
| FAP (Federation Architecture Pattern) | Standardized Blueprints for building federated services to connect different companies securely. | `eclipse-xfsc/facis-fap` |
| DCS (Data Connector Service) | open-source software for secure, automated and legally compliant contract services. | `eclipse-xfsc/facis` (Linked within the main Facis repo) |
| SLA (Service Level Agreements) | Defines the governance framework to ensure performance, security and accountability across multiple providers. | `eclipse-xfsc/facis` (Linked within the main Facis repo) |
| POC (Proof-Of-Concepts) | Real-world scenarios implementation and validation demonstrating the FAPs and DCS. | `eclipse-xfsc/facis-poc` |

### Core Component Repositories
These are the main repositories where the development work takes place. 

#### 1. FACIS-FAP (`eclipse-xfsc/facis-fap`)
This repository is responsible for implementing the standarized templates/ blueprints for the specific collaboration use cases.
- Patner onboarding (reference #facis-fap1-breakdown)
  - Specification - Technical and Functional requirements.
  - Implementation - Source code for FAP
- Other FAP directories

#### 2. FACIS-PoC (`eclipse-xfsc/facis-poc`)
This repository contains the examples of how FAPs and DCS are combined to solve the real-world problems.
- Federation Collaboration
  - Specification - Defines the use cases and the expected results.
  - Implementation - Source code and validation for the use cases.
- Other PoC directories

#### 3. Trusted Coud ('eclipse-xfsc/facis/trusted-cloud)
This repository provides the specification and implementation for the project focused on the trusted cloud services. 
- Specificaton - Detailed definition of the trusted service requirements.
- Implementation - Source code for the trusted services.

### Orchestration and Deployment Tools
These repositories contains the source code to deploy and manage the federation services according to the FAPs.
#### 4. Smart Deployment (`eclipse-xfsc/smart-deployment`)
- Main Sub-components (Easy Stack Builder (ESB))
  - ORCE (Orchestration Engine)
  - Catalogue
  - OCM-WStack
  - PCM
  - AA
- AIFlow Builder

#### 5. Orchestration Engine (`eclipse-xfsc/facis/orchestration-engine)
This repository manages service flows and monitor performance.
- core orchestration engine
- Additional Folder
  - scenarios/aw40-demonstrator
---

## Resources  
- Official Website: [facis.eu](https://www.facis.eu)  
- Eclipse XFSC Developer Hub: [eclipse-xfsc.github.io](https://eclipse-xfsc.github.io/landingpage/)  
- GitHub Repositories: [github.com/eclipse-xfsc](https://github.com/eclipse-xfsc)  

---

## License  
This project is released under the **Apache 2.0 License**.  

---

By contributing to FACIS, you are part of building the future of a **federated, secure, scalable, and trusted cloud-edge ecosystem** in Europe.  
