@UC-03-02 @FR-CWE-08 @FR-CWE-14 @FR-CWE-18 @FR-CWE-07
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

  Scenario: Only parties to contract can negotiate terms
    Given I am authenticated with role "Contract Reviewer"
    And contract "Service Agreement" involves parties "Acme Corp" and "TechVendor Inc"
    And I am a representative of party "Acme Corp"
    When I open contract "Service Agreement" for negotiation
    Then the negotiation interface is displayed
    And I can add comments to contract clauses
    And my comments are attributed to organization "Acme Corp"

  Scenario: Non-party reviewer cannot negotiate contract not assigned to them
    Given I am authenticated with role "Contract Reviewer"
    And contract "Service Agreement" involves parties "Acme Corp" and "TechVendor Inc"
    And I am a representative of organization "UnrelatedCorp"
    When I attempt to access contract "Service Agreement" for negotiation
    Then the request is denied with an "Access denied - not a party to this contract" error
    And the access denial is logged

  Scenario: Contract Creator and assigned Reviewers can negotiate
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is assigned to reviewers "Alice" and "Bob"
    And I am listed as an assigned reviewer
    When I open contract "Service Agreement" for negotiation
    Then I can add comments and propose redlines
    And only assigned reviewers and the creator can see negotiation comments
    And negotiation actions are logged with reviewer identity

  Scenario: Reviewer cannot approve own redline proposals
    Given I am authenticated with role "Contract Reviewer"
    And contract "Service Agreement" is open for negotiation
    And I have proposed a redline edit to clause "Liability"
    When I attempt to approve my own redline proposal
    Then the request is denied with a "Conflict of interest - cannot approve own proposal" error
    And another authorized reviewer must approve
    And the restriction is logged
