@UC-07-03 @FR-CSA-21
Feature: Contract Storage and Security Dashboard
  Archive Managers monitor archive status, data integrity, access logs,
  and alerts through a centralized dashboard.

  Scenario: View archive dashboard overview
    Given I am authenticated with role "Archive Manager"
    When I open the contract storage and security dashboard
    Then I see archived contract statistics
    And I see recent archive actions
    And I see storage volume metrics
    And I see expiring contracts
    And I see compliance status

  Scenario: View data integrity check results
    Given I am authenticated with role "Archive Manager"
    When I view integrity checks on the dashboard
    Then I see the results of cryptographic integrity verification
    And I see contracts that passed verification
    And I see contracts flagged with integrity issues

  Scenario: View access logs for archived contracts
    Given I am authenticated with role "Archive Manager"
    When I view access logs on the dashboard
    Then I see recent access attempts
    And I see the accessor identity and role
    And I see the accessed contract and timestamp

  Scenario: View alerts for archive anomalies
    Given I am authenticated with role "Archive Manager"
    And there are coverage or integrity anomalies in the archive
    When I open the contract storage and security dashboard
    Then I see alerts related to anomalies
    And each alert includes severity and affected contract

  Scenario: Drill down into contract details from dashboard
    Given I am authenticated with role "Archive Manager"
    And contract "Service Agreement" appears on the dashboard
    When I drill down into contract "Service Agreement"
    Then I see the full contract metadata
    And I see the archive history
    And I see access control settings

  Scenario: Export access logs for review
    Given I am authenticated with role "Archive Manager"
    When I export access logs from the dashboard
    Then the logs are exported in a standard format
    And the export is logged

  Scenario: Search and retrieve archived contracts
    Given I am authenticated with role "Archive Manager"
    When I search for contracts matching criteria "status=Active"
    Then I see matching archived contracts
    And I can retrieve selected contracts

  Scenario: Unauthorized role cannot access storage dashboard
    Given I am authenticated with role "Contract Observer"
    When I attempt to open the contract storage and security dashboard
    Then the request is denied with an authorization error
