@UC-02-09
Feature: Template Management Dashboard
  Template Managers view template status, approvals,
  and usage metrics.

  Scenario: View dashboard with template metrics
    Given I am authenticated with role "Template Manager"
    When I open the template management dashboard
    Then I see template lifecycle status
    And I see usage metrics
    And I see recent modifications

  Scenario: Unauthorized role cannot access dashboard
    Given I am authenticated with role "Template Reviewer"
    When I attempt to open the template management dashboard
    Then the request is denied with an authorization error
