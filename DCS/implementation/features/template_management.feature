# UC-02: Template Management
Feature: Template Management and Lifecycle
  As a Template Manager
  I want to create, review, approve, version, and manage contract templates
  So that templates are properly validated, versioned, and ready for contract instantiation

  Background:
    Given template validation is enabled
    And template provenance tracking is enabled

  Scenario: View available approved contract templates
    Given approved contract templates are registered in the system
    When the Contract Manager views the template catalog
    Then the system shows a list of approved contract templates
    And each template displays its identifier and current status
    And the catalog access is recorded

  Scenario: Select an approved contract template for contract creation
    Given an approved contract template is available
    When the Contract Manager selects the template for contract creation
    Then the system makes the selected template available for downstream contract creation
    And the template selection is recorded

  Scenario: Approve template changes
    Given a contract template is in "Pending Review" status
    And the template is assigned for approval
    When the Contract Manager reviews the template
    And approves the template
    Then the template status changes to "Approved"
    And the approved template becomes available for contract creation
    And the status transition is recorded for audit

