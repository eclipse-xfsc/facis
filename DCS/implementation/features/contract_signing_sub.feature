# UC-04: Contract Signing - Sub Use Cases
Feature: Contract Signing - Detailed Sub Processes
  As a Contract Signer or Contract Manager
  I want to securely review, verify, and sign contracts
  So that contracts are legally binding with valid signatures

  # UC-04-01 – Review & Sign Contract Electronically
  Scenario: Secure electronic signature process
    Given a contract is ready for signing
    When a Contract Signer accesses the secure document viewer
    Then the system should:
      | Feature                | Description                |
      | Secure Viewer          | Protected document view    |
      | Legally Binding E-Sig  | Valid digital signature    |
      | Identity/PoA Binding   | Proof of authority         |
      | Signer Authentication  | Verify identity            |
    And the system should produce signed artifact (PAdES/JAdES)
    And the system should record the signing event in the audit log

  # UC-04-02 – Verify Counterparty Authorization
  Scenario: Check legal authority to sign
    Given a signing credentials of the counterparty
    When a Contract Signer or Contract Manager checks the signing credentials
    Then the system should:
      | Check                 | Description              |
      | Present VC/PoA        | Verifiable credentials   |
      | Validate Chains       | Certificate chain valid  |
      | Check Status Lists    | Not revoked              |
    And unauthorized cases should block signing with error message

  # UC-04-03 – Verify Counterparty Signature
  Scenario: Validate signature authenticity and integrity
    Given a contract has been signed
    When a Contract Signer or Contract Manager initiates the signature verification
    Then the system should:
      | Check                 | Result                   |
      | Crypto Validation     | Signature valid          |
      | Policy Checks         | Compliance verified      |
      | Certificate Status    | Valid and unrevoked      |
      | Document Hash Match   | Content unchanged        |
    And report should show all validation results
