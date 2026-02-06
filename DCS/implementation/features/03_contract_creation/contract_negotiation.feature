@UC-03-02 @FR-CWE-08 @FR-CWE-14 @FR-CWE-18
Feature: Contract Negotiation
  Contract Managers and Contract Reviewers negotiate contract terms through
  commenting, version tracking, and structured negotiation workflows with
  redline proposals and full audit logs.

  Scenario: Open draft contract for negotiation
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Draft" status
    When I open contract "Service Agreement" for negotiation
    Then the negotiation interface is displayed
    And I can view all contract clauses

  Scenario: Add comment to contract clause
    Given I am authenticated with role "Contract Reviewer"
    And contract "Service Agreement" is open for negotiation
    When I add comment "Clarify payment terms" to clause "Payment Terms"
    Then the comment is added to the negotiation log
    And the comment is attributed to my identity
    And the comment includes a timestamp

  Scenario: Propose redline edit to contract clause
    Given I am authenticated with role "Contract Reviewer"
    And contract "Service Agreement" is open for negotiation
    When I propose a redline edit to clause "Liability"
    Then the proposed change is tracked
    And the original text is preserved
    And the redline proposal is visible to other negotiators

  Scenario: Track version history during negotiation
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has multiple negotiation edits
    When I view version history for contract "Service Agreement"
    Then I see all versions with timestamps
    And I see user attribution for each version
    And old versions remain accessible

  Scenario: Approve proposed change during negotiation
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has a pending redline proposal on clause "Liability"
    When I approve the redline proposal
    Then the change is applied to the contract
    And the approval is logged in the negotiation log
    And a new version is created

  Scenario: Reject proposed change during negotiation
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has a pending redline proposal on clause "Liability"
    When I reject the redline proposal with reason "Not acceptable"
    Then the proposal is marked as rejected
    And the rejection reason is logged
    And the original text is retained

  Scenario: View negotiation log
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has completed multiple negotiation rounds
    When I view the negotiation log for contract "Service Agreement"
    Then I see all comments and proposals
    And I see approvals and rejections
    And I see the full audit trail

  Scenario: Submit contract for review after negotiation
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" negotiation is complete
    When I submit contract "Service Agreement" for review
    Then the contract is routed to assigned reviewers
    And the contract status changes to "Under Review"
    And the submission is logged

  Scenario: Unauthorized role cannot negotiate contracts
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is in "Draft" status
    When I attempt to add a comment to contract "Service Agreement"
    Then the request is denied with an authorization error
