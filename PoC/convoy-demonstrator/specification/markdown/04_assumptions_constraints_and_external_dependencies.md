[← Integration with the XFSC/FACIS tool stack](03_integration_with_the_xfscfacis_tool_stack.md) | [↑ Table of Contents](../README.md) | [Functional Requirements →](05_functional_requirements.md)

---

## 4 Assumptions, constraints and external dependencies

#### Mandatory tool stack

ORCE, OCM W-Stack, PCM Cloud, FACIS UI Builder package, Helm on the FACIS cloud Kubernetes environment (NFR-DEL-002). One STS, three participants, one reference dummy and one traffic light (Table 5). TLS on every network endpoint (NFR-SEC-001); private keys stay with their owner and issuer keys remain with the OCM W-Stack (NFR-SEC-002). Control messages are not retained on the business broker (FR-IF-001). The world service and the vehicles use a transport independent of the business broker (FR-VEH-015). All code under Apache-2.0 in the client-designated repository (NFRDEL-003, NFR-CFG-003).

The client provides after project start:

(1) the OCM W-Stack issuance, verification and status list functions, PCM Cloud and the ORCE base images running and supported in the FACIS cloud environment;  

(2) test credentials for CD-V1 … CD-V3 and the traffic light, issued through the OCM W-Stack into their PCM Cloud holders, and the OCM W-Stack authorisation the federation gateway needs to request issuance, suspension and revocation for these participants;  

(3) a FACIS cloud namespace with ingress, TLS certificates, Helm deployment rights and a namespacescoped service account that lets lab control scale the CD deployments for fault injection and reset (Table 5d, NFR-DEP-002);  

(4) the FACIS UI Builder package with its documentation;  

(5) access to the client-designated repository and to the FACIS trust list. 

#### Hazard note

Nothing moves physically; the laboratory cannot produce real-world effects. The emergency stop of the CD is the laboratory abort of the convoy layer, not a physical emergency-stop function (FR-OPS-003). The local protective stop, the token logic and the degradation to standstill are specified so that a physical vehicle at a later stage can inherit them; this specification derives no requirement on a physical platform.

#### Assumptions

- A-1 The reference placement of Table 5f reproduces the roles LEAD, FOLLOW and FOLLOW_GAP with the Table 5 defaults (gap threshold, lane threshold, noise).
- A-2 The stopping-distance relation d_min > v_max × (sensor_max_age + delta_local) + v_max² / (2 × a_brake) + margin holds with the Table 5 defaults (about 0.85 m headroom, noise-free); it is checked for the loaded profile at start (FR-CFG-002).
- A-3 The ARMED and ROLLING timeouts of Table 5 exceed the durations of the demonstration scenarios, including T0 + 2 × offset for coordinated mode.
- A-4 The status-list propagation time of the OCM W-Stack is short compared with the token TTL; it is shown in the event log, not qualified.

---

[← Integration with the XFSC/FACIS tool stack](03_integration_with_the_xfscfacis_tool_stack.md) | [↑ Table of Contents](../README.md) | [Functional Requirements →](05_functional_requirements.md)

