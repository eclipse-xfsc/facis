@UC-15-01 @FR-SM-26
Feature: Revocation Compliance Viewer
  The compliance viewer displays signature revocation status
  and metadata for audit and compliance purposes.

  Scenario: View revoked signature status in compliance viewer
    Given I am authenticated with role "Compliance Officer"
    And contract "Service Agreement" has a revoked signature
    When I view signature compliance status for contract "Service Agreement"
    Then I see the revoked signature with signer identity
    And I see the revocation timestamp
    And I see the revocation reason

  Scenario: View signature credential chain for revoked signature
    Given I am authenticated with role "Auditor"
    And contract "Data Processing Agreement" has a revoked signature
    When I view signature compliance status for contract "Data Processing Agreement"
    Then I see the credential chain for the revoked signer
    And I see which credential in the chain was invalidated

  Scenario: Filter contracts by revocation status
    Given I am authenticated with role "Compliance Officer"
    And multiple contracts exist with different signature statuses
    When I filter contracts by signature status "Revoked"
    Then I see only contracts with revoked signatures

  Scenario: Generate revocation audit report
    Given I am authenticated with role "Auditor"
    And contracts have been revoked in the current period
    When I generate revocation audit report for period "2024-Q1"
    Then I receive a report listing all revocation events
    And the report includes signer identities and timestamps
    And the report includes revocation reasons

  Scenario: Unauthorized role cannot view revocation compliance details
    Given I am authenticated with role "Contract Creator"
    And contract "Service Agreement" has a revoked signature
    When I attempt to view signature compliance status for contract "Service Agreement"
    Then the request is denied with an authorization error

