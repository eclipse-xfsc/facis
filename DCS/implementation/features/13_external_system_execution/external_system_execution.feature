@UC-13-01 @FR-SM-10 @IR-SI-05
Feature: External System Contract Execution
  External target systems receive signed contracts via API and confirm
  execution. The DCS generates cryptographic proof of contract execution.

  Scenario: Target system receives contract deployment payload via API
    Given target system "ERP Gateway" is registered with the DCS
    And contract "Service Agreement" is in "Signed" status
    When target system "ERP Gateway" requests the deployment payload via API
    Then the API returns the signed contract and metadata
    And the payload includes contract hash, version, and timestamp

  Scenario: Target system confirms contract activation
    Given target system "ERP Gateway" has received contract "Service Agreement"
    When target system "ERP Gateway" sends an activation confirmation callback
    Then the DCS records the activation with receipt and transaction ID
    And contract "Service Agreement" status is updated to "Executed"

  Scenario: DCS generates cryptographic proof of contract execution
    Given contract "Service Agreement" has all required signatures collected
    And target system "ERP Gateway" has confirmed activation
    When the system generates proof of contract execution
    Then the proof includes hash references
    And the proof includes timestamps
    And the proof includes signer identities
    And the proof includes status confirmations

  Scenario: Contract Manager views execution proof
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Executed" status
    When I view execution proof for contract "Service Agreement"
    Then I see the cryptographic proof with hash references
    And I see the target system activation receipt
    And I see the execution timestamp

  Scenario: External system queries contract status via API
    Given target system "ERP Gateway" is registered with the DCS
    And contract "Service Agreement" is in "Deployed" status
    When target system "ERP Gateway" queries status for contract "Service Agreement"
    Then the API returns the current contract status
    And the response includes contract metadata

  Scenario: Execution proof stored for audit
    Given contract "Service Agreement" is in "Executed" status
    And cryptographic proof of execution has been generated
    When I am authenticated with role "Auditor"
    And I access execution records for contract "Service Agreement"
    Then I see the proof of execution
    And I see the target system transaction ID

  Scenario: Failed execution callback updates status
    Given target system "ERP Gateway" has received contract "Service Agreement"
    When target system "ERP Gateway" sends a failure callback with reason "Validation error"
    Then the DCS records the failure with reason
    And contract "Service Agreement" status is updated to "Execution Failed"
    And the failure event is logged

  Scenario: Unauthorized system cannot access deployment API
    Given target system "Unknown System" is not registered with the DCS
    When target system "Unknown System" requests the deployment payload for contract "Service Agreement"
    Then the request is denied with an authorization error