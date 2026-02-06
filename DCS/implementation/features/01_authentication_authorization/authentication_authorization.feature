@UC-01 @FR-UC-01-1 @FR-UC-01-2 @FR-UC-01-3
Feature: User Authentication & Authorization
  As a user, I want to authenticate securely and be authorized based on my role
  So that I can access appropriate DCS functions while maintaining security.

  Background:
    Given the DCS system is operational

  Scenario Outline: Successful authentication with valid credential
    Given I present a valid <credential_type> credential
    When I attempt to access the DCS system
    Then I am authenticated and granted access based on my role
    And my access is logged with timestamp and user ID

    Examples:
      | credential_type     |
      | verifiable          |
      | identity            |
      | PoA                 |

  Scenario: Authorization denied for invalid credential
    Given I present an expired credential
    When I attempt to access the DCS system
    Then the request is denied with error "Credential invalid or access revoked"
    And the attempt is logged for audit

  Scenario Outline: Role enforcement prevents unauthorized actions
    Given I am authenticated with role "<role>"
    When I attempt to access <restricted_function>
    Then the request is denied with an authorization error
    And the denial is logged

    Examples:
      | role             | restricted_function |
      | Contract Creator | admin functions     |
      | Template Reviewer| system settings     |

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

  Scenario: Authentication and authorization events are logged
    Given I am authenticated with role "Contract Creator"
    When I access a protected resource
    Then the authentication and authorization events are logged with timestamp and user ID