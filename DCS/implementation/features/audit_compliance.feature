# UC-08: Audit & Compliance Report
Feature: Audit and Compliance Reporting
  As a compliance officer or auditor
  I want to request activity reports, run compliance audits, and verify regulatory compliance
  So that I can ensure all actions are logged, policy violations are identified, and regulatory standards are met

  Background:
    Given audit logging is enabled for all system operations
    And compliance policies are configured
    And audit retention is configured per regulations
    And tamper-proof audit trails are enabled

  Scenario: Generate activity report for contract lifecycle
    Given contract activity logs are available
    When an Auditor or Compliance Officer requests an activity report for a specified time range
    Then the system should:
      | Action                     | Details                                   |
      | Generate Activity Report   | Report is generated from activity logs    |
      | Include Audit Information  | Actors, timestamps, and actions included  |
      | Support Compliance Use     | Report supports component/party analysis  |
      | Export Results             | Report can be exported                    |

  Scenario: Run audit on policy compliance
    Given contract contents and lifecycle history are available
    When an Auditor or Compliance Officer initiates a policy compliance audit
    Then the system should:
      | Action                | Details                               |
      | Evaluate Compliance   | Contract is checked against policies  |
      | Produce Audit Result  | Compliance findings are produced      |
      | Flag Issues           | Compliance issues are identified      |
      | Generate Audit Summary| Compliance summary is generated       |

  Scenario: Export audit results
    Given a compliance audit has been completed
    When an Auditor or Compliance Officer exports the audit results
    Then the system should:
      | Action               | Details                                   |
      | Export Audit Results | Audit results are exported successfully   |
      | Include Audit Data   | Findings and evidence are included        |

  # DCS-FR-PACM-01
  Scenario: Maintain tamper-proof audit trail for contract lifecycle events
    Given contract lifecycle events are generated (e.g., creation, edits, approvals, signatures)
    When the system records an audit log entry for a lifecycle event
    Then each log entry should include:
      | Field                       | Content                         |
      | Timestamp                   | When the event occurred         |
      | Actor Identity              | Who performed the action        |
      | Action                      | What was performed              |
      | Affected Contract Component | Which contract/component        |
    And audit log entries should be immutable
    And audit logs should be exportable for forensic review
