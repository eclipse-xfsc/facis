# UC-06: Lifecycle Management
Feature: Contract Lifecycle Management
  As a Contract Manager
  I want to manage the lifecycle states of a contract
  So that the contract transitions through defined states in a controlled and auditable manner

  Background:
    Given contract monitoring is enabled
    And SLA and compliance monitoring is configured
    And renewal and termination workflows are defined
    And alerts are configured for key milestones

  Scenario: View contract dashboard with KPIs
    Given multiple active contracts exist in the system
    When the Contract Manager opens the contract lifecycle dashboard
    Then the system shows contract lifecycle KPIs
    And the system shows alerts for contracts requiring attention
    And the system should record the dashboard access in the audit log

  Scenario: Initiate contract renewal flow
    Given a contract is active and nearing expiration
    And a renewal alert is available for the contract
    When the Contract Manager initiates the renewal flow
    Then the system creates a renewal workflow task for the contract
    And the contract enters the "Renewal Pending" state
    And the system should record the renewal initiation in the audit log

  Scenario: Confirm contract renewal with new terms
    Given a contract is in "Renewal Pending" state
    And renewal approvals are completed
    When the Contract Manager confirms the renewal
    Then the contract transitions to the "Renewed" state
    And the renewed contract terms and dates are applied
    And the system should record the state change in the audit log

  Scenario: Initiate contract termination flow
    Given a contract is in "Active" status
    And the Contract Manager is authorized to terminate the contract
    When the Contract Manager initiates the termination flow
    Then the contract enters the "Termination Pending" state
    And a termination workflow task is created
    And the system should record the termination initiation in the audit log

  Scenario: Confirm contract termination
    Given a contract is in "Termination Pending" state
    And termination approvals are completed
    When the Contract Manager confirms the termination
    Then the contract transitions to the "Terminated" state
    And the termination effective date is recorded
    And the system should record the state change in the audit log
