@UC-10-02 @FR-PACM-03
Feature: Pre-Execution Contract Validation
  Validators trigger compliance checks before contract deployment. The system
  reviews contract content, structure, and metadata for consistency with
  legal rules and internal policies.

  Scenario: Validator triggers compliance check before deployment
    Given I am authenticated with role "Validator"
    And contract "Service Agreement" is ready for deployment
    When I trigger a compliance check for contract "Service Agreement"
    Then the system reviews contract content
    And the system reviews contract structure
    And the system reviews contract metadata
    And a validation report is generated

  Scenario: Contract passes compliance validation
    Given I am authenticated with role "Validator"
    And contract "Service Agreement" complies with all regulatory frameworks
    And contract "Service Agreement" complies with internal policies
    When I trigger a compliance check for contract "Service Agreement"
    Then the validation report shows "Compliant"
    And the contract is cleared for deployment

  Scenario: Contract failing eIDAS compliance is blocked
    Given I am authenticated with role "Validator"
    And contract "High-Security Agreement" requires eIDAS compliance
    And contract "High-Security Agreement" has a signature not meeting eIDAS requirements
    When I trigger a compliance check for contract "High-Security Agreement"
    Then the validation report flags "eIDAS compliance violation"
    And the contract is blocked from deployment

  Scenario: Contract failing GDPR compliance is flagged for review
    Given I am authenticated with role "Validator"
    And contract "Data Processing Agreement" requires GDPR compliance
    And contract "Data Processing Agreement" is missing required data protection clauses
    When I trigger a compliance check for contract "Data Processing Agreement"
    Then the validation report flags "GDPR compliance violation"
    And the contract is flagged for manual review

  Scenario: Contract failing internal policy is blocked
    Given I am authenticated with role "Validator"
    And contract "Partner Agreement" is subject to internal approval policy
    And contract "Partner Agreement" is missing required approvals
    When I trigger a compliance check for contract "Partner Agreement"
    Then the validation report flags "Internal policy violation: missing approvals"
    And the contract is blocked from deployment

  Scenario: Validation report is stored with contract
    Given I am authenticated with role "Validator"
    And contract "Service Agreement" has completed compliance validation
    When I view validation history for contract "Service Agreement"
    Then I see the detailed validation report
    And the report includes compliance check results
    And the report includes timestamp and validator identity

  Scenario: Automated validation runs during contract workflow
    Given contract "Service Agreement" is in "Approved" status
    And automated compliance checks are configured
    When the contract workflow reaches the pre-deployment stage
    Then the system automatically performs compliance validation
    And the validation result is logged

  Scenario: Unauthorized role cannot trigger compliance validation
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is ready for deployment
    When I attempt to trigger a compliance check for contract "Service Agreement"
    Then the request is denied with an authorization error
