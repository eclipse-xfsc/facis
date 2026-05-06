[← Standards & Protocols](09_standards_protocols.md) · [↑ Table of Contents](README.md) · [Requirements Traceability Matrix →](11_requirements_traceability_matrix.md)

---

## 10. Validation & Acceptance Criteria

### 10.1 Protocol Conformance
1. All endpoint descriptions validate against the OpenAPI specification.
2. Other than that, protocols are, where applicable, referenced by Functional Requirements, e.g., OAI-PMH by FR-CR-01, and thus to be validated and accepted as specified below for Functional Tests.


### 10.2 Functional Tests

For each Functional Requirement, acceptance criteria have been defined. The Requirements Traceability Matrix in Section 11 below summarizes these.

### 10.3 Security Tests
1. TLS certificate validation passes for all endpoints
2. Invalid VC presentation rejected during remote connect
3. Tampered HMAC signature rejected on HTTP data access if applicable
4. Data access: Authorization rules are followed during data retrieval via REST interface


### 10.4 Performance Tests
5. Local Catalog request responds < 500ms
6. HTTP data fetch completes < 2s for 100 local asset readings
7. Kafka throughput sustains 10,000 msg/sec per topic
8. UI access: < 1 sec

### 10.5 Operational Tests
9. **Mandatory use of XFSC Orchestration Engine for all operational workflows**  
All deployment, configuration, and runtime processes of the FAP DCM MUST be executed using ORCE flows. This includes UI actions, background processing, lifecycle operations, and integration logic.
10. **Deployment starts successfully**  
The development deployment MUST start without errors and all services MUST reach a healthy state.
11. **Kubernetes Helm chart deploys without errors**  
The production setup MUST deploy successfully using the provided Helm charts and all pods MUST become ready.

---

[← Standards & Protocols](09_standards_protocolsfap_dcm_adheres_to.md) · [↑ Table of Contents](README.md) · [Requirements Traceability Matrix →](11_requirements_traceability_matrix.md)

