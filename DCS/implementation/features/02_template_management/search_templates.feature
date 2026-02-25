@UC-02-02
Feature: Search and Retrieve Contract Templates
  Users search and access existing contract templates
  filtered by role-based access rights.

  Scenario: Search templates by keyword
    Given I am authenticated with role "Template Reviewer"
    And templates exist in the system
    When I search for templates with keyword "NDA"
    Then the results are filtered by my access rights

  Scenario: Retrieve template details
    Given I am authenticated with role "Template Reviewer"
    When I retrieve template "Standard NDA"
    Then I see the template version and status
    And I see the template provenance
