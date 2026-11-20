[← Functional Requirements](05_functional_requirements.md) | [↑ Table of Contents](../README.md) | [Data and interface definitions →](07_data_and_interface_definitions.md)

---

## 6 Non-functional requirements

Overview of the 7 groups (23 requirements):

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Group</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Identifiers (numbers)</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">MUST</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">OPTION</th></tr>
</thead>
<tbody>
<tr><td>Security and trust (NFR-SEC)</td><td>001, 002, 003, 004, 005</td><td>5</td><td>0</td></tr>
<tr><td>Deployment (NFR-DEP)</td><td>001, 002, 003</td><td>3</td><td>0</td></tr>
<tr><td>Timing (NFR-TIM)</td><td>001, 002, 004, 005, 006</td><td>5</td><td>0</td></tr>
<tr><td>Event log and demonstration evidence (NFR-EVD)</td><td>001, 004</td><td>2</td><td>0</td></tr>
<tr><td>Configuration and repository (NFRCFG)</td><td>001, 003, 004</td><td>3</td><td>0</td></tr>
<tr><td>Delivery and documentation (NFR-DEL)</td><td>001, 002, 003, 005</td><td>4</td><td>0</td></tr>
<tr><td>Start-delay indicators (NFR-KPI)</td><td>001</td><td>0</td><td>1</td></tr>
<tr><td>Total</td><td></td><td>22</td><td>1</td></tr>
</tbody>
</table>


### 6.1 Security and trust (NFR-SEC)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>NFR-SEC-001</td><td>Transport security</td><td>MUST HAVE</td></tr>
<tr><td>NFR-SEC-002</td><td>Key custody</td><td>MUST HAVE</td></tr>
<tr><td>NFR-SEC-003</td><td>Identity separation</td><td>MUST HAVE</td></tr>
<tr><td>NFR-SEC-004</td><td>Broker ACLs and request authorisation</td><td>MUST HAVE</td></tr>
<tr><td>NFR-SEC-005</td><td>Secret-free logs and data minimisation</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-SEC-001] Transport security</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Security and trust</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">All network endpoints (MQTT and HTTP) MUST use TLS with certificate verification; plaintext connections MUST be refused.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Inspection of broker and ingress configuration; a plaintext connection attempt fails</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-SEC-002] Key custody</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Security and trust</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Private keys MUST remain with their owning service or vehicle; no key material is shared between vehicles or copied into the convoy layer. Issuer keys remain with the OCM W-Stack; the CD never holds an issuer key. The release-token signing key MUST be distinct in type and purpose from access-token keys.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Inspection confirms key ownership per component</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-SEC-003] Identity separation</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Security and trust</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Administrative, vehicle and service identities MUST be separate; no identity is used in more than one role. A vehicle identity calling console or lab-control endpoints MUST be rejected.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M1: a vehicle identity cannot call console or lab-control endpoints</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-SEC-004] Broker ACLs and request authorisation</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Security and trust</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Business endpoints that act on a vehicle MUST require the access token with identity and run binding. Broker ACLs MUST prevent vehicle accounts from publishing release or administration messages and from subscribing to foreign vehicle topics. Traffic-light phase messages require the infrastructure access token.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M1: vehicle A cannot act as B; a vehicle cannot publish on release topics</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-SEC-005] Secret-free logs and data minimisation</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Security and trust</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Logs and the event log MUST NOT contain private keys, credentials or usable tokens; tokens appear as fingerprints only. Only synthetic station identifiers are processed; no personal data is stored (FR-GW-015).</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Inspection of the event schema and of a demo log</td></tr>
</table>


### 6.2 Deployment (NFR-DEP)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>NFR-DEP-001</td><td>Target environment</td><td>MUST HAVE</td></tr>
<tr><td>NFR-DEP-002</td><td>Helm deployment and failure domains</td><td>MUST HAVE</td></tr>
<tr><td>NFR-DEP-003</td><td>Health and mode visibility</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-DEP-001] Target environment</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Deployment</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The CD MUST be deployed into and demonstrated in the provided FACIS Kubernetes environment; source code resides in the client-designated repository. Development builds and unit tests MAY run on contractor systems, including a local broker and test doubles of the OCM W-Stack adapters; test doubles MUST NOT be part of the deployed container images or Helm charts.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The release runs in the FACIS environment and is witnessed by the client</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-DEP-002] Helm deployment and failure domains</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Deployment</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Delivery MUST use Helm charts with separate deployments for the convoy layer (gateway, geofinder/STS, business broker), each vehicle, the traffic light, the world service and the operations UI. Fault injection MUST be able to stop exactly one of these groups while the others keep running.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">T-12: the convoy layer is stopped while world and vehicles keep running</td></tr>
<tr><td colspan="2">Install and uninstall run without manual steps</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-DEP-003] Health and mode visibility</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Deployment</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Every service MUST expose a health interface. The dashboard MUST show a demoready indicator (health, valid status, free reservations, standstill, end of the STS startup hold), the active profile, the NATIVE/MOCK labels and the release tag.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Health, demo-ready indicator and release tag are witnessed</td></tr>
</table>


