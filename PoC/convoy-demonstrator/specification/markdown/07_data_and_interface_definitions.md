[← Non-functional requirements](06_non-functional_requirements.md) | [↑ Table of Contents](../README.md) | [Architecture and implementation approach →](08_architecture_and_implementation_approach.md)

---

## 7 Data and interface definitions

This section carries the definitions the requirements refer to. Table 5a is informative.

Table 1 Agent-to-drive messages (FR-VEH-014); BRAKE_STARTED and DEGRADATION_STARTED are log events

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Message</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Direction</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Semantics</th></tr>
</thead>
<tbody>
<tr><td>TOKEN_SET</td><td>Agent → drive</td><td>Raw release JWT; validated on every receipt (FR-VEH-006); an identical current token extends nothing.</td></tr>
<tr><td>TOKEN_CLEAR</td><td>Agent → drive</td><td>Regular/emergency/reset clear; begins or preserves braking; clears a fault at standstill, never the session lock (FR-VEH-010).</td></tr>
<tr><td>SM_ACK / SM_NACK(reason)</td><td>Drive → agent</td><td>Accepted token fingerprint or typed rejection with the reason of the first failing check of Table 3a (Table 5).</td></tr>
<tr><td>SM_STATE</td><td>Drive → agent</td><td>IDLE/ARMED/ROLLING/FAULT; ROLLING continues while braking; IDLE, ARMED and FAULT only at standstill (FR-VEH-007).</td></tr>
</tbody>
</table>


Table 2 Drive state machine (FR-VEH-006 … 013); rejection reasons follow Table 2a

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">State</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Event → behaviour / next state</th></tr>
</thead>
<tbody>
<tr><td>IDLE (standstill)</td><td>Valid TOKEN_SET(ARMED) of a new admissible session → ARMED · TOKEN_SET(GO) → SM_NACK(SESSION_STATE_INVALID) · invalid token → SM_NACK(reason) · token of a locked session → SM_NACK(SESSION_CLOSED) · TOKEN_CLEAR → stays</td></tr>
<tr><td>ARMED (standstill)</td><td>TOKEN_SET(GO), same session, higher token_seq, valid distance ≥ d_min → ROLLING · invalid or over-age sample → SM_NACK(SENSOR_FAULT) · distance &lt; d_min → SM_NACK(SAFETY_STOP) · identical redelivery → SM_ACK, extends nothing · renewal TOKEN_SET(ARMED), same session, higher token_seq → stays ARMED, new deadline · lower token_seq → SM_NACK(TOKEN_STALE) · TOKEN_CLEAR → IDLE, session locked · deadline reached → FAULT(TOKEN_EXPIRED), session locked, DEGRADATION_STARTED</td></tr>
<tr><td>ROLLING (≤ v_max; continues while braking)</td><td>Renewal TOKEN_SET(GO), same session, higher token_seq → stays, new deadline · lower token_seq → SM_NACK(TOKEN_STALE) · deadline reached → braking within delta_local, DEGRADATION_STARTED → FAULT(TOKEN_EXPIRED) at standstill · TOKEN_CLEAR → braking → IDLE · free distance &lt; d_min → braking → FAULT(SAFETY_STOP) · missing/invalid/over-age sample → braking → FAULT(SENSOR_FAULT) · TOKEN_SET of the locked session → SM_NACK(SESSION_CLOSED) · role/phase/rank change → SM_NACK(SESSION_STATE_INVALID)</td></tr>
<tr><td>FAULT(reason) (latched, standstill)</td><td>TOKEN_SET of the locked session → SM_NACK(SESSION_CLOSED) · TOKEN_SET of a new session → SM_NACK(FAULT_LATCHED) · TOKEN_CLEAR → IDLE (fault cleared, session lock kept; never starts motion)</td></tr>
</tbody>
</table>


