@UC-09-01 @FR-UC-09-1
Feature: Role-Based Access Configuration
  System Administrators configure RBAC settings including
  user roles, permissions, access scopes, and account status.

  Scenario: Add a new user role
    Given I am authenticated with role "System Administrator"
    When I add role "Contract Auditor" with permissions for audit log access
    Then the role is created
    And the role takes effect immediately
    And the action is logged with actor identity and timestamp

  Scenario: Edit an existing user role
    Given I am authenticated with role "System Administrator"
    And role "Contract Reviewer" exists
    When I edit role "Contract Reviewer" to include permission "template review"
    Then the role permissions are updated
    And the change takes effect immediately
    And the action is logged with actor identity and timestamp

  Scenario: Remove a user role
    Given I am authenticated with role "System Administrator"
    And role "Legacy Role" exists
    And no active users are assigned to role "Legacy Role"
    When I remove role "Legacy Role"
    Then the role is removed from the system
    And the action is logged with actor identity and timestamp

  Scenario: Assign permissions and access scope to a role
    Given I am authenticated with role "System Administrator"
    And role "Archive Manager" exists
    When I define access scope for role "Archive Manager" to resource "Contract Archive"
    Then the access scope is applied
    And the role grants access only to the defined scope

  Scenario: Deactivate a user account
    Given I am authenticated with role "System Administrator"
    And user account "alice@example.com" is active
    When I deactivate account "alice@example.com"
    Then the account status is "Deactivated"
    And the user can no longer access the system
    And the deactivation is logged with actor identity and timestamp

  Scenario: Reactivate a user account
    Given I am authenticated with role "System Administrator"
    And user account "alice@example.com" is in "Deactivated" status
    When I reactivate account "alice@example.com"
    Then the account status is "Active"
    And the reactivation is logged with actor identity and timestamp

  Scenario: Unauthorized role cannot configure RBAC
    Given I am authenticated with role "Contract Manager"
    When I attempt to add role "New Role" with permissions for contract access
    Then the request is denied with an authorization error
    And the unauthorized attempt is logged

