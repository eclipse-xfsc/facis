[← Other Requirements](05_other_requirements.md) · [↑ Table of Contents](../README.md) · [Appendix →](07_appendix.md)

---

## 6 Verification

This verification plan qualifies the DCS by demonstrating end-to-end acceptance scenarios that parallel the Use Cases in Section 4. Rather than verifying every requirement individually, each scenario exercises the functional path with realistic inputs and records objective evidence (logs, signatures, artifacts, reports) that the system fulfills its specified behavior. Non-functional observations MAY be recorded during the runs but are not formal pass/fail criteria unless explicitly noted. Table 6 captures the acceptance criteria for the use cases defined in Section 4, whereas Table 7 depicts the acceptance criteria for sub use cases in Section 4. In addition to the acceptance criteria in the tables, the following requirements apply as acceptance criteria to all scenarios in Table 6 and Table 7:
1. All acceptance scenarios SHOULD be specified and executed as executables in Behaviour-driven development (BDD) framework using Gherkin and Behave step definitions, run via the XFSC bddexecutor. The acceptance presentation SHOULD demonstrate these tests live, and the acceptor SHOULD be able to run the same pack locally. A Rancher Desktop Setup would be preferred for easy adoption during verification, instead of Docker Compose.
2. Implementations SHOULD conform to the XFSC OCM W Default Toolstack (service mesh, databases, messaging, CI/CD, Helm, Kubernetes, API design, etc.). The preference is to use Golang and provide adapters to Cassandra (for data persistence) or NATS (for messaging) for external sources, and eventing/messaging SHOULD be demonstrable with NATS.
3. All deployments SHOULD be scripted via Helm and installable in Kubernetes; charts SHOULD support configuration profiles (DEV, Acceptance, Prod) and use secretRefs (no clear-text secrets). Charts SHOULD be suitable for Argo CD and published to a Helm repository.
<br><br>


<p align="center"><em>Table 6 – Acceptance criteria defined for Section 4 use cases</em></p>

|Use Case|Description|Acceptance Criteria|
|---|---|---|
|UC-01 User Authentication & Authorization|Authenticate; access a roleprotected page/API; attempt an unauthorized action|Authorized access succeeds; unauthorized action denied; audit entry shows actor, role, decision|
|UC-02 Template Management|Create template; submit for review; approve; search & open|Template stored with version/provenance; status transitions logged; search returns approved item|
|UC-03 Contract Creation & Approval|Instantiate from template; edit metadata; route for approval; lock content|Contract ID issued; “Approved” status; immutable hash/provenance recorded; audit trail complete|
|UC-04 Contract Signing|Open secure viewer; present identity/PoA; execute signature; verify result|Valid signature attached; signer & PoA bound; verification OK; timestamp and evidence stored|
|UC-05 Contract Deployment|Trigger deployment; observe outbound call; confirm receipt|Target acknowledges deployment; DCS status “Deployed;” correlation ID and receipt archived|
|UC-06 Lifecycle Management|View KPIs/alerts; initiate renew or terminate flow; confirm state change|KPIs visible; new term or terminated state recorded; notifications and logs captured|
|UC-07 Storage & Archive|Store in archive; search; retrieve artifact|Entry stored as PDF/A-3 (or configured format); search finds it; retrieval returns intact file; audit event written|
|UC-08 Audit & Compliance|Request activity report; run policy audit; export results|Report lists actors/timestamps/actions; violations (if any) flagged with reasons; exports available|
|UC-09 Administration|Create/modify roles; assign to user; open monitoring/logs|Role takes effect immediately; changes and admin actions logged; health metrics visible|
|UC-10 Automation/Orche stration|Invoke HTTP node to start process; receive webhooks/callbacks; complete flow|End-to-end completes with 2xx responses; callback received; trace shows ordered events|
|UC-11 API & Integrations|Call API to create, sign, and validate; inspect responses|Auth succeeds; APIs return HTTP 2xx; validation result returned; request/response logs with correlation IDs|
|UC-12 SystemBased Contract Mgmt|Create → review → approve → sign → archive via API|Each step updates status; signature evidence stored; archive entry created; full audit chain present|
|UC-13 External Execution|Submit execution payload; verify activation in target|Target confirms activation; DCS stores proof (receipt/hash/tx-id); status reflects “Executed”|
|UC-14 Identity & PoA|Fetch credentials; validate; bind to session|Credentials verified (valid, unrevoked); authorization check passes or blocks with reason; event logged|
|UC-15 Access Rights Revocation|Revoke role/credential; attempt prior action (access/sign)|Access/signing denied; affected items flagged (if configured); revocation visible in logs/status lists|
|UC-EUDI|EUDI PID verification|Verify Person Identification Data (PID) presented from an EUDI-compliant wallet (e.g., Lissi EUDI Wallet Connector or EU EUDI Wallet Reference Implementation).|
<br><br>