Table 2a Token acceptance order (FR-VEH-006). The first failing check gives the single SM_NACK reason.

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Step</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Check (fails when …)<br><br></th><th align="left" style="background-color:#6b6b6b;color:#ffffff">SM_NACK reason</th></tr>
</thead>
<tbody>
<tr><td>1</td><td>Schema, typ cdrelease+jwt, algorithm ES256, exact claim set or policy_version is wrong; an access token presented as a release token fails here</td><td>TOKEN_SCHEMA_INVALID</td></tr>
<tr><td>2</td><td>Signature is invalid or the key is not the STS releasetoken key (issuer/kid)</td><td>SIGNATURE_INVALID</td></tr>
<tr><td>3</td><td>station_id differs from the vehicle's stationId</td><td>STATION_MISMATCH</td></tr>
<tr><td>4</td><td>run_id differs from the current run, or no current run_id is set</td><td>RUN_MISMATCH</td></tr>
<tr><td>5</td><td>Token belongs to a locked session, also while braking or in FAULT</td><td>SESSION_CLOSED</td></tr>
<tr><td>6</td><td>Token of a new session while FAULT is latched</td><td>FAULT_LATCHED</td></tr>
<tr><td>7</td><td>now ≥ exp, or nbf > now + nbf_tolerance</td><td>TOKEN_EXPIRED; NBF_FUTURE</td></tr>
<tr><td>8</td><td>Token of the current session with a lower token_seq than the current token, or with the same token_seq and different content (an identical current token is answered SM_ACK and extends nothing); token_seq is never compared across sessions</td><td>TOKEN_STALE; TOKEN_SCHEMA_INVALID</td></tr>
<tr><td>9</td><td>GO from IDLE, GO-to-ARMED regression, change of role, predecessor or rank, or a token of another session that is not locked while the drive logic is ARMED or ROLLING (including braking)</td><td>SESSION_STATE_INVALID</td></tr>
<tr><td>10</td><td>For ARMED-toROLLING: missing, invalid or over-age distance sample; then valid distance below d_min</td><td>SENSOR_FAULT; SAFETY_STOP</td></tr>
</tbody>
</table>


#### Table 3 Interfaces

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Interface</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Direction</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Semantics</th></tr>
</thead>
<tbody>
<tr><td>HAL</td><td>Vehicle ↔ world service (independent transport)</td><td>setTargetSpeed, stop, getDistance, getMotionState with units, validity and timestamps (FR-VEH-015).</td></tr>
<tr><td>Position source</td><td>World service → agent</td><td>Timestamped x/y/speed with noise; the agent publishes authenticated reports at the profile interval (FR-GEO-005).</td></tr>
<tr><td>Uplink switch</td><td>Lab control → vehicle</td><td>Per-vehicle switch that suppresses the vehicle's outgoing business traffic (uplink-off fault, Table 6d).</td></tr>
<tr><td>Run control</td><td>Lab control → drive logic and agent of each vehicle (authenticated)</td><td>run_id at the initial start and at reset step 4 (Table 6e); until it is received the drive logic rejects every token (FR-VEH-004, Table 3a step 4).</td></tr>
<tr><td>Credential</td><td>Agent → PCM Cloud → gateway</td><td>Credentials issued by the OCM W-Stack into the vehicle's PCM Cloud holder; presented to the gateway (FR-GW-001, FR-VEH-001).</td></tr>
<tr><td>Verification</td><td>Gateway → OCM W-Stack</td><td>Presentation verification; result labelled NATIVE, with a separate MOCK label for a client-approved supplementing check (FR-GW-003).</td></tr>
<tr><td>Status</td><td>Gateway → OCM W-Stack status list</td><td>Polling, invalidation and recovery (FR-GW-005, FRGW-006).</td></tr>
<tr><td>Traffic-light phase</td><td>Traffic light → business broker → STS, dashboard</td><td>Authenticated phase messages with infrastructure access token (FR-TL-001, NFR-SEC-004).</td></tr>
<tr><td>Console / lab control</td><td>Operator → ORCE operations instance</td><td>Start, invalidation/recovery, faults of Table 6d, agent stop and status-list block for integration tests, emergency stop, reset (FR-OPS-002 … 004, FRSIM-004).</td></tr>
</tbody>
</table>


