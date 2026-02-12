@UC-15-01 @FR-SM-20
Feature: Signature Revocation
  The system revokes signatures when credentials are invalidated
  or organizational policies require revocation.

  Scenario: Auditor revokes signature due to credential invalidation
    Given I am authenticated with role "Auditor"
    And contract "Service Agreement" has valid signatures
    And signer "Alice" credentials have been revoked in the status list
    When I revoke signature for signer "Alice" on contract "Service Agreement"
    Then the signature is marked as revoked
    And the contract status is updated to "Revoked"
    And the revocation event is logged with timestamp and reason

  Scenario: Compliance Officer revokes signature due to policy breach
    Given I am authenticated with role "Compliance Officer"
    And contract "Data Processing Agreement" has valid signatures
    And organizational policy requires revocation for signer "Bob"
    When I revoke signature for signer "Bob" on contract "Data Processing Agreement"
    Then the signature is marked as revoked
    And the contract status is updated to "Revoked"
    And the revocation event is logged with timestamp and reason

  Scenario: Revoked contract requires re-signing to restore validity
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is in "Revoked" status
    When I attempt to execute contract "Service Agreement"
    Then the request is denied
    And I receive error "Contract requires re-signing"

  Scenario: Re-sign revoked contract restores validity
    Given I am authenticated with role "Contract Signer"
    And contract "Service Agreement" is in "Revoked" status
    And signer has valid credentials
    When I re-sign contract "Service Agreement"
    Then the contract status is updated to "Active"
    And the re-signing event is logged

  Scenario: Revocation propagates to dependent systems immediately
    Given I am authenticated with role "Auditor"
    And contract "Master Agreement" has valid signatures
    And contract "Master Agreement" is deployed to target system "ERP Gateway"
    When I revoke signature for signer "Alice" on contract "Master Agreement"
    Then the revocation is propagated to "ERP Gateway"
    And the target system receives revocation notification

  Scenario: Access rights invalidated upon signature revocation
    Given I am authenticated with role "Compliance Officer"
    And contract "API Access Agreement" grants access rights to party "Acme Corp"
    And contract "API Access Agreement" has valid signatures
    When I revoke signature for signer "Alice" on contract "API Access Agreement"
    Then access rights for party "Acme Corp" are invalidated
    And the access revocation is logged

  Scenario: Unauthorized role cannot revoke signatures
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" has valid signatures
    When I attempt to revoke signature for signer "Alice" on contract "Service Agreement"
    Then the request is denied with an authorization error
    And the unauthorized attempt is logged

