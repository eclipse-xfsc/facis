@UC-12-03 @FR-CWE-25
Feature: Approve Contract via API
  System Contract Approvers handle automated approvals
  through API requests with origin validation.

  Scenario: Approve contract via API
    Given a system service authenticates via API
    And contract "Service Agreement" is in "Under Review" status
    When the system sends approval request for contract "Service Agreement"
    Then the request origin is validated
    And the contract is marked as approved
    And the decision is logged with system metadata

  Scenario: API approval with conditional logic
    Given approval requires specific conditions
    When the system submits approval with condition data
    Then conditions are evaluated
    And approval is granted if conditions met

  Scenario: Invalid approval request rejected
    Given contract is not in approvable status
    When the system attempts approval via API
    Then the request is denied with error "Invalid status"