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