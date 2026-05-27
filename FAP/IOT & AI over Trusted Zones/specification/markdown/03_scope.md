[← Background & Context](02_background_context.md) | [↑ Table of Contents](../README.md) | [Conceptual Architecture →](04_conceptual_architecture.md)

---

## 3. Scope

This chapter defines the overall scope of the FAP. It clarifies what capabilities are delivered end-to-end, from device data collection, through DSP-governed data transfer and exchange, to governed consumption in the data lake/lakehouse and what items/topics are excluded. Furthermore, the visualisation in dashboards and enrichment by LLMs. The intent is to give implementation teams a concrete build plan while enabling business stakeholders to understand feasibility, effort, and boundaries.

### 3.1 In Scope

Below is defined what the implementation must deliver to be compliant, maintainable, and useful in production.

**Transfer Process Protocol**, implementations MUST implement the Transfer Process Protocol as defined in DSP 2025-1 RC4. This includes:

- The complete state machine for transfer processes
- Message exchanges for Transfer Request, Transfer Start, Transfer Suspension, Transfer Completion, and Transfer Termination
- Support for both push and pull transfer types
- Support for both finite and non-finite data transfers


**Transfer Process HTTPS Binding**, implementations MUST expose the transfer API as REST over HTTPS with the binding's error semantics. Specifically:

- HTTP 400 responses MUST be returned on invalid state transitions
- HTTP 400 responses MUST include a Transfer Error payload as defined in DSP 2025-1 RC4
- All other error semantics defined in the HTTPS binding MUST be implemented


**Agreement Prerequisites**, implementations MUST assume that a valid agreement exists before initiating a transfer. This FAP does not define contract negotiation workflows. Implementations MUST require an Agreement ID to be available before starting any transfer process.

**Data Sink and Catalogue**, implementations MUST:

- Provide a Data Sink component positioned near data sources
- Derive the Provider connector catalogue from that Data Sink
- Catalogue publication MAY remain minimal as contract negotiation is outside the scope of this FAP


**Consumer Connector**, implementations MUST provide a Consumer connector that:

- Starts transfers using a valid Agreement ID
- MAY implement discovery capabilities (discovery is OPTIONAL)


**Data Plane**, implementations MUST provide data-plane implementations that are separate from the DSP control plane. The data plane MUST support:

- Pull mechanisms for files and objects
- Batch delivery capabilities
- Streaming data delivery


Note: Specific tooling and technology choices are not mandated; examples provided in this specification are illustrative only.

**Protocol-to-Streaming Bridge**, implementations MAY provide a protocol-to-streaming bridge for sensor data streams. This capability is OPTIONAL.

**Data Ingestion and Medallion Architecture**, implementations MUST provide receiver-side data ingestion that:

- lands incoming data into a bronze layer (raw data storage)
- provides curation capabilities to transform data into Silver (validated, enriched) and gold (business-ready) layers
- implements the Medallion architecture pattern


**Data lake/Lakehouse Storage**, implementations MUST provide data lake/lakehouse storage with the following characteristics:

- use of a transactional table format (e.g., Delta Lake, Iceberg, Hudi)
- storage in open columnar file formats
- practical partitioning strategies for query performance


**Batch and Stream Processing**, implementations MUST support both batch and streaming processing modes. The Gold layer MUST contain curated business models and KPIs suitable for analytics consumption.

**Governance and Identity**, implementations MAY provide:

- policy enforcement hooks for data usage purpose, time-to-live, and rate limiting
- identity validation mechanisms
- claims and verifiable credentials (VC) validation capabilities
- Policy based data access control


**Audit and Observability**, implementations MUST provide audit and observability capabilities across:

- transfer processes
- data ingestion operations
- data transformations


**Semantic and API Access**, implementations MUST provide semantic and API access for dashboards that support:

- KPI queries
- time-series data access
- MAY provide LLM-ready aggregates and metadata


**LLM Enrichment**, implementations MAY provide LLM enrichment capabilities with the following constraints:

- Retrieval-Augmented Generation (RAG) SHOULD operate only over allowed metadata and curated aggregates
- structured outputs SHOULD be stored in separate tables
- LLM access MUST NOT widen data access beyond the negotiated scope defined in the Agreement
- this capability is entirely OPTIONAL

### 3.2 Out of Scope 
The following capabilities and features are explicitly out of scope for this FAP specification.


**Contract Negotiation**, contract negotiation workflows are out of scope. This specification treats contract negotiation as a prerequisite that supplies an Agreement ID. The negotiation process itself is not specified here.

**Dataspace Federation Governance**, data federation, governance and marketplace operations are out of scope for this specification.

**OT Protocol Implementations**, deep Operational Technology (OT) protocol server implementations are out of scope.

**Complete Analytics Platform**, building a full analytics platform, ML training pipelines, or dashboard products are out of scope. This specification focuses on integration via APIs rather than providing complete end-user applications.

**Vendor-Specific Implementations**, binding the architectural design to specific vendors is out of scope. Examples provided in this specification remain illustrative and technology-agnostic.

**Advanced Security Features**, security features such as Hardware Security Modules (HSM) and confidential computing are out of scope beyond the basic security requirements defined in this FAP.

**Enterprise Monitoring Stacks**. production-grade enterprise monitoring stack selection and implementation are out of scope. This specification defines requirements for exposing logs and metrics, but platform selection is left to implementers.

**Advanced Data Governance**, advanced data governance capabilities beyond the technical controls specified in above section are out of scope.

**High Availability Design**, detailed backup, failover, and high availability (HA) design specifications are out of scope.

**Event-Driven Dashboard Updates**, implementations provide eventing mechanisms so that dashboards can refresh only the visual components affected by data changes, rather than requiring full page refreshes.

**DevOps Specifics**, DevOps implementation details including Infrastructure as Code (IaC) and CI/CD pipelines are out of scope for this specification.

---

[← Background & Context](02_background_context.md) | [↑ Table of Contents](../README.md) | [Conceptual Architecture →](04_conceptual_architecture.md)
