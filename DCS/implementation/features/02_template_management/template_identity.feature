@UC-02-13
Feature: Template Identity and Traceability
  Templates are assigned unique identifiers
  for traceability across contract workflows.

  Scenario: Template receives UUID on creation
    Given I am authenticated with role "Template Creator"
    When I create a template "Standard NDA" in category "Legal"
    Then the template is assigned a UUID
    And the UUID is unique across the system

  Scenario: Assign DID to template
    Given I am authenticated with role "Template Manager"
    And template "Standard NDA" exists
    When I assign a DID to template "Standard NDA"
    Then the template has a resolvable DID
    And the DID is linked to template metadata

  Scenario: Retrieve template by UUID
    Given I am authenticated with role "Template Reviewer"
    And template "Standard NDA" exists with UUID
    When I retrieve template by UUID
    Then I receive the correct template

  Scenario: Retrieve template by DID
    Given I am authenticated with role "Template Reviewer"
    And template "Standard NDA" has a DID assigned
    When I retrieve template by DID
    Then I receive the correct template
    And the DID resolution is verified

