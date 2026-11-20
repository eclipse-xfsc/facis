[← Assumptions, constraints and external dependencies](04_assumptions_constraints_and_external_dependencies.md) | [↑ Table of Contents](../README.md) | [Non-functional requirements →](06_non-functional_requirements.md)

---

## 5 Functional Requirements

Every requirement is stated with identifier, name, priority (MUST HAVE / OPTION), group, requirement text and acceptance criteria. Requirement text uses MUST / MUST NOT / SHOULD / MAY in their [RFC 2119](https://rfc-editor.org/rfc/rfc2119) sense. Acceptance criteria name the scenario (M1 … M5, R), edge check (T-04, T-05, T-10, T12), integration test (Section 11.1), unit test that provides the evidence. A criterion that names none of these is evidenced by the scenario named in another criterion of the same requirement; where there is none, by inspection of the tagged release or of the demonstration event log, recorded in the demonstration protocol.


Overview of the 9 groups (67 requirements):

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Group</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Identifiers (numbers)</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">MUST</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">OPTION</th></tr>
</thead>
<tbody>
<tr><td>Federation gateway (FR-GW)</td><td>001, 002, 003, 004, 005, 006, 007, 008, 009, 010, 011, 012, 013, 014, 015</td><td>15</td><td>0</td></tr>
<tr><td>Geofinder (FR-GEO)</td><td>001, 002, 003, 004, 005</td><td>5</td><td>0</td></tr>
<tr><td>STS (FR-STS)</td><td>001, 002, 004, 005, 006, 007, 008, 009, 010, 012, 013, 014, 015</td><td>13</td><td>0</td></tr>
<tr><td>Vehicle software (FR-VEH)</td><td>001, 002, 004, 006, 007, 008, 009, 010, 011, 012, 013, 014, 015, 016, 017</td><td>15</td><td>0</td></tr>
<tr><td>World service (FR-SIM)</td><td>001, 002, 003, 004</td><td>4</td><td>0</td></tr>
<tr><td>Dashboard, console, emergency stop, reset (FR-OPS)</td><td>001, 002, 003, 004, 006, 007, 010</td><td>6</td><td>1</td></tr>
<tr><td>Business interface (FR-IF)</td><td>001, 002</td><td>2</td><td>0</td></tr>
<tr><td>Configuration profile and fixtures (FRCFG)</td><td>001, 002, 003</td><td>3</td><td>0</td></tr>
<tr><td>Traffic light, T0, coordinated release (FR-TL)</td><td>001, 002, 003</td><td>3</td><td>0</td></tr>
<tr><td>Total</td><td></td><td>66</td><td>1</td></tr>
</tbody>
</table>


### 5.1 Federation gateway: admission and status (FR-GW)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>FR-GW-001</td><td>Credential profile via OCM W-Stack and PCM Cloud</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-002</td><td>Access-token identity binding</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-003</td><td>Presentation verification via OCM W-Stack</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-004</td><td>Admission decision and typed rejection</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-005</td><td>Invalidation and recovery via the status list</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-006</td><td>Status polling</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-007</td><td>Status age rule</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-008</td><td>Issuance block on known invalidation</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-009</td><td>Recovery requires fresh status and admission</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-010</td><td>Reachability and no silent fallback</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-011</td><td>Status decision rule</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-012</td><td>Recovery after connectivity return</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-013</td><td>Mandatory XFSC tools</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-014</td><td>Separate holder per vehicle</td><td>MUST HAVE</td></tr>
<tr><td>FR-GW-015</td><td>No driver identity</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-001] Credential profile via OCM W-Stack and PCM Cloud</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The federation gateway MUST admit a vehicle or the traffic light only with verifiable credentials (DID-based) issued through the XFSC OCM W-Stack in the credential profile currently supported by FACIS, as recorded in the Integration Note. Holders MUST be provided by PCM Cloud in the arrangement of FR-GW-014; no alternative credential ecosystem is used.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The Integration Note records credential format, flow, issuer and the OCM W-Stack and PCM Cloud versions used.</td></tr>
<tr><td colspan="2">M1 shows that every credential used was issued exclusively through the OCM WStack into PCM Cloud, including any credential re-issued by the CD after a revocation</td></tr>
<tr><td colspan="2">A presentation outside the recorded profile is rejected with VP_INVALID</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-002] Access-token identity binding</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The federation gateway MUST bind each access token to stationId, tenant and the OEM/vehicle credential identifiers taken from the OCM W-Stack verification result and controlled provisioning data. Identity fields requested by the client MUST NOT be used for the binding.</td></tr>
<tr><td rowspan="4" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Positive admission produces the documented binding (stationId, tenant, credential identifiers) in the issued access token</td></tr>
<tr><td colspan="2">M1: vehicle A cannot obtain or use authority for B; the attempt is rejected with IDENTITY_MISMATCH or ACCESS_TOKEN_INVALID</td></tr>
<tr><td colspan="2">Requested identity fields in the admission request have no influence on the binding</td></tr>
<tr><td colspan="2">An access token past its lifetime (default 10 min, Table 5) is rejected by every request receiver</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-003] Presentation verification via OCM W-Stack</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The federation gateway MUST verify credential presentations through the verification function of the OCM W-Stack; admission always requires the positive native result (FR-GW-004). A mock MAY only add a check that the OCM W-Stack demonstrably does not provide, only with written client approval, and MUST NOT replace or override a native result. Such a check MUST be recorded in the Integration Note and shown with its own MOCK label wherever its result is shown. Labels are given per capability (issuance, verification, status list) and per check only where the OCM WStack reports individual checks or a check is mocked.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M1 exercises positive and negative presentations (invalid signature or holder binding, revoked credential)</td></tr>
<tr><td colspan="2">The system-identification screen shows NATIVE or MOCK per capability and a separate MOCK label for each mocked check (FR-OPS-006)</td></tr>
<tr><td colspan="2">No mocked result is shown as native verification</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-004] Admission decision and typed rejection</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Admission MUST require a positive OCM W-Stack verification result and a valid status (Table 5b). A credential whose status is suspended or revoked MUST be rejected with VP_INVALID and sub-reason CREDENTIAL_REVOKED, derived from the status list. Any other invalid presentation MUST produce VP_INVALID; the subreasons CHAIN_INVALID and BINDING_INVALID are set only where the OCM WStack result distinguishes them (Integration Note), otherwise the OCM W-Stack reason is recorded in the event without secrets. An unavailable or unparseable service MUST produce SERVICE_UNAVAILABLE.</td></tr>
<tr><td rowspan="4" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Admission is rejected while the status of the credential is blocked</td></tr>
<tr><td colspan="2">M1: the revoked credential is rejected with VP_INVALID and sub-reason CREDENTIAL_REVOKED</td></tr>
<tr><td colspan="2">A verification failure or timeout of the OCM W-Stack is reported as SERVICE_UNAVAILABLE and never as a proven invalid credential</td></tr>
<tr><td colspan="2">Each rejection carries exactly one Table 4 code</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-005] Invalidation and recovery via the status list</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The federation gateway MUST perform credential invalidation (suspension or revocation) and recovery through the status list service of the OCM W-Stack and MUST preserve its semantics: a suspension is lifted; an irreversibly revoked credential is replaced through OCM W-Stack issuance, not reactivated.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M1 and M4 record operation and affected credential in STATUS_CHANGED events</td></tr>
<tr><td colspan="2">Reset restores valid participation without reversing an irreversible revocation</td></tr>
<tr><td colspan="2">A revoked credential is replaced through issuance, not reactivated</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-006] Status polling</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The federation gateway MUST read the status of every admitted credential from the OCM W-Stack status list at the configured poll interval (default 1 s, Table 5) and MUST verify the authenticity of the status list as provided by the OCM W-Stack. Every observation records the start time of its request.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">A status list that fails authenticity or integrity checks is treated as blocked</td></tr>
<tr><td colspan="2">Every status change appears as STATUS_CHANGED in the event log with the request start of its observation</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-007] Status age rule</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">A status older than the configured maximum age (default 30 s, Table 5), measured from the request start of the last successful observation, MUST be treated as blocked; a status whose age equals the maximum age is blocked. A failed observation MUST NOT refresh the age. An observation whose request start is not later than that of the last recorded observation MUST be discarded. Without any successful observation the status is blocked.</td></tr>
<tr><td rowspan="4" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Unit test: an age just below, equal to and above the maximum age yields valid, blocked and blocked</td></tr>
<tr><td colspan="2">Unit test: a failed poll leaves the age unchanged</td></tr>
<tr><td colspan="2">Unit test: an observation that completes after a newer one is discarded</td></tr>
<tr><td colspan="2">Unit test: an empty status cache is blocked</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-008] Issuance block on known invalidation</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">A known invalidation MUST block every further token issuance for the affected vehicle, including GO promotion, and MUST remove the vehicle from new discovery and session formation.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M4: no TOKEN_ISSUED for the affected vehicle after t_disable; RENEWAL_REFUSED carries the disable time</td></tr>
<tr><td colspan="2">M4: the affected vehicle stops by local token expiry; unaffected participants complete</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-009] Recovery requires fresh status and admission</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Recovery after invalidation MUST require a valid status and renewed admission. An ended session MUST NOT resume, and a vehicle MUST NOT start automatically after recovery.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">After recovery M1 shows standstill and a successful fresh admission</td></tr>
<tr><td colspan="2">Tokens of the ended session remain rejected by the drive module (SESSION_CLOSED)</td></tr>
<tr><td colspan="2">No TOKEN_ISSUED event occurs for the recovered vehicle without a new session</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-010] Reachability and no silent fallback</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Reachability of the OCM W-Stack verification and status functions MUST be shown per function. An unreachable function MUST produce SERVICE_UNAVAILABLE; the system MUST NOT switch to a mock automatically.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The dashboard shows reachability per function</td></tr>
<tr><td colspan="2">Inspection: no automatic fallback from OCM W-Stack to a mock exists</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-011] Status decision rule</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The gateway and the STS MUST apply the decision rule of Table 5b at every admission and issuance decision: with a valid status admission, new sessions, initial ARMED issuance, GO promotion and renewal are allowed; with a blocked status all of them are blocked. The age rule of FR-GW-007 MUST be evaluated at the decision, independently of the polling timer.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Unit test: no issuance decision is allowed once the status is blocked</td></tr>
<tr><td colspan="2">M4: GO promotion and renewal stop for the invalidated vehicle</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-012] Recovery after connectivity return</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">After the OCM W-Stack becomes reachable again, a fresh valid status MUST restore eligible admission without restart of gateway, geofinder or STS. Recovery MUST NOT reopen ended sessions.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Integration test: after a blocked connection to the status list is released, admission succeeds again without restart</td></tr>
<tr><td colspan="2">No automatic vehicle motion follows recovery; a new session requires standstill and discovery</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-013] Mandatory XFSC tools</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The federation gateway MUST consume the OCM W-Stack (issuance, verification, status list) and PCM Cloud in the versions recorded in the Integration Note. No native XFSC service is modified, re-hosted or reimplemented. Each OCM W-Stack function MUST be accessed through one adapter module; test doubles of the adapters are used only in CI and local development and are never part of the deployed container images or Helm charts. A runtime mock requires written client approval and is limited to the supplementing checks recorded under FR-GW-003; issuance, verification and status-list results on the admission (E1) and invalidation (E3) paths always come from the native OCM W-Stack.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The Integration Note lists tool, version and, where applicable, the recorded gap per capability</td></tr>
<tr><td colspan="2">Inspection: no XFSC service is modified, re-hosted or reimplemented</td></tr>
<tr><td colspan="2">Inspection: the container images and Helm charts of the tagged release contain no test double; every runtime mock has a recorded client approval</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-014] Separate holder per vehicle</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Each simulated vehicle MUST hold its credentials in a holder of its own; no holder, credential or key is shared between vehicles. The holders MAY be separate holders within one PCM Cloud tenant.; the arrangement is recorded in the Integration Note. A dedicated PCM Cloud instance per vehicle is option O-1 (Section 2.3).</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Inspection: one holder per vehicle; credential identifiers differ per vehicle</td></tr>
<tr><td colspan="2">M1: no cross-vehicle credential use is possible</td></tr>
<tr><td colspan="2">With option O-1 (Section 2.3): the second M1 run and inspection show a dedicated PCM Cloud instance per vehicle</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GW-015] No driver identity</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Federation gateway</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The system MUST NOT depend on any driver or other personal credential. Admission, session and release MUST bind to vehicle/OEM and service identities only, and personal data MUST NOT be processed or stored in the event log.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Inspection: no schema, credential type or console field references a driver or natural person</td></tr>
<tr><td colspan="2">Admission with vehicle/OEM credentials only succeeds (M1)</td></tr>
</table>


