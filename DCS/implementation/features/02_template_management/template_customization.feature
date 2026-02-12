@UC-02 @FR-TR-12
Feature: Template Customization with Dynamic Placeholders
  The template repository supports dynamic placeholders and automated
  population of contract terms based on predefined SLA rules, reducing
  manual input errors and enhancing efficiency.

  Background:
    Given I am authenticated with role "Template Manager"

  Scenario: Create template with dynamic placeholders
    Given I create a template "SLA Service Contract"
    When I define placeholder "{{service_level}}" with type "enum" and values "Gold, Silver, Bronze"
    And I define placeholder "{{response_time}}" with type "duration"
    And I define placeholder "{{uptime_guarantee}}" with type "percentage"
    Then the template contains 3 dynamic placeholders
    And each placeholder has defined validation rules

  Scenario: Define SLA rule for automated placeholder population
    Given template "SLA Service Contract" has placeholder "{{response_time}}"
    When I define SLA rule "Gold tier response time"
      | condition         | service_level equals "Gold" |
      | populate          | response_time               |
      | value             | 1 hour                      |
    Then the SLA rule is saved and linked to the template

  Scenario: SLA rules auto-populate placeholders during contract generation
    Given template "SLA Service Contract" has SLA rules configured
      | rule_name                  | condition                   | placeholder       | value       |
      | Gold tier response time    | service_level equals "Gold" | response_time     | 1 hour      |
      | Gold tier uptime           | service_level equals "Gold" | uptime_guarantee  | 99.9%       |
      | Silver tier response time  | service_level equals "Silver" | response_time   | 4 hours     |
      | Silver tier uptime         | service_level equals "Silver" | uptime_guarantee | 99.5%       |
    When I generate a contract with service_level "Gold"
    Then placeholder "{{response_time}}" is auto-populated with "1 hour"
    And placeholder "{{uptime_guarantee}}" is auto-populated with "99.9%"

  Scenario: Cascading SLA rules populate dependent placeholders
    Given template "Enterprise Agreement" has cascading SLA rules
    And placeholder "{{support_tier}}" affects "{{support_hours}}" and "{{escalation_time}}"
    When I generate a contract with support_tier "Premium"
    Then "{{support_hours}}" is auto-populated with "24/7"
    And "{{escalation_time}}" is auto-populated with "15 minutes"

  Scenario: Placeholder validation prevents invalid values
    Given template "SLA Service Contract" has placeholder "{{uptime_guarantee}}" with type "percentage"
    And the placeholder has validation rule "minimum: 90%, maximum: 100%"
    When I attempt to generate a contract with uptime_guarantee "85%"
    Then the generation fails with error "Value 85% is below minimum threshold 90%"

  Scenario: Dynamic placeholder supports conditional visibility
    Given template "Conditional Contract" has placeholder "{{penalty_clause}}"
    And the placeholder has visibility rule "show when uptime_guarantee > 99%"
    When I generate a contract with uptime_guarantee "99.5%"
    Then the penalty clause section is included in the contract
    When I generate a contract with uptime_guarantee "98%"
    Then the penalty clause section is excluded from the contract

  Scenario: Template preview shows placeholder resolution
    Given template "Preview Template" has multiple dynamic placeholders
    When I preview the template with sample data
      | placeholder        | value        |
      | service_level      | Gold         |
      | response_time      | 1 hour       |
      | uptime_guarantee   | 99.9%        |
    Then the preview renders with all placeholders resolved
    And the preview highlights which values came from SLA rules

  Scenario: Placeholder supports external data source integration
    Given template "External Data Template" has placeholder "{{customer_name}}"
    And the placeholder is linked to external data source "CRM System"
    When I generate a contract for customer ID "CUST-12345"
    Then the system queries the CRM for customer data
    And "{{customer_name}}" is auto-populated with the retrieved value

  Scenario: Audit trail records placeholder population source
    Given template "Auditable Template" has SLA rules configured
    When I generate contract "Audited Contract" with auto-populated values
    Then the contract metadata includes placeholder population audit trail
    And the audit trail shows each placeholder source (manual, SLA rule, or external)

  Scenario: Batch contract generation with dynamic placeholders
    Given template "Batch Contract Template" has placeholders for customer-specific data
    When I batch generate contracts for 10 customers
    Then each contract has placeholders populated based on customer-specific SLA rules
    And a generation report shows successful and failed populations

  Scenario: Unauthorized role cannot modify SLA rules
    Given I am authenticated with role "Contract Observer"
    When I attempt to modify SLA rules for template "SLA Service Contract"
    Then the request is denied with an authorization error

