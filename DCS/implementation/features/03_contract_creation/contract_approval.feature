@UC-03-04 @FR-CWE-15 @FR-CWE-16 @FR-CWE-25 @FR-PACM-03 @FR-PACM-02
Feature: Contract Approval
  Contract Approvers and Contract Managers route contracts to required
  approvers before signing. The system logs approvals with timestamps,
  locks content upon completion, and transitions to signing phase.

  Scenario: Initiate approval process for finalized contract
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Under Review" status
    When I initiate the approval process for contract "Service Agreement"
    Then the contract is routed to required approvers
    And the contract status shows "Pending Approval"

  Scenario: Approve contract via approval interface
    Given I am authenticated with role "Contract Approver"
    And contract "Service Agreement" requires my approval
    When I access the approval interface for contract "Service Agreement"
    And I approve contract "Service Agreement"
    Then my approval is logged with timestamp
    And my approval is logged with digital credentials
    And the approval status is updated

  Scenario: Reject contract with comments
    Given I am authenticated with role "Contract Approver"
    And contract "Service Agreement" requires my approval
    When I reject contract "Service Agreement" with reason "Missing compliance clause"
    Then the rejection is logged with comments and timestamp
    And the contract status returns to "Draft"
    And the contract is returned for revision

  Scenario: All required approvals gathered
    Given contract "Service Agreement" requires approvals from "Legal" and "Finance"
    And "Legal" has approved the contract
    And "Finance" has approved the contract
    When the system evaluates approval status
    Then all required approvals are recorded
    And the contract content is locked
    And the contract is marked as ready for execution

  Scenario: Contract transitions to signing phase upon approval
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has all required approvals
    When the approval process completes
    Then the contract is marked as "Approved"
    And the contract transitions to the signing phase

  Scenario: Approval interface supports highlighting and comments
    Given I am authenticated with role "Contract Approver"
    And contract "Service Agreement" requires my approval
    When I access the approval interface for contract "Service Agreement"
    Then I can highlight sections for attention
    And I can add comments to specific clauses
    And I can view previous reviewer comments

  Scenario: Automated compliance check during approval
    Given I am authenticated with role "Contract Approver"
    And contract "Service Agreement" is pending approval
    When automated compliance checks are performed
    Then the system validates against regulatory frameworks
    And the system validates against organizational policies
    And compliance issues are flagged for review

  Scenario: Compliance monitoring detects risk during approval
    Given contract "Service Agreement" is pending approval
    And the contract has a missing required approval from "Risk Officer"
    When the system monitors compliance
    Then a compliance risk is detected
    And the risk is flagged and reported

  Scenario: Track approval routing status
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in approval workflow
    When I view approval status for contract "Service Agreement"
    Then I see pending approvals
    And I see completed approvals with timestamps
    And I see the overall approval progress

  Scenario: Unauthorized role cannot approve contracts
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is pending approval
    When I attempt to approve contract "Service Agreement"
    Then the request is denied with an authorization error
