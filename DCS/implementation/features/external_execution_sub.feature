# UC-13: External Execution - Sub Use Cases
Feature: Contract Execution in Target Systems - Detailed Sub Processes
  ## This feature covers the deployment of signed contracts to external target systems
  ## and the verification of contract activation and execution.
  As an execution manager
  I want to deploy contracts to external systems for execution
  So that contracts are processed in downstream applications

  # UC-13-01 – Deploy Contract to Target System
  Scenario: Execute contract in ERP target systems
    Given a contract is signed and validated
    And a target system is configured and available
    When the target system requests or receives a contract deployment payload
    Then the system should:
      | Action                    | Result              |
      | Deliver Payload           | Send to ERP         |
      | Target Confirms           | Activation ack      |
      | Record Proof              | Delivery evidence   |
      | Reference Documentation  | Archive proof       |
    And DCS should store proof of execution reference
