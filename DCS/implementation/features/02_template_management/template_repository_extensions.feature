@UC-02-14
Feature: Template Repository Extensions
  Advanced repository features for interoperability, governance, and dependencies.

  Background:
    Given I am authenticated with role "Template Manager"
    And the template repository is operational

  Scenario: Maintain durable links with cryptographic checksums
    Given template "Standard NDA" has machine-readable and human-readable artefacts
    When I store the template artefacts
    Then durable links are maintained between sources and artefacts
    And cryptographic checksums are generated for integrity verification

  Scenario: Capture dependency model for templates and schemas
    Given templates "Base Contract" and "Amendment Schema" exist
    When I define dependency "Base Contract" requires "Amendment Schema"
    Then the dependency relation is captured
    And the model supports includes/extends/requires relations

  Scenario: Unified export of versioned templates with dependencies
    Given template "Master Agreement" has dependencies and artefacts
    When I export template "Master Agreement" version "1.0"
    Then a unified package is created
    And the package includes versioned template, dependencies, and artefacts
    And the package is suitable for external system consumption

  Scenario: Multi-party review workflow with assignments and comments
    Given template "Complex Agreement" requires multi-party review
    When I assign reviewers "Alice" and "Bob" with comments enabled
    Then the workflow supports defined states, assignments, and comments
    And administrative interfaces provide search, diff, and lifecycle controls

  Scenario: Provenance graph expansion
    Given template "Standard NDA" has contributors and approvals
    When I view provenance for template "Standard NDA"
    Then a graph relates contributors, approvals, artefact hashes, and upstream dependencies

  Scenario: Subscription mechanism for template changes
    Given I am authenticated with role "Template User"
    And I am subscribed to template "Standard NDA"
    When template "Standard NDA" is updated
    Then I receive notification of the change
    And the notification includes impact analysis across dependency trees

  Scenario: Adapters for non-RDF structures
    Given JSON Schema structure is required for template "API Contract"
    When I store the JSON Schema alongside RDF
    Then adapters permit side-by-side storage
    And CAT remains the canonical source