# FACIS: Federation Architecture for Composed Infrastructure Services

## Introduction  
The FACIS landing page act as an entry-point for all open-source components, specification, and implementation developed under FACIS project. The goal is to guide the developers and contributors with the foundational blueprints to build a secure, interoperable and scalable multi-provider cloud-edge continuum. 

FACIS combines innovative technologies such as **Federation Architecture Patterns (FAPs)**, **machine-readable Service Level Agreements (SLAs)**, and **low-code orchestration engines**. These along with strong governance frameworks, improves scalability, security, and compliance with regulations, while enabling organizations to retain control of their data. 

 FACIS is an **open-source and collaborative project** that promotes transparency, inclusiveness, and innovation across the European digital ecosystem. 

Code-related deliverables are published via GitHub, while non-code results- such as frameworks, rulebooks and other supporting materials are and will be made available on the FACIS website : [https://www.facis.eu/results/](https://www.facis.eu/results/)

---

## FACIS Key Deliverables Repository
This repository serve as the central-entry point for all the FACIS components. The table provides a high-level view of the core components and their goals.
| Component | Primary Goal | Repository Link |
|-----------|--------------|:-----------------:|
| *FAP (Federation Architecture Pattern)* | Standardized Blueprints for building federated services to connect different companies securely. | [`eclipse-xfsc/facis-fap`](https://github.com/eclipse-xfsc/facis/tree/main/FAP) |
| *DCS (Digital Contracting Services)* | open-source software for secure, automated and legally compliant contract services. | [`eclipse-xfsc/facis-DCS`](https://github.com/eclipse-xfsc/facis/tree/main/DCS) |
| *SLA (Service Level Agreements)* | Defines the governance framework to ensure performance, security and accountability across multiple providers. | [`eclipse-xfsc/facis-SLA`](https://github.com/eclipse-xfsc/facis/tree/main/SLA) |
| *PoC (Proof-Of-Concepts)* | Real-world scenarios implementation and validation demonstrating the FAPs and DCS. | [`eclipse-xfsc/facis-poc`](https://github.com/eclipse-xfsc/facis/tree/main/PoC) |
| *Demonstrators* | prototype implementation showcasing the real-world use cases | *Coming Soon.* |


#### 1. FACIS Federation Architecture Pattern (FAPs) 
This repository is responsible for implementing the standarized templates/ blueprints for the specific collaboration use cases.
| FAP Repos | Description | Repository Link |
|-----------|-------------|:-----------------:|
| *FAP 1: Partner onboarding* | contains technical specification and implementation. | [`eclipse-xfsc/facis/fap1-implementation`](https://github.com/eclipse-xfsc/facis/tree/main/FAP/Partner%20Onboarding%20(Reference%20FAP)/implementation) |
| *FAP 2: Decentralized Catalogue Managment* | Enables trusted service discovery across federated infrastructures. | [`eclipse-xfsc/facis/fap2-implementation`](https://github.com/eclipse-xfsc/facis/tree/main/FAP/Decentralised%20Catalogue%20Management/implementation) |
|*FAP 3: IOT & AI pipeline over trusted services* | integrates sensing data with IoT and AI based data analysis for dashboard visualization. | [`eclipse-xfsc/facis/fap3-implementation`](https://github.com/eclipse-xfsc/facis/tree/main/FAP/IOT%20%26%20AI%20over%20Trusted%20Zones/implementation) |

#### 2. FACIS Proof-Of-Concepts (PoC) 
| PoC | Description | Repository Link |
|-----|-------------|:-----------------:|
| *Aviation Collaboration* | It specifies the industrial usecases for secure cross-organizational service orchestration. | [`eclipse-xfsc/facis-aviation-poc`](https://github.com/eclipse-xfsc/facis/tree/main/PoC/aviation-poc) |
| *Other PoC directories* | - | *Coming Soon.*|


#### 4. Orchestration and Smart Deployment Tools
These repositories contains the source code to deploy and manage the federation services according to the FAPs.

##### 4.1 Orchestration Engine 
| Component | Description | Repository Link |
|-----------|-------------|:-----------------:|
| *Orchestration Engine* | Core Orchestration Engine- Manages federated service flows and monitors performance. | [`eclipse-xfsc/orchestration-engine`](https://github.com/eclipse-xfsc/orchestration-engine) |
| *scenarios/aw40-demonstrator* | - | [`eclipse-xfsc/aw40-demonstrator`](https://github.com/eclipse-xfsc/orchestration-engine/tree/main/scenarios/aw40-demonstrator) |

##### 4.2 ESB: Easy Stack Builder 
A Modular Deployment Service integrated with the visual orchestration Engine that enables users to create and execute backend deployment and policy logic through drag and drop nodes.
| Tool | Description | Repository Link |
|------|--------------|:-----------------:|
| *ESB* | The reference repository for the Easy Stack Builder | [`eclipse-xfsc/easy-stack-builder`](https://github.com/eclipse-xfsc/smartdeployment/tree/main/Easy%20Stack%20Builder%20(ESB)) |
| *ESB ORCE (Orchestration Engine)* | Streamlined orchestration workspace simplifies the kubernetes deployment for federation services. | [`eclipse-xfsc/easy-stack-builder-orce`](https://github.com/eclipse-xfsc/smartdeployment/tree/main/Easy%20Stack%20Builder%20(ESB)/ORCE) |
| *ESB Catalogue* | Federated Catalogue - core component of XFSC for resource discovery, allow visual query self-descriptions within ORCE environments.  | [`eclipse-xfsc/easy-stack-builder-catalogue`](https://github.com/eclipse-xfsc/smartdeployment/tree/main/Easy%20Stack%20Builder%20(ESB)/Catalogue) |
| *ESB OCM-Wstack* | Enhances the participant’s interaction with the SSI-based ecosystem in a trustful and secure fashion. | [`eclipse-xfsc/easy-stack-builder-ocm-wstack`](https://github.com/eclipse-xfsc/smartdeployment/tree/main/Easy%20Stack%20Builder%20(ESB)/OCM-WStack) |
| *ESB PCM* | The user manages their credentials themselves, which supports decentralized architecture. |  [`eclipse-xfsc/easy-stack-builder-pcm`](https://github.com/eclipse-xfsc/smartdeployment/tree/main/Easy%20Stack%20Builder%20(ESB)/PCM) |
| *ESB TSA* | - | *Coming Soon.* |
| *AI Flow Builder* | - | [`eclipse-xfsc/ai-flow-builder`](https://github.com/eclipse-xfsc/smartdeployment/tree/main/AI%20Flow%20Builder) |

## CAT Enhancements  - FACIS XFSC

| Component | Description | Repository Link |
|-----------|-------------|:-----------------:|
| *Federated Catalogue* | The Federated Catalogue under XFSC has been enhanced to align with FACIS requirements, improving the way metadata objects are managed and verified.  | [`eclipse-xfsc/docs/federated-catalogue`](https://github.com/eclipse-xfsc/docs/tree/main/federated-catalogue) |



---

## Installation and Usage  
All outcomes of the FACIS project will be provided as **open-source**. Organizations and developers can access these tools through the **official FACIS website** and the related GitHub repositories.  

---

## Contributing  
FACIS is part of the **Eclipse XFSC Project (Cross Federation Services Components)**.  
Contributors are welcome to collaborate via GitHub under the organization [`eclipse-xfsc`](https://github.com/eclipse-xfsc).  

To contribute, you need to sign the **Eclipse Contributor Agreement (ECA)** and then fork and submit pull requests to the corresponding repository.  

---

## Resources  
- Official Website: [facis.eu](https://www.facis.eu)
- FACIS GitHub:  [eclipse-xfsc/facis](https://github.com/eclipse-xfsc/facis)
- Eclipse XFSC Developer Hub: [eclipse-xfsc.github.io](https://eclipse-xfsc.github.io/landingpage/)  
- GitHub Repositories: [github.com/eclipse-xfsc](https://github.com/eclipse-xfsc)  

---

## License  
This project is released under the **Apache 2.0 License**.  

---

By contributing to FACIS, you are part of building the future of a **federated, secure, scalable, and trusted cloud-edge ecosystem** in Europe.  