#### Table 4 Codes

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Code / group</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Emitter</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Meaning</th></tr>
</thead>
<tbody>
<tr><td>VP_INVALID</td><td>Gateway</td><td>Negative verification result; sub-reason CREDENTIAL_REVOKED from the status list; CHAIN_INVALID or BINDING_INVALID where the OCM W-Stack distinguishes them (FR-GW004).</td></tr>
<tr><td>ACCESS_TOKEN_INVALID / IDENTITY_MISMATCH</td><td>Request receivers</td><td>Authorisation failure or wrong bound identity; also unauthenticated phase messages (FR-GW-002, FR-TL-001).</td></tr>
<tr><td>SERVICE_UNAVAILABLE</td><td>Gateway / STS</td><td>OCM W-Stack or PCM Cloud unreachable, invalid answer or timeout (FR-GW-004, NFRTIM-002).</td></tr>
<tr><td>SESSION_CONFLICT / STATE_TIMEOUT / LEAD_UNAVAILABLE</td><td>STS</td><td>Reservation conflict, named state timeout, lead failure (FR-STS-001, -004, -008).</td></tr>
<tr><td>SESSION_STATE_INVALID</td><td>STS / drive</td><td>Operation or phase incompatible with the current state.</td></tr>
<tr><td>POSITION_INVALID</td><td>Geofinder</td><td>Invalid, stale or foreign position report (FR-GEO001, FR-GEO-005).</td></tr>
<tr><td>TOKEN_SCHEMA_INVALID / SIGNATURE_INVALID / TOKEN_EXPIRED / NBF_FUTURE / STATION_MISMATCH / RUN_MISMATCH / TOKEN_STALE</td><td>Drive</td><td>Release-token validation failure (FR-VEH-006, Table 3a).</td></tr>
<tr><td>SESSION_CLOSED / FAULT_LATCHED</td><td>Drive</td><td>Locked session; latched fault (FR-VEH-010, FRVEH-013, Table 3a).</td></tr>
<tr><td>SENSOR_FAULT / SAFETY_STOP</td><td>Drive</td><td>Invalid sensing; valid obstacle distance below d_min (FR-VEH-011, FR-VEH-012).</td></tr>
<tr><td>CONFIG_INVALID / RESET_INCOMPLETE</td><td>Lab control / starting component</td><td>Invalid profile or failed consistency check; failed reset (FR-CFG-001, FR-CFG-002, FR-OPS-004).</td></tr>
</tbody>
</table>


Table 4a Business events (NFR-EVD-001). Every event carries event_type, timestamp, component, run_id and release_mode.

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Event</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Emitter</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Additional fields</th></tr>
</thead>
<tbody>
<tr><td>TOKEN_ISSUED</td><td>STS</td><td>Operation type (initial ARMED / GO promotion / renewal), sequence, phase, nbf/exp, fingerprint; for a LEAD GO with trigger traffic-light the phase_event_id and T0.</td></tr>
<tr><td>TOKEN_ACCEPTED</td><td>Drive</td><td>Fingerprint, deadline, state.</td></tr>
<tr><td>RENEWAL_REFUSED</td><td>STS</td><td>Request ID, code, t_disable where applicable.</td></tr>
<tr><td>PHASE_CHANGED</td><td>STS</td><td>Previous/new phase; motion report IDs (motion-proof) or rank and offset (coordinated).</td></tr>
<tr><td>BRAKE_STARTED</td><td>Drive</td><td>Cause and brake time.</td></tr>
<tr><td>DEGRADATION_STARTED</td><td>Drive</td><td>Mode (standstill), t_exp, session_id, station_id.</td></tr>
<tr><td>STANDSTILL</td><td>World / drive</td><td>Observed speed, timestamp, drive state.</td></tr>
<tr><td>SESSION_ENDED</td><td>STS</td><td>DONE/ABORTED and reason.</td></tr>
<tr><td>FAULT_INJECTED</td><td>Lab control</td><td>Fault type (a Table 6d fault or EMERGENCY_STOP), onset, affected component.</td></tr>
<tr><td>STATUS_CHANGED</td><td>Gateway</td><td>Credential, operation, NATIVE/MOCK label, request start of the observation.</td></tr>
<tr><td>RESET_COMPLETED</td><td>Lab control</td><td>New run_id.</td></tr>
</tbody>
</table>


