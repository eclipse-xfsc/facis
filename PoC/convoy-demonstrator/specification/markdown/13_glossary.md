[← Storyline traceability](12_storyline_traceability.md) | [↑ Table of Contents](../README.md)

---

## 13 Glossary

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">Term</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Meaning</th></tr>
</thead>
<tbody>
<tr><td>Access token</td><td>Token issued by the gateway after admission, bound to stationId, tenant and credential identifiers (FR-GW-002).</td></tr>
<tr><td>B_stop</td><td>delta_local + v_max/a_brake: local reaction plus maximum braking duration.</td></tr>
<tr><td>Conditions precedent</td><td>Services, credentials and access the client provides after project start, outside the effort frame (Section 4).</td></tr>
<tr><td>delta_local / sensor_max_age</td><td>Maximum time from a local stop decision to the start of braking / maximum age of a distance sample that may be used (Table 5).</td></tr>
<tr><td>Demonstration protocol</td><td>Record of the witnessed demonstration per scenario with date, result and witness.</td></tr>
<tr><td>Discovery reference vector</td><td>Client-defined geofinder input with its expected outcome (Table 5g).</td></tr>
<tr><td>FACIS UI Builder package</td><td>FACIS package for building FAP-conformant user interfaces; used for dashboard and console.</td></tr>
<tr><td>Geofinder</td><td>Cloud component that discovers formations from authenticated position reports.</td></tr>
<tr><td>Integration Note</td><td>Records of the FACIS credential profile, the versions of OCM W-Stack, PCM Cloud, ORCE and FACIS UI Builder, the FACIS trust list, the holder arrangement, the verification sub-reasons provided and any client-approved mock (NFR-DEL-002).</td></tr>
<tr><td>Laboratory abort</td><td>The emergency stop of the CD (FR-OPS-003); not a physical emergency stop.</td></tr>
<tr><td>NATIVE / MOCK</td><td>Result produced by the OCM W-Stack / by an explicit, client-approved mock that supplements a native result for a recorded gap (FR-GW-003).</td></tr>
<tr><td>OCM W-Stack / PCM Cloud</td><td>XFSC organisational credential manager (issuance, verification, status list) / XFSC personal credential manager used as holder per vehicle.</td></tr>
<tr><td>OPTION</td><td>Priority of a requirement that belongs to an option of Section 2.3; delivered and accepted only if the option is ordered.</td></tr>
<tr><td>ORCE</td><td>Eclipse XFSC orchestration engine based on Node-Red; runtime of all CD components. Link: <a href="https://github.com/eclipse-xfsc/orchestration-engine">https://github.com/eclipse-xfsc/orchestration-engine</a></td></tr>
<tr><td>Release mode</td><td>motion-proof (default; GO after proven predecessor motion) or coordinated (GO at T0 + r × offset).</td></tr>
<tr><td>Start-up hold</td><td>Interval of TTL + B_stop after an STS start during which no session is opened and no token is signed (FR-STS-002).</td></tr>
<tr><td>STS</td><td>Smart-traffic service: the single cloud component that reserves participants, runs the session protocol and issues release tokens.</td></tr>
<tr><td>t_disable / t_exp</td><td>Instant from which the STS signs nothing more for a vehicle / local expiry instant of the vehicle's last accepted token (FR-VEH-016).</td></tr>
<tr><td>T0</td><td>Green-onset time in an authenticated traffic-light phase message.</td></tr>
<tr><td>Test double</td><td>Replacement of an OCM W-Stack adapter used in CI and local development only; never deployed (FR-GW-013).</td></tr>
<tr><td>Trigger source</td><td>console or traffic-light T0 (FR-TL-002).</td></tr>
<tr><td>TTL</td><td>Release-token lifetime, exp − nbf (Table 5).</td></tr>
<tr><td>Wave predecessor</td><td>Previous authorised participant whose motion releases the follower in motionproof mode.</td></tr>
</tbody>
</table>

---

[← Storyline traceability](12_storyline_traceability.md) | [↑ Table of Contents](../README.md)

