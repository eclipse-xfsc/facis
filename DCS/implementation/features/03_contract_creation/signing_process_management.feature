@UC-03-06 @FR-SM-13 @FR-SM-07 @FR-SM-14
Feature: Contract Signing Process Management
  Contract Managers coordinate the structured signing process for all
  parties. The system schedules and tracks signing steps, assigns
  signatories, enforces order and deadlines, and integrates identity checks.

  Scenario: Initiate contract signing workflow
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Approved" status
    When I initiate the signing workflow for contract "Service Agreement"
    Then the signing workflow is started
    And the workflow is logged with timestamp

  Scenario: Configure signers and sequence
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" requires signatures
    When I configure signers "Alice", "Bob", and "Charlie" for contract "Service Agreement"
    And I set the signing sequence as "Alice" then "Bob" then "Charlie"
    Then the signatory assignment is recorded
    And the signing order is enforced

  Scenario: System schedules signing steps
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has configured signers
    When the signing workflow is initiated
    Then the system schedules signing steps for each signer
    And deadlines are assigned based on configuration

  Scenario: Send reminder to pending signer
    Given contract "Service Agreement" has pending signature from "Alice"
    And the signing deadline is approaching
    When the system evaluates pending signatures
    Then a reminder is sent to "Alice"
    And the reminder is logged

  Scenario: Track signing status for all parties
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has multiple signers
    When I view signing status for contract "Service Agreement"
    Then I see which signers have completed
    And I see which signers are pending
    And I see completion timestamps for each signer

  Scenario: Enforce signing order dependencies
    Given contract "Service Agreement" requires "Alice" to sign before "Bob"
    And "Alice" has not signed
    When "Bob" attempts to sign contract "Service Agreement"
    Then the signing request is denied
    And the error indicates signing order dependency

  Scenario: Enforce signing deadline
    Given contract "Service Agreement" has signing deadline of today
    And signer "Alice" has not signed
    When the deadline passes
    Then the system flags the missed deadline
    And appropriate stakeholders are notified

  Scenario: Integrate identity check in signing workflow
    Given contract "Service Agreement" requires identity verification
    And signer "Alice" is assigned to sign
    When "Alice" initiates signing
    Then the system performs identity check
    And the identity verification result is recorded

  Scenario: Complete signing workflow
    Given contract "Service Agreement" requires signatures from "Alice" and "Bob"
    And "Alice" has signed
    And "Bob" has signed
    When the system evaluates signing completion
    Then the signing workflow is marked as complete
    And the contract status is updated to "Signed"
    And the completion is logged

  Scenario: Unauthorized role cannot manage signing process
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is in "Approved" status
    When I attempt to initiate the signing workflow for contract "Service Agreement"
    Then the request is denied with an authorization error

  Scenario: Designated signatory with required role can sign contract
    Given I am authenticated with role "Contract Signer"
    And contract "Service Agreement" designates me as signatory
    And I hold the required credential for this signing position
    When I initiate signing for contract "Service Agreement"
    Then the signing action is permitted
    And the signatory assignment with my identity is recorded
    And the signature is applied to the contract

  Scenario: Non-designated signer cannot sign contract even with system role
    Given I am authenticated with role "Contract Signer"
    And contract "Service Agreement" is in "Approved" status
    And I am not designated as a signatory for contract "Service Agreement"
    When I attempt to sign contract "Service Agreement"
    Then the request is denied with a "Not a designated signatory for this contract" error
    And the rejection is logged

  Scenario: Enforce role-specific signing permissions within workflow
    Given I am authenticated with role "Contract Manager"
    And contract "Multi-Party Agreement" requires distinct roles at each position
    And position 1 requires role "CFO"
    And position 2 requires role "Legal Officer"
    When I configure signers "Alice" as "CFO" and "Bob" as "Legal Officer"
    Then the role requirements are recorded for each position
    And signing order is enforced with role validation
    And only users with matching credentials can sign each position

  Scenario: Signer without required role credential cannot sign contract
    Given I am authenticated with role "Contract Signer"
    And I hold a PoA credential from "Authority A"
    And contract "Procurement Agreement" requires PoA from "Authority B"
    And I am designated as a signatory on the contract
    When I attempt to sign contract "Procurement Agreement"
    Then the request is denied with a "Required credential from Authority B not held" error
    And the credential verification failure is logged
    And the contract remains unsigned
