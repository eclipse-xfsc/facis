# UC-07: Storage & Archive - Sub Use Cases
Feature: Storage and Archive Management - Detailed Sub Processes
  As a Contract Manager
  I want to manage secure contract storage and access
  So that contracts are preserved and accessible for compliance

  # UC-07-01 – Store Contract in Secure Archive
  Scenario: Tamper-proof long-term contract storage
    Given a contract has been signed
    When a Contract Manager user stores the signed contract
    Then the system should:
      | Action              | Result                |
      | Seal Contract       | Immutable copy        |
      | Add Timestamp       | Archival time         |
      | Encrypt Content     | Security protection   |
      | Return Archive ID   | Reference identifier  |
    And retrieval should confirm integrity

  # UC-07-02 – Manage Contract Permissions & Access
  Scenario: Control RBAC for stored contracts
    Given contracts are stored in archive
    When a Contract Manager user modifies access and permission settings for a contract
    Then the system should:
      | Control            | Behavior              |
      | Change Policy      | Update access rules   |
      | Deny Unauthorized  | Block access          |
      | Permit Roles       | Allow access          |
      | Log Changes        | Audit trail entry     |
      | Log Access Attempts| Security tracking     |
    And the system should record the access changes in the audit log

  # UC-07-03 – Storage & Security Dashboard
  Scenario: Monitor archive status and integrity
    Given contracts are archived
    When a Archive Manager opens the contract archive dashboard
    Then the system should:
      | Metric              | Description          |
      | Coverage/Integrity  | Archive health       |
      | Alerts              | Any integrity issues |
      | Recent Access       | Access history       |
    And logs should be exportable for incident review
