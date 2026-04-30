[← Conceptual Architecture](04_conceptual_architecture.md) | [↑ Table of Contents](README.md) | [Technical Architecture →](06_technical_architecture.md)

---

## 5. Functional Requirements

### 5.1 Dataspace Protocol Control Plane

#### FR-DSP-001: DSP Catalogue Service

Priority: SHOULD HAVE Description: The Provider connector SHOULD expose a catalogue endpoint that returns datasets and offers metadata conforming to DSP 1.0 specification (see Appendix B).

Acceptance Criteria:

- POST /dsp/catalogue/request returns HTTP 200 with valid JSON
- Response includes datasets array with id, metadata, and offers
- Pagination supported with nextCursor field
- Filtering by assetType, dataset IDs accepted
- Passes DSP TCK catalogue suite


#### FR-DSP-002: DSP Contract Negotiation

Priority: MAY HAVE Description: The connector MAY implement async contract negotiation state machine per DSP 1.0 (REQUESTED → FINALIZED → TERMINATED states).

Acceptance Criteria:

- POST /dsp/negotiations creates negotiation and returns 202 with negotiation Id
- GET /dsp/negotiations/{id} returns current state and agreement Id when FINALIZED
- POST /dsp/negotiations/{id}/terminate sets TERMINATED state
- State transitions logged with correlation IDs
- Passes DSP TCK negotiation suite


#### FR-DSP-003: DSP Transfer Process

Priority: MUST HAVE Description: The connector MUST support transfer process creation, state tracking, and access parameter provisioning per DSP 1.0.

Acceptance Criteria:

- POST /dsp/transfers with agreementId creates transfer and returns 202 with transferId
- GET /dsp/transfers/{id} returns state and access object when COMPLETED
- Access object contains data plane parameters (URL or Kafka connection)
- Error states include reason field
- Passes DSP TCK transfer suite


### 5.2 Data Plane Profiles

#### FR-DP-001: DSP HTTP Pull Profile

Priority: MUST HAVE Description: The system MUST support HTTP pull data plane for time-windowed snapshots with signed URLs.

Acceptance Criteria:

- Transfer with format: http-pull returns { url, token, expiresAt }
- URL accepts from/to query parameters for time windows
- Token validates and expires per TTL
- Consumer can fetch data within validity window
- Rate limits enforced per agreement


#### FR-DP-002: Streaming Profile

Priority: Should HAVE Description: The system MUST support Kafka streaming data plane with per-transfer topics and SASL credentials.

Acceptance Criteria:

- Transfer with format: Kafka returns { bootstrap, topic, sasl, expiresAt }
- Per-transfer topic created on-demand
- SASL PLAIN or SCRAM credentials provisioned
- Consumer can subscribe and receive events
- Credentials expire per TTL and ACLs cleaned up


#### FR-DP-003: MQTT to Kafka Bridge


Priority: SHOULD HAVE Description: The system SHOULD provide a bridge service forwarding MQTT messages to Kafka topics.

Acceptance Criteria:

