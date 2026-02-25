@UC-11-01 @FR-CWE-28 @FR-CSA-25 @FR-SM-25
Feature: API-Based Contract Workflows
  Integration Managers configure and invoke APIs to trigger contract-related
  events. The system authenticates requests, initiates workflows, and logs
  interactions for traceability.

  Scenario: Create contract via API
    Given I am authenticated with role "Integration Manager" via API
    When I invoke the contract creation API with valid payload
    Then the system creates a new contract
    And the API returns HTTP 2xx status
    And the interaction is logged with timestamp and actor identity

  Scenario: Update contract metadata via API
    Given I am authenticated with role "Integration Manager" via API
    And contract "Service Agreement" exists
    When I invoke the metadata update API for contract "Service Agreement"
    Then the metadata is updated
    And the API returns HTTP 2xx status
    And the interaction is logged with timestamp and actor identity

  Scenario: Query contract via API
    Given I am authenticated with role "Integration Manager" via API
    And contract "Service Agreement" exists
    When I invoke the contract query API for contract "Service Agreement"
    Then the API returns the contract data
    And the response includes contract metadata

  Scenario: Archive contract via API
    Given I am authenticated with role "Integration Manager" via API
    And contract "Expired Agreement" is in "Completed" status
    When I invoke the contract archival API for contract "Expired Agreement"
    Then the contract is archived
    And the API returns HTTP 2xx status
    And the action is logged with timestamp and actor identity

  Scenario: Trigger automated signature via API
    Given I am authenticated with role "Integration Manager" via API
    And contract "Automation Agreement" requires a system signature
    And pre-authorized credentials are configured for signing
    When I invoke the automated signature API for contract "Automation Agreement"
    Then a digital signature is applied using pre-authorized credentials
    And the contract status is updated
    And the signature event is logged with timestamp and actor identity

  Scenario: API enforces authentication
    Given I invoke the contract creation API without authentication
    Then the request is denied with an authorization error
    And the API returns HTTP 401 status

  Scenario: API enforces rate limits
    Given I am authenticated as "Integration Manager" via API
    When I exceed the configured rate limit for API calls
    Then the API returns HTTP 429 status
    And I receive error "Rate limit exceeded"

  Scenario: API validates action parameters
    Given I am authenticated as "Integration Manager" via API
    When I invoke the contract creation API with invalid payload
    Then the API returns HTTP 400 status
    And I receive validation error details

  Scenario: Tag contract via API
    Given I am authenticated as "Integration Manager" via API
    And contract "Service Agreement" exists
    When I invoke the tagging API to add tag "priority" to contract "Service Agreement"
    Then the tag is applied to the contract
    And the tagging action is logged

  Scenario: Retrieve contract via API
    Given I am authenticated as "Integration Manager" via API
    And contract "Service Agreement" is archived
    When I invoke the retrieval API for contract "Service Agreement"
    Then the API returns the archived contract
    And the retrieval is logged for traceability

  Scenario: Unauthorized role cannot access contract API
    Given I am authenticated as "Contract Observer" via API
    When I invoke the contract creation API with valid payload
    Then the request is denied with an authorization error
    And the API returns HTTP 403 status
