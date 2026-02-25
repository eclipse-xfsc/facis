@UC-02-03
Feature: Generate Contract from Template
  Template Approvers generate contract instances
  by populating approved templates with data.

  Scenario: Generate contract from approved template
    Given I am authenticated with role "Template Approver"
    And template "Standard NDA" is in "Approved" status
    When I generate a contract from template "Standard NDA"
    Then a contract is created linked to the template
    And both machine-readable and human-readable versions are available

  Scenario: Unauthorized role cannot generate contract
    Given I am authenticated with role "Template Creator"
    And template "Standard NDA" is in "Approved" status
    When I attempt to generate a contract from template "Standard NDA"
    Then the request is denied with an authorization error
