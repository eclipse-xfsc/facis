# Behave Feature File Authoring Guide

This document captures the process and conventions for writing Gherkin feature files for the FACIS DCS system.

## Context

We use [Behave](https://behave.readthedocs.io/en/stable/tutorial/) (Python BDD framework) for behavior-driven development. Feature files define acceptance criteria in Gherkin syntax; step definitions implement them in Python.

## Specification Reference

The authoritative source is `DCS/specification/spec.txt`. It's large (~4000+ lines), so use grep:

```bash
# Find functional requirements for a component
grep -n "FR-TR-" DCS/specification/spec.txt      # Template Repository
grep -n "FR-CWE-" DCS/specification/spec.txt     # Contract Workflow Engine
grep -n "FR-SM-" DCS/specification/spec.txt      # Signature Management
grep -n "FR-PACM-" DCS/specification/spec.txt    # Process Audit & Compliance

# Find use case definitions
grep -n "UC-02" DCS/specification/spec.txt       # Template Management
grep -n "UC-03" DCS/specification/spec.txt       # Contract Creation (7 sub-UCs)
grep -n "UC-04" DCS/specification/spec.txt       # Contract Signing
grep -n "UC-05" DCS/specification/spec.txt       # Contract Deployment
grep -n "UC-08" DCS/specification/spec.txt       # Contract Compliance & Auditing
grep -n "UC-09" DCS/specification/spec.txt       # DCS Administration
grep -n "UC-14" DCS/specification/spec.txt       # Identity & PoA Credential Acquisition
grep -n "UC-06" DCS/specification/spec.txt       # Contract Lifecycle Management
grep -n "UC-07" DCS/specification/spec.txt       # Contract Storage & Security
grep -n "UC-10" DCS/specification/spec.txt       # Contract Automation & Integration
grep -n "UC-11" DCS/specification/spec.txt       # API & System Integrations
grep -n "UC-13" DCS/specification/spec.txt       # External System Contract Execution
grep -n "UC-15" DCS/specification/spec.txt       # Access Rights Revocation

# Find role definitions
grep -n "Table 4" DCS/specification/spec.txt     # User roles by component
grep -n "Section 2.4" DCS/specification/spec.txt # User classes
```

### Key Spec Sections

| Section | Content |
|---------|---------|
| 2.4 | User Classes and Roles (Table 4 is authoritative for roles) |
| 3.1 | Interface Requirements (UI descriptions) |
| 3.2 | Functional Requirements (FR-XX-YY codes) |
| 4.x | Use Cases (UC-XX-YY) with Stimulus/Response mappings |

### Spec Inconsistencies

The spec has inconsistencies between sections. Resolution order:
1. **Table 4 (Section 2.4)** - Authoritative for role definitions
2. **Stimulus/Response (Section 4.x)** - Authoritative for role-to-action mapping
3. **FR requirements** - May conflict; defer to above

## Contract Creation Roles (UC-03)

| Role | Responsibility | UI |
|------|----------------|----|
| Contract Creator | Drafts new contracts using templates, initiates contracting process | Contract Creation UI |
| Contract Reviewer | Reviews draft contracts, verifies accuracy, negotiates terms | Contract Review Interface |
| Contract Approver | Validates final versions before signing, ensures compliance | Contract Approval Interface |
| Contract Manager | Manages contract lifecycle, initiates signing, tracks dashboard | Contract Management Dashboard |
| Contract Observer | Read-only access for monitoring and oversight | Contract Management Dashboard |

## Template Management Roles (UC-02)

| Role | Responsibility | UI |
|------|----------------|----|
| Template Creator | Creates and updates templates | Template Builder |
| Template Reviewer | Validates before approval, deprecates | Template Review |
| Template Approver | Gives final approval, adds provenance | Template Approval |
| Template Manager | Verifies provenance, manages schemas, deletes | Dashboard |

## Contract Storage & Security Roles (UC-07)

| Role | Responsibility | UI |
|------|----------------|----|
| Contract Manager | Stores signed contracts, configures access permissions | Contract Management Dashboard |
| Archive Manager | Monitors archive status, integrity, access logs | Archive Manager Dashboard |
| Legal Officer | Retrieves archived contracts for legal review | Archive Search |
| Auditor | Accesses audit logs for compliance review | Audit Log Viewer |

## Contract Lifecycle Management Roles (UC-06)

| Role | Responsibility | UI |
|------|----------------|----|
| Contract Manager | Monitors performance, initiates renewal/termination | Contract Lifecycle Dashboard |
| Contract Observer | Read-only access for monitoring and oversight | Contract Lifecycle Dashboard |

## Contract Signing Roles (UC-04)

| Role | Responsibility | UI |
|------|----------------|----|
| Contract Signer | Reviews and signs contracts in secure viewer | Signing Interface |
| Contract Manager | Manages signing workflow, verifies counterparty | Contract Management Dashboard |

## Contract Deployment Roles (UC-05)

| Role | Responsibility | UI |
|------|----------------|----|
| Contract Manager | Submits signed contracts for deployment | Contract Management Dashboard |

## Audit & Compliance Roles (UC-08)

| Role | Responsibility | UI |
|------|----------------|----|
| Auditor | Conducts audits on contract data and process history | Auditing Tool |
| Compliance Officer | Ensures regulatory compliance of templates and contracts | Non-Compliance Investigation |

## DCS Administration Roles (UC-09)

| Role | Responsibility | UI |
|------|----------------|----|
| System Administrator | Configures RBAC, manages accounts, monitors system | System Monitoring Dashboard |

## Contract Automation Roles (UC-10)

| Role | Responsibility | UI |
|------|----------------|----|
| Process Orchestrator | Automates contract workflows within ERP or AI-driven environments | Orchestration Dashboard |
| Validator | Runs integrity and policy compliance checks before contract execution | Validation Interface |

## API & System Integration Roles (UC-11)

| Role | Responsibility | Interface |
|------|----------------|-----------|
| Integration Manager | Configures and invokes APIs for contract workflows | API |

## External System Execution Roles (UC-13)

| Role | Responsibility | Interface |
|------|----------------|-----------|
| Target System (DCS-TRG-SYS) | Receives deployment payloads, confirms execution | External API |
| Contract Manager | Views execution proofs and status | Contract Management Dashboard |
| Auditor | Accesses execution records for compliance review | Auditing Tool |

## Identity & Credential Acquisition Roles (UC-14)

| Role | Responsibility | UI |
|------|----------------|----|
| Contract Signer | Presents identity and PoA credentials for signing | Signing Interface |
| System Contract Signer | Presents pre-authorized credentials via API | API |
| Contract Manager | Verifies counterparty credentials | Signature Compliance Viewer |

## Access Revocation Roles (UC-15)

| Role | Responsibility | UI |
|------|----------------|----|
| Auditor | Identifies revoked credentials, triggers revocation | Signature Compliance Viewer |
| Compliance Officer | Enforces organizational revocation policies | Signature Compliance Viewer |

## Feature File Conventions

### File Naming
```
{action}_{entity}.feature
```
Examples: `create_template.feature`, `template_workflow.feature`

### Structure
```gherkin
@UC-XX-YY
Feature: Short Title
  Brief description of what this feature covers
  and why it exists.

  Scenario: Happy path description
    Given I am authenticated with role "{role}"
    And preconditions...
    When I perform action
    Then expected outcome

  Scenario: Unauthorized role cannot {action}
    Given I am authenticated with role "{wrong_role}"
    When I attempt to {action}
    Then the request is denied with an authorization error
```

### What to Avoid

- **No Background sections** with always-true preconditions ("system is available")
- **No @smoke tags** unless you have a real smoke test strategy
- **No scenarios in wrong files** (e.g., usage scenarios in creation feature)
- **No noise** - every Given/When/Then should be meaningful

## Reusable Step Patterns

These patterns are designed to work across multiple UCs by swapping entity names.

### Authentication
```gherkin
Given I am authenticated with role "{role}"
```

### Contract Creation & Management
```gherkin
When I create a contract from template "{template}"
When I assemble a contract using clauses "{clause1}", "{clause2}", and "{clause3}"
When I bundle contracts "{contract1}" and "{contract2}" into package "{package}"
When I open contract "{name}" for negotiation
When I add comment "{comment}" to clause "{clause}"
When I propose a redline edit to clause "{clause}"
When I submit contract "{name}" for review
When I adjust clause "{clause}" with new text
When I compare version "{v1}" with version "{v2}"
When I rollback contract "{name}" to version "{version}"
When I initiate the approval process for contract "{name}"
When I approve contract "{name}"
When I reject contract "{name}" with reason "{reason}"
When I view contract "{name}" in machine-readable format
When I view contract "{name}" in human-readable format
When I request synchronized view of contract "{name}"
When I initiate the signing workflow for contract "{name}"
When I configure signers for contract "{name}"
When I open the contract management dashboard
When I search for contracts containing "{text}"
When I search for contracts with status "{status}" and party "{party}"
Then a draft contract is generated
Then the contract is assigned a unique contract ID
Then the assembly process validates structure
Then a new version is created with timestamp and user attribution
Then the contract content is locked
Then the signing workflow is started
```

### Entity State
```gherkin
Given {entity} "{name}" exists
Given {entity} "{name}" is in "{status}" status
Given {entity} "{name}" version "{version}" exists
Given {entity} "{name}" has {attribute}
```

### Status Transitions
```gherkin
When I submit {entity} "{name}" for review
When I approve {entity} "{name}"
When I reject {entity} "{name}" with reason "{reason}"
Then the {entity} status is "{status}"
```

### CRUD Operations
```gherkin
When I create a {entity} "{name}" in category "{category}"
When I create a {entity} "{name}" of type "{type}"
When I update {entity} "{name}"
When I delete {entity} "{name}"
Then the {entity} is created in "{status}" status
Then the {entity} is removed from the system
Then a new version "{version}" is created
```

### Hierarchy/Linking
```gherkin
When I link {entity} "{child}" to parent "{parent}"
When I define dependency from "{source}" to "{target}"
Then the {entity} hierarchy is established
```

### Identity
```gherkin
Then the {entity} is assigned a UUID
When I assign a DID to {entity} "{name}"
When I retrieve {entity} by UUID
When I retrieve {entity} by DID
```

### Authorization Denial
```gherkin
When I attempt to {action}
Then the request is denied with an authorization error
```

### Audit & Compliance
```gherkin
Then the {action} is recorded in audit log
When I access audit logs for {entity} "{name}"
When I generate activity log report for {entity} "{name}"
When I initiate compliance audit for {entity} "{name}"
When I validate {entity} "{name}" against regulatory framework "{framework}"
When I validate structural integrity of package "{name}"
Then a compliance summary is generated
Then the audit flags "{issue}" as a compliance issue
Then the {entity} is marked as "{status}"
```

### Contract Storage & Security
```gherkin
When I store contract "{name}" in the secure archive
When I retrieve contract "{name}" from the archive
When I configure access permissions for contract "{name}"
When I grant role "{role}" access to contract "{name}"
When I revoke access for role "{role}" to contract "{name}"
When I configure per-party access for contract "{name}"
When I access audit logs for contract "{name}"
When I open the contract storage and security dashboard
When I view integrity checks on the dashboard
When I view access logs on the dashboard
When I drill down into contract "{name}"
When I export access logs from the dashboard
Then the contract is sealed with tamper-proof cryptographic mechanisms
Then an archive ID is returned
Then the system verifies cryptographic integrity
Then the access control rules are updated
Then the unauthorized access attempt is logged
```

### Contract Lifecycle Management
```gherkin
When I open the contract lifecycle dashboard
When I view contract "{name}" on the dashboard
When I view performance metrics for contract "{name}"
When I view SLA compliance for contract "{name}"
When I configure alert notifications for contract "{name}"
When I view the expiration management interface
When I renew contract "{name}"
When I initiate the renewal workflow for contract "{name}"
When I terminate contract "{name}" with reason "{reason}"
When I create an extension contract for "{name}"
Then I see contracts across all lifecycle states
Then I see the current lifecycle stage
Then I see timestamps for each stage transition
Then I see the action history
Then an alert is raised for underperformance
Then an alert is raised for missed target
Then a new contract instance is created
Then the new instance retains linked metadata from the original
Then the contract is marked as "Terminated"
```

### Signing
```gherkin
When I open contract "{name}" in the secure viewer
When I apply my digital signature to contract "{name}"
When I apply my digital signature via the signing service
When I view signing status for contract "{name}"
When I validate the counterparty signature on contract "{name}"
When I verify signature compliance for contract "{name}"
When I export validation results for contract "{name}"
Then a signed artifact is produced
Then signature integrity is validated upon signing
```

### Deployment
```gherkin
When I deploy contract "{name}" to target system "{system}"
Then the target system acknowledges receipt
Then the contract status is updated to "Deployed"
Then the deployment payload includes the signed contract
Then the deployment event is logged
```

### Administration
```gherkin
When I add role "{role}" with permissions for {scope}
When I edit role "{role}" to include permission "{permission}"
When I remove role "{role}"
When I deactivate account "{user}"
When I reactivate account "{user}"
Then the action is logged with actor identity and timestamp
When I view system security logs
When I filter system logs by severity "{level}" and period "{period}"
```

### Credential Acquisition & Verification
```gherkin
Given I hold a valid identity credential issued by a recognized authority
Given I hold a valid PoA credential for organization "{org}"
When I initiate signing for contract "{name}"
When I verify counterparty authorization for "{party}"
Then the system validates my identity credential
Then the system validates my PoA credential
Then the delegation chain is validated as traceable
```

### Contract Automation & Orchestration
```gherkin
Given contract "{name}" has milestone "{milestone}"
Given external system "{system}" is configured for milestone triggers
When milestone "{milestone}" is reached on contract "{name}"
When I initiate synchronized execution for contract "{name}"
When external system "{system}" sends a webhook callback with status "{status}"
When I view the workflow trace for contract "{name}"
Then the system triggers an action on external system "{system}"
Then contract milestones are translated into actionable triggers
Then I see ordered events from initiation to completion
```

### Pre-Execution Validation
```gherkin
When I trigger a compliance check for contract "{name}"
When I view validation history for contract "{name}"
Then the system reviews contract content
Then the system reviews contract structure
Then the system reviews contract metadata
Then a validation report is generated
Then the validation report shows "{status}"
Then the validation report flags "{violation}"
Then the contract is blocked from deployment
Then the contract is flagged for manual review
Then the contract is cleared for deployment
```

### API & System Integration
```gherkin
Given I am authenticated as "{role}" via API
When I invoke the contract creation API with valid payload
When I invoke the contract creation API without authentication
When I invoke the metadata update API for contract "{name}"
When I invoke the contract query API for contract "{name}"
When I invoke the contract archival API for contract "{name}"
When I invoke the automated signature API for contract "{name}"
When I invoke the tagging API to add tag "{tag}" to contract "{name}"
When I invoke the retrieval API for contract "{name}"
When I exceed the configured rate limit for API calls
Then the API returns HTTP {status} status
Then the interaction is logged for traceability
Then an audit trail entry is generated
```

### External System Execution
```gherkin
Given target system "{system}" is registered with the DCS
When target system "{system}" requests the deployment payload via API
When target system "{system}" sends an activation confirmation callback
When target system "{system}" sends a failure callback with reason "{reason}"
When target system "{system}" queries status for contract "{name}"
When the system generates proof of contract execution
When I view execution proof for contract "{name}"
Then the DCS records the activation with receipt and transaction ID
Then the proof includes hash references
Then the proof includes timestamps
Then the proof includes signer identities
Then the proof includes status confirmations
Then contract "{name}" status is updated to "Executed"
```

### Revocation
```gherkin
Given signer "{name}" credentials have been revoked in the status list
When I revoke signature for signer "{name}" on contract "{contract}"
Then the signature is marked as revoked
Then the revocation event is logged with timestamp and reason
Then the revocation is propagated to "{system}"
When I view signature compliance status for contract "{name}"
When I re-sign contract "{name}"
```

## Behave Step Definition Notes

**Important**: Parameterization is a step definition concern, not Gherkin syntax.

Feature file (same either way):
```gherkin
Then the template status is "Approved"
```

Auto-generated stub (literal match):
```python
@then('the template status is "Approved"')
def step_impl(context):
    raise NotImplementedError(...)
```

Manual refactor (parameterized):
```python
@then('the template status is "{status}"')
def step_impl(context, status):
    assert context.template.status == status
```

The `{placeholder}` syntax uses Behave's `parse` library. Quotes in feature files are literal text that visually delineate values.

## Coverage Validation

After writing features, validate coverage against FR requirements:

```bash
# List all feature files
ls DCS/implementation/features/02_template_management/*.feature

# Cross-reference with spec
grep -n "FR-TR-" DCS/specification/spec.txt | head -30

# Dry run to check syntax
behave --dry-run DCS/implementation/features/02_template_management/
```

## UC-02 Feature Files (Template Management)

| File | UC | FR Coverage |
|------|-----|-------------|
| create_template.feature | UC-02-01 | FR-TR-13 |
| search_templates.feature | UC-02-02 | FR-TR-10, FR-TR-19 |
| generate_contract.feature | UC-02-03 | FR-TR-04 |
| update_template.feature | UC-02-04 | FR-TR-05, FR-TR-16 |
| deprecate_template.feature | UC-02-05 | FR-TR-17 |
| template_provenance.feature | UC-02-06 | FR-TR-08, FR-TR-09 |
| verify_template.feature | UC-02-07 | FR-TR-20 |
| semantic_schemas.feature | UC-02-08 | FR-TR-03 |
| dashboard.feature | UC-02-09 | FR-TR-28 |
| template_workflow.feature | UC-02-10 | FR-TR-14, FR-TR-15 |
| template_deletion.feature | UC-02-11 | FR-TR-18 |
| template_hierarchy.feature | UC-02-12 | FR-TR-02, FR-TR-23, FR-TR-24, FR-TR-26, FR-TR-27 |
| template_identity.feature | UC-02-13 | FR-TR-11 |

## UC-03 Feature Files (Contract Creation)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| contract_creation.feature | UC-03-01 | FR-CWE-13, FR-CWE-03, FR-CWE-30 |
| contract_negotiation.feature | UC-03-02 | FR-CWE-08, FR-CWE-14, FR-CWE-18 |
| contract_adjustment.feature | UC-03-03 | FR-CWE-08, FR-CWE-17 |
| contract_approval.feature | UC-03-04 | FR-CWE-15, FR-CWE-16, FR-CWE-25, FR-PACM-03, FR-PACM-02 |
| contract_format_review.feature | UC-03-05 | FR-CWE-04 |
| signing_process_management.feature | UC-03-06 | FR-SM-13 |
| contract_dashboard_search.feature | UC-03-07 | FR-CWE-24 |

### Cross-Cutting Concerns

UC-03-04 shares FR-PACM-03 and FR-PACM-02 with UC-08 (Audit & Compliance) and UC-10 (Pre-Execution Validation). UC-03-06 (FR-SM-13) overlaps with UC-04 (Contract Signing) — UC-03-06 covers signing workflow management from the Contract Manager perspective; UC-04 covers the signer's perspective. UC-03-07 (FR-CWE-24) complements UC-06-01 (FR-CWE-24) — both use the dashboard but for different purposes.

## UC-04 Feature Files (Contract Signing)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| contract_signing.feature | UC-04-01 | FR-CWE-19, FR-CWE-26, FR-SM-13, FR-SM-16 |
| signature_validation.feature | UC-04-02/03 | FR-SM-18, FR-SM-21 |

### Cross-Cutting Concerns

UC-04-02 (Verify Counterparty Authorization) overlaps with UC-14 (Identity & PoA Credential Acquisition). Counterparty credential verification is covered in `14_credential_acquisition/counterparty_verification.feature`.

## UC-05 Feature Files (Contract Deployment)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| contract_deployment.feature | UC-05-01 | FR-SM-12, FR-CWE-06 |

## UC-06 Feature Files (Contract Lifecycle Management)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| contract_performance_monitoring.feature | UC-06-01 | FR-CWE-24, FR-CWE-27, FR-CWE-31, FR-CWE-09, FR-CSA-20 |
| renewal_termination_management.feature | UC-06-02 | FR-CWE-11, FR-CWE-12, FR-CWE-22, FR-CWE-23, FR-CSA-04, FR-CSA-14, FR-CSA-15, FR-CSA-16, FR-CSA-23 |

### Cross-Cutting Concerns

UC-06-01 shares FR-PACM-01, FR-PACM-02, FR-PACM-05 with UC-08 (Audit & Compliance). UC-06 focuses on operational monitoring and alerts; UC-08 focuses on audit/compliance investigation. UC-06-02 interacts with UC-15 for VC revocation on contract termination.

## UC-07 Feature Files (Contract Storage & Security)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| secure_archive_storage.feature | UC-07-01 | FR-CSA-01, FR-CSA-08, FR-CWE-20, FR-CSA-05, FR-CSA-06, FR-CSA-26 |
| contract_permissions_access.feature | UC-07-02 | FR-CSA-02, FR-PACM-04 |
| storage_security_dashboard.feature | UC-07-03 | FR-CSA-21 |

### Cross-Cutting Concerns

UC-07-02 shares FR-PACM-04 with UC-08 (Audit & Compliance). UC-07 focuses on storage RBAC; UC-08 focuses on audit log access for compliance review. UC-07-01 integrates with UC-04 (signature completion triggers archival) and UC-06 (termination/renewal affects archive status).

## UC-10 Feature Files (Contract Automation & Integration)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| workflow_automation.feature | UC-10-01 | FR-CWE-28, FR-CSA-25 |
| pre_execution_validation.feature | UC-10-02 | FR-PACM-03 |

### Cross-Cutting Concerns

UC-10-01 shares FR-CWE-28 and FR-CSA-25 with UC-11. UC-10 focuses on orchestration (milestone triggers, AI/ERP integration) while UC-11 covers the general API interface. UC-10-02 (FR-PACM-03) complements UC-08 compliance features by adding pre-deployment validation gates.

## UC-11 Feature Files (API & System Integrations)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| api_contract_workflows.feature | UC-11-01 | FR-CWE-28, FR-CSA-25, FR-SM-25 |

## UC-13 Feature Files (External System Contract Execution)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| external_system_execution.feature | UC-13-01 | FR-SM-10, IR-SI-05 |

### Cross-Cutting Concerns

UC-11 provides the API layer that UC-13 consumes for external system interactions. UC-13 complements UC-05: UC-05 covers deployment from the DCS/Contract Manager perspective; UC-13 covers the external target system API interface, execution confirmation callbacks, and cryptographic proof of execution generation.

## UC-08 Feature Files (Audit & Compliance)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| activity_log_report.feature | UC-08-01 | FR-PACM-01, FR-PACM-07 |
| compliance_audit.feature | UC-08-02 | FR-PACM-02, FR-PACM-03, FR-PACM-05 |
| regulatory_compliance.feature | UC-08-03 | FR-PACM-03 (eIDAS/GDPR/ISO) |
| audit_log_access.feature | FR-PACM-04 | FR-PACM-04 |
| template_compliance.feature | FR-TR-07 | FR-TR-07 (cross-cutting) |
| multi_contract_validation.feature | FR-PACM-06 | FR-PACM-06 |

### Cross-Cutting Concerns

The `template_compliance.feature` file addresses FR-TR-07 which spans UC-02 (Template Management) and UC-08 (Audit & Compliance). The Compliance Officer role from UC-08 validates templates before they can be used in contract creation.

## UC-09 Feature Files (DCS Administration)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| rbac_configuration.feature | UC-09-01 | FR-UC-09-1 |
| system_monitoring.feature | UC-09-02 | FR-UC-09-2 |

## UC-14 Feature Files (Identity & PoA Credential Acquisition)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| credential_acquisition.feature | UC-14-01 | FR-SM-03, FR-SM-05 |
| counterparty_verification.feature | UC-14-01 | FR-SM-04, FR-SM-26 |

## UC-15 Feature Files (Access Rights Revocation)

| File | UC/FR | FR Coverage |
|------|-------|-------------|
| signature_revocation.feature | UC-15-01 | FR-SM-20 |
| revocation_compliance_viewer.feature | UC-15-01 | FR-SM-26 |

### Business Rules

UC-15 implements DCS-NFR-BR-06 (Revocation & Termination Propagation): Revocation of credentials, signatures, or contracts MUST take immediate effect and be propagated across dependent systems.

## Workflow for New UCs

1. **Grep the spec** for UC-XX and FR-XX requirements
2. **Identify roles** from Table 4 (Section 2.4)
3. **Map Stimulus/Response** to role-action pairs (Section 4.x)
4. **Draft feature files** using reusable patterns above
5. **Add role violation scenarios** for each action
6. **Validate coverage** against FR requirements
7. **Run dry-run** to check Gherkin syntax

