[← Standards & Protocols](10_standards_protocols.md) | [↑ Table of Contents](../README.md) | [Requirements Traceability Matrix →](12_requirements_traceability_matrix.md)

---

## 11. Validation & Acceptance Criteria

### 11.1 Protocol Conformance
1. Eclipse DSP [TCK](https://github.com/eclipse-dataspacetck/dsp-tck) transfer suite passes with 100% success rate
2. All Data lake/ Protocol endpoints validate against OpenAPI specification

### 11.2 Functional Tests
3. End-to-end test: Catalog discovery → Negotiation (preset) → HTTP Pull transfer → Data landed in Bronze
4. End-to-end test: Catalog discovery → Negotiation (preset) → Kafka streaming → Data in Bronze Parquet
5. MQTT to Kafka bridge test: Publish to MQTT → Verify in Kafka topic within 5 seconds
6. Policy enforcement test: Rate limit exceeded returns 429 with Retry-After header
7. Token expiry test: Expired access token rejected with 401
8. End-to-End test data processing: ETL processes data: Bronze --> Silver --> Gold Layer
9. Data access test: Data can be queried by query engine

### 11.3 Security Tests
10. TLS certificate validation passes for all endpoints
11. Invalid VC presentation rejected during negotiation
12. Tampered HMAC signature rejected on HTTP data access
13. Kafka SASL authentication failure logged and access denied
14. Data access: Authorization rules are followed during data retrieval via JDBC interface
15. Data access: Authorization rules are followed during data retrieval via REST interface

### 11.4 Performance Tests
16. Catalog request responds < 500ms at p95
17. Negotiation completes within 5 seconds
18. HTTP data fetch completes < 2s for 1000 sensor readings
19. Kafka throughput sustains 10,000 msg/sec per topic
20. Data access: data retrieval via JDBC interface < 1 sec
21. Data access: data retrieval via REST interface < 1 sec

### 11.5 Operational Tests
22. Docker Compose deployment starts successfully
23. Kubernetes Helm chart deploys without errors
24. Health checks report healthy within 30 seconds of startup
25. Rolling update completes without downtime
26. Audit logs queryable for all DSP operations within 1 minute
27. End-to-end test: Data lake query → LLM inference → Visualization update within 2s.
28. Performance test: Modify data in lake → API reflects changes < 10s.
29. Security test: Unauthorized API call rejected.
30. Performance test: Handle 1 req/min with < 5s latency at p95.
31. LLM response matches expected structure (e.g., JSON) and accuracy (>90% on sample anomalies).

---

[← Standards & Protocols](10_standards_protocols.md) | [↑ Table of Contents](../README.md) | [Requirements Traceability Matrix →](12_requirements_traceability_matrix.md)