### 5.2 Geofinder: queue discovery (FR-GEO)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>FR-GEO-001</td><td>Position-report authentication</td><td>MUST HAVE</td></tr>
<tr><td>FR-GEO-002</td><td>Formation eligibility</td><td>MUST HAVE</td></tr>
<tr><td>FR-GEO-003</td><td>Along-track ordering</td><td>MUST HAVE</td></tr>
<tr><td>FR-GEO-004</td><td>Gap segmentation and stability</td><td>MUST HAVE</td></tr>
<tr><td>FR-GEO-005</td><td>Position message schema</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GEO-001] Position-report authentication</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Geofinder</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The geofinder MUST accept only authenticated, schema-valid position reports that match the current run, stationId, tenant and access token. Reports older than the position-stale threshold (default 3 s, Table 5) MUST be rejected. Per stationId only a report whose measurement timestamp is later than that of the last accepted report MUST be accepted; a duplicate or out-of-order report MUST be discarded without effect.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Reports with a foreign identity, run or access token are rejected with POSITION_INVALID, ACCESS_TOKEN_INVALID or IDENTITY_MISMATCH</td></tr>
<tr><td colspan="2">A report older than the stale threshold is rejected</td></tr>
<tr><td colspan="2">Unit test: a redelivered report (same measurement timestamp) and an older report are discarded and do not count towards stability (Table 5g, D-08); for the motion proof see FR-STS-006</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GEO-002] Formation eligibility</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Geofinder</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">A new formation MUST use only unreserved, in-lane vehicles whose last accepted position report is not older than the position-stale threshold (default 3 s, Table 5) and that meet the standstill criterion (discovery standstill threshold and duration; defaults 0.05 m/s for 3 s, Table 5).</td></tr>
<tr><td rowspan="6" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">A vehicle with an active reservation is not included in a new formation</td></tr>
<tr><td colspan="2">A vehicle outside the lane threshold (default 0.30 m) is not included</td></tr>
<tr><td colspan="2">A vehicle moving above the discovery standstill threshold, or standing for less than the required duration, is not included</td></tr>
<tr><td colspan="2">A vehicle whose last accepted position report is older than the stale threshold is not included</td></tr>
<tr><td colspan="2">The dummy is treated as a passive obstacle and never as a participant</td></tr>
<tr><td colspan="2">Unit tests: Table 5g vectors D-05, D-06, D-07 and D-09 produce their expected outcome</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GEO-003] Along-track ordering</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Geofinder</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Participants MUST be ordered along the closed track by cutting the largest free arc; the participant directly before that arc in driving direction is the LEAD. Arcs are measured from front to front in driving direction and compared after rounding to the discovery distance resolution (default 1 mm, Table 5). A formation MUST NOT be reported when it has only one participant, when the two largest arcs differ by less than the cut tolerance (default 0.10 m, Table 5), or when its span from the last participant to the LEAD exceeds half the track perimeter.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M2 with the reference placement and the origin-shifted placement reproduces the reference order CD-V1, CD-V2, dummy, CD-V3</td></tr>
<tr><td colspan="2">Unit tests: Table 6g vectors D-01, D-02, D-07, D-11 and D-12 produce their expected outcome</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GEO-004] Gap segmentation and stability</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Geofinder</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Two consecutive participants whose arc exceeds the configured gap threshold (default 2.20 m, Table 5) are separated by a gap; an arc equal to the threshold is not a gap. A formation MUST be reported only after participant identities, order and segment boundaries have remained unchanged for the configured number of consecutive geofinder cycles (default 3 cycles of 1 s, Table 5).</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The reference placement yields one gap segment: CD-V3 becomes FOLLOW_GAP behind the dummy (M2)</td></tr>
<tr><td colspan="2">Unit test: no formation is reported before the required stable-cycle count (Table 5g, D01 and D-10)</td></tr>
<tr><td colspan="2">Unit tests: Table 5g vectors D-03, D-04 and D-10 produce their expected outcome</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-GEO-005] Position message schema</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Geofinder</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">A position report MUST contain stationId, tenant, run_id, x, y, speed, measurement timestamp and schemaVersion; units and value ranges MUST be fixed in the versioned schema. Speed MUST come from the motion source, not from differences of noisy reports.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Reports with missing fields or non-finite values are rejected</td></tr>
<tr><td colspan="2">Inspection: speed is taken from the position-source interface, not derived from report differences</td></tr>
</table>


