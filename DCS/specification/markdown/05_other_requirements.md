[← System Features](04_system_features.md) · [↑ Table of Contents](../README.md) · [Verification →](06_verification.md)

---

## 5 Other Requirements

#### C2PA Content & Life Cycle Credentials for PDF Contracts

[C2PA (Coalition for Content Provenance and Authenticity)](www.c2pa.org) is an open standard for tamper-evident provenance metadata called “Content Credentials.” It records who created a file, which tools were used, and what changed. Adobe, Microsoft, and others are standardising the format and integrating it into media tools, cameras, platforms, and PDF workflows.

This is important because provenance can be verified across systems for audit and compliance. In digital contract signing services, we add a C2PA manifest to the signed PDF (or host a remote manifest). It binds the contract ID and file hash, tracks lifecycle states (active, amended, terminated), and can link to a verifiable credential and status list. The legal e-signature (or PCM, OCM signature) stays as is; C2PA adds verifiable context and status. C2PA document life-cycle assertions can be added incrementally with every life-cycleevent.

##### [DCS-OR-C2PA-001] Use of C2PA for Contract Provenance     
The system MUST use the C2PA standard to record origin and edits of contract PDFs. C2PA is an open standard that adds tamper-evident Content Credentials. It helps detect manipulation and supports audit and compliance.

- Measurement: Share of contract PDFs with a valid C2PA manifest (target 100%).
- Verification Method: Tool-based C2PA validation; documentation review.


##### [DCS-OR-C2PA-002] PDF Embedding and Incremental Updates   
The system MUST embed a C2PA manifest in each signed contract PDF or link a remote manifest. It MUST use PDF incremental updates so existing legal signatures remain valid.

- Measurement: PDFs that pass both PDF signature checks and C2PA verification after an update (target 100%).
- Verification Method: Sign→append→verify test; PDF/C2PA tool checks.


##### [DCS-OR-C2PA-003] Contract Lifecycle Assertions     
The system MUST model lifecycle states as C2PA assertions: draft, active, amended, suspended, terminated, expired, replaced. Each assertion MUST include: contract_id, file_hash, status, reason, effective_at, authority, vc_id, prev_manifest_hash (if any).

- Measurement: Coverage of all states and fields in test assets (target 100%).
- Verification Method: Schema validation; unit tests on sample manifests.


##### [DCS-OR-C2PA-004] Verifiable Credential Binding     
The system MUST issue a W3C VC for contract status. The VC MUST bind to contract_id and file_hash and repeat status, reason, effective_at. The C2PA manifest MUST carry a link to the VC (vc_id) or an embedded copy.

- Measurement: Lifecycle events that have a matching VC (target 100%).
- Verification Method: VC signature verification; cross-check VC ↔ C2PA fields.


##### [DCS-OR-C2PA-005] Status Publication and Revocation     
The system MUST publish current contract status in a verifiable list (e.g., Status List 2021/2023 or equivalent). It MUST support real-time suspension and termination.

- Measurement: Time from status approval to list update (target ≤ 5 minutes).
- Verification Method: Integration tests; timestamp comparison.


##### [DCS-OR-C2PA-006] Verifier Behavior and UI  
The verifier MUST check PDF signatures, C2PA manifests, the VC signature, and the status list. It MUST show a clear banner: Active, Suspended, Terminated, Replaced, Expired, or Draft.

- Measurement: Correct banner shown for all test cases (target 100%).
- Verification Method: Automated verifier tests; manual UX check.


##### [DCS-OR-C2PA-007] Trust Anchors and Delegation    
Issuer keys MUST be anchored to the organization (e.g., org DID with LPID/eIDAS data or Qualified eSeal/QES). Delegation for status changes MUST be proven by a PoA credential. Keys MUST support rotation and revocation.

- Measurement: Existence of key and PoA policy; successful rotation drills (2/year).
- Verification Method: Policy review; drill reports; audit of key IDs in VC/C2PA.


##### [DCS-OR-C2PA-008] Resilience to Metadata Stripping    
A remote C2PA manifest MUST exist for every contract. The verifier MUST fetch it if the embedded manifest is missing or stripped.

- Measurement: Successful verification after stripping in test copies (target 100%).
- Verification Method: Strip-then-verify tests; remote fetch logs.


##### [DCS-OR-C2PA-009] Audit and Trusted Time  
Each lifecycle assertion and VC issuance SHOULD be time-stamped (RFC 3161 or equivalent). An appendonly audit log SHOULD record who changed status and why.

- Measurement: Time-stamp and audit entries for all events (target 100%).
- Verification Method: Log review; TSA signature checks.


##### [DCS-OR-C2PA-010] Backward Compatibility with Legal Signatures    
Adding or updating C2PA manifests MUST NOT break existing PDF legal signatures.


- Measurement: PDFs failing signature validation after C2PA updates (target 0).
- Verification Method: PDF signature validation before and after updates.

---

[← System Features](04_system_features.md) · [↑ Table of Contents](../README.md) · [Verification →](06_verification.md)

