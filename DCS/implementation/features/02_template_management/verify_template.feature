@UC-02-07
Feature: Verify Template and Provenance
  Template Managers verify template correctness
  including metadata, semantics, and authenticity.

  Scenario: Verify template with valid provenance
    Given I am authenticated with role "Template Manager"
    And template "Standard NDA" has provenance metadata
    When I verify template "Standard NDA"
    Then the JSON-LD context is validated
    And the SHACL constraints are validated
    And the digital signatures are verified

  Scenario: Unauthorized role cannot verify template
    Given I am authenticated with role "Template Approver"
    And template "Standard NDA" has provenance metadata
    When I attempt to verify template "Standard NDA"
    Then the request is denied with an authorization error