### 5.3 STS: reservation, session and token lifecycle (FR-STS)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>FR-STS-001</td><td>Atomic participant reservation</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-002</td><td>No session migration or resumption</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-004</td><td>Session protocol</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-005</td><td>Role and order binding</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-006</td><td>GO release by predecessor motion proof (release mode motion-proof)</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-007</td><td>Lead progress, target STOP and DONE</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-008</td><td>Lead loss abort</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-009</td><td>Release-token signing and sequence</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-010</td><td>Issuance checks</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-012</td><td>Renewal semantics</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-013</td><td>Withdrawal by non-issuance; STOP as accelerator</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-014</td><td>Release-token schema</td><td>MUST HAVE</td></tr>
<tr><td>FR-STS-015</td><td>Composition in the session proposal</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-001] Atomic participant reservation</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The single STS MUST atomically reserve every participant of a formation before opening its session. A formation that contains an already reserved vehicle MUST be rejected with SESSION_CONFLICT.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Conflicting proposals create exactly one active assignment per vehicle (unit test)</td></tr>
<tr><td colspan="2">The accepted session proceeds to PROPOSED; a conflicting one is rejected with SESSION_CONFLICT</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-002] No session migration or resumption</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">An aborted or failed session MUST NOT migrate or resume. Reservations MUST persist until the last issued token has expired plus B_stop; re-participation MUST require fresh standstill and a cleared local fault state. After a start or restart the STS MUST NOT open a session or sign a token until TTL + B_stop have elapsed since its start (start-up hold).</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M5: no participant is reassigned before its last token has expired</td></tr>
<tr><td colspan="2">A vehicle is admitted to discovery again only after standstill and cleared fault state</td></tr>
<tr><td colspan="2">Unit test: no session is opened and no token is signed during the start-up hold</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-004] Session protocol</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The STS MUST implement the session protocol of Table 5c (PROPOSED, CONFIRMED, TOKENS_ISSUED, ARMED, ROLLING, DONE, ABORTED) with the state timeouts of Table 5 and abort on rejection or timeout with a typed reason naming the state.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M3 runs through every state up to DONE</td></tr>
<tr><td colspan="2">STATE_TIMEOUT names the state in which the timeout occurred</td></tr>
<tr><td colspan="2">Terminal sessions (DONE, ABORTED) issue no further tokens</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-005] Role and order binding</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Roles and order MUST be computed before initial token issuance and become binding at ARMED: first participant LEAD/NONE; first participant behind a gap FOLLOW_GAP/GAP; all others FOLLOW with their direct predecessor. The STS MUST separately retain the preceding authorised participant as wave_predecessor.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M2/M3 show the reference roles: V1 LEAD/NONE, V2 FOLLOW/V1, V3 FOLLOW_GAP/GAP with wave_predecessor V2</td></tr>
<tr><td colspan="2">No role, predecessor or rank changes during a session; a changed claim at the same token_seq is rejected by the drive module (T-05)</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-006] GO release by predecessor motion proof (release mode motion-proof)</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The LEAD MAY receive GO without predecessor motion. In release mode motionproof (default) every other participant MUST receive GO only after its wave_predecessor has supplied the configured number of consecutive fresh motion reports (default 2 reports above v_move 0.10 m/s, Table 5) timestamped after that predecessor's GO issuance. Only reports with distinct, strictly increasing measurement timestamps count; a duplicate report does not count. A dummy cannot trigger GO. The release mode coordinated is specified in FR-TL-003.</td></tr>
<tr><td rowspan="4" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M3(a): FOLLOW_GAP starts only after the participant before the gap has moved</td></tr>
<tr><td colspan="2">T-10: predecessor loss before the required motion proof never releases the dependent follower</td></tr>
<tr><td colspan="2">Unit test: a redelivered motion report does not count twice</td></tr>
<tr><td colspan="2">PHASE_CHANGED records the motion report IDs that triggered the promotion</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-007] Lead progress, target STOP and DONE</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Lead progress MUST be accumulated as unwrapped along-track travel from the initial position. At the scenario target the STS MUST halt issuance and send a run/sessionbound STOP; DONE MUST require all participants standing.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M3 reaches the target and ends in DONE</td></tr>
<tr><td colspan="2">After the target no further TOKEN_ISSUED occurs for the session</td></tr>
<tr><td colspan="2">DONE is entered only after STANDSTILL of every participant</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-008] Lead loss abort</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Loss of the LEAD before the target (blocked status or stale position) MUST abort the session with LEAD_UNAVAILABLE and halt all issuance for that session.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">A simulated lead loss produces SESSION_ENDED(ABORTED, LEAD_UNAVAILABLE)</td></tr>
<tr><td colspan="2">No token is issued for the session after the abort; followers stop by expiry or STOP</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-009] Release-token signing and sequence</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The STS MUST sign release tokens with ES256 using the release-token schema of FR-STS-014, current run/session binding and a strictly increasing token_seq per vehicle-session. nbf MUST equal the issuance time rounded down to whole seconds and exp MUST equal nbf plus TTL (Table 5).</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Unit test: schema and sequence of the issued tokens</td></tr>
<tr><td colspan="2">Release-token keys and type cannot be confused with access-token keys and type</td></tr>
<tr><td colspan="2">TOKEN_ISSUED carries operation type, sequence, phase, nbf/exp and fingerprint</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-010] Issuance checks</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Initial ARMED issuance, GO promotion and renewal MUST be distinct operations. Every operation MUST check session state, halt flag, identity, access token, fresh position (age at most position_stale, Table 5) and status before signing. Session state, halt flag, position freshness and status MUST be evaluated again immediately before the signed token is released; a token whose second evaluation fails MUST be discarded and not sent. TOKEN_ISSUED is emitted only for a released token; a discarded token is logged as RENEWAL_REFUSED with its reason.</td></tr>
<tr><td rowspan="4" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M4/M5: no issuance after invalidation, halt or uplink loss beyond position_stale</td></tr>
<tr><td colspan="2">A failing check results in no signature (unit test)</td></tr>
<tr><td colspan="2">Unit test: a status change, halt, target, session abort or stale position that occurs while a token is being signed prevents its release and produces no TOKEN_ISSUED</td></tr>
<tr><td colspan="2">Each operation type is identifiable in TOKEN_ISSUED</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-012] Renewal semantics</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Renewal MUST preserve role and phase; GO promotion MUST be logged separately. A refused request MUST extend nothing, and a request MUST NOT reopen a closed session.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Renewals never change role or phase; each promotion appears as PHASE_CHANGED</td></tr>
<tr><td colspan="2">A request for a DONE/ABORTED session is refused</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-013] Withdrawal by non-issuance; STOP as accelerator</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Federation- or status-conditioned withdrawal MUST work solely through non-issuance and local token expiry without requiring any message to reach the vehicle. Regular completion and emergency stop MAY use authenticated STOP/TOKEN_CLEAR as accelerators; expiry MUST remain the independent fallback.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M4 demonstrates expiry stopping with the business downlink of the affected vehicle blocked</td></tr>
<tr><td colspan="2">Inspection: no code path requires receipt of a message to bring a vehicle to standstill</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-014] Release-token schema</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">A release token MUST use ES256, typ=cd-release+jwt, an issuer-bound kid and exactly the claims session_id, sts_instance, station_id, kolonnen_index, rolle (LEAD/FOLLOW/FOLLOW_GAP), vorgaenger (stationId/GAP/NONE), phase (ARMED/GO), nbf, exp, policy_version, run_id and token_seq. kolonnen_index starts at 0 for the LEAD. No motion-control values are allowed.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Unit test: exact fields and types; tokens with additional or unknown claims fail validation</td></tr>
<tr><td colspan="2">Access tokens use a distinct type and trust purpose</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-STS-015] Composition in the session proposal</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: STS</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The session proposal sent in state PROPOSED MUST contain the identities (stationId, tenant) of all participants, the recipient's rank (kolonnen_index), its predecessor and its wave_predecessor, and the release mode of the session.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The proposal schema contains participant list, rank, predecessor, wave_predecessor and release mode</td></tr>
<tr><td colspan="2">The agent logs the received composition</td></tr>
</table>


