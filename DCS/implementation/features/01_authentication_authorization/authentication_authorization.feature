@UC-01 @FR-UC-01-1 @FR-UC-01-2 @FR-UC-01-3
Feature: User Authentication & Authorization
  Users authenticate securely and are authorized based on roles and credentials.

  Scenario: Successful authentication with valid credential
    Given I present a valid verifiable credential
    When I attempt to access the DCS system
    Then I am authenticated and granted access based on my role
    And my access is logged with timestamp and user ID

  Scenario: Authorization denied for invalid credential
    Given I present an expired credential
    When I attempt to access the DCS system
    Then the request is denied with error "Credential invalid or access revoked"
    And the attempt is logged for audit

  Scenario: Role enforcement prevents unauthorized actions
    Given I am authenticated with role "Contract Creator"
    When I attempt to access admin functions
    Then the request is denied with an authorization error
    And the denial is logged

  Scenario: PoA credential validation for signing
    Given I am authenticated with role "Contract Signer"
    And I hold a valid PoA credential for organization "Example Corp"
    When I initiate a signing process
    Then the PoA credential is validated
    And signing proceeds if authorized

  Scenario: Revoked credential blocks access
    Given my credential has been revoked via XFSC Revocation List
    When I attempt to access the DCS system
    Then the request is denied
    And access rights are invalidated until re-credentialing

  # FR-UC-01-4: Multiple invalid credential attempts trigger lockout
  Scenario: Multiple failed credential attempts trigger account lockout
    Given I present an invalid credential
    When I fail authentication 5 consecutive times
    Then my account is locked
    And I receive error "Account locked due to multiple failed attempts"
    And the lockout event is logged for security monitoring

  Scenario: Locked account cannot authenticate even with valid credential
    Given my account has been locked due to failed attempts
    When I present a valid verifiable credential
    Then the request is denied with error "Account locked"
    And I am instructed to contact an administrator

  Scenario: Administrator can unlock a locked account
    Given user "locked.user@example.com" has a locked account
    And I am authenticated with role "System Administrator"
    When I unlock the account for user "locked.user@example.com"
    Then the account is unlocked
    And the user can authenticate with valid credentials
    And the unlock action is logged for audit

  Scenario: Wallet integration failure allows retry
    Given I am authenticated with role "Contract Signer"
    And my wallet integration encounters a temporary failure
    When I attempt to sign a contract
    Then the system notifies me of the wallet failure
    And I am offered the option to retry
    And the failure is logged for troubleshooting