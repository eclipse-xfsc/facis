[↑ Table of Contents](../README.md) | [Background & Context →](02_background_context.md)

---

## 1. Executive Summary

This Federation Architecture Pattern (FAP) Specification defines the technical requirements, architecture, interfaces, and acceptance criteria for implementing a federated IoT & AI data pipeline with IoT sensing and data collection, data transfer via OT/IT connectors using data connectors compliant with the Eclipse Dataspace Protocol [DSP](https://projects.eclipse.org/projects/technology.dataspace-protocol-base), data aggregation within a data lake tech-stack and LLM-based data enrichment to accompany dashboard data charts visualization.

The specification of this FAP describes how data moves from raw sensing to governed insight via visual dashboards in a way that is interoperable, auditable, and scalable. The process flow includes IoT sensoring which generates operational data that is collected in a data sink, coming from the IoT source. DSP-compatible connectors establish a bi-directional connection between data provider (IoT sources) and data consumer (data lake up to dashboard).

On the receiving side, the data should be transferred in a data lake/lakehouse setup that separates ingestion, curation, and serving into Bronze, Silver, and Gold data buckets/layers. The data lake/lakehouse is the single source of truth for the data which will be visualized in the dashboards while querying the data to render charts, for example, time-series views of sensor values, while an optional LLM service adds explanations and contextual guidance on the data. The data lake/lakehouse exposes governed interfaces that both the dashboard and the LLM can use in batch as well as in streaming mode, and it maintains the structure and metadata needed for humans and systems to understand and trust the data.

Technically, the solution separates the process flow cleanly. The Eclipse Dataspace Protocol (DSP) provides the interoperable control plane for catalogue discovery, policy-aware negotiation, and data transfer initiation, while the data plane is pluggable and implementation specific according to the technical scenario. For this implementation, only the data plane is in scope but the option to define sub-flows to the control plane must be considered. Additionally, there will be a clear data structure within the data lake/lakehouse which provides a clean data storage and access according to the use case scenarios. And finally, the dashboard with support of the LLM functionality can access the IoT data and provide the respective charts for human readability and data understanding.

The federated architecture pattern describes an overall system which enables therefore a secure, sovereign data exchange from IoT sensors at the edge through dataspace connector functionality to big data platforms in the cloud.


With regards to IoT sensing and data collection the specification covers seven primary components:

- IoT Sensors, Protocols (e.g. MQTT, OPC-UA, Modbus)
- Data Sink: Centralized data collection and normalization of IoT Data
- Provider Data Connector: Maintains a catalogue of available data in the Data Sink and exposes the DSP data plane (transfer services) and simulate the control plane (catalogue, negotiation,)
- Consumer Data Connector: receives data plane access credentials
- Data Connectors will transfer the data on a peer-to-peer base between data sink and data lake/lakehouse
- Data lake/lakehouse provides the interfaces to store and process the data according to the use case scenario with respective meta data and data policies and provides access to the data for the LLM up to the dashboard
- LLM agents and the dashboarding will enrich and visualize the data for data interpretation and exploration


The FAP specification and respective implementation follows open standards including [W3C](https://www.w3.org/TR/did-1.0/), [HTTPS](https://www.rfc-editor.org/info/rfc2818), Eclipse Dataspace Protocol, and aligns with federated dataspace architectures. The design supports multiple data profiles such as HTTPS pull, or Kafka for streaming and includes comprehensive security, trust, and governance controls.

With regards to the data lake/lakehouse the specification describes the following core functionalities and corresponding components:

- Storage (centralized) object-based cloud storage (S3, HDFS, Azure Blob, GCS)
- Data Format uniform data storage: Storage of structured, semi-structured and unstructured data in the same system (e.g. Parquet, ORC, JSON, CSV, images, logs, etc.) based on open storage format and schema information management (metadata)
- Table Format Transactional data management (ACID) supporting ACID transactions on data in the lake and enabling insert/update/delete/merge operations as in classic warehouses.
- Data Processing A common engine can execute batch and streaming jobs. Streaming data can be written incrementally to the lake and queried consistently with batch data. Supports near real-time analytics.
- Query Engine SQL-based and advanced analysis: Native support for SQL queries on lake data. Integration with BI tools, support for machine learning and data science. Enables uniform data queries across multiple formats and sources


For the AI supported Dashboard the AI integration will leverage open standards for promptbased inference to ensure interoperability. Relevant data from the data lake/lakehouse (e.g.,


via SQL queries or REST APIs) are retrieved and embedded into prompts and sent to an OpenAI-compatible endpoint. This approach maintains data sovereignty by processing data minimally and on-demand, with outputs governed by the same policies as the underlying datasets. Data outputs will leverage the same open standards and visualize either directly via LLM and/or through a use case optimized method.

![image 1](assets/images/imageFile1.png)

<p align="center"><em>Figure 1 FAP IoT & AI: Architecture Overview</em></p>

The purpose of this tender is to commission software development services for Lot “Federation Architecture Pattern IoT & AI”. The delivery of the software is provisionally by Q2 of 2026. The final clarification will be communicated after the award of the tender.

---

[↑ Table of Contents](../README.md) | [Background & Context →](02_background_context.md)
