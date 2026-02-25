@UC-09-02 @FR-UC-09-2
Feature: System Monitoring and Logging
  System Administrators monitor critical system activities
  and review security-related event logs.

  Scenario: View operational health metrics
    Given I am authenticated with role "System Administrator"
    When I open the system monitoring dashboard
    Then I see operational health metrics
    And I see system event statistics

  Scenario: View security event logs
    Given I am authenticated with role "System Administrator"
    When I view system security logs
    Then I see logged events with timestamps and actor identification
    And events include access attempts, configuration changes, and failures

  Scenario: Filter logs by severity and time range
    Given I am authenticated with role "System Administrator"
    When I filter system logs by severity "Error" and period "2024-Q1"
    Then I see only events matching the filter criteria

  Scenario: Authentication events are logged
    Given a user attempts to authenticate with the system
    When the authentication attempt completes
    Then the attempt is logged with user identifier and timestamp
    And the log records whether access was granted or denied

  Scenario: Account deactivation is logged
    Given I am authenticated with role "System Administrator"
    When I deactivate account "bob@example.com"
    Then the deactivation event is logged with actor identity and timestamp

  Scenario: Admin actions are logged for audit trails
    Given I am authenticated with role "System Administrator"
    When I modify system configuration settings
    Then the configuration change is logged with actor identity and timestamp
    And the log captures previous and new values

  Scenario: Export logs for incident review
    Given I am authenticated with role "System Administrator"
    And security events exist in the system logs
    When I export system logs for period "2024-Q1"
    Then I receive an exportable log report
    And the report supports incident review

  Scenario: Unauthorized role cannot access system monitoring
    Given I am authenticated with role "Contract Observer"
    When I attempt to open the system monitoring dashboard
    Then the request is denied with an authorization error

