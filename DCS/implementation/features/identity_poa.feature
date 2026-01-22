# UC-14: Identity & Proof of Authority Credential Acquisition
Feature: Identity Verification and Proof of Authority Management
  As a Contract Signer
  I want my identity and proof of authority credentials to be retrieved, validated, and bound before signing
  So that only authorized and valid credentials are used when executing a contract

  Background:
    Given credential validation is enabled
    And XFSC Revocation List is accessible
    And trusted external credential sources are configured
    And credential binding to sessions is enabled

  Scenario: Retrieve identity and PoA credentials before signing
    Given a contract requires signing
    And the Contract Signer is authenticated
    When the Contract Signer initiates the signing preparation
    Then the system retrieves the Contract Signer identity credential
    And the system retrieves the Contract Signer proof of authority (PoA)
    And the retrieval outcome is recorded

  Scenario: Fetch and validate identity credentials from trusted sources
    Given a contract requires signing
    And the Contract Signer is authenticated
    When identity credentials are requested for the Contract Signer
    Then the system fetches the identity credentials from configured trusted sources
    And the credentials are available for further validation
    And the fetch outcome is recorded

  Scenario: Validate identity credential authenticity
    Given an identity credential is available for the Contract Signer
    And identity validation is required for signing
    When the system validates the identity credential
    Then the identity credential is verified as valid or invalid
    And if invalid, the Contract Signer is blocked from proceeding to signing
    And the validation outcome is recorded

  Scenario: Validate proof of authority authenticity and scope
    Given a proof of authority (PoA) is available for the Contract Signer
    And proof of authority is required for signing
    When the system validates the proof of authority for the contract
    Then the proof of authority is verified as valid or invalid
    And the system determines whether the proof of authority authorizes signing this contract
    And if authorization fails, the Contract Signer is blocked from proceeding to signing
    And the validation outcome is recorded

  Scenario: Bind credentials to signing session
    Given the Contract Signer identity credential is validated successfully
    And the Contract Signer proof of authority is validated successfully
    When the system prepares the signing operation for the contract
    Then the system binds the validated identity credential to the signing session
    And the system binds the validated proof of authority to the signing session
    And the binding is recorded

  Scenario: Store identity and PoA evidence in contract record
    Given credentials are bound to the signing session
    When the signing operation is completed
    Then the system stores identity and proof of authority evidence in the contract record
    And the stored evidence supports later audit and verification
    And the storage is recorded

  Scenario: Manage credential revocation and status
    Given a credential previously used for signing becomes revoked
    When the system checks the credential status
    Then the system marks the affected credential as revoked
    And the system prevents new signing actions that depend on the revoked credential
    And the status change is recorded

  Scenario: Support credential verification viewer
    Given a signed contract has recorded identity and proof of authority evidence
    When an Auditor or Compliance Officer requests to review signing evidence
    Then the system provides the identity verification result and the proof of authority validation result
    And the system provides the current revocation status of relevant credentials
    And the review activity is recorded
