# UC-03: Contract Creation & Approval - Sub Use Cases
Feature: Contract Creation and Approval - Detailed Sub Processes
  ## This feature covers the detailed sub-processes involved in contract creation, 
  ## review, approval, and preparation for signing.
  As a contract originator
  I want to manage contract creation and approval workflows
  So that contracts are properly negotiated, approved, and ready for signing

  # UC-03-01 – Create Contract
  Scenario: Create and receive contract ID
    Given a template "Standard NDA 2025" is available
    When Contract Creator submits a request to create a new contract from the template
    Then the system should:
      | Action                   | Result                |
      | Generate Contract ID     | Unique identifier     |
      | Create Draft Status      | Initial state         |
      | Both Renderings          | Machine & human views |
      | Audit Logging            | Track creation        |
    And the contract should be traceable to the template version

  # UC-03-02 – Negotiate Contract Terms
  Scenario: Collaborate on contract negotiation
    Given a contract is in "Draft" status
    When a Contract Manager or Contract Reviewer opens a draft contract to negotiate contract clauses
    Then the system should support:
      | Feature                | Description             |
      | Add Comments/Edits     | Suggest changes         |
      | Track Changes          | See modifications       |
      | Negotiation Log        | View discussion history |
      | Version History        | Maintain all versions   |
    And all changes should be logged with actor and timestamp

  # UC-03-03 – Adjust Contract Terms
  Scenario: Granular clause edits without regeneration
    Given a contract in "Draft" status exists
    When a Contract Manager or Contract Reviewer requests to adjust specific terms in the contract
    Then the system should:
      | Check                 | Result                |
      | Integrity Checks      | Validation passes     |
      | Targeted Updates      | Only sections change  |
      | Preserve Structure    | Format maintained     |
      | Audit Trail           | Updates recorded      |
    And the full contract should not need regeneration

  # UC-03-04 – Approve Contract
  Scenario: Route contract to required approvers
    Given a contract is ready for approval
    When a Contract Approver or Contract Manager initiates the approval process for a finalized contract
    Then the system should:
      | Action                    | Result              |
      | Record Approver States    | Pending approval    |
      | Record Approvals          | With timestamps     |
      | Lock Content              | Upon completion     |
      | Create Audit Entry        | Track approval      |
    And all required approvals must be recorded

  # UC-03-05 – Review Machine/Human Consistency
  Scenario: Validate machine and human readable consistency
    Given a contract has both renderings
    When a Contract Creator, Contract Reviewer, or Contract Manager performs consistency review
    Then the system should:
      | Check                | Result                |
      | Open Both Views      | Display renderings    |
      | Highlight Issues     | Show inconsistencies  |
      | Export Both          | With same version tag |
    And no inconsistencies should exist after fixes

  # UC-03-06 – Manage Contract Signing Process
  Scenario: Coordinate structured signing steps
    Given a contract is signable
    When a Contract Manager initiates the contract signing workflow
    Then the system should:
      | Feature              | Description              |
      | Configure Signers    | Who signs               |
      | Set Sequence         | Order of signing        |
      | Schedule Reminders   | Automated notifications |
      | Track Status         | Signing progress        |
    And changes to signing sequence should be logged

  # UC-03-07 – Contract Dashboard & Search
  Scenario: Track contract progress and search
    Given multiple contracts exist in the system
    When a Contract Manager or Contract Observer accesses the contract dashboard
    Then it should display:
      | Feature              | Description           |
      | Lifecycle States     | Current status        |
      | Full-Text Search     | Search contract text  |
      | Metadata Search      | Filter by fields      |
      | RBAC Enforcement     | Role-based visibility |
    And expected contracts should be returned in search results
