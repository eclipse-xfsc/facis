@UC-08 @FR-PACM-04
Feature: Audit Log Access Control
  Access to audit logs is restricted based on roles
  with all access logged for traceability.

  Scenario: Auditor accesses audit logs
    Given I am authenticated with role "Auditor"
    When I access audit logs for contract "Project Agreement"
    Then I receive the audit trail entries
    And my access is logged with timestamp

  Scenario: Compliance Officer accesses audit logs
    Given I am authenticated with role "Compliance Officer"
    When I access audit logs for contract "Project Agreement"
    Then I receive the audit trail entries
    And my access is logged with timestamp

  Scenario: Admin accesses audit logs
    Given I am authenticated with role "Admin"
    When I access audit logs for contract "Project Agreement"
    Then I receive the audit trail entries
    And my access is logged with timestamp

  Scenario: Audit log access requires justification
    Given I am authenticated with role "Auditor"
    When I access audit logs for contract "Sensitive Agreement"
    And I provide access justification "Quarterly compliance review"
    Then my access is logged with the justification

  Scenario: Unauthorized role cannot access audit logs
    Given I am authenticated with role "Contract Creator"
    When I attempt to access audit logs for contract "Project Agreement"
    Then the request is denied with an authorization error
    And the unauthorized access attempt is logged

  Scenario: Search audit logs by criteria
    Given I am authenticated with role "Auditor"
    When I search audit logs with criteria "action:signature" and "date:2024-01"
    Then I receive filtered audit entries matching the criteria

  Scenario: Audit log access attempt is always recorded
    Given I am authenticated with role "Auditor"
    When I access audit logs for contract "Project Agreement"
    Then an access record is created
    And the record includes accessor identity, timestamp, and scope