### 6.3 Timing (NFR-TIM)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>NFR-TIM-001</td><td>Stopping bounds (informative)</td><td>MUST HAVE</td></tr>
<tr><td>NFR-TIM-002</td><td>Call timeouts</td><td>MUST HAVE</td></tr>
<tr><td>NFR-TIM-004</td><td>Issuance halt</td><td>MUST HAVE</td></tr>
<tr><td>NFR-TIM-005</td><td>UI update</td><td>MUST HAVE</td></tr>
<tr><td>NFR-TIM-006</td><td>Time base</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-TIM-001] Stopping bounds (informative)</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Timing</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The system MUST implement the stopping mechanisms behind the bounds of Table 6a so that every vehicle reaches standstill by local expiry or protective stop in each demonstrated fault case. Table 5a is informative: it explains the expected stopping time with the Table 5 defaults; measured times are shown in the event log, not qualified against the bounds.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M4/M5: every affected vehicle reaches standstill; times are visible in the event log</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-TIM-002] Call timeouts</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Timing</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Every call to the OCM W-Stack or PCM Cloud MUST have a timeout (call_deadline, default 5 s, Table 5); on timeout the result is SERVICE_UNAVAILABLE.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Unit test: a delayed response leads to SERVICE_UNAVAILABLE</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-TIM-004] Issuance halt</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Timing</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The emergency stop MUST halt all STS issuance within halt_budget (default 1 s, Table 5), with reachable and blocked downlinks alike.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M5: the confirmed emergency-stop command is recorded as FAULT_INJECTED (fault type EMERGENCY_STOP); no TOKEN_ISSUED is signed later than its onset plus halt_budget; the dashboard shows the halt as successful only after the STS has acknowledged it</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-TIM-005] UI update</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Timing</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Dashboard fields MUST update within the UI update interval (default 1 s, Table 6); when no update arrives the display MUST mark itself stale.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">A paused event stream is shown as stale</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-TIM-006] Time base</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Timing</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">All components MUST use the NTP-synchronised clock of the Kubernetes environment for timestamps. Local deadlines and protective-stop timers MUST run on a monotonic clock and MUST NOT be affected by wall-clock adjustments.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Inspection: deadline and protective-stop timers use the monotonic clock</td></tr>
</table>


### 6.4 Event log and demonstration evidence (NFR-EVD)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>NFR-EVD-001</td><td>Event log</td><td>MUST HAVE</td></tr>
<tr><td>NFR-EVD-004</td><td>No-message demonstration</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-EVD-001] Event log</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Event log and demonstration evidence</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Each business event MUST carry event_type, timestamp, component, run_id, release_mode, the capability label (NATIVE/MOCK) where a verification or status result is involved, and the applicable session and station IDs. Failure events carry a Table 4 code. The events of Table 5a MUST be emitted and shown in the dashboard.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The event log of the demonstration contains the Table 4a events with the listed fields</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-EVD-004] No-message demonstration</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Event log and demonstration evidence</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">In M4 the business downlink of the affected vehicle MUST be blocked during the withdrawal window, and the event log MUST show that no business message and no TOKEN_CLEAR reached that vehicle until standstill.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M4: blocked downlink, local expiry stop and server-side invalidation are visible in the event log</td></tr>
</table>