### 5.4 Vehicle software: agent, drive logic and protective stop (FR-VEH)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>FR-VEH-001</td><td>Agent credential custody and gateway use</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-002</td><td>Position reporting, renewal and STOP translation</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-004</td><td>Agent failure</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-006</td><td>Token validation</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-007</td><td>Drive state machine</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-008</td><td>Monotonic token deadline</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-009</td><td>Expiry handling and stopping latch</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-010</td><td>Session lock and TOKEN_CLEAR semantics</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-011</td><td>Protective stop on obstacle distance</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-012</td><td>Sensor validity handling</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-013</td><td>Fault latch</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-014</td><td>Agent-to-drive messages</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-015</td><td>HAL and position-source interfaces</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-016</td><td>Termination of convoy authorisation on expiry</td><td>MUST HAVE</td></tr>
<tr><td>FR-VEH-017</td><td>Degradation behaviour: standstill</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-001] Agent credential custody and gateway use</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The vehicle agent MUST use its PCM Cloud holder for its credentials, MUST hold its own vehicle key and MUST use the federation gateway for all external credential operations.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M1 shows the provisioning route per vehicle</td></tr>
<tr><td colspan="2">Inspection: all federation traffic of the vehicle passes the gateway</td></tr>
<tr><td colspan="2">The vehicle private key never leaves the vehicle service</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-002] Position reporting, renewal and STOP translation</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The vehicle agent MUST publish position reports at the configured interval (default 1 s), request renewal at the configured fraction of token lifetime (default 0.5) and translate only a STOP of the current run and session into TOKEN_CLEAR. A missing reply MUST NOT trigger TOKEN_CLEAR.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">An old or foreign-session STOP is ignored; only a current run/session STOP produces TOKEN_CLEAR</td></tr>
<tr><td colspan="2">After a missing renewal reply the vehicle stops by expiry</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-004] Agent failure</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">A failure or restart of the agent logic MUST prevent new releases; the drive logic MUST complete its local expiry stop unaffected. After a start or restart the drive logic MUST command stop() and MUST reject every token until it receives a run_id distributed by lab control over the run-control interface (Table 3) at the initial start or in a reset (Table 5e, step 4); lab control does not re-send the current run_id to a drive logic that restarts during a run. Such tokens are rejected with RUN_MISMATCH unless an earlier check of Table 2a fails.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Integration test: after the agent logic of a rolling vehicle is halted with the agent-stop switch (FR-SIM-004), the vehicle stops by expiry; no old token restarts motion</td></tr>
<tr><td colspan="2">Unit test: after a start the drive logic commands stop() and rejects tokens until a run_id is distributed</td></tr>
<tr><td colspan="2">Unit test: after a restart within a run, a still-valid token of the current run is rejected with RUN_MISMATCH until the next reset</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-006] Token validation</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The drive logic MUST check every TOKEN_SET in the order of Table 2a and MUST answer a rejected token with exactly one SM_NACK whose reason is that of the first failing check. The checks cover schema, type and policy_version, ES256 signature and issuer/key assignment, station and run binding, session lock, fault latch, validity window (nbf/exp with nbf_tolerance, Table 5), sequence, phase/state and, for the ARMED-to-ROLLING transition, sensing. An invalid token MUST NOT replace a valid current token. Every requirement and acceptance criterion of this specification that names an SM_NACK reason applies when no earlier check of Table 2a fails.</td></tr>
<tr><td rowspan="4" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">T-05: each check of Table 2a failing alone yields its reason; each combined-failure vector of T-05 yields the reason of the earlier check</td></tr>
<tr><td colspan="2">An access token presented as a release token is rejected with TOKEN_SCHEMA_INVALID</td></tr>
<tr><td colspan="2">Unit test: exactly one SM_NACK is sent per rejected TOKEN_SET</td></tr>
<tr><td colspan="2">The current valid token remains in force after any rejection</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-007] Drive state machine</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The drive logic MUST implement the state machine of Table 2: from IDLE only ARMED of a new admissible session is accepted; GO requires the same session, a higher token_seq and a valid distance of at least d_min; IDLE, ARMED and FAULT mean standstill.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Unit tests cover every transition of Table 2</td></tr>
<tr><td colspan="2">A direct GO from IDLE is rejected with SESSION_STATE_INVALID</td></tr>
<tr><td colspan="2">A distance below d_min or an invalid sample prevents the ARMED-to-ROLLING transition</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-008] Monotonic token deadline</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">An accepted token MUST establish a local deadline = t_receipt + min(exp − now, exp − nbf), evaluated once at acceptance with the synchronised clock and then tracked on the monotonic clock only, so that the remaining validity never exceeds TTL after receipt. An identical redelivery or a wall-clock adjustment MUST NOT extend an existing deadline.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Unit test: the deadline runs on the monotonic clock; a wall-clock step forward or backward after acceptance does not change it</td></tr>
<tr><td colspan="2">Unit test: an identical redelivery extends nothing</td></tr>
<tr><td colspan="2">TOKEN_ACCEPTED records fingerprint, deadline and current state</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-009] Expiry handling and stopping latch</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">On deadline expiry the drive logic MUST start braking to standstill within delta_local (default 0.10 s, Table 5) (degradation behaviour standstill, FR-VEH-017). An internal stopping latch MUST reject any resumption of convoy motion for the locked session until standstill and then report FAULT(TOKEN_EXPIRED), or IDLE after TOKEN_CLEAR.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M4/M5: after expiry the vehicle brakes and reaches standstill; BRAKE_STARTED records cause and time</td></tr>
<tr><td colspan="2">Any TOKEN_SET for the locked session while stopping is rejected with SESSION_CLOSED</td></tr>
<tr><td colspan="2">FAULT(TOKEN_EXPIRED) is reported at standstill; IDLE only after TOKEN_CLEAR</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-010] Session lock and TOKEN_CLEAR semantics</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Braking, TOKEN_CLEAR or a terminal fault MUST lock the session for the rest of the run; a TOKEN_SET of a locked session is rejected with SESSION_CLOSED unless an earlier check of Table 3a fails. TOKEN_CLEAR MAY clear a fault and change the stopping destination to IDLE but MUST NOT remove the session lock or start motion.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">T-04: a still-valid old ARMED/GO token replayed after clear is rejected; the vehicle stays non-moving</td></tr>
<tr><td colspan="2">TOKEN_CLEAR never produces motion and never unlocks the session</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-011] Protective stop on obstacle distance</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">During ROLLING a free distance below d_min MUST trigger braking within delta_local and FAULT(SAFETY_STOP) at standstill. Distance MUST provide only a start-safety gate and a stopping condition, not following-speed control; no following controller is active and none is driven by release tokens.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M3: the FOLLOW_GAP vehicle stops before the dummy without overlap</td></tr>
<tr><td colspan="2">Inspection: no speed or distance controller acts on the target speed during ROLLING</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-012] Sensor validity handling</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">A missing, invalid or over-age distance sample (sensor_max_age, default 0.20 s) MUST inhibit start and MUST trigger a protective stop while rolling, reported as SENSOR_FAULT.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M5: an invalid sample injected while rolling stops the vehicle with FAULT(SENSOR_FAULT)</td></tr>
<tr><td colspan="2">Start with an invalid sample is rejected with SM_NACK(SENSOR_FAULT)</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-013] Fault latch</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">FAULT MUST remain latched until TOKEN_CLEAR. While latched, a TOKEN_SET of a new session MUST be answered with SM_NACK(FAULT_LATCHED) and a TOKEN_SET of the locked session with SM_NACK(SESSION_CLOSED), unless an earlier check of Table 3a fails.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Unit test: a GO token of a new session after a fault is rejected with FAULT_LATCHED</td></tr>
<tr><td colspan="2">TOKEN_CLEAR leaves the vehicle standing in IDLE with the old session closed</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-014] Agent-to-drive messages</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Agent and drive logic of one vehicle MUST exchange only the messages of Table 1 (TOKEN_SET, TOKEN_CLEAR, SM_ACK, SM_NACK(reason), SM_STATE). Both MAY run in one ORCE instance per vehicle.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Inspection: only the Table 1 message families are exchanged</td></tr>
<tr><td colspan="2">Unit tests exercise the drive logic only through the Table 1 messages and the runcontrol input (Table 3)</td></tr>
<tr><td colspan="2">SM_STATE values are IDLE/ARMED/ROLLING/FAULT and conform to actual standstill</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-015] HAL and position-source interfaces</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The hardware abstraction layer MUST provide setTargetSpeed(v), stop(), getDistance() -> (metres, valid, timestamp) and getMotionState() -> (speed, valid, timestamp) towards the world service; a position-source interface MUST supply (x, y, speed, timestamp) to the agent. Both MUST use a transport independent of the business broker and be documented.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Inspection: all motion and sensor access uses these interfaces</td></tr>
<tr><td colspan="2">Stopping the business broker does not interrupt HAL or position-source traffic (T-12)</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-016] Termination of convoy authorisation on expiry</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The end of a vehicle's convoy authorisation MUST rest on two independent mechanisms: (1) from the disable instant t_disable (known invalidation, halt flag, session abort or missing fresh position/status) the STS signs no further token for the vehicle (FR-GW-008, FR-STS-010); (2) from the local expiry instant t_exp of the last accepted token the drive logic locks the session, accepts no further GO or renewal for it and emits DEGRADATION_STARTED. Neither mechanism requires a message to reach the vehicle.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M4: t_disable and t_exp of the affected vehicle are visible in the event log and on the operations screen</td></tr>
<tr><td colspan="2">Unit test: after t_exp every TOKEN_SET for the locked session is answered SESSION_CLOSED (Table 2a, step 5)</td></tr>
<tr><td colspan="2">Convoy authorisation is never restored without fresh admission, discovery and a new session</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-VEH-017] Degradation behaviour: standstill</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Vehicle software</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">After the end of convoy authorisation (FR-VEH-016) the vehicle MUST brake to standstill (FR-VEH-009). DEGRADATION_STARTED MUST carry the mode standstill.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M4/M5: every degradation ends in standstill; DEGRADATION_STARTED(mode=standstill) is emitted</td></tr>
</table>


