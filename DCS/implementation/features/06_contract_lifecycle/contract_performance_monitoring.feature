@UC-06-01 @FR-CWE-24 @FR-CWE-27 @FR-CWE-31 @FR-CWE-09 @FR-CSA-20
Feature: Contract Performance Monitoring
  Contract Managers and Contract Observers monitor contract performance
  through a lifecycle dashboard displaying real-time status, KPIs,
  milestones, and compliance alerts.

  Scenario: View contract lifecycle dashboard
    Given I am authenticated with role "Contract Manager"
    When I open the contract lifecycle dashboard
    Then I see contracts across all lifecycle states
    And I see filtering options for contract search
    And the dashboard displays live updates

  Scenario: View real-time contract status
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Active" status
    When I view contract "Service Agreement" on the dashboard
    Then I see the current lifecycle stage
    And I see timestamps for each stage transition
    And I see the action history

  Scenario: Track contract KPIs and milestones
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has defined KPIs
    When I view performance metrics for contract "Service Agreement"
    Then I see delivery timeline status
    And I see milestone completion status
    And I see financial terms status

  Scenario: Alert raised for underperformance
    Given contract "Service Agreement" has KPI "delivery_time" with threshold "5 days"
    And actual delivery time has exceeded "5 days"
    When the system evaluates contract KPIs
    Then an alert is raised for underperformance
    And the alert includes the violated KPI and threshold

  Scenario: Alert raised for missed deadline
    Given contract "Service Agreement" has milestone "quarterly_review" due today
    And milestone "quarterly_review" has not been completed
    When the system evaluates contract milestones
    Then an alert is raised for missed target
    And the alert is logged with timestamp

  Scenario: Monitor SLA compliance
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has SLA obligations
    When I view SLA compliance for contract "Service Agreement"
    Then I see SLA violation flags if any
    And compliance rules are displayed

  Scenario: Configure alert notifications
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Active" status
    When I configure alert notifications for contract "Service Agreement"
    Then I can set notification channels as UI, email, or API
    And the notification preferences are saved

  Scenario: Contract Observer views dashboard with read-only access
    Given I am authenticated with role "Contract Observer"
    When I open the contract lifecycle dashboard
    Then I see contracts across all lifecycle states
    And I cannot modify contract data

  Scenario: Dashboard supports bulk actions
    Given I am authenticated with role "Contract Manager"
    And multiple contracts are approaching renewal
    When I select multiple contracts on the dashboard
    Then I can perform bulk actions on selected contracts

  Scenario: Unauthorized role cannot access lifecycle dashboard
    Given I am authenticated with role "Template Creator"
    When I attempt to open the contract lifecycle dashboard
    Then the request is denied with an authorization error
