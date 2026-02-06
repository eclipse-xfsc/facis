@UC-10-01 @FR-CWE-28 @FR-CSA-25
Feature: Contract Workflow Automation
  Process Orchestrators integrate contract workflows with external AI/ERP
  systems. The system translates contract milestones into actionable triggers
  and maintains end-to-end traceability.

  Scenario: Orchestrator triggers external action from contract milestone
    Given I am authenticated with role "Process Orchestrator"
    And contract "Service Agreement" has milestone "payment_due"
    And external system "ERP Gateway" is configured for milestone triggers
    When milestone "payment_due" is reached on contract "Service Agreement"
    Then the system triggers an action on external system "ERP Gateway"
    And the external system receives the milestone event
    And the trigger is logged with timestamp and correlation ID

  Scenario: External system executes triggered action
    Given contract "Service Agreement" has triggered milestone "payment_due"
    And external system "ERP Gateway" has received the trigger
    When external system "ERP Gateway" executes the triggered action
    Then the system receives a completion callback
    And the milestone status is updated to "Executed"

  Scenario: End-to-end workflow trace is visible
    Given I am authenticated with role "Process Orchestrator"
    And contract "Service Agreement" has completed multiple milestones
    When I view the workflow trace for contract "Service Agreement"
    Then I see ordered events from initiation to completion
    And each event includes timestamp and actor identity
    And the trace shows external system interactions

  Scenario: Orchestrator initiates synchronized execution with AI platform
    Given I am authenticated with role "Process Orchestrator"
    And contract "AI Service Agreement" is configured for AI platform integration
    When I initiate synchronized execution for contract "AI Service Agreement"
    Then the system connects with the configured AI platform
    And contract milestones are translated into actionable triggers
    And synchronized execution begins

  Scenario: Webhook callback updates contract status
    Given contract "Service Agreement" has an active workflow
    And external system "ERP Gateway" is processing a milestone
    When external system "ERP Gateway" sends a webhook callback with status "completed"
    Then the contract milestone status is updated
    And the callback is logged for traceability

  Scenario: Failed external action is logged and flagged
    Given contract "Service Agreement" has triggered milestone "payment_due"
    And external system "ERP Gateway" has received the trigger
    When external system "ERP Gateway" returns a failure response
    Then the failure is logged with reason
    And the milestone status is updated to "Failed"
    And an alert is generated for review

  Scenario: Unauthorized role cannot initiate workflow automation
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" has milestone "payment_due"
    When I attempt to trigger external action for contract "Service Agreement"
    Then the request is denied with an authorization error
