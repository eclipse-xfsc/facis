# UC-01: Authentication & Authorization
Feature: Authentication and Authorization
  As a user (human or system)
  I want to authenticate using verifiable credentials with role-based authorization
  So that only authorized users can access role-protected resources

  Background:
    Given the system is configured with credential validation enabled
    And the XFSC Revocation List is accessible

  Scenario: Authorized user successfully accesses a protected resource
    Given a user presents a valid verifiable credential containing role-based authorization data
    When the user attempts to access a protected resource
    Then the system should:
      | Action                      | Details                                                        |
      | Verify Credential           | Credential authenticity is verified                             |
      | Confirm Role                | User role is confirmed                                          |
      | Enforce Access Policy       | Access is granted according to role-based permissions           |
      | Log Access Attempt          | Access attempt is logged for audit and security monitoring      |
    And the audit log entry should include:
      | Field       | Value                      |
      | Actor       | User identifier            |
      | Resource    | Target resource            |
      | Decision    | Allow                      |
      | Timestamp   | Exact time of the attempt  |

  Scenario: Reject access with invalid or revoked credentials
    Given a user presents an invalid verifiable credential
    When the user attempts to authenticate or access a role-protected resource
    Then the system should:
      | Action                | Details                                      |
      | Reject Credential     | Credential is expired, revoked, or malformed |
      | Deny Access           | Access is not granted                        |
      | Return Error Message  | "Credential invalid or access revoked"       |
      | Log Unauthorized Try  | Attempt is logged for audit and security     |

  # DCS-FR-UC-01-4
  Scenario: Block user after multiple invalid credential attempts
    Given a user has repeatedly failed authentication with invalid credentials
    When the user attempts authentication again
    Then the system should block the user account
    And further authentication attempts should be denied
    And the blocking event should be logged for audit and security monitoring

  Scenario: Unauthenticated request to a protected API
    Given no authentication credential is presented
    When a request is made to a role-protected API endpoint
    Then the system should deny access
    And the system should return HTTP 401 Unauthorized
    And the unauthorized access attempt should be logged with timestamp and targeted resource

  Scenario: Wallet integration failure handling
    Given a user initiates authentication requiring wallet integration
    When the wallet integration fails (e.g., signer unavailable)
    Then the system should notify the user with error message
    And the user should be offered retry option or fallback mechanism
    And the system should log the wallet integration failure
    And fallback authentication method should be available (if configured)
