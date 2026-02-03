@UC-02-06
Feature: Add Template Provenance Information
  Template Approvers add provenance metadata
  to ensure traceability.

  Scenario: Add provenance to template
    Given I am authenticated with role "Template Approver"
    And template "Standard NDA" exists
    When I add provenance metadata to template "Standard NDA"
    Then the template records origin, contributors, and timestamps

  Scenario: Unauthorized role cannot add provenance
    Given I am authenticated with role "Template Reviewer"
    And template "Standard NDA" exists
    When I attempt to add provenance metadata to template "Standard NDA"
    Then the request is denied with an authorization error