Table 5 Parameters (fixed demonstration defaults; may be adjusted during integration within the checks of FR-CFG-002)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Parameter</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Default</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Used by</th></tr>
</thead>
<tbody>
<tr><td>TTL / renewal fraction</td><td>10 s / 0.5</td><td>FR-STS-009, FR-VEH-002</td></tr>
<tr><td>nbf_tolerance</td><td>1 s</td><td>FR-STS-009, FR-VEH-006</td></tr>
<tr><td>Access-token lifetime</td><td>10 min</td><td>FR-GW-002</td></tr>
<tr><td>Status poll interval / maximum status age</td><td>1 s / 30 s</td><td>FR-GW-006, FR-GW-007</td></tr>
<tr><td>delta_local / sensor_max_age</td><td>0.10 s / 0.20 s</td><td>FR-VEH-009, FR-VEH-011, FR-VEH012</td></tr>
<tr><td>halt_budget / call_deadline</td><td>1 s / 5 s</td><td>FR-OPS-003, NFR-TIM-002, NFRTIM-004</td></tr>
<tr><td>World tick / drive tick / position sample / report interval</td><td>0.05 s / 0.05 s / 0.10 s / 1 s</td><td>FR-VEH-002, FR-SIM-001</td></tr>
<tr><td>position_stale</td><td>3 s</td><td>FR-GEO-001, FR-GEO-002, FR-STS010, Table 6g D-09</td></tr>
<tr><td>v_max / a_accel / a_brake</td><td>0.3 m/s / 1 m/s² / 1 m/s²</td><td>FR-SIM-001</td></tr>
<tr><td>d_min / distance margin</td><td>1.0 m / 0.01 m</td><td>FR-VEH-007, FR-VEH-011</td></tr>
<tr><td>Vehicle / dummy length</td><td>0.20 m / 0.20 m</td><td>FR-SIM-001</td></tr>
<tr><td>sigma_pos / lane threshold</td><td>0.10 m per axis / 0.30 m</td><td>FR-GEO-002, FR-SIM-002</td></tr>
<tr><td>Gap threshold / stable cycles / geofinder cycle</td><td>2.20 m / 3 / 1 s</td><td>FR-GEO-004</td></tr>
<tr><td>Cut tolerance / discovery distance resolution</td><td>0.10 m / 1 mm</td><td>FR-GEO-003</td></tr>
<tr><td>Discovery standstill / duration</td><td>0.05 m/s / 3 s</td><td>FR-GEO-002</td></tr>
<tr><td>v_move / motion reports</td><td>0.10 m/s / 2</td><td>FR-STS-006</td></tr>
<tr><td>State timeouts proposed/confirmed/issued/armed/rolling</td><td>3/3/3/10/60 s</td><td>FR-STS-004, FR-TL-003</td></tr>
<tr><td>standstill_epsilon</td><td>0.001 m/s</td><td>FR-STS-007</td></tr>
<tr><td>Track points / direction</td><td>(0,0),(3,0),(3,3),(0,3),(0,0); listed order (12 m perimeter)</td><td>FR-SIM-001, FR-GEO-003</td></tr>
<tr><td>Reference lead target</td><td>2.0 m</td><td>FR-STS-007</td></tr>
<tr><td>UI update interval</td><td>1 s</td><td>NFR-TIM-005</td></tr>
<tr><td>release_mode</td><td>motion-proof (default) or coordinated</td><td>FR-STS-006, FR-TL-003</td></tr>
<tr><td>Trigger source</td><td>console or traffic-light</td><td>FR-TL-002</td></tr>
<tr><td>Coordinated GO offset per rank</td><td>1.0 s (to be confirmed by the client within check (4) of FR-CFG-002)</td><td>FR-TL-003</td></tr>
<tr><td>Participants / STS / traffic light</td><td>3 participants and one reference dummy / one STS / one light (fixed scope)</td><td>FR-OPS-007, FR-TL-001</td></tr>
</tbody>
</table>





