@UC-04-02 @UC-14 @FR-SM-04 @FR-SM-26
Feature: Counterparty Authorization and PoA Credential Chain Verification
  The system verifies counterparty PoA credentials and delegation
  chains before allowing contract signing to proceed.
  Note: Implements UC-04-02 (Verify Counterparty Authorization) as part of
  UC-14 (Identity and PoA Credential Acquisition) workflows.

  Scenario: Verify valid counterparty PoA credential chain
    Given I am authenticated with role "Contract Signer"
    And contract "Partnership Agreement" requires counterparty signature
    And counterparty "Global Corp" holds a valid PoA credential chain
    When I verify counterparty authorization for "Global Corp"
    Then the delegation chain is validated as traceable
    And the chain is confirmed anchored in a trusted registry
    And counterparty authorization is confirmed

  Scenario: Reject counterparty with broken delegation chain
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" requires counterparty signature
    And counterparty "Unknown Ltd" has a broken PoA delegation chain
    When I verify counterparty authorization for "Unknown Ltd"
    Then the verification fails
    And I receive error "Counterparty delegation chain is not traceable"

  Scenario: Reject counterparty with unanchored credentials
    Given I am authenticated with role "Contract Signer"
    And contract "Data Agreement" requires counterparty signature
    And counterparty "Offshore Inc" holds credentials not anchored in a trusted registry
    When I verify counterparty authorization for "Offshore Inc"
    Then the verification fails
    And the failure is logged with counterparty identity and reason

  Scenario: View counterparty credential compliance status
    Given I am authenticated with role "Contract Manager"
    And counterparty "Global Corp" has completed credential verification
    When I view signature compliance status for contract "Partnership Agreement"
    Then I see the counterparty signer identity and role
    And I see the credential chain with delegation path
    And I see the verification timestamp
    And I see the cryptographic integrity proof

  Scenario: Contract Manager triggers counterparty verification
    Given I am authenticated with role "Contract Manager"
    And contract "Master Agreement" has pending counterparty signatures
    When I verify counterparty authorization for "Partner AG"
    Then the system checks stored credentials and third-party trust anchors
    And the verification result is recorded

  Scenario: Unauthorized role cannot verify counterparty credentials
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" requires counterparty signature
    When I attempt to verify counterparty authorization for "Global Corp"
    Then the request is denied with an authorization error
