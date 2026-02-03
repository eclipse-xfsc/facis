@UC-02-08
Feature: Create and Maintain Semantic Schemas
  Template Managers create and manage semantic schemas
  used for template validation.

  Scenario: Create a semantic schema
    Given I am authenticated with role "Template Manager"
    When I create a schema "contract-base-v1"
    Then the schema is available for template linking

  Scenario: Link schema to template
    Given I am authenticated with role "Template Manager"
    And schema "contract-base-v1" exists
    When I link schema "contract-base-v1" to template "Standard NDA"
    Then the template enforces schema conformity

  Scenario: Unauthorized role cannot create schema
    Given I am authenticated with role "Template Creator"
    When I attempt to create a schema "contract-base-v1"
    Then the request is denied with an authorization error
