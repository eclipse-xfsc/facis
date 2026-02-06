@UC-03-07 @FR-CWE-24
Feature: Contract Dashboard and Search
  Contract Managers and Contract Observers track contract progress,
  approvals, and execution status through a dashboard. The system
  supports full-text and metadata search respecting RBAC.

  Scenario: View contract management dashboard
    Given I am authenticated with role "Contract Manager"
    When I open the contract management dashboard
    Then I see contracts across all lifecycle states
    And I see approval steps for pending contracts
    And I see execution status for active contracts

  Scenario: Dashboard displays real-time lifecycle status
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Approved" status
    When I view contract "Service Agreement" on the dashboard
    Then I see the real-time lifecycle status
    And I see the current stage and next actions

  Scenario: Search contracts by full-text
    Given I am authenticated with role "Contract Manager"
    And multiple contracts exist with various content
    When I search for contracts containing "payment terms"
    Then contracts matching "payment terms" are returned
    And results respect my RBAC permissions

  Scenario: Search contracts by metadata
    Given I am authenticated with role "Contract Manager"
    And contracts with various metadata exist
    When I search for contracts with status "Active" and party "Acme Corp"
    Then contracts matching the metadata criteria are returned
    And results respect my RBAC permissions

  Scenario: Filter contracts on dashboard
    Given I am authenticated with role "Contract Manager"
    And contracts in various states exist
    When I filter the dashboard by status "Pending Approval"
    Then only contracts with status "Pending Approval" are displayed

  Scenario: View searchable logs for completed contracts
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Signed" status
    When I search completed contracts for "Service Agreement"
    Then the contract appears in search results
    And I can view the completion history

  Scenario: View searchable logs for pending contracts
    Given I am authenticated with role "Contract Manager"
    And contract "Draft Agreement" is in "Draft" status
    When I search pending contracts for "Draft Agreement"
    Then the contract appears in search results
    And I can view the current workflow status

  Scenario: Contract Observer has read-only dashboard access
    Given I am authenticated with role "Contract Observer"
    When I open the contract management dashboard
    Then I see contracts across all lifecycle states
    And I cannot modify contract data
    And I can search and filter contracts

  Scenario: Dashboard supports bulk actions
    Given I am authenticated with role "Contract Manager"
    And multiple contracts are pending approval
    When I select multiple contracts on the dashboard
    Then I can perform bulk actions on selected contracts

  Scenario: Dashboard shows responsibilities and deadlines
    Given I am authenticated with role "Contract Manager"
    When I view the contract management dashboard
    Then I see responsibilities assigned to each contract
    And I see deadlines for pending actions
    And I see live updates as status changes

  Scenario: RBAC restricts search results
    Given I am authenticated with role "Contract Observer"
    And contract "Confidential Agreement" is restricted to "Contract Manager" role
    When I search for "Confidential Agreement"
    Then "Confidential Agreement" is not returned in search results

  Scenario: Unauthorized role cannot access dashboard
    Given I am authenticated with role "Template Creator"
    When I attempt to open the contract management dashboard
    Then the request is denied with an authorization error
