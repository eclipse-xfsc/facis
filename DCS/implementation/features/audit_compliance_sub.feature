# UC-08: Audit & Compliance - Sub Use Cases
Feature: Audit and Compliance - Detailed Sub Processes
  As a Auditor or Compliance Officer
  I want to generate comprehensive audit reports and verify compliance
  So that all actions are traceable and policies are enforced

  # UC-08-01 – Report Contract Activity Logs & Timestamps
  Scenario: Generate auditable activity reports
    Given a contract activity logs exist
    When an Auditor or Compliance Officer submits a request to generate an activity report
    Then it should include:
      | Field         | Content                |
      | Actors        | Users who took actions |
      | Timestamps    | When actions occurred  |
      | Actions       | What was performed     |
      | Resources     | Which contracts/items  |
    And the report should be exportable to CSV/PDF

  # UC-08-02 – Audit Contract Compliance
  Scenario: Run compliance audit against policies
    Given an activity report has been generated
    And contract contents are available
    And contract lifecycle history is available
    When an Auditor or Compliance Officer initiates a compliance audit
    Then the system should:
      | Check              | Result                |
      | Check Policies     | Legal/organizational  |
      | List Violations    | Issues with rules     |
      | Flag Violations    | Clear identification  |
      | Pass/Fail Summary  | Overall status        |
    And violations should be archived for compliance proof

  # UC-08-03 – Audit Logs / Compliance against eIDAS / EUDI Logging Regulations
  Scenario: Audit logs for regulatory compliance (eIDAS / GDPR / ETSI)
    Given audit logs related to contract lifecycle events are available
    When an Auditor or Compliance Officer initiates a compliance audit
    Then the system evaluates audit logs against applicable regulatory and legal requirements
    And potential compliance issues are identified and flagged
    And a compliance audit summary is generated
    And the audit results are recorded in the audit trail for traceability
