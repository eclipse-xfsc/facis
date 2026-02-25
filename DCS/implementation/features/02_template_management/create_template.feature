@UC-02-01
Feature: Create Contract Template
  Template Creators create reusable contract templates
  that serve as the basis for contract generation.

  Scenario: Create a new contract template
    Given I am authenticated with role "Template Creator"
    When I create a template "Standard NDA" in category "Legal"
    Then the template is created in "Draft" status
    And the template is assigned version "1.0"

  Scenario: Unauthorized role cannot create template
    Given I am authenticated with role "Template Reviewer"
    When I attempt to create a template
    Then the request is denied with an authorization error
