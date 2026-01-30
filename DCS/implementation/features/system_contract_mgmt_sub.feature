# UC-12: System-Based Contract Management - Sub Use Cases
Feature: API-Based Contract Lifecycle - Detailed Sub Processes
  ## This feature covers system-initiated contract lifecycle operations via API,
  ## including automated creation, review, approval, lifecycle management, and signing.
  As an integration manager
  I want to manage contract lifecycle through system APIs
  So that contracts can be created, reviewed, approved, and signed automatically

  # UC-12-01 – Create Contract via API
  Scenario: Automated contract creation through system integration
    Given the API endpoint for contract creation is available
    When a System Contract Creator invokes the contract creation API
    Then the system should:
      | Action              | Result                |
      | Post Create Call    | Trigger creation      |
      | Return ID & Status  | Response with details |
      | Pull from System    | Fetch integrated data |
      | Record Requester    | Audit log entry       |
    And the contract should be created with audit trail

  # UC-12-02 – Review Contract via API
  Scenario: System-driven validation checks
    Given a contract exists and is available for review
    When a System Contract Reviewer initiates a contract review via API
    Then the system should:
      | Check              | Result                |
      | Validate Rules     | Run compliance tests  |
      | List Issues        | Violations reported   |
      | Fail Prevention     | Cannot proceed        |
    And response should list all validation issues

  # UC-12-03 – Approve Contract via API
  Scenario: Automated approvals via API
    Given a contract passes validation
    When a System Contract Approver service submits an approval request
    Then the system should:
      | Action              | Result                |
      | Require AuthN/AuthZ | Verify caller         |
      | Mark Approved       | Update status         |
      | Log Approver        | Record identity       |
      | Audit Change        | Compliance logging    |
    And approver identity should be logged

  # UC-12-04 – Manage Contracts via API
  Scenario: Query and update contract lifecycle
    Given a contract is under lifecycle management
    When a System Contract Manager component requests access to manage the contract’s lifecycle
    Then the system should:
      | Operation           | Description          |
      | List Contracts      | Query all            |
      | Update Metadata     | Modify fields        |
      | Read History        | Access audit trail   |
      | Enforce RBAC        | Role-based access    |
      | Version Changes     | Track modifications  |
    And the system should record the lifecycle changes in the audit log

  # UC-12-05 – Sign Contract via API
  Scenario: Automated/AI-driven signing via API
    Given a contract is ready for signing
    When a System Contract Signer initiates a signature operation via API
    Then the system should:
      | Action              | Result                |
      | Produce Artifact    | Valid signature file  |
      | Bind VC/PoA         | Link credentials      |
      | Update Status       | Mark as signed        |
      | Verify Signature    | Validation successful |
    And signature should be valid and verifiable
