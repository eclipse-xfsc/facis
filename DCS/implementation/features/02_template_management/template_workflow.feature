@UC-02-10
Feature: Template Approval Workflow
  Templates progress through submission, review, and approval
  before becoming available for contract generation.

  Scenario: Submit template for review
    Given I am authenticated with role "Template Creator"
    And template "Standard NDA" is in "Draft" status
    When I submit template "Standard NDA" for review
    Then the template status is "Submitted"

  Scenario: Review and recommend template for approval
    Given I am authenticated with role "Template Reviewer"
    And template "Standard NDA" is in "Submitted" status
    When I review template "Standard NDA"
    And I recommend template "Standard NDA" for approval
    Then the template status is "Reviewed"

  Scenario: Approve reviewed template
    Given I am authenticated with role "Template Approver"
    And template "Standard NDA" is in "Reviewed" status
    When I approve template "Standard NDA"
    Then the template status is "Approved"
    And the template is available for contract generation

  Scenario: Reject template with reason
    Given I am authenticated with role "Template Approver"
    And template "Standard NDA" is in "Reviewed" status
    When I reject template "Standard NDA" with reason "Missing compliance clause"
    Then the template status is "Draft"
    And the rejection reason is recorded

  Scenario: Unauthorized role cannot approve template
    Given I am authenticated with role "Template Creator"
    And template "Standard NDA" is in "Reviewed" status
    When I attempt to approve template "Standard NDA"
    Then the request is denied with an authorization error

