# UC-15: Access Rights and Signature Revocation
Feature: Access Rights Revocation and Signature Invalidation
  As a System Administrator
  I want to revoke user roles, credentials, and contract signatures
  So that former employees, contractors, or invalid credentials cannot access the system or valid contracts remain uncompromised

  Background:
    Given access control mechanisms are fully operational
    And revocation lists are maintained and accessible
    And immediate access termination is possible
    And audit logging is enabled for all revocation events

  Scenario: Revoke user role and permissions immediately
    Given a user "jane.smith" has role "Contract Signer"
    And the user currently has active sessions and permissions
    When a System Administrator initiates role revocation
    Then the system should immediately:
      | Action                             | Details                        |
      | Revoke Role                        | Remove role assignment         |
      | Revoke All Associated Perms        | All permissions removed        |
      | Update Access Rules                | Role-protected access removed  |
      | Update Revocation List             | Update to XFSC revocation list |
    And revocation should be logged with:
      | Audit Field              | Value                  |
      | Event Type               | Role Revocation        |
      | User Revoked             | jane.smith             |
      | Revocation Reason        | Employee departure     |
      | Revoked By               | Administrator name     |
      | Revocation Timestamp     | Precise revocation time|
      | Effective Immediately    | Yes                    |

  Scenario: Revoke active signing authority
    Given the role "Contract Signer" for user "jane.smith" has been revoked
    And a contract is signable
    When "jane.smith" attempts to sign the contract
    Then the system should:
      | Action            | Details                     |
      | Deny Signing      | Signing denied after revocation |
      | Log Denied Attempt| Denial recorded             |
