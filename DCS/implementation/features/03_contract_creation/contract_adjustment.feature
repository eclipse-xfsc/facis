@UC-03-03 @FR-CWE-08 @FR-CWE-17
Feature: Contract Term Adjustment
  Contract Managers and Contract Reviewers make granular clause edits
  without regenerating the entire contract. The system maintains document
  integrity and full audit history.

  Scenario: Adjust specific contract clause
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Draft" status
    When I adjust clause "Payment Terms" with new text
    Then only the targeted clause is changed
    And the rest of the contract remains unchanged
    And the document integrity is maintained

  Scenario: Integrity check passes after clause adjustment
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has been adjusted
    When the system performs integrity checks
    Then the integrity checks pass
    And the contract structure is valid

  Scenario: Audit trail updated after adjustment
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Draft" status
    When I adjust clause "Liability" with new text
    Then the audit trail is updated
    And the change includes the editor identity
    And the change includes a timestamp
    And the previous clause text is preserved in history

  Scenario: Side-by-side version comparison
    Given I am authenticated with role "Contract Reviewer"
    And contract "Service Agreement" has multiple versions
    When I compare version "1.0" with version "2.0"
    Then I see a side-by-side comparison
    And differences are highlighted
    And I can identify which clauses changed

  Scenario: Redline view of adjustments
    Given I am authenticated with role "Contract Reviewer"
    And contract "Service Agreement" has pending adjustments
    When I view the redline for contract "Service Agreement"
    Then I see additions highlighted
    And I see deletions struck through
    And I can accept or reject individual changes

  Scenario: Automated check for missing fields after adjustment
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has been adjusted
    When the system performs automated checks
    Then missing fields are flagged
    And inconsistencies are identified

  Scenario: Rollback to previous version
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has version "2.0" with unwanted changes
    When I rollback contract "Service Agreement" to version "1.0"
    Then the contract is restored to version "1.0"
    And the rollback is logged in audit history
    And the rolled-back version becomes the current version

  Scenario: Unauthorized role cannot adjust contracts
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is in "Draft" status
    When I attempt to adjust clause "Payment Terms"
    Then the request is denied with an authorization error
