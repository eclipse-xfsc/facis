@UC-03-05 @FR-CWE-04
Feature: Machine-Readable and Human-Readable Contract Review
  Contract Creators, Contract Reviewers, and Contract Managers review
  contracts in both machine-readable and human-readable formats. The system
  ensures synchronization and highlights any inconsistencies.

  Scenario: View contract in machine-readable format
    Given I am authenticated with role "Contract Reviewer"
    And contract "Service Agreement" exists
    When I view contract "Service Agreement" in machine-readable format
    Then the JSON-LD or XML representation is displayed
    And the structure is valid

  Scenario: View contract in human-readable format
    Given I am authenticated with role "Contract Reviewer"
    And contract "Service Agreement" exists
    When I view contract "Service Agreement" in human-readable format
    Then the PDF or document view is displayed
    And the content is readable

  Scenario: Synchronized view of both formats
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" exists
    When I request synchronized view of contract "Service Agreement"
    Then both machine-readable and human-readable views are rendered
    And both formats are derived from the same source
    And both formats have matching content hashes

  Scenario: System highlights inconsistencies between formats
    Given I am authenticated with role "Contract Reviewer"
    And contract "Service Agreement" has a formatting error
    When I review both formats of contract "Service Agreement"
    Then the system highlights inconsistencies
    And the specific discrepancies are identified

  Scenario: Export both formats with same version tag
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" version "2.0" exists
    When I export contract "Service Agreement" in both formats
    Then the machine-readable export has version tag "2.0"
    And the human-readable export has version tag "2.0"
    And both exports are consistent

  Scenario: Validate machine-readable structure
    Given I am authenticated with role "Contract Reviewer"
    And contract "Service Agreement" has machine-readable representation
    When I validate the machine-readable structure
    Then the schema validation passes
    And required fields are present
    And data types are correct

  Scenario: Fix inconsistency and re-validate
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has a detected inconsistency
    When I fix the inconsistency
    And I re-validate contract "Service Agreement"
    Then no inconsistencies are highlighted
    And both formats are synchronized

  Scenario: Unauthorized role cannot access format review
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" exists
    When I attempt to access the synchronized view of contract "Service Agreement"
    Then the request is denied with an authorization error
