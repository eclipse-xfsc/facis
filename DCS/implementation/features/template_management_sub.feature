# UC-02: Template Management - Sub Use Cases
Feature: Template Management - Detailed Sub Processes
  As a Template Manager
  I want to manage contract templates comprehensively
  So that templates are well-organized, versioned, and maintainable

  Background:
    Given the system has semantic validation configured with JSON-LD and SHACL
    And template provenance tracking is enabled

  # UC-02-01 – Create Contract Template
  Scenario: Create reusable contract template
    Given the user is logged in with role "Template Manager" or "Template Approver"
    When the user submits a request to create a new template with:
      | Field               | Value                    |
      | Template Name       | Standard NDA 2025        |
      | Description         | Non-Disclosure Agreement |
      | Category            | Legal - Confidentiality  |
      | Required Metadata   | Party Name, Effective Date|
    Then a template should be created with required metadata
    And the system should return a unique Template ID and version
    And the template should appear in search results
    And the creation action should be audit-logged with user and timestamp

  # UC-02-02 – Search & Retrieve Templates
  Scenario: Search and retrieve existing templates
    Given multiple templates exist in the system
    When a Template Reviewer searches templates with filters:
      | Filter      | Value          |
      | Keyword     | NDA            |
      | Category    | Legal          |
      | Status      | Approved       |
    Then search results should respect RBAC rules
    And opening a template should display:
      | Information        | Content           |
      | Current Version    | Latest version #  |
      | Provenance         | Creator/changes   |
      | Template Status    | Approved/Draft    |
    And access events should be logged

  # UC-02-03 – Generate Contract from Template
  Scenario: Generate contract from template
    Given an approved template "Standard NDA 2025" exists
    When a Template Approver provides required inputs to generate a contract instance
    Then the system should produce a draft contract with:
      | Property            | Value                 |
      | Linked Template ID  | Template reference    |
      | Machine-Readable    | Valid format rendering|
      | Human-Readable      | PDF/document view     |
    And both versions should render correctly
    And contract generation should be logged

  # UC-02-04 – Update Contract Template
  Scenario: Update contract template with versioning
    Given a template "Standard NDA 2025" version "1.0" exists
    When a Template Creator updates the contract template
    Then the system should create a new immutable version "1.1"
    And previous version should remain readable
    And the system should show:
      | Information | Value                    |
      | Diff        | Changes between versions |
      | Author      | Who made the change      |
      | Timestamp   | When changed             |
    And the change should be logged

  # UC-02-05 – Deprecate Contract Template
  Scenario: Deprecate contract template
    Given an active contract template "Old NDA Template"
    When a Template Reviewer deprecates the contract template
    Then the system should:
      | Action                        | Effect              |
      | Prevent New Generation        | No new contracts    |
      | Show Deprecation Banner       | UI displays status  |
      | Log Deprecation Event         | Audit trail entry   |
    And the timestamp and deprecating user should be recorded

  # UC-02-06 – Add Template Provenance
  Scenario: Add provenance to template
    Given a template is being created or updated
    And a user is logged in with role "Template Approver"
    When a Template Approver adds provenance fields
    Then the system should capture:
      | Field          | Content                |
      | Origin         | Creator and date       |
      | Contributors   | Who modified it        |
      | Identifiers    | Version and ID         |
      | Timestamps     | Creation and changes   |
    And provenance should be validated and recorded

  # UC-02-07 – Verify Template & Provenance
  Scenario: Verify template correctness and authenticity
    Given a template with provenance exists
    When a Template Manager verifies the template and its provenance
    Then the system should validate:
      | Check              | Description              |
      | Schema Validation  | JSON-LD/SHACL compliance |
      | Signature Check    | Digital signature valid  |
      | VC Validation      | Verifiable credential    |
    And success report should list all schema checks and validation results

  # UC-02-08 – Create & Maintain Semantic Schemas
  Scenario: Manage semantic schemas for templates
    Given a user is logged in with role "Template Manager"
    When the user creates or updates a schema
    Then the system should:
      | Action             | Result                 |
      | Create Schema      | New schema defined     |
      | Link to Templates  | Templates use schema   |
      | Validate Entries   | Conformity enforced    |
    And schema versioning and rollback should be supported

  # UC-02-09 – Template Management Dashboard
  Scenario: Monitor template lifecycle and usage
    Given a user is logged in with role "Template Manager"
    When the user opens the template management dashboard
    Then it should display:
      | Metric                 | Description              |
      | Per-Template Lifecycle | Creation to deprecation  |
      | Usage Metrics          | Contracts generated      |
      | Last Changes           | Recent modifications     |
      | Approval Status        | Current state            |
    And filtering and export capabilities should be available
    And access should be controlled by RBAC
