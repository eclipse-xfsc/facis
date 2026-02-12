@UC-02-11
Feature: Delete Contract Template
  Template Managers delete deprecated templates
  that are no longer needed.

  Scenario: Delete deprecated template
    Given I am authenticated with role "Template Manager"
    And template "Old NDA" is in "Deprecated" status
    When I delete template "Old NDA"
    Then the template is removed from the system
    And the deletion is recorded in audit log

  Scenario: Cannot delete non-deprecated template
    Given I am authenticated with role "Template Manager"
    And template "Standard NDA" is in "Approved" status
    When I attempt to delete template "Standard NDA"
    Then the request is denied
    And I receive error "Only deprecated templates can be deleted"

  Scenario: Unauthorized role cannot delete template
    Given I am authenticated with role "Template Reviewer"
    And template "Old NDA" is in "Deprecated" status
    When I attempt to delete template "Old NDA"
    Then the request is denied with an authorization error