#### Table 5a Expected stopping times (informative; NFR-TIM-001)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Case</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Expected stop</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Remark</th></tr>
</thead>
<tbody>
<tr><td>Local expiry</td><td>braking starts ≤ t_exp + delta_local; standstill ≤ t_exp + B_stop</td><td>B_stop = delta_local + v_max/a_brake = 0.4 s with Table 6 defaults.</td></tr>
<tr><td>Uplink off while ROLLING</td><td>standstill ≤ t_fault + TTL + B_stop (+ processing time of a renewal sent before t_fault)</td><td>No renewal request arrives after t_fault.</td></tr>
<tr><td>Uplink off while ARMED / awaiting GO</td><td>standstill ≤ t_fault + position_stale + TTL + B_stop</td><td>No GO is signed without a fresh position (FR-STS-010).</td></tr>
<tr><td>STS or convoy-layer stop</td><td>standstill ≤ t_fault + TTL + B_stop</td><td>No signature after the stop; world and vehicles continue.</td></tr>
<tr><td>Credential invalidation</td><td>standstill ≤ t_fault + propagation + TTL<br><br>+ B_stop</td><td>Propagation of the OCM WStack status list is shown, not qualified.</td></tr>
<tr><td>Emergency stop</td><td>standstill ≤ t_fault + halt_budget + TTL<br><br>+ B_stop</td><td>Also with blocked downlink (FR-OPS-003).</td></tr>
<tr><td>Sensor invalid while ROLLING</td><td>detection ≤ last valid sample + sensor_max_age + delta_local; then braking</td><td>Protective stop (FR-VEH-012).</td></tr>
</tbody>
</table>


#### Table 5b Status decision rule (FR-GW-011)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Status</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Condition</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Admission / new session / ARMED / GO<br><br></th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Renewal</th></tr>
</thead>
<tbody>
<tr><td>Valid</td><td>Authentic status list, at least one successful observation, age &lt; maximum status age (measured from the request start of the last successful observation, FR-GW-007), credential not suspended or revoked</td><td>Allowed</td><td>Allowed</td></tr>
<tr><td>Blocked</td><td>No successful observation, unauthentic status list, age ≥ maximum status age, or credential suspended/revoked</td><td>Blocked</td><td>Blocked</td></tr>
</tbody>
</table>


#### Table 5c Session protocol (FR-STS-004)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">State</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Entry / behaviour</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Transition</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Timeout</th></tr>
</thead>
<tbody>
<tr><td>PROPOSED</td><td>Atomically reserve participants; send proposal with participants, rank, predecessor, wave_predecessor and release mode (FR-STS-001, FR-STS-015).</td><td>All confirm → CONFIRMED; reject/timeout → ABORTED.</td><td>proposed</td></tr>
<tr><td>CONFIRMED</td><td>Check roles, identities and valid status.</td><td>All initial ARMED tokens issued → TOKENS_ISSUED; failed check → ABORTED.</td><td>confirmed</td></tr>
<tr><td>TOKENS_ISSUED</td><td>Await drive acknowledgements; renewal of ARMED tokens with valid status.</td><td>All ARMED → ARMED; reject/timeout → ABORTED.</td><td>issued</td></tr>
<tr><td>ARMED</td><td>Roles binding (FR-STS-005); LEAD GO on console start or not before T0 of a valid phase message (FR-TL-002).</td><td>LEAD motion → ROLLING; failure/timeout/red before LEAD GO → ABORTED.</td><td>armed</td></tr>
<tr><td>ROLLING</td><td>Follower GO by motion proof (FR-STS-006) or at T0 + r × offset (FR-TL-003); at target halt issuance and send STOP (FR-STS007).</td><td>Target and all standing → DONE; lead loss/timeout<br><br>→ ABORTED (FR-STS008); in release mode coordinated, a follower GO not signed within the ARMED timeout after T0<br><br>→ ABORTED with STATE_TIMEOUT naming ROLLING (FR-TL003).</td><td>rolling</td></tr>
<tr><td>DONE</td><td>All standing; no more issuance.</td><td>Terminal.</td><td>–</td></tr>
<tr><td>ABORTED</td><td>No more issuance; vehicles may still be stopping.</td><td>Terminal; reservations persist until the last token has expired plus B_stop (FR-STS-002).</td><td>–</td></tr>
</tbody>
</table>


