@UC-02-08 @FR-TR-03
Feature: Create and Maintain Semantic Schemas
  Template Managers create and manage semantic schemas
  used for template validation, including version control
  and schema lifecycle management.

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

  # FR-TR-03: Semantic Hub for Schema Storage with Versioning
  Scenario: Create versioned semantic schema
    Given I am authenticated with role "Template Manager"
    When I create schema "contract-base" version "1.0"
    Then the schema is created with version "1.0"
    And the schema version is tracked in the Semantic Hub
    And the schema is marked as the current version

  Scenario: Update schema with new version
    Given I am authenticated with role "Template Manager"
    And schema "contract-base" version "1.0" exists
    When I create schema "contract-base" version "2.0"
    Then the new version "2.0" is created
    And version "1.0" remains accessible
    And version "2.0" is marked as the current version

  Scenario: Access previous schema versions
    Given I am authenticated with role "Template Manager"
    And schema "contract-base" has versions "1.0", "1.1", and "2.0"
    When I retrieve schema "contract-base" version "1.1"
    Then I receive the schema content for version "1.1"
    And I can see the full version history

  Scenario: Template references specific schema version
    Given I am authenticated with role "Template Manager"
    And schema "contract-base" has versions "1.0" and "2.0"
    When I link schema "contract-base" version "1.0" to template "Legacy NDA"
    Then the template is validated against schema version "1.0"
    And upgrading the schema does not affect the template validation

  Scenario: Deprecate schema version
    Given I am authenticated with role "Template Manager"
    And schema "contract-base" version "1.0" is in use
    When I deprecate schema "contract-base" version "1.0"
    Then the schema version is marked as deprecated
    And templates using deprecated schema receive a warning
    And new templates cannot link to the deprecated version

  Scenario: Schema version compatibility check
    Given I am authenticated with role "Template Manager"
    And template "Standard NDA" uses schema "contract-base" version "1.0"
    When I check compatibility with schema "contract-base" version "2.0"
    Then the system analyzes schema differences
    And I receive a compatibility report with required changes

  Scenario: Migrate template to new schema version
    Given I am authenticated with role "Template Manager"
    And template "Standard NDA" uses schema "contract-base" version "1.0"
    And schema "contract-base" version "2.0" is backward compatible
    When I migrate template "Standard NDA" to schema version "2.0"
    Then the template is updated to reference version "2.0"
    And the migration is logged with old and new versions

  Scenario: Schema version history audit
    Given I am authenticated with role "Auditor"
    And schema "contract-base" has multiple versions
    When I retrieve the version history for schema "contract-base"
    Then I see all versions with creation timestamps
    And I see the author of each version
    And I see the change summary for each version
