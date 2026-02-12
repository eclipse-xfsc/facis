@UC-04-03 @FR-SM-18 @FR-SM-21 @FR-SM-11
Feature: Signature Validation
  The system validates counterparty signatures for cryptographic
  integrity and compliance with legal and organizational policies,
  including linked machine-readable and human-readable signatures.

  Scenario: Validate counterparty signature cryptographic integrity
    Given I am authenticated with role "Contract Signer"
    And contract "Partnership Agreement" has a counterparty signature
    When I validate the counterparty signature on contract "Partnership Agreement"
    Then the cryptographic integrity is confirmed
    And the signature matches the registered signer
    And the document is confirmed unaltered

  Scenario: Validate signature credential status
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has a counterparty signature
    When I validate the counterparty signature on contract "Service Agreement"
    Then the signer credential status is checked against the status list
    And the validation result includes credential status and timestamp

  Scenario: Signature compliance verification against policies
    Given I am authenticated with role "Contract Manager"
    And contract "Regulated Agreement" has signatures applied
    When I verify signature compliance for contract "Regulated Agreement"
    Then each signature is assessed against legal signature policies
    And the assessment includes signature type, credential status, and role
    And any policy violations are flagged

  Scenario: Detect non-compliant signature type
    Given I am authenticated with role "Contract Manager"
    And contract "High-Security Agreement" requires QES signatures
    And a signature of type "AES" has been applied
    When I verify signature compliance for contract "High-Security Agreement"
    Then the system flags "Signature type does not meet QES requirement"

  Scenario: Export validation results for compliance
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has completed signature validation
    When I export validation results for contract "Service Agreement"
    Then I receive an exportable validation report
    And the report includes credential status, integrity proof, and timestamps

  Scenario: Reject tampered document during validation
    Given I am authenticated with role "Contract Signer"
    And contract "Tampered Agreement" has been modified after signing
    When I validate the counterparty signature on contract "Tampered Agreement"
    Then the validation fails
    And I receive error "Document integrity check failed"

  Scenario: Unauthorized role cannot validate signatures
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" has a counterparty signature
    When I attempt to validate the counterparty signature on contract "Service Agreement"
    Then the request is denied with an authorization error

  # FR-SM-11: Linked Machine-Readable and Human-Readable Signatures
  Scenario: Validate linked MR and HR signature binding
    Given I am authenticated with role "Contract Manager"
    And contract "Dual Format Agreement" has machine-readable and human-readable versions
    And both versions have been signed
    When I validate signature linking for contract "Dual Format Agreement"
    Then the MR signature is confirmed linked to the HR signature
    And both signatures reference the same signer credentials
    And the binding hash is verified

  Scenario: Detect signature mismatch between MR and HR versions
    Given I am authenticated with role "Contract Manager"
    And contract "Mismatched Agreement" has separate MR and HR signatures
    And the signatures are not properly linked
    When I validate signature linking for contract "Mismatched Agreement"
    Then the validation fails
    And I receive error "Machine-readable and human-readable signatures are not linked"

  Scenario: Validate unified signature covers both representations
    Given I am authenticated with role "Contract Signer"
    And contract "Unified Agreement" has a single signature covering both formats
    When I validate the signature on contract "Unified Agreement"
    Then the signature is confirmed to cover the machine-readable content
    And the signature is confirmed to cover the human-readable content
    And the content hash binding is verified

  Scenario: Cross-verify MR and HR content integrity via signatures
    Given I am authenticated with role "Auditor"
    And contract "Cross-Verified Agreement" has linked MR and HR signatures
    When I perform cross-verification for contract "Cross-Verified Agreement"
    Then the MR content hash matches the signature reference
    And the HR content hash matches the signature reference
    And any discrepancies between representations are flagged