- Table 5d Demonstrated faults (FR-SIM-004)


<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Fault</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Stopped or blocked</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Remains active</th></tr>
</thead>
<tbody>
<tr><td>Uplink off</td><td>Outgoing business traffic of the chosen vehicle (uplink switch)</td><td>Agent, drive, world, other vehicles</td></tr>
<tr><td>STS stop</td><td>STS (ORCE instance scaled to zero until the following reset)</td><td>Gateway, vehicles, world, dashboard</td></tr>
<tr><td>Convoy-layer stop</td><td>Gateway, geofinder/STS and business broker</td><td>Vehicles, world, dashboard (local view) (T-12)</td></tr>
<tr><td>Sensor invalid</td><td>Distance validity of the chosen vehicle</td><td>Drive, world</td></tr>
<tr><td>Downlink block (M4)</td><td>All business traffic to the affected vehicle, including STOP</td><td>Outgoing reports of that vehicle, world</td></tr>
</tbody>
</table>


Table 5e Reset (FR-OPS-004)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Step</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Action</th></tr>
</thead>
<tbody>
<tr><td>1</td><td>Block new sessions and token issuance.</td></tr>
<tr><td>2</td><td>Wait for standstill of every vehicle (by STOP or expiry).</td></tr>
<tr><td>3</td><td>Restore this run's credential changes via the OCM W-Stack status list (lift suspension or re-issue); TOKEN_CLEAR local faults; end every injected fault of Table 6d and restart every component it stopped; restore the scenario placement.</td></tr>
<tr><td>4</td><td>Distribute a new run_id over the run-control interface (Table 4); lift the block of step 1 and any emergency-stop halt (FR-OPS-003); report demo-ready only after health, valid status, free reservations, standstill and the end of the STS start-up hold (FR-STS-002). Any failure → RESET_INCOMPLETE.</td></tr>
</tbody>
</table>


Table 5f Reference placement for M2/M3 (FR-GEO-003, FR-GEO-004, FR-STS-005; vector D-01 of Table 6g)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Object</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Front arc length</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Role</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Clearance</th></tr>
</thead>
<tbody>
<tr><td>CD-V1</td><td>4.90 m</td><td>LEAD / NONE</td><td>1.70 m to CD-V2 (free distance 1.50 m<br><br>= d_min + 0.50 m)</td></tr>
<tr><td>CD-V2</td><td>3.20 m</td><td>FOLLOW / CD-V1</td><td>1.00 m to the dummy; 2.70 m to CD-V3 (gap threshold 2.20 m + 0.50 m)</td></tr>
<tr><td>Dummy</td><td>2.20 m</td><td>Passive obstacle</td><td>1.70 m to CD-V3 (free distance 1.50 m; 0.50 m of travel before the protective stop at d_min)</td></tr>
<tr><td>CD-V3</td><td>0.50 m</td><td>FOLLOW_GAP / GAP; wave_predecessor CD-V2</td><td>Formation span 4.40 m, below half the 12 m perimeter</td></tr>
</tbody>
</table>