### 5.5 World service and fault injection (FR-SIM)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>FR-SIM-001</td><td>Track and kinematic model</td><td>MUST HAVE</td></tr>
<tr><td>FR-SIM-002</td><td>World service</td><td>MUST HAVE</td></tr>
<tr><td>FR-SIM-003</td><td>Independence during convoy-layer faults</td><td>MUST HAVE</td></tr>
<tr><td>FR-SIM-004</td><td>Fault injection for the demonstration</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-SIM-001] Track and kinematic model</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: World service</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The simulator MUST use a closed 2D polyline with one-dimensional along-track motion and occupied vehicle/dummy length intervals. Positions are front points and distance is the front-to-next-rear free path; configured acceleration and braking MUST be integrated to zero without negative speed.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Unit tests validate distance, acceleration and stopping distance against the model</td></tr>
<tr><td colspan="2">Speed never becomes negative; braking integrates to zero</td></tr>
<tr><td colspan="2">The reference track (12 m perimeter) is delivered</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-SIM-002] World service</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: World service</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">A world service separate from the convoy layer MUST supply timestamped position/speed and distance/motion feedback over a transport independent of the business broker. Position reports MUST carry normally distributed noise (sigma_pos, Table 5); the geofinder MUST receive only agent-published reports, never world ground truth.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Inspection verifies the separation of world service, vehicles and convoy layer</td></tr>
<tr><td colspan="2">The geofinder receives only agent-published reports</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-SIM-003] Independence during convoy-layer faults</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: World service</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The world service and the vehicles MUST keep running when the convoy layer is stopped.</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">T-12 stops only the convoy layer; world and vehicles continue and the vehicles stop by expiry</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-SIM-004] Fault injection for the demonstration</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: World service</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Lab control MUST be able to inject the faults of Table 5d (uplink off per vehicle, STS stop, convoy-layer stop, sensor invalid, business downlink block for M4), record each injection as FAULT_INJECTED and keep the listed unaffected components running. For integration tests lab control MUST also provide an agent-stop switch per vehicle (FR-VEH-004) and a block of the connection to the status list (FR-GW-012).</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Each Table 6d fault is injectable from the console</td></tr>
<tr><td colspan="2">FAULT_INJECTED records fault type, onset and affected component</td></tr>
</table>


