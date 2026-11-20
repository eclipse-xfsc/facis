[← Purpose and exit criteria](01_purpose_and_exit_criteria.md) | [↑ Table of Contents](../README.md) | [Integration with the XFSC/FACIS tool stack →](03_integration_with_the_xfscfacis_tool_stack.md)

---

## 2 Scope
### 2.1 In scope

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Item</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Deliverables</th></tr>
</thead>
<tbody>
<tr><td>Convoy layer – federation gateway</td><td>ORCE flows and custom nodes for admission, verification and status via OCM W-Stack, access tokens and the issuance block (FR-GW-001 … 015).</td></tr>
<tr><td>Convoy layer – geofinder and STS</td><td>One ORCE instance with the geofinder (FR-GEO-001 … 005) and the single STS with both release modes and the token lifecycle (FR-STS-001 … 015, FR-TL-002, FR-TL-003).</td></tr>
<tr><td>Convoy layer – business broker</td><td>A dedicated MQTT broker over TLS with ACLs (FR-IF-001, NFR-SEC-001, NFR-SEC-004).</td></tr>
<tr><td>Dashboard, console and lab control</td><td>Built with the FACIS UI Builder package: operations screen and systemidentification screen, console with fault injection, emergency stop and reset (FR-OPS-001 … 007).</td></tr>
<tr><td>Vehicle software</td><td>Three vehicle services, each one ORCE instance with agent and drive logic (FR-VEH-001 … 017).</td></tr>
<tr><td>World service</td><td>Closed 2D track, kinematics, front-distance model and position noise, on a transport independent of the business broker (FR-SIM-001 … 004).</td></tr>
<tr><td>Simulated traffic light</td><td>One ORCE instance admitted with its own OCM W-Stack infrastructure credential (FR-TL-001).</td></tr>
<tr><td>Event log</td><td>Structured events shown in the dashboard (NFR-EVD-001, NFR-EVD-004).</td></tr>
<tr><td>Configuration profile and fixtures</td><td>One versioned profile with schema and consistency checks, three fixtures and the discovery reference vectors of Table 5g (FR-CFG-001 … 003).</td></tr>
<tr><td>Deployment</td><td>Helm charts for the FACIS cloud environment (NFR-DEP-001 … 003).</td></tr>
<tr><td>Demonstration and handover</td><td>Demonstration script M1–M5 and R, runbook and README (NFR-DEL-001, NFR-DEL-005).</td></tr>
</tbody>
</table>

### 2.2 Out of scope


<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Item</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Reason</th></tr>
</thead>
<tbody>
<tr><td>Physical vehicles, positioning hardware, embedded boards, a trial day</td><td>The HAL and position-source interfaces (FR-VEH-015) are kept so that hardware can be attached later. The traffic light is simulated (FRTL-001).</td></tr>
<tr><td>Modifying, re-hosting or reimplementing XFSC services</td><td>FR-GW-013: OCM W-Stack and PCM Cloud are consumed as provided.</td></tr>
<tr><td>A second STS, a dispatcher, a variable number of participants, more than one intersection</td><td>Fixed scope: three participants, one reference dummy, one STS, one traffic light (Table 5).</td></tr>
<tr><td>Following-speed or distance control between vehicles, sensor-assisted convoy mode</td><td>FR-VEH-011: distance is only a start gate and a stopping condition.</td></tr>
<tr><td>Any withdrawal message as a precondition for stopping</td><td>FR-STS-013, FR-VEH-016.</td></tr>
<tr><td>A physical emergency-stop function</td><td>FR-OPS-003: the emergency stop is the laboratory abort of the convoy layer.</td></tr>
<tr><td>Driver or other personal credentials</td><td>FR-GW-015.</td></tr>
<tr><td>ETSI ITS PKI certificates, ETSI CAM/SPaT/MAP mappings</td><td>Participants are identified with FACIS federation credentials only.</td></tr>
<tr><td>Gaia-X / GXDCH compliance, XFSC Federated Catalogue registration, FACIS Digital Contracting Service, federation-based operator sign-on</td><td>No contribution to E1–E5.</td></tr>
<tr><td>Calibration, qualification freeze, repeated acceptance runs, statistical</td><td>Not required for a TRL 4 laboratory demonstrator; the witnessed demonstration is the acceptance (NFR-DEL-005).</td></tr>
<tr><td>KPI and latency evidence, independent evidence re-analysis, safety argument</td><td></td></tr>
<tr><td>Operational QoS targets, availability, endurance</td><td>Not required for a laboratory demonstrator.</td></tr>
<tr><td>Operation of the OCM W-Stack, PCM Cloud and the FACIS cloud environment; initial issuance of the test credentials at kick-off</td><td>Client conditions precedent (Section 4). Suspension, revocation, recovery and re-issuance during the demonstration and the reset are performed by the CD through the OCM W-Stack (FR-GW-005, Table 5e).</td></tr>
</tbody>
</table>


### 2.3 Optional positions

Options are offered separately from the core scope. An option is delivered only if the client orders it. Requirements that belong to an option carry the priority OPTION. An ordered option is accepted separately on the demonstration protocol against the acceptance criteria stated for it (O-1: this table and FR-GW-014; O-2: FR-OPS-010, NFR-KPI-001); its outcome does not affect acceptance of the core scope.

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Option</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Content</th></tr>
</thead>
<tbody>
<tr><td>O-1 Dedicated PCM Cloud instance per vehicle</td><td>The client provides one PCM Cloud instance per simulated vehicle when it orders O-1 and issues the test credentials into it (condition precedent applies to these instances from the order). After the M1 run of the core scope, the contractor binds each vehicle agent to its own instance, records the holder arrangement and runs M1 a second time with this arrangement, recorded separately in the demonstration protocol (extends FR-GW-014). Acceptance: inspection shows one PCM Cloud instance per vehicle and no shared instance; the second M1 run passes.</td></tr>
<tr><td>O-2 Release-mode comparison and start-delay indicators</td><td>Comparison view of the last run of each release mode and start-delay indicators per rank (FR-OPS-010, NFR-KPI-001).</td></tr>
</tbody>
</table>

---

[← Purpose and exit criteria](01_purpose_and_exit_criteria.md) | [↑ Table of Contents](../README.md) | [Integration with the XFSC/FACIS tool stack →](03_integration_with_the_xfscfacis_tool_stack.md)

