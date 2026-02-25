@UC-02-12
Feature: Hierarchical Contract Templates
  Template Managers define relationships between templates
  for frame agreements, sub-agreements, and addendums.

  Scenario: Create frame agreement template
    Given I am authenticated with role "Template Creator"
    When I create a template "Master Service Agreement" of type "Frame Agreement"
    Then the template is created in "Draft" status
    And the template type is "Frame Agreement"

  Scenario: Create sub-agreement linked to frame
    Given I am authenticated with role "Template Creator"
    And template "Master Service Agreement" exists
    And template "Master Service Agreement" is of type "Frame Agreement"
    When I create a template "Project SOW" of type "Sub Agreement"
    And I link template "Project SOW" to parent "Master Service Agreement"
    Then the template hierarchy is established
    And "Project SOW" inherits terms from "Master Service Agreement"

  Scenario: Create addendum template
    Given I am authenticated with role "Template Creator"
    And template "Standard NDA" exists
    When I create a template "NDA Amendment" of type "Addendum"
    And I link template "NDA Amendment" to parent "Standard NDA"
    Then the template hierarchy is established

  Scenario: Define structural dependency between templates
    Given I am authenticated with role "Template Manager"
    And template "Master Service Agreement" exists
    And template "Data Protection Annex" exists
    When I define dependency from "Master Service Agreement" to "Data Protection Annex"
    Then the dependency is recorded
    And contracts using "Master Service Agreement" require "Data Protection Annex"

  Scenario: Export hierarchical template structure
    Given I am authenticated with role "Template Manager"
    And template "Master Service Agreement" has linked components
    When I export template structure "Master Service Agreement"
    Then I receive a bundled format containing all linked templates

  Scenario: Validate structural dependencies
    Given I am authenticated with role "Template Manager"
    And template "Master Service Agreement" has dependencies defined
    When I validate template structure "Master Service Agreement"
    Then all dependencies are checked for consistency
    And invalid combinations are reported

