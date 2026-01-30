# UC-04: Contract Signing
Feature: Contract Signing and Signature Validation
  As a Contract Signer or Contract Manager
  I want to securely sign contracts with identity verification and proof of authority (PoA)
  So that signatures are legally valid, verifiable, and recorded with auditable evidence


  Background:
    Given a secure document viewer is configured
    And signature validation is enabled
    And the system is configured with credential validation enabled

  Scenario: Open secure viewer
    Given a contract is ready for signing
    And a Contract Signer is assigned to the contract
    When a Contract Signer accesses the secure document viewer for the contract
    Then the system should:
      | Feature               | Description                          |
      | Secure Viewer         | Protected contract view              |
      | Access Control        | Only authenticated/authorized access |
      | Signing Context       | Contract shown in signing mode       |
    And the system should record the viewer access in the audit log

  Scenario: Present identity and proof of authority (PoA)
    Given a contract is open in the secure document viewer
    When a Contract Signer presents identity credentials for the signing session
    And a Contract Signer presents proof of authority (PoA) credentials for the signing session
    Then the system should:
      | Check                    | Result / Expectation                         |
      | Validate Identity         | Credential is valid and acceptable           |
      | Validate PoA              | Credential is valid and acceptable           |
      | Bind Identity + PoA       | Bound to the signing session for the contract|
    And the system should record the credential presentation in the audit log

  Scenario: Verify result
    Given a contract has been signed
    When a Contract Signer or Contract Manager initiates signature verification
    Then the system should:
      | Check                 | Result / Expectation            |
      | Crypto Validation     | Signature is cryptographically valid |
      | Certificate Status    | Certificates are valid/unrevoked     |
      | Policy Checks         | Signature complies with policy       |
      | Document Integrity    | Content unchanged after signing      |
    And the system should produce a verification report
    And the system should record the signature verification in the audit log

  Scenario: Verify signer identity
    Given a contract is open in the secure contract viewer
    And identity verification is required for signing
    When the Contract Signer presents an identity credential
    Then the system verifies the identity of the Contract Signer
    And the Contract Signer is allowed to proceed with signing
    And the system should record the identity verification in the audit log

  Scenario: Validate proof of authority
    Given the Contract Signer is identified
    And proof of authority is required for signing
    When the Contract Signer presents a proof of authority
    Then the system validates the authority for the contract
    And the Contract Signer is authorized to sign
    And the system should record the authorization result in the audit log

  Scenario: Execute digital signature
    Given a signer is verified and has reviewed the contract
    When the signer executes the signature action
    And confirms intention to sign digitally
    And applies their digital signature (qualified or advanced electronic signature)
    Then the signature should be recorded as valid
    And a unique signature identifier should be generated
    And a cryptographic timestamp should be attached
    And signature metadata should include:
      | Field               | Value                  |
      | Signer Identity     | Verified identity      |
      | Proof of Authority  | PoA credentials        |
      | Signature ID        | Unique identifier      |
      | Timestamp           | Precise signing time   |
      | Certificate         | Digital certificate   |

  Scenario: Complete multi-party signing workflow
    Given a contract requires signatures from multiple parties
    When all required parties complete their signing actions
    Then the contract reaches a fully signed state
    And the system should record the signing completion in the audit log
