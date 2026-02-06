@UC-06-02 @FR-CWE-11 @FR-CWE-12 @FR-CWE-22 @FR-CWE-23 @FR-CSA-04 @FR-CSA-14 @FR-CSA-15 @FR-CSA-16 @FR-CSA-23
Feature: Contract Renewal and Termination Management
  Contract Managers manage contract renewal and termination processes
  including expiration tracking, renewal workflows, formal termination,
  and VC revocation.

  Scenario: Renew contract with retained metadata and signatures
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is approaching expiration
    When I renew contract "Service Agreement"
    Then a new contract instance is created
    And the new instance retains linked metadata from the original
    And the new instance retains signature references from the original
    And the new instance has reference links to the original contract

  Scenario: Renewal workflow with template reuse
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is eligible for renewal
    When I initiate the renewal workflow for contract "Service Agreement"
    Then the original template is reused
    And metadata is automatically carried over
    And involved parties are notified about the renewal deadline

  Scenario: Monitor contract expiration timelines
    Given I am authenticated with role "Contract Manager"
    When I view the expiration management interface
    Then I see contracts ordered by expiration date
    And I see renewal status for each contract
    And I can perform bulk renewal actions

  Scenario: Alert generated for approaching expiration
    Given contract "Service Agreement" has expiration date in "30 days"
    And expiration alert threshold is configured as "30 days"
    When the system monitors contract expiration timelines
    Then an alert is generated for approaching expiration
    And the alert is delivered according to notification preferences

  Scenario: Formally terminate contract
    Given contract "Service Agreement" is in "Active" status
    When I terminate contract "Service Agreement" with reason "Mutual agreement"
    Then the contract is marked as "Terminated"
    And the termination reason is recorded
    And the termination author and timestamp are recorded
    And the contract status is preserved for compliance

  Scenario: Terminated contract removed from active workflows
    Given contract "Service Agreement" has been terminated
    When I view active contract workflows
    Then contract "Service Agreement" is not included
    And the contract remains accessible in read-only mode

  Scenario: Expired contract flagged and removed from active workflows
    Given contract "Service Agreement" has passed its expiration date
    When the system processes expired contracts
    Then the contract is flagged as "Expired"
    And the contract is removed from active workflows
    And the contract cannot be used for new transactions

  Scenario: Create extension contract linked to original
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is archived
    When I create an extension contract for "Service Agreement"
    Then the extension is linked to the archived original
    And the extension retains references to the original version and ID
    And the extension retains references to the original signatures

  Scenario: Termination triggers VC revocation
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has associated metadata VCs
    When I terminate contract "Service Agreement"
    Then the associated metadata VCs are revoked
    And the revocation is logged

  Scenario: Unauthorized role cannot terminate contract
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is in "Active" status
    When I attempt to terminate contract "Service Agreement"
    Then the request is denied with an authorization error
