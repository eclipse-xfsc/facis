[← Validation & Acceptance Criteria](11_validation_acceptance_criteria.md) | [↑ Table of Contents](README.md) | [Appendices →](13_appendices.md)

---

## 12. Requirements Traceability Matrix

Once the requirements highlighted in Table 7 are fulfilled, all other requirements marked as MUST in this overall specification document are automatically inherited and considered part of the validation process. In other words, meeting these top-level requirements ensures that the dependent MUST, SHOULD etc. requirements are also respected.

<p align="center"><em>Table 7 Requirements Matrix</em></p>


|Req ID|Component|Interface/API|Test Case|
|---|---|---|---|
|FR-DSP-001|Catalogue Service|POST /dsp/catalog/request|TC-CAT-001: Catalogue discovery|
|FR-DSP-002|Negotiation Service|POST /dsp/negotiations|TC-NEG-001: Contract flow|
|FR-DSP-003|Transfer Service|POST /dsp/transfers|TC-TRX-001: Transfer init|
|FR-DP-001|HTTP Data Plane|GET /api/data/{asset}|TC-HTTP-001: Pull data|
|FR-DP-002|Kafka Data Plane|Kafka Consumer API|TC-KFK-001: Stream data|
|FR-DP-003|MQTT Bridge|N/A (Internal)|TC-MQTT-001: Bridge flow|
|FR-IAM-001|Identity Hub|POST /trust/credentials|TC-IAM-001: VC issuance|
|FR-IAM-002|DCP Verifier|Internal verification|TC-DCP-001: VP verification|
|FR-DL-001|HTTP Ingest|Internal service|TC-ING-001: HTTP land|
|FR-DL-002|Kafka Ingest|Consumer service|TC-ING-002: Kafka land|
|FR-DL-003|Lake Layering|ETL jobs|TC-LAKE-001: Bronze→Gold|
|FR-AI-001|Orchestrator|GET /api/data/{layer}/{assetId}|TC-AI-001: Data retrieval|
|FR-AI-002|LLM Inference Service|POST /v1/chat/completions|TC-AI-002: Inference flow|

---

[← Validation & Acceptance Criteria](11_validation_acceptance_criteria.md) | [↑ Table of Contents](README.md) | [Appendices →](13_appendices.md)
