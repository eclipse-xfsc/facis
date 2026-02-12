@UC-05-01 @FR-SM-12 @FR-CWE-06
Feature: Contract Deployment
  Signed contracts are deployed to target systems for execution
  upon completion of the signing process.

  Scenario: Deploy signed contract to target system
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Signed" status
    And target system "ERP Gateway" is configured
    When I deploy contract "Service Agreement" to target system "ERP Gateway"
    Then the target system acknowledges receipt
    And the contract status is updated to "Deployed"
    And a correlation ID is assigned and archived

  Scenario: Deployment payload includes signed contract and metadata
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Signed" status
    When I deploy contract "Service Agreement" to target system "ERP Gateway"
    Then the deployment payload includes the signed contract
    And the payload includes contract hash, version, and timestamp

  Scenario: Automatic deployment triggered after all signatures collected
    Given contract "Partnership Agreement" requires signatures from all parties
    And all required signatures have been collected
    When the signing process completes
    Then the system automatically triggers deployment to the configured target system
    And the deployment event is logged

  Scenario: Event-driven deployment triggered by lifecycle event
    Given contract "Supply Agreement" has a deployment rule on event "approval completed"
    When the event "approval completed" occurs for contract "Supply Agreement"
    Then the system triggers the deployment workflow
    And the event is logged with timestamp

  Scenario: Deployment logs proof of delivery
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has been deployed to target system "ERP Gateway"
    When I view deployment status for contract "Service Agreement"
    Then I see proof of delivery with target acknowledgement
    And I see the deployment timestamp and correlation ID

  Scenario: Deployment fails when target system is unavailable
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Signed" status
    And target system "ERP Gateway" is unavailable
    When I deploy contract "Service Agreement" to target system "ERP Gateway"
    Then the deployment fails
    And the failure is logged with reason
    And the contract status remains "Signed"

  Scenario: Cannot deploy unsigned contract
    Given I am authenticated with role "Contract Manager"
    And contract "Draft Agreement" is in "Draft" status
    When I attempt to deploy contract "Draft Agreement" to target system "ERP Gateway"
    Then the request is denied
    And I receive error "Contract must be signed before deployment"

  Scenario: Unauthorized role cannot deploy contracts
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is in "Signed" status
    When I attempt to deploy contract "Service Agreement" to target system "ERP Gateway"
    Then the request is denied with an authorization error

