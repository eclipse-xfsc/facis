@UC-12-05 @FR-SM-25
Feature: Sign Contract via API
  System Contract Signers perform automated signing
  through API with verifiable credentials.

  Scenario: Sign contract via API
    Given a system service is authenticated via API
    And contract "Service Agreement" is in "Approved" status
    When the system initiates signature operation for contract "Service Agreement"
    Then a digital signature is generated
    And the signature is bound using verifiable credentials
    And the contract status is updated to "Signed"
    And the signing is logged with timestamp and actor identity

  Scenario: API signing with AI-driven logic
    Given a system service is authenticated via API
    And AI system determines signing conditions
    When the system submits signing request with AI data
    Then signing proceeds based on AI evaluation
    And the process is logged with timestamp and actor identity

  Scenario: Signing API with credential validation
    Given a system service provides invalid credentials
    When the system attempts signing via API
    Then the request is denied with an authorization error
    And the attempt is logged with timestamp and actor identity