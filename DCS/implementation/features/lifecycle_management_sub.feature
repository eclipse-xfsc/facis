# UC-06: Lifecycle Management - Sub Use Cases
Feature: Lifecycle Management - Detailed Sub Processes
  As a Contract Manager or Contract Observer
  I want to monitor and manage contract lifecycle events
  So that contracts are renewed or terminated appropriately

  # UC-06-01 – Monitor Contract Performance
  Scenario: Dashboard displays SLA and compliance tracking
    Given a contract is under lifecycle management
    When a Contract Manager or Contract Observer opens the contract lifecycle dashboard
    Then the system should:
      | Metric              | Description          |
      | KPIs/Milestones     | Performance targets  |
      | Alerts              | SLA violations       |
      | History             | Fulfilled terms      |
    And alerts should fire for any compliance violations

  # UC-06-02 – Renewal or Termination
  Scenario: Manage contract renewal and termination
    Given a contract is in "Active" status
    When a Contract Manager initiates a renewal or termination request
    Then the system should:
      | Action                | Result                |
      | Update State          | New lifecycle state   |
      | Issue/Update VC Revoc | Where applicable      |
      | Send Notifications    | To stakeholders       |
      | Create Logs           | Audit trail entry     |
    And all parties should be notified of state changes