### 5.6 Dashboard, console, emergency stop and reset (FR-OPS)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>FR-OPS-001</td><td>Dashboard content and freshness</td><td>MUST HAVE</td></tr>
<tr><td>FR-OPS-002</td><td>Authenticated console</td><td>MUST HAVE</td></tr>
<tr><td>FR-OPS-003</td><td>Emergency stop (laboratory abort)</td><td>MUST HAVE</td></tr>
<tr><td>FR-OPS-004</td><td>Reset procedure</td><td>MUST HAVE</td></tr>
<tr><td>FR-OPS-006</td><td>System-identification screen</td><td>MUST HAVE</td></tr>
<tr><td>FR-OPS-007</td><td>Operations screen</td><td>MUST HAVE</td></tr>
<tr><td>FR-OPS-010</td><td>Release-mode comparison view</td><td>OPTION</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-OPS-001] Dashboard content and freshness</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Dashboard, console, emergency stop, reset</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The dashboard MUST be built with the FACIS UI Builder package and consist of the operations screen (FR-OPS-007) and the system-identification screen (FR-OPS-006). It MUST show track and vehicles, tenant, order/gaps/segments, session, roles, phases, remaining TTL, drive state, status and reachability per credential, the active profile and NATIVE/MOCK labels. A stale display MUST be distinguishable from fresh data. Its appearance follows the FAP UI implementation guideline as implemented by the UI Builder package.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M2–M5 show every listed field and label</td></tr>
<tr><td colspan="2">Remaining TTL, drive state, release mode and degradation state per vehicle are visible during the wave</td></tr>
<tr><td colspan="2">A paused event stream is shown as stale</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-OPS-002] Authenticated console</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Dashboard, console, emergency stop, reset</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">A separately authenticated console MUST support start, reset, invalidation/recovery and the Table 5d faults. Destructive actions MUST require confirmation, and console access MUST be limited to the client operators.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Unauthenticated console or lab-control calls fail</td></tr>
<tr><td colspan="2">Confirmation is required for invalidation, STS stop and emergency stop</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-OPS-003] Emergency stop (laboratory abort)</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Dashboard, console, emergency stop, reset</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The emergency stop is the laboratory abort of the convoy layer, not a physical emergency-stop function of a vehicle platform. Its effect path MUST be: (1) the STS blocks new sessions and halts every token issuance within halt_budget (default 1 s, Table 5); (2) the STS sends run/session-bound STOP to reachable vehicles as an accelerator; (3) every vehicle stops at the latest by local token expiry, whether or not STOP was received. Confirmation state and standstill count MUST be displayed.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M5: emergency stop with reachable and with blocked business downlink; all vehicles reach standstill</td></tr>
<tr><td colspan="2">An unconfirmed halt never appears as successful; the standstill count matches the world-observed standstills</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-OPS-004] Reset procedure</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Dashboard, console, emergency stop, reset</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Reset MUST follow the steps of Table 6e, restore this run's credential changes through the OCM W-Stack status list and issue a new run_id only after standstill. Any failure MUST produce RESET_INCOMPLETE and never a demo-ready state.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M5 ends with a reset that reports demo-ready only after health, valid status, free reservations, standstill and the end of the STS start-up hold</td></tr>
<tr><td colspan="2">RESET_COMPLETED is emitted with the new run_id</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-OPS-006] System-identification screen</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Dashboard, console, emergency stop, reset</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The dashboard MUST provide a system-identification screen listing every participant (vehicles, traffic light) and every convoy-layer service with its identifier (DID or service identifier), credential status, trust status and NATIVE/MOCK label per capability.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Each participant and service appears with identifier, credential status and trust status</td></tr>
<tr><td colspan="2">Status changes (STATUS_CHANGED) are reflected on the screen</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-OPS-007] Operations screen</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Dashboard, console, emergency stop, reset</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The dashboard MUST provide an operations screen showing the track with all vehicles and the dummy, the sessions of the current run (state, run_id, release mode, result with reason), the connected traffic light with its current phase and, per vehicle, rank, role, predecessor, wave_predecessor, phase (ARMED/GO), remaining TTL, drive state, GO issuance time and, in coordinated mode, the configured GO offset relative to T0.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">All listed fields are visible during M3 (both release modes)</td></tr>
<tr><td colspan="2">A completed run shows DONE/ABORTED per session with reason</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-OPS-010] Release-mode comparison view</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">OPTION</th></tr>
<tr><td colspan="3">Priority: OPTION (O-2) Group: Dashboard, console, emergency stop, reset</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">With option O-2 the operations screen MUST show, for the last run of each release mode, the GO issuance times and start lag per rank side by side (NFR-KPI-001).</td></tr>
<tr><td valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">After M3(a) and M3(b) both runs are shown side by side</td></tr>
</table>


