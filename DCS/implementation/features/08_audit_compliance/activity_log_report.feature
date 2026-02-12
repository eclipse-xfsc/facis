@UC-08-01
Feature: Contract Activity Log Reports
  Auditors generate reports of contract activity logs
  and timestamps for auditing purposes.

  Scenario: Generate activity log report for contract
    Given I am authenticated with role "Auditor"
    And contract "Project Agreement" has lifecycle events
    When I generate activity log report for contract "Project Agreement"
    Then I receive a report containing creation, edits, approvals, and signatures
    And each log entry includes timestamp, actor identity, and action taken

  Scenario: Export activity log report
    Given I am authenticated with role "Auditor"
    And contract "Project Agreement" has lifecycle events
    When I generate activity log report for contract "Project Agreement"
    And I export the report as "PDF"
    Then I receive an exportable audit report

  Scenario: Generate report segmented by contract component
    Given I am authenticated with role "Compliance Officer"
    And contract "Master Agreement" has multiple components
    When I generate compliance report for contract "Master Agreement" by component
    Then I receive a report segmented by clauses and appendices
    And each component shows compliance status and timestamps

  Scenario: Generate report segmented by party
    Given I am authenticated with role "Compliance Officer"
    And contract "Partnership Agreement" involves multiple parties
    When I generate compliance report for contract "Partnership Agreement" by party
    Then I receive a report segmented by involved parties
    And each party section includes credential metadata

  Scenario: Audit logs are tamper-proof
    Given I am authenticated with role "Auditor"
    And contract "Project Agreement" has audit trail entries
    When I verify audit trail integrity for contract "Project Agreement"
    Then the audit trail is confirmed immutable
    And any tampering attempts are detectable

  Scenario: Unauthorized role cannot generate audit reports
    Given I am authenticated with role "Contract Creator"
    When I attempt to generate activity log report for contract "Project Agreement"
    Then the request is denied with an authorization error

