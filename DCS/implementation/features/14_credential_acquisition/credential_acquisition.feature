@UC-14-01 @FR-SM-03 @FR-SM-05
Feature: Identity and PoA Credential Acquisition
  The system retrieves and verifies identity and PoA credentials
  before authorizing contract signing or execution.

  Scenario: Contract Signer presents valid identity and PoA credentials
    Given I am authenticated with role "Contract Signer"
    And I hold a valid identity credential issued by a recognized authority
    And I hold a valid PoA credential for organization "Acme Corp"
    When I initiate signing for contract "Service Agreement"
    Then the system validates my identity credential
    And the system validates my PoA credential
    And signing is authorized

  Scenario: System acquires missing credentials from external source
    Given I am authenticated with role "Contract Signer"
    And I hold a valid identity credential issued by a recognized authority
    And I do not hold a PoA credential for organization "Acme Corp"
    When I initiate signing for contract "Service Agreement"
    Then the system queries trusted external sources for PoA credentials
    And the acquired credential is associated with my session
    And signing is authorized

  Scenario: Reject expired identity credential
    Given I am authenticated with role "Contract Signer"
    And I hold an expired identity credential
    When I initiate signing for contract "Service Agreement"
    Then the request is denied
    And I receive error "Credential invalid or access revoked."

  Scenario: Reject revoked PoA credential
    Given I am authenticated with role "Contract Signer"
    And I hold a valid identity credential issued by a recognized authority
    And I hold a revoked PoA credential for organization "Acme Corp"
    When I initiate signing for contract "Service Agreement"
    Then the request is denied
    And the rejection is logged with signer identity and timestamp

  Scenario: Credentials verified against W3C and eIDAS data models
    Given I am authenticated with role "Contract Signer"
    And I hold a verifiable credential compliant with W3C data model
    And I hold a PoA credential compliant with eIDAS framework
    When I initiate signing for contract "Data Processing Agreement"
    Then the system verifies the credential against W3C standards
    And the system verifies the credential against eIDAS standards
    And signing is authorized

  Scenario: System Contract Signer presents credentials via API
    Given I am authenticated with role "System Contract Signer"
    And the system holds pre-authorized identity credentials
    When I initiate signing for contract "Automated Supply Agreement" via API
    Then the system validates the pre-authorized credentials
    And signing is authorized

  Scenario: Unauthorized role cannot initiate credential-based signing
    Given I am authenticated with role "Contract Observer"
    When I attempt to initiate signing for contract "Service Agreement"
    Then the request is denied with an authorization error