### 5.7 Business interface, events and codes (FR-IF)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>FR-IF-001</td><td>Business interface contract</td><td>MUST HAVE</td></tr>
<tr><td>FR-IF-002</td><td>Codes and events</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-IF-001] Business interface contract</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Business interface</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The contractor MUST deliver versioned schemas, MQTT topics and request correlation for admission, positions, proposals, confirmations, token operations, status, health, console and traffic-light phase messages. Control messages MUST NOT be retained on the business broker.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Interface description and example messages for every operation</td></tr>
<tr><td colspan="2">Retain is disabled for control topics on the broker</td></tr>
<tr><td colspan="2">Every request carries a correlation identifier and every error a Table 4 code</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-IF-002] Codes and events</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Business interface</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The codes of Table 4 and the events of Table 4a MUST cover every emitted error and event. An unknown value MUST NOT be treated as success.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Inspection of the code and event list against the implementation</td></tr>
<tr><td colspan="2">Unit test: every drive rejection reason of Table 2a is asserted</td></tr>
<tr><td colspan="2">An unknown phase or adapter output fails closed (unit test)</td></tr>
</table>


### 5.8 Configuration profile and fixtures (FR-CFG)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>FR-CFG-001</td><td>Configuration profile</td><td>MUST HAVE</td></tr>
<tr><td>FR-CFG-002</td><td>Profile consistency checks</td><td>MUST HAVE</td></tr>
<tr><td>FR-CFG-003</td><td>Shipped fixtures</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-CFG-001] Configuration profile</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Configuration profile and fixtures</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The contractor MUST deliver one versioned configuration profile (JSON with schema) covering the Table 5 parameters, deployment bindings, polyline, direction, placements and scenario targets. Runtime-generated IDs and secrets MUST remain outside the profile.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Invalid or incomplete profiles are rejected at start with CONFIG_INVALID</td></tr>
<tr><td colspan="2">run_id and secrets are not part of the profile file</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-CFG-002] Profile consistency checks</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Configuration profile and fixtures</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">Every component MUST load the profile through one shared loader that validates it against the schema and against the following checks before start: (1) the stoppingdistance relation of assumption A-2 holds with the loaded values of d_min, v_max, sensor_max_age, delta_local, a_brake and the distance margin; (2) the renewal fraction lies strictly between 0 and 1; (3) the maximum status age exceeds the status poll interval; (4) the ARMED timeout exceeds (number of participants of Table 5 − 1) × coordinated GO offset, whatever release mode the profile selects. A failed check MUST reject the profile with CONFIG_INVALID. The loader MUST log the derived B_stop and the stopping-distance headroom.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">Unit tests: a profile that violates any one of the checks is rejected with CONFIG_INVALID</td></tr>
<tr><td colspan="2">The Table 5 defaults pass all checks; the loader logs B_stop = 0.40 s and a stoppingdistance headroom of about 0.85 m</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-CFG-003] Shipped fixtures</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Configuration profile and fixtures</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The reference placement (Table 5f), its origin-shifted variant (Table 5g, D-02) and one obstacle-free fixture for M4 and M5 MUST be shipped with the source, each with its expected outcome. The discovery reference vectors of Table 5g MUST be shipped as unit-test data. The obstacle-free fixture MUST allow the M4/M5 observation windows to complete before any participant approaches another one on the closed track.</td></tr>
<tr><td rowspan="3" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M2–M5 run with the shipped fixtures</td></tr>
<tr><td colspan="2">Each fixture states its expected outcome</td></tr>
<tr><td colspan="2">All Table 5g vectors pass in CI</td></tr>
</table>


