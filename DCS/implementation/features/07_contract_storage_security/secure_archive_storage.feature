@UC-07-01 @FR-CSA-01 @FR-CSA-08 @FR-CWE-20 @FR-CSA-05 @FR-CSA-06 @FR-CSA-26
Feature: Secure Contract Archive Storage
  Contract Managers store signed contracts in a tamper-proof archive
  with cryptographic sealing, hierarchical structure, and multi-party
  component management.

  Scenario: Store signed contract in secure archive
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Signed" status
    When I store contract "Service Agreement" in the secure archive
    Then the system validates the contract
    And the system timestamps the archive entry
    And the contract is sealed with tamper-proof cryptographic mechanisms
    And the contract is stored in long-term encrypted storage
    And an archive ID is returned

  Scenario: Archived contract includes signature metadata
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has completed signature workflow
    When I store contract "Service Agreement" in the secure archive
    Then the archive entry includes the finalized contract
    And the archive entry includes all signature data
    And the archive entry includes version history
    And the archive entry includes credential hashes

  Scenario: Tamper detection on archived contract
    Given contract "Service Agreement" is stored in the archive
    When I retrieve contract "Service Agreement" from the archive
    Then the system verifies cryptographic integrity
    And any unauthorized modifications are detected

  Scenario: Archived contracts are immutable and auditable
    Given contract "Service Agreement" is stored in the archive
    When I attempt to modify contract "Service Agreement" in the archive
    Then the modification is prohibited
    And the attempt is logged with full traceability

  Scenario: Store contracts in hierarchical structure
    Given I am authenticated with role "Contract Manager"
    And contract "Frame Agreement" exists as a parent contract
    And contract "Sub-Contract A" is linked to "Frame Agreement"
    When I store contract "Sub-Contract A" in the secure archive
    Then the contract is stored with hierarchical metadata
    And the relationship to "Frame Agreement" is preserved

  Scenario: Store machine-readable alongside human-readable versions
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has both JSON-LD and PDF versions
    When I store contract "Service Agreement" in the secure archive
    Then the machine-readable version is stored
    And the human-readable version is stored
    And the system validates synchronization between both formats

  Scenario: Archive multi-party contract with per-party sections
    Given I am authenticated with role "Contract Manager"
    And contract "Partnership Agreement" involves parties "Alpha Corp" and "Beta Inc"
    And each party has assigned sections in the contract
    When I store contract "Partnership Agreement" in the secure archive
    Then each party's sections are individually archived
    And sections are linked to the overall contract package

  Scenario: Automatic archival upon signature workflow completion
    Given contract "Service Agreement" requires all signatures
    When all required signatures are collected
    Then the system automatically stores the contract in the archive
    And document integrity is ensured
    And all verifiable metadata is preserved

  Scenario: Unauthorized role cannot store contracts in archive
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is in "Signed" status
    When I attempt to store contract "Service Agreement" in the secure archive
    Then the request is denied with an authorization error
