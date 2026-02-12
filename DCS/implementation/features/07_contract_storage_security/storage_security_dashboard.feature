@UC-07-03 @FR-CSA-21 @FR-CSA-02 @FR-CWE-07
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

  Scenario: Archive Manager can only retrieve contracts they have access to
    Given I am authenticated with role "Archive Manager"
    And I manage contracts for department "Finance"
    And contract "Invoice Agreement" is archived for department "Finance"
    And contract "HR Policy Contract" is archived for department "Human Resources"
    When I view archived contracts on the dashboard
    Then I see contract "Invoice Agreement"
    And I cannot see contract "HR Policy Contract"
    And access denial is logged

  Scenario: Contract party can retrieve archived contracts they are involved in
    Given I am authenticated with role "Contract Manager"
    And I am a representative of party "Acme Corp"
    And contract "Service Agreement" involves party "Acme Corp" and is archived
    And contract "Unrelated Agreement" does not involve party "Acme Corp"
    When I retrieve contract "Service Agreement" from the archive
    Then the contract is accessible with full audit trail
    And the access is logged with timestamp and party identity
    And contract "Unrelated Agreement" is inaccessible

  Scenario: User cannot retrieve archived contracts they are not party to
    Given I am authenticated with role "Contract Manager"
    And I am a representative of party "UnrelatedCorp"
    And contract "Third-Party Agreement" was archived with parties "Acme Corp" and "TechVendor Inc"
    When I attempt to retrieve contract "Third-Party Agreement" from the archive
    Then the request is denied with a "Access denied - not a party to this archived contract" error
    And the access attempt is logged

  Scenario: Legal Officer can retrieve contracts requiring legal compliance review
    Given I am authenticated with role "Legal Officer"
    And contract "Compliance Agreement" requires legal compliance review
    And contract "Compliance Agreement" is archived
    And I have authorization for compliance review access
    When I retrieve contract "Compliance Agreement" from the archive
    Then the contract is accessible with compliance metadata
    And the compliance review status is displayed
    And the retrieval is logged as a compliance review access