### 5.9 Traffic light, T0 and coordinated release (FR-TL)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Name</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Priority</th></tr>
</thead>
<tbody>
<tr><td>FR-TL-001</td><td>Federation-identified traffic light</td><td>MUST HAVE</td></tr>
<tr><td>FR-TL-002</td><td>T0-bound session start</td><td>MUST HAVE</td></tr>
<tr><td>FR-TL-003</td><td>Coordinated release mode</td><td>MUST HAVE</td></tr>
</tbody>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-TL-001] Federation-identified traffic light</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Traffic light, T0, coordinated release</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">The system MUST include a simulated traffic-light service that is admitted through the federation gateway with its own infrastructure credential issued by the OCM W-Stack and that publishes authenticated signal-phase messages on the business broker. Each phase message MUST carry light_id, intersection_id, a strictly increasing phase_event_id, phase (red/green), the green-onset time T0, validity_until, the stopline position, a timestamp and schemaVersion.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">The traffic light is admitted with a distinct infrastructure credential (M1) and shown on the system-identification screen</td></tr>
<tr><td colspan="2">Unauthenticated phase messages are rejected</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-TL-002] T0-bound session start</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Traffic light, T0, coordinated release</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">When the trigger source is traffic-light, the STS MUST issue the LEAD GO of an ARMED session not before the green-onset time T0 of a valid, not yet consumed phase message of the light bound to the session. A phase change to red before the LEAD GO MUST cancel the pending start; a session that is not ARMED at T0 MUST NOT start on that event. With trigger source console the console start applies (FROPS-002).</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M3(b): LEAD GO is issued not before T0; T0 and phase_event_id are recorded in TOKEN_ISSUED</td></tr>
<tr><td colspan="2">Unit test: a consumed or not increasing phase_event_id, a phase message of a light not bound to the session, a message past validity_until and a red phase before LEAD GO do not start the session</td></tr>
</table>


<table>
<tr><th colspan="2" align="left" style="background-color:#6b6b6b;color:#ffffff">[FR-TL-003] Coordinated release mode</th><th align="right" style="background-color:#6b6b6b;color:#ffffff">MUST HAVE</th></tr>
<tr><td colspan="3">Priority: MUST HAVE Group: Traffic light, T0, coordinated release</td></tr>
<tr><td valign="top" width="22%"><b>Requirement</b></td><td colspan="2">In release mode coordinated the STS MUST issue the follower GO of rank r (kolonnen_index r ≥ 1) not before T0 + r × offset (offset from the profile, Table 5), and only while status and position of that participant are valid (FR-GW-011, FR-STS-010). If the GO of a follower cannot be signed within the ARMED timeout (Table 5) counted from T0, the session is aborted with STATE_TIMEOUT naming ROLLING, the session state at that time (Table 5c). A follower's approach is bounded solely by the d_min gate and protective stop (FR-VEH-007, FR-VEH-011); token schema and deadline handling are the same as in release mode motion-proof.</td></tr>
<tr><td rowspan="2" valign="top" width="22%"><b>Acceptance criteria</b></td><td colspan="2">M3(b): GO issuance instants per rank follow T0 + r × offset</td></tr>
<tr><td colspan="2">M3(b): FOLLOW_GAP stops before the dummy by the protective stop</td></tr>
</table>

---

[← Assumptions, constraints and external dependencies](04_assumptions_constraints_and_external_dependencies.md) | [↑ Table of Contents](../README.md) | [Non-functional requirements →](06_non-functional_requirements.md)

