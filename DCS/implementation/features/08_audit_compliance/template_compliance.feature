@UC-08 @FR-TR-07 @cross-cutting
Feature: Template Compliance Validation
  Compliance Officers validate templates against regulatory frameworks
  before they can be used in contract creation.

  Scenario: Validate template against regulatory framework
    Given I am authenticated with role "Compliance Officer"
    And template "Standard NDA" is in "Approved" status
    When I validate template "Standard NDA" against regulatory framework "eIDAS"
    Then the template compliance status is recorded
    And the validation timestamp is captured

  Scenario: Template passes compliance validation
    Given I am authenticated with role "Compliance Officer"
    And template "Data Processing Agreement" exists
    When I validate template "Data Processing Agreement" against regulatory framework "GDPR"
    Then the template is marked as "Compliant"
    And the template is available for contract generation

  Scenario: Template fails compliance validation
    Given I am authenticated with role "Compliance Officer"
    And template "Outdated Agreement" has missing required clauses
    When I validate template "Outdated Agreement" against regulatory framework "eIDAS"
    Then the template is marked as "Non-Compliant"
    And the non-compliance reasons are recorded
    And the template is blocked from contract generation

  Scenario: Template compliance required before contract creation
    Given I am authenticated with role "Contract Creator"
    And template "Unvalidated Template" has not been compliance validated
    When I attempt to generate a contract from template "Unvalidated Template"
    Then the request is denied
    And I receive error "Template requires compliance validation"

  Scenario: Re-validate template after update
    Given I am authenticated with role "Compliance Officer"
    And template "Standard NDA" was previously validated
    And template "Standard NDA" has been updated to a new version
    When I validate template "Standard NDA" against regulatory framework "eIDAS"
    Then the new version compliance status is recorded
    And previous validation records are preserved

  Scenario: View template compliance history
    Given I am authenticated with role "Compliance Officer"
    And template "Standard NDA" has compliance validation history
    When I view compliance history for template "Standard NDA"
    Then I see all validation events with timestamps
    And I see the applicable frameworks for each validation

  Scenario: Unauthorized role cannot validate template compliance
    Given I am authenticated with role "Template Approver"
    And template "Standard NDA" exists
    When I attempt to validate template "Standard NDA" against regulatory framework "eIDAS"
    Then the request is denied with an authorization error

