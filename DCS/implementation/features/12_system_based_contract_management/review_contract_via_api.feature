@UC-12-02 @FR-CWE-17 @FR-CWE-15
Feature: Review Contract via API
  System Contract Reviewers perform automated validation
  through API-based checks and rule evaluation.

  Scenario: Review contract via API for compliance
    Given a system service is authenticated via API
    And contract "Service Agreement" is in "Draft" status
    When the system sends a review request for contract "Service Agreement"
    Then the contract is validated against predefined rules
    And inconsistencies are flagged
    And a validation report is returned

  Scenario: API review triggers automated corrections
    Given a system service is authenticated via API
    And contract validation identifies issues
    When the system receives review results via API
    Then automated correction suggestions are provided
    And the contract can be updated via API

  Scenario: Review API with role-based access
    Given a system service without review permissions is authenticated via API
    When the system attempts contract review via API
    Then the request is denied with an authorization error