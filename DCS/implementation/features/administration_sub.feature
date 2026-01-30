# UC-09: Administration - Sub Use Cases
Feature: System Administration - Detailed Sub Processes
  As a System Administrator
  I want to manage system configuration and monitor system health
  So that the system operates securely and efficiently

  # UC-09-01 – System Configuration & User Management
  Scenario: Administer roles, security, and settings
    Given the administrator accesses system settings
    When system configuration is performed
    Then the system should:
      | Item                | Actions              |
      | Roles & Permissions | Create/modify/delete |
      | User Assignments    | Assign/revoke roles  |
      | Security Settings   | Configure policies   |
    And the system should record the configuration changes in the audit log

  # UC-09-02 – System Monitoring & Logging
  Scenario: Monitor health metrics and security logs
    Given the monitoring dashboard is available
    When the system is observed
    Then the system should:
      | Metric              | Description          |
      | Health Metrics      | System status        |
      | Searchable Logs     | Filterable events    |
      | Severity Filters    | By severity level    |
      | Time Filters        | By date/time         |
    And exports should support incident review and analysis
