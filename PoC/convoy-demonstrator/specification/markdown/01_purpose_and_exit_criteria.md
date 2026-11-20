[↑ Table of Contents](../README.md) | [Scope →](02_scope.md)

---

## 1 Purpose and exit criteria

### 1.1 Purpose

The FACIS Convoy Demonstrator (CD) reproduces an authorised convoy start as software: simulated vehicles of different virtual OEM (Original Equipment Manufacturer) tenants are admitted through the federation gateway on the basis of verifiable credentials issued by the [XFSC OCM W-Stack](https://github.com/eclipse-xfsc/deployment/tree/main/OCM%20W-Stack) and held in [PCM Cloud](https://github.com/eclipse-xfsc/deployment/tree/main/PCM%20Cloud) (FR-GW-001 … 004), discovered as a queue by the cloud from their authenticated position reports (FR-GEO-001 … 005), started as a coordinated wave by one smart-traffic service (STS; FR-STS-001 … 015), and stopped – on credential invalidation, on loss of a required service or on an injected fault – solely by the local expiry of short-lived release tokens, with authenticated STOP and TOKEN_CLEAR as accelerators only (FRSTS-013, FR-VEH-016).

A simulated traffic light is admitted through the same gateway with its own infrastructure credential and publishes authenticated signal-phase messages with the green-onset time T0 (FR-TL-001). The STS supports two release modes: in motion-proof (default) every follower receives GO only after its wave predecessor has demonstrably moved (FR-STS-006); in coordinated the STS issues follower GO tokens at T0 plus a fixed offset per rank (FR-TL-003). In both modes a follower's approach is bounded by the local distance gate and protective stop (FR-VEH-007, FR-VEH-011).

The Demonstrator shows that a federation decision (admission, invalidation, unavailability) is sufficient to authorise and to withdraw convoy motion end to end without any withdrawal message reaching the vehicle. All components are built on the mandatory XFSC tool stack and deployed in the FACIS cloud environment.

### 1.2 Exit criteria

The exit criteria are demonstration goals. Each is met when the named scenarios of Section 10.2 have been executed once in the FACIS cloud environment, have shown the described behaviour and are recorded in the demonstration protocol witnessed by the client, and when the named edge checks of Section 10.3 are met in their stated form: T-04, T-05 and T-10 pass in the CI report of the tagged release (NFR-CFG-004); T-12 is shown within M5.

<table>
<thead>
<tr><th align="left" style="background-color:#6b6b6b;color:#ffffff">ID</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Criterion</th><th align="left" style="background-color:#6b6b6b;color:#ffffff">Scenarios</th></tr>
</thead>
<tbody>
<tr><td>E1</td><td>Vehicles and the traffic light are admitted with credentials issued by the OCM W-Stack and held in PCM Cloud; invalid, revoked, identityforged and role-violating requests are rejected; revocation and recovery work through the OCM W-Stack status list.</td><td>M1</td></tr>
<tr><td>E2</td><td>The reference and the origin-shifted formation are discovered with the correct order and roles; the wave starts in release mode motion-proof (console) and in release mode coordinated (traffic-light T0); the FOLLOW_GAP vehicle stops before the dummy by the protective stop; the session ends in DONE.</td><td>M2, M3(a), M3(b), T-05, T10</td></tr>
<tr><td>E3</td><td>Revocation of a rolling vehicle's credential blocks further issuance and the vehicle stops by local token expiry while its business downlink is blocked; unaffected participants complete.</td><td>M4</td></tr>
<tr><td>E4</td><td>For each demonstrated fault (uplink off, STS stop, convoy-layer stop, sensor invalid, emergency stop with reachable and blocked downlink) every affected vehicle reaches standstill; a reset restores the demoready state.</td><td>M5, T-04, T-12</td></tr>
<tr><td>E5</td><td>The tagged release is deployed with Helm into the FACIS cloud environment on the mandatory tool stack, the runbook is followed by a client operator, and the demonstration recorded by the client.</td><td>R</td></tr>
</tbody>
</table>


---

[↑ Table of Contents](../README.md) | [Scope →](02_scope.md)

