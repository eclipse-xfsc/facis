![Version](https://img.shields.io/badge/version-1.0-blue)
[![License](https://img.shields.io/badge/license-CC--BY--4.0-orange)](http://creativecommons.org/licenses/by/4.0/)
[![PDF Specification](https://img.shields.io/badge/specification-PDF-blue)](https://github.com/eclipse-xfsc/facis/blob/main/PoC/convoy-demonstrator/specification/FACIS_CD_SRS.pdf)
# Federation Architecture for Composed Infrastructure Services (FACIS) Convoy Demonstrator
The FACIS Convoy Demonstrator reproduces an authorised convoy start as software. Simulated vehicles of different virtual OEM tenants are admitted through a federation gateway on the basis of verifiable credentials, started as a coordinated wave by a smart-traffic service, and stopped on credential invalidation, loss of a required service or an injected fault. It shows that a federation decision (admission, invalidation, unavailability) is sufficient to authorise and withdraw convoy motion end to end. All components are built on the XFSC tool stack and deployed in the FACIS cloud environment.

## Table of Contents

[1 Purpose and exit criteria](markdown/01_purpose_and_exit_criteria.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[1.1 Purpose](markdown/01_purpose_and_exit_criteria.md#11-purpose)  
&nbsp;&nbsp;&nbsp;&nbsp;[1.2 Exit criteria](markdown/01_purpose_and_exit_criteria.md#12-exit-criteria)  
[2 Scope](markdown/02_scope.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[2.1 In scope](markdown/02_scope.md#21-in-scope)  
&nbsp;&nbsp;&nbsp;&nbsp;[2.2 Out of scope](markdown/02_scope.md#22-out-of-scope)  
&nbsp;&nbsp;&nbsp;&nbsp;[2.3 Optional positions](markdown/02_scope.md#23-optional-positions)  
[3 Integration with the XFSC/FACIS tool stack](markdown/03_integration_with_the_xfscfacis_tool_stack.md)  
[4 Assumptions, constraints and external dependencies](markdown/04_assumptions_constraints_and_external_dependencies.md)  
[5 Functional Requirements](markdown/05_functional_requirements.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.1 Federation gateway: admission and status (FR-GW)](markdown/05_functional_requirements.md#51-federation-gateway-admission-and-status-fr-gw)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.2 Geofinder: queue discovery (FR-GEO)](markdown/05_functional_requirements.md#52-geofinder-queue-discovery-fr-geo)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.3 STS: reservation, session and token lifecycle (FR-STS)](markdown/05_functional_requirements.md#53-sts-reservation-session-and-token-lifecycle-fr-sts)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.4 Vehicle software: agent, drive logic and protective stop (FR-VEH)](markdown/05_functional_requirements.md#54-vehicle-software-agent-drive-logic-and-protective-stop-fr-veh)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.5 World service and fault injection (FR-SIM)](markdown/05_functional_requirements.md#55-world-service-and-fault-injection-fr-sim)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.6 Dashboard, console, emergency stop and reset (FR-OPS)](markdown/05_functional_requirements.md#56-dashboard-console-emergency-stop-and-reset-fr-ops)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.7 Business interface, events and codes (FR-IF)](markdown/05_functional_requirements.md#57-business-interface-events-and-codes-fr-if)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.8 Configuration profile and fixtures (FR-CFG)](markdown/05_functional_requirements.md#58-configuration-profile-and-fixtures-fr-cfg)  
&nbsp;&nbsp;&nbsp;&nbsp;[5.9 Traffic light, T0 and coordinated release (FR-TL)](markdown/05_functional_requirements.md#59-traffic-light-t0-and-coordinated-release-fr-tl)  
[6 Non-functional requirements](markdown/06_non-functional_requirements.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.1 Security and trust (NFR-SEC)](markdown/06_non-functional_requirements.md#61-security-and-trust-nfr-sec)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.2 Deployment (NFR-DEP)](markdown/06_non-functional_requirements.md#62-deployment-nfr-dep)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.3 Timing (NFR-TIM)](markdown/06_non-functional_requirements.md#63-timing-nfr-tim)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.4 Event log and demonstration evidence (NFR-EVD)](markdown/06_non-functional_requirements.md#64-event-log-and-demonstration-evidence-nfr-evd)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.5 Configuration and repository (NFR-CFG)](markdown/06_non-functional_requirements.md#65-configuration-and-repository-nfr-cfg)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.6 Delivery and documentation (NFR-DEL)](markdown/06_non-functional_requirements.md#66-delivery-and-documentation-nfr-del)  
&nbsp;&nbsp;&nbsp;&nbsp;[6.7 Start-delay indicators (NFR-KPI)](markdown/06_non-functional_requirements.md#67-start-delay-indicators-nfr-kpi)  
[7 Data and interface definitions](markdown/07_data_and_interface_definitions.md)  
[8 Architecture and implementation approach](markdown/08_architecture_and_implementation_approach.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[8.1 Component overview](markdown/08_architecture_and_implementation_approach.md#81-component-overview)  
&nbsp;&nbsp;&nbsp;&nbsp;[8.2 Design decisions](markdown/08_architecture_and_implementation_approach.md#82-design-decisions)  
&nbsp;&nbsp;&nbsp;&nbsp;[8.3 Dependencies and licences](markdown/08_architecture_and_implementation_approach.md#83-dependencies-and-licences)  
[9 Repository and delivery](markdown/09_repository_and_delivery.md)  
[10 Demonstration and verification](markdown/10_demonstration_and_verification.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.1 Environment and fixtures](markdown/10_demonstration_and_verification.md#101-environment-and-fixtures)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.2 Demonstration scenarios](markdown/10_demonstration_and_verification.md#102-demonstration-scenarios)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.3 Edge checks](markdown/10_demonstration_and_verification.md#103-edge-checks)  
&nbsp;&nbsp;&nbsp;&nbsp;[10.4 Unit tests in CI](markdown/10_demonstration_and_verification.md#104-unit-tests-in-ci)  
[11 Delivery, acceptance and scope control](markdown/11_delivery_acceptance_and_scope_control.md)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.1 Change control](markdown/11_delivery_acceptance_and_scope_control.md#111-change-control)  
&nbsp;&nbsp;&nbsp;&nbsp;[11.2 Client acceptance](markdown/11_delivery_acceptance_and_scope_control.md#112-client-acceptance)  
[12 Storyline traceability](markdown/12_storyline_traceability.md)  
[13 Glossary](markdown/13_glossary.md)  

---

## License

This work is licensed under the [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).

© eco – Association of the Internet Industry (eco – Verband der Internetwirtschaft e.V.)
