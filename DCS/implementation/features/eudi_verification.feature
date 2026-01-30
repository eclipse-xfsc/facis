# UC-EUDI: EUDI PID Verification
Feature: EU Digital Identity (EUDI) Person Identification Data Verification
  As a digital identity compliance officer
  I want to verify Person Identification Data (PID) from EUDI-compliant wallets
  So that signers can be authenticated using trusted digital identity sources

  Scenario: Verify EUDI PID from compliant wallet
    Given a signer uses an EUDI-compliant wallet
    When EUDI PID verification is initiated
    Then the system should:
      | Wallet Provider            | Example              |
      | Lissi EUDI Wallet          | Connector available  |
      | EU EUDI Reference Impl      | Reference implementation |
    And the verification process should be seamless

  Scenario: End-to-end workflow completion with EUDI
    Given EUDI PID verification is configured
    When the complete signing workflow is executed
    Then the system should:
      | Requirement            | Verification      |
      | End-to-End Response    | 2xx status codes  |
      | Callback Received      | Async notification|
      | Trace Ordered Events   | Sequence logged   |
    And all responses should be successful (2xx)

  Scenario: EUDI PID authentication succeeds
    Given valid EUDI PID credentials are presented
    When authentication is performed
    Then the system should:
      | Check              | Result            |
      | API Auth           | Returns 2xx       |
      | Validation Result  | Returned in API   |
      | Request/Response   | Correlation ID    |
      | Logging            | Full audit trail  |
    And correlation IDs should link all related operations

  Scenario: EUDI PID wallet integration
    Given EUDI wallet integration is configured
    When a user initiates PID verification
    Then the system should:
      | Feature                    | Implementation |
      | Wallet Selection           | List available |
      | Redirect to Wallet         | OAuth/SAML flow|
      | Receive PID in Safe Way    | Encrypted      |
      | Validate PID Certificate   | Chain check    |
      | Bind to Signer Session     | Create binding |
    And the binding should enable contract signing
