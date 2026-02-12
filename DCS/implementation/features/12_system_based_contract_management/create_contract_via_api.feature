@UC-12-01 @FR-CWE-13 @FR-CWE-28
Feature: Create Contract via API
  System Contract Creators trigger automated contract generation
  through API integrations with external systems.

  Scenario: Create contract via API with template selection
    Given a system service is authenticated via API
    And template "Service Agreement Template" is available
    When the system sends a POST request to create contract with template "Service Agreement Template"
    Then a draft contract is generated
    And the contract is assigned a unique ID
    And metadata is populated from API payload
    And the creation is logged with timestamp and actor identity

  Scenario: API contract creation with data population
    Given a system service is authenticated via API
    And the service provides contract data in the request payload
    When the system submits contract creation request with populated fields
    Then the contract is created with provided data
    And validation ensures required fields are present
    And the contract status is set to "Draft"

  Scenario: Unauthorized API request denied
    Given a system service provides an invalid API key
    When the system attempts to create contract via API
    Then the request is denied with an authorization error
    And the attempt is logged with timestamp and actor identity