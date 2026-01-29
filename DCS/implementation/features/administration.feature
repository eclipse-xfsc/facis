# UC-09: Administration
Feature: System Administration and User Management
  As a system administrator
  I want to manage roles, permissions, user access, and monitor system health
  So that users have appropriate permissions, access is controlled, and system performance is tracked

  Background:
    Given RBAC is fully configured
    And system monitoring is enabled
    And audit logging is active for all admin actions
    And user account management is available

  Scenario: Create new role with specific permissions
    Given the System Administrator is logged in and has role management permissions
    When the administrator creates a new role "Template Creator" with defined permissions
    Then the system should:
      | Action               | Details                          |
      | Create Role          | Role "Template Creator" created  |
      | Apply Permissions    | Permissions associated to role   |
      | Make Role Available  | Role can be assigned to users    |
      | Log Admin Action     | Role creation recorded           |

  Scenario: Modify existing role and apply changes to users
    Given the role "Template Creator" exists
    And the role "Template Creator" is assigned to one or more users
    When the System Administrator modifies the role permissions
    Then the system should:
      | Action                       | Details                                         |
      | Update Role Permissions      | Role "Template Creator" permissions are updated |
      | Apply Changes Immediately    | Updated permissions take effect immediately     |
      | Apply To Assigned Users      | All users with role "Template Creator" inherit the changes |
      | Log Admin Action             | Role modification is recorded                   |

  Scenario: Assign role to new user
    Given a user "jane.smith" exists in the system
    And the role "Template Creator" exists
    When the System Administrator assigns the role "Template Creator" to user "jane.smith"
    Then the system should:
      | Action                  | Details                                      |
      | Assign Role             | Role "Template Creator" assigned to user     |
      | Apply Role Immediately  | Role takes effect immediately                |
      | Log Admin Action        | Role assignment is recorded                  |

  Scenario: Deactivate user account
    Given a user account "jane.smith" exists and is active
    When a System Administrator deactivates the user account "jane.smith"
    Then the system should:
      | Action             | Details                        |
      | Deactivate Account | Account status set to inactive |
      | Deny Access        | Access denied                  |
      | Log Admin Action   | Deactivation recorded          |

  Scenario: Reactivate user account
    Given a user account "jane.smith" exists and is inactive
    When a System Administrator reactivates the user account "jane.smith"
    Then the system should:
      | Action             | Details                      |
      | Reactivate Account | Account status set to active |
      | Restore Access     | Access restored              |
      | Log Admin Action   | Reactivation recorded        |


  Scenario: Revoke role from user immediately
    Given a user "jane.smith" has role "Template Creator"
    And the user currently has active sessions
    When the System Administrator revokes role "Template Creator" from user "jane.smith"
    Then the system should immediately:
      | Action                | Details                |
      | Revoke Role           | Remove from user       |
      | Revoke Permissions    | All associated perms   |
      | Update Access Lists   | Remove from all acls   |
      | Prevent Re-access     | Until re-assigned      |
    And the revocation should take effect immediately
    And the audit trail should include:
      | Audit Field           | Value                  |
      | Event Type            | Role Revoked           |
      | Revoked By            | Administrator          |
      | Revoked From          | User name              |
      | Revocation Reason     | Provided reason        |
      | Timestamp             | Exact revocation time  |

  Scenario: View role-based access configuration
    Given role-based access configuration exists
    When a System Administrator views the current RBAC configuration
    Then the system should display:
      | Configuration Element | Details                |
      | Defined Roles         | Roles are listed       |
      | Role Permissions      | Permissions are shown  |
      | User-Role Mapping     | Assignments are shown  |

  Scenario: Monitor system health and performance
    Given the monitoring dashboard is available
    When a System Administrator views system health metrics
    Then the system should:
      | Action                      | Details                                              |
      | Present operational health  | Operational health metrics are visible               |
      | Present searchable logs     | Security-related events are available for review     |
      | Include audit information   | Logs include timestamps and actor identification     |

  Scenario: Log account deactivation event
    Given a user account "jane.smith" exists and is active
    When a System Administrator deactivates the user account "jane.smith"
    Then the system should:
      | Action             | Details                                  |
      | Log security event | Account deactivation is logged           |
      | Include audit info | Timestamp and actor identification exist |

  Scenario: Log template and contract life-cycle events
    Given template and contract life-cycle events occur
    When the system records these events
    Then the system should:
      | Action             | Details                                  |
      | Log security event | Template & contract life-cycle events are logged |
      | Include audit info | Timestamp and actor identification exist |