- Bridge subscribes to MQTT topic pattern (e.g., iot/#)
- Messages forwarded to Kafka with enriched metadata (timestamp, source topic)
- Configurable topic mapping and message transformation
- Handles backpressure and reconnection


### 5.3 Identity & Trust

#### FR-IAM-001: Organization Identity

Priority: MUST HAVE Description: Organizations MUST be identified by W3C DIDs and hold Verifiable Credentials for participant role.

Acceptance Criteria:

- Each organization has DID (did:web5 or did:key6)
- Participant VC issued per OIDC4VCI flow
- VC contains claims: id, name, roles, trust framework reference
- Credentials stored in Identity Hub with query API


#### FR-IAM-002: DCP Integration

Priority: SHOULD HAVE Description: The system SHOULD support Decentralized Claims Protocol for VC presentation and verification.

Acceptance Criteria:

- Negotiation request includes VP with participant VC
- Connector verifies VP signature and VC validity
- Expired or revoked credentials rejected
- Verification result logged for audit

### 5.4 Data Lake Integration: Data Ingest

#### FR-DL-001: HTTP Ingest Service

Priority: MUST HAVE Description: The data lake MUST provide HTTP ingest endpoint validating signed URLs and storing objects to Bronze layer.

Acceptance Criteria:

- Validates token and URL expiry
- Fetches data from provider endpoint
- Stores to object storage with partition key (e.g. agreementId, timestamp, ...)
- Registers landed data with governance catalog
- Tags with metadata (provider, asset, agreement, policy)


#### FR-DL-002: Kafka Ingest Service


Priority: MUST HAVE Description: The data lake MUST provide Kafka consumer groups landing stream data to Bronze layer.

Acceptance Criteria:

- Subscribes using transfer access parameters (bootstrap, topic, credentials)
- Validates message schema against registry
- Writes to Bronze in Parquet format with hourly partitions
- Commits offsets after successful write
- Handles late-arriving data and duplicate detection


#### FR-DL-003: File Ingest Service

Priority: MUST HAVE Description: The data lake MUST provide an SFTP file service

Acceptance Criteria: SFTP protocol is supported for file ingest

### 5.5 Data Lakehouse Data Storage

#### FR-DL-004 Data Storage

Priority: MUST HAVE Description: The data lake MUST provide an S3-compatible object storage and use efficient storage formats

Acceptance Criteria:

- Files can be stored in an S3 Object Storage
- At least in silver and gold layer data are stored using a columnar file storage format (Parquet, ORC)
- Data storage supports ACID transactions, schema evolution and time travel, Apache (Iceberg)


#### FR-DL-005: Data Storage: Logical Lake Layering

Priority: SHOULD HAVE Description: The data lake SHOULD implement Medallion architecture (Bronze/Silver/Gold) architecture for progressive refinement. The Medallion Architecture is an architecture pattern used in modern data lakehouse architectures to organize data into progressive quality layers — typically called Bronze, Silver, and Gold – to improve data quality, structure, and usability step by step.

Acceptance Criteria:

- Bronze: Raw ingested data with no / minimal transformation, accessible by role data engineer; data are partitioned by load timestamp
- Silver: Cleansed, validated, and enriched data, accessible by roles data engineer, data scientist
- Gold: Business-domain specific aggregates ready for data products: analytics, ML, BI, applications
- Data is stored in open formats (e.g. Parquet, ORC, Delta, Iceberg)
- Retention policies enforced per agreement terms

### 5.6 Data Lakehouse Data Processing


#### FR-DL-006: Realtime Data ProcessingPriority: MUST HAVE

Description: Near real-time ETL/ELT pipelines are the operational backbone of a data lakehouse if data updates are time critical. Data are ingested, transformed, and organized in real time ensuring that every layer (Bronze, Silver, Gold) is kept accurate, fresh, and analysis-ready.

##### Acceptance Criteria:

- Trigger: data processing (ingestion) is triggered event-driven
- Data Source: Can subscribe to message bus topics, read from (log) event streams
- Processing: Continuous, record-by-record or micro-batch
- Window functions


#### FR-DL-007: Batch Data Processing

Priority: MUST Description:

Automated ETL/ELT pipelines are the operational backbone of a lakehouse. They ingest, transform, and organize data in regular time intervals ensuring that every layer (Bronze, Silver, Gold) is kept accurate, fresh, and analysis-ready.

Acceptance Criteria:

- Trigger: Data processing time-based (hourly, daily, weekly) or event-based batch
- ETL jobs to promote data between layers, persistent view where appropriate
- Data Sources: Files, databases, APIs
- Processing: Process chunks (batches) of data periodically


#### FR-DL-008: Process Orchestration

Priority: SHOULD HAVE Description: Process automation is a key enabler in a data lakehouse architecture, because it ensures that data flows, transformations, and quality checks happen reliably, repeatably, and at scale without manual intervention. Without automation, a lakehouse would quickly become unreliable or inconsistent. Automation ensures that:

- Data arrives on time (e.g., IoT, logs, APIs)
- Transformations run in the correct order and dependencies
- Quality and governance rules are applied
- Pipelines recover from failures
- The system can scale without human intervention


Acceptance Criteria:

- Orchestration Manage and schedule data pipelines (order, dependencies, retries)
- Ingestion Automation: Automatically pull data from sources


- Run data transformations (i.e. data cleaning, enrichment, aggregation jobs) on schedule or trigger
- Mechanism for pipelines recover from failures (“backfill”)


### 5.7 Data Lakehouse data access

#### FR-DL-009 SQL Query Engine

Priority: MUST HAVE Description:

The query engine is a core component of any data lakehouse architecture because it enables SQL-style access and analytics directly on data stored in open formats (e.g. Parquet, ORC, Delta, Iceberg). The query engine is responsible for:

- Reading data from the lake’s open storage (S3, HDFS, etc.)
- Interpreting metadata (from a metastore or catalogue like Hive, Glue, or Unity Catalog)
- Optimizing and executing queries (SQL or DataFrame-based)
- Returning results to BI tools, notebooks, applications or LLMs


Acceptance Criteria:

- SQL Query Execution: Run ad-hoc or scheduled SQL queries over large datasets
- Cost-based Optimization (CBO): Chooses efficient query plans and file reads
- Predicate Pushdown: Reads only the necessary data blocks for a query
- Federation: Optionally joins data across multiple sources (Lake, DB, APIs)
- Caching / Materialization: Speeds up repeated queries
- Concurrency: Supports many parallel users and queries


#### FR-DL-010 Data Access

Priority: MUST HAVE Description:

Data access in a lakehouse is the controlled ability to interact with data, encompassing who can access which datasets, under what conditions, and through which interfaces, while ensuring security, governance, and operational efficiency.

##### Acceptance Criteria:

- Data are accessible via REST API
- Data are accessible via ODBC / JDBC protocol
- (CAN HAVE) Data Access via MCP protocol
- (CAN HAVE) Data Access via BI tool connectors
- Streaming ingestion/consumption
- Data access is restricted by role/policy-based access control, Granularity: Table/Column/Row level
- Authentication: Integration with identity providers (Keycloack), Support for service accounts or API tokens for applications (CAN HAVE) multi-factor authentication (MFA)


### 5.8 Data Governance

#### FR-DL-011 Data Access Control

Priority: SHOULD HAVE Description:

Data governance is the set of processes, policies, and technologies that ensures data within the lakehouse is accurate, consistent, secure, discoverable, and used responsibly across the organization, while meeting regulatory, legal, and operational requirements. In the scope of this FAP we only consider technical functions that support data security and data access policies (authentication / authorization) for reasons of simplicity.

Acceptance Criteria:

- Authentication to store data via SSI
- Policy based data lake access to store data (on organization level)
- Authentication to access data via SSI
- Policy based data lake access to access data
- Policies refer to roles or attributes. RBAC/ABAC


### 5.9 AI Processing

##### FR-AI-001: Data Retrieval from Data Lake

Priority: MUST HAVE Description: The system MUST retrieve data from Silver/Gold layers via REST API or ODBC/JDBC (per FR-DL-010)

Acceptance Criteria:

- Queries filter by timestamp, assetId, or agreementId.
- Detects data modifications.
- Handles policy-based access control, rejecting unauthorized requests with 403.
- Response time < 500ms for 1000 records at p95.


##### FR-AI-002: LLM Inference via OpenAI-Compatible API

Priority: MUST Description: The system MUST send retrieved data to an OpenAI-compatible LLM service (e.g., IONOS AI Model Hub) via its API for inference (e.g., summarization, anomaly detection).

Acceptance Criteria:

- Uses configurable HTTPS POST to /v1/chat/completions (or equivalent) with API key authentication.
- Payload: JSON with model (e.g., “llama-2-7b-chat”), messages array including data as prompt.
- Handles responses: Extracts choices[0].message.content as output.
- Rate limits: Enforce per agreement (e.g., 10 req/min) via policy hooks.
- Error handling: Retry on 429/5xx, log failures.
- Provides Output via API


##### FR-AI-003: Governed LLM Access to Data Lake

Priority: SHOULD HAVE Description: The system SHOULD enable LLMs to access data lake content via standardized, OpenAI-compatible API prompts that incorporate queries to lake interfaces (e.g., REST API or ODBC/JDBC per FR-DL-010). Prompts SHALL be formatted to include contextual data (e.g., 'Query the Silver layer for sensor data from [timestamp] and summarize anomalies'), with responses governed by policies (e.g., RBAC/ABAC from FR-DL-005).

Acceptance Criteria:

- Prompts use JSON structures compatible with OpenAI's /v1/chat/completions endpoint.
- Access rejects unauthorized queries per policy (e.g., HTTP 403).
- Supports batch (e.g., daily summaries) and streaming (e.g., real-time anomaly detection) modes.

---

[← Conceptual Architecture](04_conceptual_architecture.md) | [↑ Table of Contents](README.md) | [Technical Architecture →](06_technical_architecture.md)
