@UC-04-01 @FR-CWE-19 @FR-CWE-26 @FR-SM-13 @FR-SM-16
Feature: Contract Signing
  Contract Signers review contracts in a secure viewer and apply
  legally binding digital signatures with identity and PoA credentials.

  Scenario: Sign contract in secure viewer
    Given I am authenticated with role "Contract Signer"
    And contract "Service Agreement" is in "Approved" status
    When I open contract "Service Agreement" in the secure viewer
    And I apply my digital signature to contract "Service Agreement"
    Then a signed artifact is produced
    And the contract status is updated to "Signed"
    And the signing action is logged with timestamp and signer ID

  Scenario: Signature includes identity and PoA credentials
    Given I am authenticated with role "Contract Signer"
    And I hold a valid identity credential issued by a recognized authority
    And I hold a valid PoA credential for organization "Acme Corp"
    When I apply my digital signature to contract "Service Agreement"
    Then the signature binds my identity credential
    And the signature binds my PoA credential

  Scenario: Signing interface supports wallet integration
    Given I am authenticated with role "Contract Signer"
    And I have a configured digital wallet
    And contract "Service Agreement" is in "Approved" status
    When I open the signing interface for contract "Service Agreement"
    Then the interface integrates with my wallet for signature operations
    And the interface displays my pending signer tasks

  Scenario: Signature workflow enforces signing order
    Given I am authenticated with role "Contract Manager"
    And contract "Multi-Party Agreement" requires sequential signatures
    And signer "Alice" must sign before signer "Bob"
    When signer "Bob" attempts to sign before signer "Alice"
    Then the request is denied
    And I receive error "Signing order dependency not met"

  Scenario: Signature workflow enforces deadlines
    Given I am authenticated with role "Contract Signer"
    And contract "Time-Bound Agreement" has a signing deadline that has passed
    When I attempt to apply my digital signature to contract "Time-Bound Agreement"
    Then the request is denied
    And I receive error "Signing deadline has expired"

  Scenario: Multi-signer contract tracks completion in real time
    Given I am authenticated with role "Contract Manager"
    And contract "Partnership Agreement" requires signatures from 3 parties
    And 2 of 3 signatures have been collected
    When I view signing status for contract "Partnership Agreement"
    Then I see 2 signatures completed and 1 pending
    And I see timestamps for each completed signature

  Scenario: Digital signature applied via signing service
    Given I am authenticated with role "Contract Signer"
    And contract "Service Agreement" is in "Approved" status
    When I apply my digital signature via the signing service
    Then the system ensures secure key usage
    And signature integrity is validated upon signing

  Scenario: Cannot sign unapproved contract
    Given I am authenticated with role "Contract Signer"
    And contract "Draft Agreement" is in "Draft" status
    When I attempt to apply my digital signature to contract "Draft Agreement"
    Then the request is denied
    And I receive error "Contract must be approved before signing"

  Scenario: Unauthorized role cannot sign contracts
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is in "Approved" status
    When I attempt to apply my digital signature to contract "Service Agreement"
    Then the request is denied with an authorization error

