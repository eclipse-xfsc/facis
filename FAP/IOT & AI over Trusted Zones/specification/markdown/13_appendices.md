[← Requirements Traceability Matrix](12_requirements_traceability_matrix.md) | [↑ Table of Contents](../README.md)

---

## 13. Appendices

### Appendix A: Glossary

<p align="center"><em>Table 8 Terms & Abbreviations</em></p>


|Term|Full Name|Definition|
|---|---|---|
|DSP|Dataspace Protocol|Eclipse Foundation protocol for interoperable data exchange|
|DCP|Decentralized Claims Protocol|Protocol for conveying organizational identities and trust|
|DID|Decentralized Identifier|W3C standard for decentralized digital identities|
|VC|Verifiable Credential|W3C standard for tamper-evident credentials|
|VP|Verifiable Presentation|Package of one or more VCs for presentation to verifier|
|TCK|Dataspace Protocol Technology Compatibility Kit|Test suite for protocol conformance|
|OT|Operational Technology|Hardware and software controlling industrial operations|
|SASL|Simple Authentication and Security Layer|Framework for authentication in protocols|
|SCRAM|Salted Challenge Response Authentication Mechanism|Password-based authentication|


### Appendix B: References
1. Eclipse Dataspace Protocol Specification 1.0 https://projects.eclipse.org/projects/technology.dataspace-protocol-base
2. Eclipse Dataspace Components (EDC) Documentation - https://eclipseedc.github.io/docs
3. Eclipse DSP TCK Repository - https://github.com/eclipse-dataspacetck/dsp-tck
4. W3C DID Core Specification - https://www.w3.org/TR/did-core/
5. W3C Verifiable Credentials Data Model - https://www.w3.org/TR/vc-data-model/
6. OpenID Connect for Verifiable Credential Issuance (OIDC4VCI) https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html
7. OpenID Connect for Verifiable Presentations (OIDC4VP) https://openid.net/specs/openid-4-verifiable-presentations-1_0.html
8. RFC 2119: Key words for use in RFCs to Indicate Requirement Levels https://www.rfceditor.org/rfc/rfc2119
9. OpenAI Chat Completions API Specification - https://platform.openai.com/docs/apireference/chat


### Appendix C: Alignment with FAP IoT & AI

This specification realizes the FAP IoT & AI objectives by providing:

- Unified data pipeline from sensor to dashboard across federated ecosystems • Standardized data transfer via DSP control plane and HTTP/Kafka data planes • Cloud-enabled aggregation with Bronze/Silver/Gold lake architecture
- Trust services integration with DCP, W3C DIDs, and Verifiable Credentials
- Full abstraction layers for data gathering, transfer, aggregation, and visualization

---

[← Requirements Traceability Matrix](12_requirements_traceability_matrix.md) | [↑ Table of Contents](../README.md)
