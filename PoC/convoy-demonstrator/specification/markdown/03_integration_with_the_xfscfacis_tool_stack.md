[← Scope](02_scope.md) | [↑ Table of Contents](../README.md) | [Assumptions, constraints and external dependencies →](04_assumptions_constraints_and_external_dependencies.md)

---

## 3 Integration with the XFSC/FACIS tool stack

#### Integration Note (NFR-DEL-002)

The contractor records the credential profile currently supported by FACIS (format, flow, issuer), the OCM W-Stack, PCM Cloud, ORCE and FACIS UI Builder versions, the MQTT broker product, the FACIS trust list used for verification, the holder arrangement per vehicle, whether the OCM W-Stack distinguishes verification sub-reasons, and any client-approved mock.

#### Native first

Issuance, presentation verification and the status list are consumed from the OCM W-Stack; holders are provided by PCM Cloud (FR-GW-001, FR-GW-003, FR-GW-005, FR-GW-014). A mock may only add a check the OCM W-Stack demonstrably does not provide, never replace a native result, and only with written client approval; it is recorded in the Integration Note and shown with its own MOCK label on the dashboard. The admission path of E1 and the invalidation path of E3 always rely on native OCM W-Stack results (FR-GW-003, FR-GW-013, FR-OPS-006).

#### No silent fallback.

An unreachable OCM W-Stack function produces SERVICE_UNAVAILABLE; there is no automatic switch to a mock (FR-GW-010).

#### Identity scheme

Vehicles and the traffic light are identified with DID-based verifiable credentials issued via the OCM WStack (FR-GW-001, FR-TL-001); convoy-layer services hold separate service identities (NFR-SEC003); no driver or personal credential is used (FR-GW-015).

#### Environments

The Demonstrator is deployed into and demonstrated in the FACIS cloud Kubernetes environment with Helm (NFR-DEP-001, NFR-DEP-002); all components use the cluster's synchronised clock (NFR-TIM-006). Development and unit tests may run on contractor systems with a local broker and test doubles of the OCM W-Stack adapters; test doubles are never deployed (FR-GW-013).

---

[← Scope](02_scope.md) | [↑ Table of Contents](../README.md) | [Assumptions, constraints and external dependencies →](04_assumptions_constraints_and_external_dependencies.md)

