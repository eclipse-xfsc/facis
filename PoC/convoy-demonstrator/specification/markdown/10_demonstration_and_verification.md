[← Repository and delivery](09_repository_and_delivery.md) | [↑ Table of Contents](../README.md) | [Delivery, acceptance and scope control →](11_delivery_acceptance_and_scope_control.md)

---

## 10 Demonstration and verification

### 10.1 Environment and fixtures

All scenarios run once in the FACIS cloud environment with the profile of the tagged release (NFRCFG-001): the Table 5 defaults or values adjusted within the checks of FR-CFG-002, with release_mode and trigger source set per M3 run. Fixtures: the reference placement of Table 5f, its origin-shifted variant (Table 5g, D-02) and one obstacle-free fixture for M4 and M5 (FR-CFG-003). Station identifiers CD-V1 … CD-V3 are synthetic. M3 runs once per release mode (NFR-DEL-005).

Integration tests run once in the FACIS cloud environment with the lab-control switches of FR-SIM-004 and are recorded in the demonstration protocol: the connection to the status list is blocked and released, and admission succeeds again without restart (FR-GW-012); the agent logic of a rolling vehicle is halted with the agent-stop switch, and the vehicle stops by local expiry without any old token restarting motion (FR-VEH-004).

### 10.2 Demonstration scenarios

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Scenario</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Content</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Exit</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Main requirements</th></tr>
</thead>
<tbody>
<tr><td>M1 Admission and status</td><td>Credentials of CD-V1 … V3 and the traffic light issued via the OCM W-Stack into PCM Cloud (condition precedent); positive admission; rejection of an invalid presentation, a revoked credential and a forged identity (vehicle A for B); rejection of a vehicle identity calling a console or lab-control endpoint and of a vehicle publishing on a release topic; revocation, re-issuance via the OCM W-Stack and recovery via the status list without automatic start.</td><td>E1</td><td>FR-GW-001 … 015, FR-VEH-001, FR-TL001, NFR-SEC-003, NFR-SEC-004</td></tr>
<tr><td>M2 Formation</td><td>Reference placement and origin-shifted variant; order, gap segmentation and roles shown on the dashboard.</td><td>E2</td><td>FR-GEO-001 … 005, FR-STS-001, FRSTS-005, FR-OPS001</td></tr>
<tr><td>M3 Wave</td><td>(a) motion-proof / console; (b) coordinated / trafficlight T0 with offset per rank. In both: FOLLOW_GAP protective stop before the dummy, target STOP, DONE. With option O-2 the start-delay indicators are shown.</td><td>E2</td><td>FR-STS-004 … 009, FR-STS-014, FRVEH-007, FR-VEH011, FR-TL-002, FRTL-003, FR-OPS-007</td></tr>
<tr><td>M4 Withdrawal without message</td><td>Obstacle-free fixture; last participant rolling; its credential is revoked via the status list; its business downlink is blocked; it stops by local expiry; the others complete.</td><td>E3</td><td>FR-GW-005, FRGW-008, FR-<a href="https://github.com/eclipse-xfsc/deployment/tree/main/PCM%20Cloud">STS01</a>, FR-VEH-016, FR-VEH-017, NFREVD-004</td></tr>
<tr><td>M5 Faults and reset</td><td>Obstacle-free fixture; uplink off; STS stop; convoylayer stop (T-12); sensor invalid; emergency stop with reachable and blocked downlink; each followed by a reset to demo-ready.</td><td>E4</td><td>FR-STS-002, FRVEH-009, FR-<a href="https://github.com/eclipse-xfsc/deployment/tree/main/OCM%20W-Stack">VEH01</a>, FR-SIM-003, FR-SIM-004, FROPS-002 … 004, NFR-TIM-004</td></tr>
<tr><td>R Deployment and handover</td><td>Helm deployment of the tagged release in FACIS cloud environment; client operator follows the runbook; demonstration protocol signed.</td><td>E5</td><td>NFR-DEP-001 … 003, NFR-CFG-003, NFR-DEL-001 … 005</td></tr>
</tbody>
</table>


### 10.3 Edge checks

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Check</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Case</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Expected result</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Form</th></tr>
</thead>
<tbody>
<tr><td>T-04</td><td>TOKEN_CLEAR, then an old still-valid GO token</td><td>No motion; old session stays closed (SESSION_CLOSED)</td><td>Unit test</td></tr>
<tr><td>T-05</td><td>Each check of Table 2a failing alone. Combined failures: locked session and expired; locked session and invalid signature; FAULT latched, new session and wrong station; old ARMED token of the same session, still within its validity window, after GO; GO from IDLE with an invalid sensor sample; old run and expired after reset. Access token as release token.</td><td>SM_NACK with the reason of the first failing check of Table 2a (SESSION_CLOSED, SIGNATURE_INVALID, STATION_MISMATCH, TOKEN_STALE, SESSION_STATE_INVALID, RUN_MISMATCH, TOKEN_SCHEMA_INVALID for the listed combinations); no motion; valid state unchanged</td><td>Unit test</td></tr>
<tr><td>T-10</td><td>The wave_predecessor of the FOLLOW_GAP participant becomes unavailable (stale position or blocked status) before its motion proof</td><td>No GO for the dependent follower; it remains at standstill</td><td>Unit test</td></tr>
<tr><td>T-12</td><td>Convoy-layer stop with the world running</td><td>Vehicles stop by local expiry; vehicle services are not stopped</td><td>Demonstrated in M5</td></tr>
</tbody>
</table>


### 10.4 Unit tests in CI

Unit tests cover token validation in the order of Table 2a and the drive state machine (T-04, T-05), the token deadline, the discovery reference vectors of Table 5g, the motion proof including T-10, the STS session logic, the status age rule (FR-GW-007), the profile consistency checks (FR-CFG-002) and the traffic-light checks of FR-TL-002; they run in CI (NFR-CFG-004).

---

[← Repository and delivery](09_repository_and_delivery.md) | [↑ Table of Contents](../README.md) | [Delivery, acceptance and scope control →](11_delivery_acceptance_and_scope_control.md)

