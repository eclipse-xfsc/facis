@UC-12-04 @FR-CWE-24 @FR-CWE-31
Feature: Manage Contracts via API
  System Contract Managers access lifecycle management
  through APIs for querying, updating, and tracking.

  Scenario: Query contract status via API
    Given a system service is authenticated via API
    When the system queries contract "Service Agreement" status
    Then the current status and metadata are returned
    And access respects RBAC

  Scenario: Update contract via API
    Given a system service is authenticated via API
    And contract "Service Agreement" is in "Active" status
    When the system sends update request with new terms
    Then the contract is updated
    And changes are versioned and logged with timestamp and actor identity

  Scenario: Track contract performance via API
    Given a system service is authenticated via API
    And contract has KPIs defined
    When the system requests performance metrics via API
    Then KPI data is returned
    And alerts are included if thresholds exceeded