Table 5g defines the discovery reference vectors. Inputs are noise-free position reports at the report interval of 1 s, fed into an empty geofinder state from t = −3 s on, unless a vector states an earlier start; geofinder cycle n runs at t = n − 1 s and evaluates the reports received up to that time. Unless stated otherwise, CD-V1 … V3 are admitted, unreserved, on the lane centre line and report speed 0 m/s in every report, so that they meet the discovery standstill duration from cycle 1; the dummy sends no reports. Positions are front arc lengths s along the Table 5 track in driving direction (perimeter 12 m); arcs are measured front to front in driving direction. Outcomes give the formation reported under the stable-cycle rule of FR-GEO-004 and, where stated, the cycle at whose end it is reported.

#### Table 5g Discovery reference vectors (FR-GEO-001 … 004, FR-CFG-003; unit tests in CI)

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Input</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Expected outcome</th></tr>
</thead>
<tbody>
<tr><td>D-01</td><td>Reference placement: V1 4.90 m, V2 3.20 m, V3 0.50 m</td><td>V1 LEAD/NONE, V2 FOLLOW/V1, V3 FOLLOW_GAP/GAP; wave_predecessor of V3 is V2; reported at the end of cycle 3</td></tr>
<tr><td>D-02</td><td>Origin-shifted: every position of D-01 plus 8.00 m modulo 12 m (V1 0.90 m, V2 11.20 m, V3 8.50 m)</td><td>As D-01</td></tr>
<tr><td>D-03</td><td>As D-01 with V3 at 1.00 m (arc V3 to V2 equals the gap threshold of 2.20 m)</td><td>V1 LEAD/NONE, V2 FOLLOW/V1, V3 FOLLOW/V2 (no gap)</td></tr>
<tr><td>D-04</td><td>As D-01 with V3 at 0.90 m (arc V3 to V2 is 2.30 m)</td><td>As D-01</td></tr>
<tr><td>D-05</td><td>As D-01 with V2 reported 0.35 m to the outside of the track at x = 3.35 m, y = 0.20 m (nearest track point s = 3.20 m; lateral distance 0.35 m, above the lane threshold of 0.30 m)</td><td>V2 not eligible; V1 LEAD/NONE, V3 FOLLOW_GAP/GAP; wave_predecessor of V3 is V1</td></tr>
<tr><td>D-06</td><td>As D-01 with V2 reporting a speed of 0.08 m/s</td><td>As D-05</td></tr>
<tr><td>D-07</td><td>As D-01 with V1 and V2 holding an active reservation</td><td>No formation (one participant)</td></tr>
<tr><td>D-08</td><td>As D-01; every report of V2 is delivered twice, and one older report of V2 arrives after a newer one</td><td>Duplicates and the older report are discarded; the D-01 formation is reported at the end of cycle 3, as in D-01</td></tr>
<tr><td>D-09</td><td>As D-01, but the input starts at t = −8 s; V3 reports (standing) only from t = −8 s to t = −4 s, so that its last accepted report is older than position_stale in every cycle</td><td>V3 not eligible; V1 LEAD/NONE, V2 FOLLOW/V1</td></tr>
<tr><td>D-10</td><td>Cycle 1 as D-05; from cycle 2 on as D-01</td><td>No formation is reported at the end of cycles 1, 2 and 3; the D-01 formation is reported at the end of cycle 4</td></tr>
<tr><td>D-11</td><td>V1 7.00 m, V2 3.50 m, V3 0.50 m (span 6.50 m)</td><td>No formation (span above half the perimeter)</td></tr>
<tr><td>D-12</td><td>V1 6.54 m, V3 0.50 m; V2 at 3.20 m holding an active reservation (arcs 6.04 m and 5.96 m, difference 0.08 m below the cut tolerance; span 5.96 m)</td><td>No formation (ambiguous cut); without the cut tolerance V3 would be LEAD/NONE and V1 FOLLOW_GAP/GAP</td></tr>
</tbody>
</table>

---

[← Non-functional requirements](06_non-functional_requirements.md) | [↑ Table of Contents](../README.md) | [Architecture and implementation approach →](08_architecture_and_implementation_approach.md)