<p align="center"><em>Table 7 – Acceptance Criteria defined for Section 4 sub use cases</em></p>

|Sub Use Case|Description|Acceptance Criteria|
|---|---|---|
|UC-02-01 – Create Contract Template|Create reusable template by Template Manager/Approver.|Show a template is created with required metadata/provenance; repository returns a template ID/version; entry appears in search; action is auditlogged.|
|UC-02-02 – Search & Retrieve Templates|Find and access existing templates.|Execute search with filters; results respect RBAC; opening a template displays current version & provenance; access events logged.|
|UC-02-03 – Generate Contract from Template|Populate template with context data to create a contract.|Given inputs, system produces a draft with linked template ID; both machine- and human-readable versions render; creation logged.|
|UC-02-04 – Update Contract Template|Edit existing template with versioning.|Update creates a new immutable version; previous remains readable; diff and author shown; change logged.|
|UC-02-05 – Deprecate Contract Template|Mark a template deprecated.|Deprecation prevents new contract generation; banner shows status; event logged with timestamp and user.|
|UC-02-06 – Add Template Provenance|Capture origin, contributors, identifiers.|Add provenance fields; system validates/records; provenance visible in UI/API and included in exports.|
|UC-02-07 – Verify Template & Provenance|Validate correctness, semantics (JSONLD/SHACL) and authenticity.|Run verification; success report lists schema checks and signature/VC validation; failures block generation.|
|UC-02-08 – Create & Maintain Semantic Schemas|Manage schemas used by templates.|Create/update schema; link to templates; validation enforces conformity; schema versioning and rollback demonstrated.|
|UC-02-09 – Template Management Dashboard|Track status, approvals, usage.|Dashboard shows per-template lifecycle, usage metrics, last changes; supports filtering and export; access controlled.|
|UC-03-01 – Create Contract|Generate contract from predefined templates.|Create a draft; receive contract ID; both views render; creation logged and traceable to template version.|
|UC-03-02 – Negotiate Contract Terms|Collaboratively adjust clauses before finalization.|Add comments/edits; see tracked changes and negotiation log; version history preserved.|
|UC-03-03 – Adjust Contract Terms|Granular clause edits without regenerating.|Edit a clause; integrity checks pass; only targeted sections change; audit trail updated.|
|UC-03-04 – Approve Contract|Route to required approvers before signing.|Route shows pending/approved states; all required approvals recorded with timestamps; content locked on completion.|
|UC-03-05 – Review MR/HR Correctness & Versions|Validate machine- and human-readable consistency.|Open both renderings; system highlights inconsistencies (none expected after fix); export both with same version/tag.|
|UC-03-06 – Manage Contract Signing Process|Coordinate structured signing steps.|Configure signers/sequence; system schedules, reminds, and tracks status; changes logged.|
|UC-03-07 – Contract Dashboard & Search|Track progress and search contracts.|Dashboard shows lifecycle states; full-text and metadata search returns expected contracts respecting RBAC.|
|UC-04-01 – Review & Sign Contract Electronically|Secure viewer; legally binding e-signature incl. identity/PoA.|Signer authenticates; signs in viewer; system produces signed artifact (e.g., PAdES/JAdES) and updates status; event logged.|
|UC-04-02 – Verify Counterparty Authorization|Check legal authority to sign (identity/PoA).|Present counterparty VC/PoA; system validates chains/status lists; unauthorized cases block signing with error.|
|UC-04-03 – Verify Counterparty Signature|Validate authenticity/integrity of signature.|Run crypto validation and policy checks; report shows certificate/VC status and document hash match.|
|UC-05-01 – Deploy Signed Contract to Target System|Make signed contract available for execution.|Push deployment payload to target; receive ack/callback; target reads content; DCS logs proof of delivery.|
|UC-06-01 – Monitor Contract Performance|SLA/compliance monitoring & tracking.|Dashboard displays KPIs/milestones; alerts fire for violations; history shows fulfilled terms.|
|UC-06-02 – Renewal or Termination|Manage renewal/termination incl. VC revocation.|Trigger renewal/termination; system updates state, issues/updates revocation where applicable; notifications/logs produced.|
|UC-07-01 – Store Contract in Secure Archive|Tamper-proof, longterm storage of signed contracts.|Archive a signed contract; system seals, timestamps, encrypts, and returns archive ID; retrieval confirms integrity.|
|UC-07-02 – Manage Contract Permissions & Access|Control RBAC for stored contracts.|Change access policy; unauthorized access is denied; permitted roles can retrieve; changes and access attempts logged.|
|UC-07-03 – Storage & Security Dashboard|Track archive status, integrity, access logs.|Dashboard shows coverage/integrity checks, alerts, and recent access; export of logs available.|
|UC-08-01 – Report Contract Activity Logs & Timestamps|Produce auditable reports.|Generate report with creation/approval/signature events; includes timestamps/actors; export to CSV/PDF.|
|UC-08-02 – Audit Contract Compliance|Check against legal/organizational policies.|Run compliance scan; issues listed with rule references; pass/fail summary produced and archived.|
|UC-09-01 – System Configuration & User Management|Administer roles, security, settings.|Admin changes a role/setting; effect visible immediately; all admin actions logged with actor/time.|
|UC-09-02 – System Monitoring & Logging|Operational monitoring and security logs.|Show health metrics & searchable logs; filters by severity/time; export supports incident review.|
|UC-10-01 – Automate Contract Workflow Processes|Integrate workflows with AI/ERP (orchestration).|Orchestrator triggers external action from a contract milestone; target system receives and executes; trace visible end-to-end.|
|UC-10-02 – Validate Contract Integrity & Compliance|Pre-execution automated validation.|Run validation; violations block deployment; detailed report stored with contract.|
|UC-11-01 – Manage API-Based Contract Workflows|Ensure automation via API integrations.|Invoke API to create/sign/validate; request is authenticated; workflow executes; interaction logged for traceability.|
|UC-12-01 – Create Contract via API|Automated contract creation through system integration.|POST creates contract; returns ID & status; data pulled from integrated system; audit log records requester/system.|
|UC-12-02 – Review Contract via API|System-driven validation checks.|API call runs rule checks; response lists issues; failing contracts cannot proceed to approval.|
|UC-12-03 – Approve Contract via API|Automated approvals.|API marks contract approved; requires authN/authZ; status changes and approver identity logged.|
|UC-12-04 – Manage Contracts via API|Query/update/track lifecycle.|Use APIs to list/update metadata and read history; RBAC enforced; changes versioned and logged.|
|UC-12-05 – Sign Contract via API|Automated/AI-driven signing.|Sign endpoint produces valid signature artifact; binds signer VC/PoA; status → “signed”; verification succeeds.|
|UC-13-01 – Deploy Contract to Target System|Execute in ERP targets.|Deliver deployment payload; target confirms activation/execution; DCS records proof-of-execution reference.|
|UC-14-01 – Retrieve Identity & PoA Credentials|Acquire verified identity/PoA before signing/execution.|Missing credentials trigger retrieval; chain and status verified; authorization granted only on success; events logged.|
|UC-15-01 – Revoke Access Rights & Signatures|Invalidate access when credentials/signatures are revoked.|Detect revocation via status list; mark contract state “revoked”; rights withdrawn; audit entry created; requires re-sign to restore.|

---

[← Other Requirements](05_other_requirements.md) · [↑ Table of Contents](../README.md) · [Appendix →](07_appendix.md)

