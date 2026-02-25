@UC-08-02
Feature: Contract Compliance Audit
  Auditors and Compliance Officers conduct compliance checks
  against legal and organizational frameworks.

  Scenario: Initiate compliance audit on contract
    Given I am authenticated with role "Auditor"
    And contract "Service Agreement" exists
    When I initiate compliance audit for contract "Service Agreement"
    Then the system evaluates contract against predefined compliance criteria
    And a compliance summary is generated

  Scenario: Compliance audit flags policy violations
    Given I am authenticated with role "Auditor"
    And contract "Incomplete Agreement" has missing approvals
    When I initiate compliance audit for contract "Incomplete Agreement"
    Then the audit flags "missing approvals" as a compliance issue
    And the issue is included in the compliance summary

  Scenario: Continuous compliance monitoring detects risks
    Given I am authenticated with role "Compliance Officer"
    And compliance monitoring is enabled for contract "Active Contract"
    When a compliance violation is detected
    Then a real-time alert is generated
    And the violation is flagged on the compliance dashboard

  Scenario: Detect expired credentials during audit
    Given I am authenticated with role "Compliance Officer"
    And contract "Signed Agreement" has a signer with expired credentials
    When I initiate compliance audit for contract "Signed Agreement"
    Then the audit flags "expired credentials" as a risk
    And remediation actions are recommended

  Scenario: Investigate non-compliance event
    Given I am authenticated with role "Compliance Officer"
    And contract "Disputed Contract" has flagged compliance issues
    When I investigate non-compliance for contract "Disputed Contract"
    Then I can view detailed event history
    And I can generate a case file for regulatory review

  Scenario: Generate non-compliance report
    Given I am authenticated with role "Compliance Officer"
    And contract "Flagged Contract" has non-compliance events
    When I generate non-compliance report for contract "Flagged Contract"
    Then the report includes incomplete workflows and late signatures
    And the report is exportable for external review

  Scenario: Unauthorized role cannot initiate compliance audit
    Given I am authenticated with role "Contract Reviewer"
    When I attempt to initiate compliance audit for contract "Service Agreement"
    Then the request is denied with an authorization error