### 6.5 Configuration and repository (NFR-CFG)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>NFR-CFG-001</td><td>Versioned configuration</td><td>MUST HAVE</td></tr>
<tr><td>NFR-CFG-003</td><td>Repository, build and CI</td><td>MUST HAVE</td></tr>
<tr><td>NFR-CFG-004</td><td>Unit tests</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-CFG-001] Versioned configuration</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Configuration and repository</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">All timing, model and scenario settings MUST be versioned in the repository together with the profile schema (FR-CFG-001). Secrets and generated run IDs MUST NOT be configuration inputs.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The profile used in the witnessed demonstration is identified by its repository tag</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-CFG-003] Repository, build and CI</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Configuration and repository</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The complete CD implementation (ORCE flows, custom nodes, UI, Helm charts, fixtures, tests) MUST be delivered in the client-designated repository with pinned dependencies and reproducible build instructions. CI (GitHub Actions) MUST run lint, unit tests and the standard XFSC licence/dependency scan. Every change to the main branch MUST enter through a pull request that a named person has approved after review; direct pushes to the main branch MUST be disabled. Code and tests produced with AI assistance follow the same rule.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The client rebuilds and deploys the tagged release from the repository</td></tr>
<tr><td colspan="2">Inspection: branch protection of the main branch requires an approving review, and every merged pull request of the tagged release shows a named approver</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-CFG-004] Unit tests</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Configuration and repository</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Unit tests MUST cover token validation in the order of Table 2a and the drive state machine (T-04, T-05), the token deadline, the discovery reference vectors of Table 5g, the motion proof including T-10, the STS session logic, the status age rule, the profile consistency checks and the traffic-light checks; they run in CI. Each test that implements a step of Table 3a, a row of Table 5b or 5c, a vector of Table 5g or an edge check of Section 10.3 MUST name that step, row, vector or check and assert the result stated there.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The CI report of the tagged release shows these tests passing</td></tr>
<tr><td colspan="2">Inspection: every step of Table 2a, every vector D-01 … D-12, every combined vector of T-05 and T-10 maps to at least one named test that asserts the stated result</td></tr>
</table>


### 6.6 Delivery and documentation (NFR-DEL)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>NFR-DEL-001</td><td>Handover documentation</td><td>MUST HAVE</td></tr>
<tr><td>NFR-DEL-002</td><td>Integration Note and mandatory tool stack</td><td>MUST HAVE</td></tr>
<tr><td>NFR-DEL-003</td><td>Licences</td><td>MUST HAVE</td></tr>
<tr><td>NFR-DEL-005</td><td>Demonstration script</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-DEL-001] Handover documentation</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Delivery and documentation</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The handover MUST contain an English README, installation, start, stop and reset instructions, the interface description, credential provisioning instructions via OCM WStack/PCM Cloud, the documented mocks (if any) and a demo runbook covering M1– M5.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">A client operator follows the runbook and runs a nominal demonstration</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-DEL-002] Integration Note and mandatory tool stack</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Delivery and documentation</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The contractor MUST deliver an Integration Note (1–2 pages) recording the FACIS credential profile, the OCM W-Stack, PCM Cloud, ORCE and FACIS UI Builder versions used, the MQTT broker product and version, the FACIS trust list used for verification, the holder arrangement (FR-GW-014), whether the OCM W-Stack distinguishes verification sub-reasons (FR-GW-004) and any client-approved mock (FR-GW-003). The CD MUST be built on ORCE (flows and custom nodes), OCM WStack, PCM Cloud and the FACIS UI Builder package.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Client review of the Integration Note</td></tr>
<tr><td colspan="2">All components run as ORCE instances; credentials via OCM W-Stack/PCM Cloud; UI via FACIS UI Builder</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-DEL-003] Licences</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Delivery and documentation</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">All code MUST be licensed under Apache-2.0; only FOSS dependencies compatible with Apache-2.0 MAY be used, and licence notices MUST be delivered with the source.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Inspection of the delivery and the CI licence scan</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-DEL-005] Demonstration script</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Delivery and documentation</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The demonstration script of Section 10.2 consists of M1–M5 and R, each executed once in the FACIS environment and witnessed by the client; M3 is executed once per release mode (motion-proof/console and coordinated/traffic-light). No other combination is required. The further acceptance evidence is stated in Section 11.2.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The demonstration protocol records each scenario with date, result and witness</td></tr>
</table>


### 6.7 Start-delay indicators (NFR-KPI)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>NFR-KPI-001</td><td>Start-delay indicators</td><td>OPTION</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[NFR-KPI-001] Start-delay indicators</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">OPTION</th></tr>
<tr><td colspan="3">Priority: OPTION (O-2) Group: Start-delay indicators</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">With option O-2, for each M3 run the event log MUST record, per rank, the GO issuance time t_GO(r), the motion-onset time t_move(r) and the start lag t_GO(r) − t_GO(r−1). No acceptance threshold applies; values are indicators for the comparison of the release modes (FR-OPS-010).</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Values are visible after M3(a) and M3(b)</td></tr>
</table>

---

[← Functional Requirements](05_functional_requirements.md) | [↑ Table of Contents](../README.md) | [Data and interface definitions →](07_data_and_interface_definitions.md)

