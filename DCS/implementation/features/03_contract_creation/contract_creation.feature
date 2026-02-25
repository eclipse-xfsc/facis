@UC-03-01 @FR-CWE-13 @FR-CWE-03 @FR-CWE-30 @FR-CWE-07
Feature: Contract Creation
  Contract Creators generate contracts from predefined templates with
  auto-filled metadata. The system supports dynamic contract assembling
  from reusable clauses and contract package bundling.

  Scenario: Create contract from template
    Given I am authenticated with role "Contract Creator"
    And template "Service Agreement Template" is approved and available
    When I create a contract from template "Service Agreement Template"
    Then a draft contract is generated
    And the contract is assigned a unique contract ID
    And metadata is auto-filled including parties, jurisdiction, and applicable schemas
    And the creation is logged and traceable to the template version

  Scenario: Created contract renders in both machine-readable and human-readable views
    Given I am authenticated with role "Contract Creator"
    And I have created contract "Service Agreement" from a template
    When I view contract "Service Agreement"
    Then the machine-readable view renders correctly
    And the human-readable view renders correctly

  Scenario: Draft contract is editable and versioned
    Given I am authenticated with role "Contract Creator"
    And contract "Service Agreement" is in "Draft" status
    When I edit contract "Service Agreement"
    Then the changes are saved
    And a new version is created with timestamp and user attribution

  Scenario: Assemble contract from reusable clauses
    Given I am authenticated with role "Contract Creator"
    And reusable clauses "Payment Terms", "Liability", and "Confidentiality" exist
    When I assemble a contract using clauses "Payment Terms", "Liability", and "Confidentiality"
    Then the assembly process validates structure
    And the assembly process validates required metadata
    And the assembly process validates content logic
    And a draft contract is generated

  Scenario: Create contract with hierarchical structure
    Given I am authenticated with role "Contract Creator"
    And master agreement template "Framework Agreement" exists
    When I create a contract with sub-agreements and annexes
    Then the hierarchical structure is established
    And components are logically linked
    And components are version-controlled

  Scenario: Bundle multiple contracts into a package
    Given I am authenticated with role "Contract Manager"
    And contracts "Service Agreement" and "SLA Addendum" exist
    When I bundle contracts "Service Agreement" and "SLA Addendum" into package "Service Bundle"
    Then a contract package is created
    And the package maintains internal references
    And the package maintains shared metadata
    And the package tracks signature states

  Scenario: Auto-fill metadata from template
    Given I am authenticated with role "Contract Creator"
    And template "NDA Template" has predefined metadata fields
    When I create a contract from template "NDA Template"
    Then the contract inherits metadata from the template
    And I can override specific metadata values

  Scenario: Unauthorized role cannot create contracts
    Given I am authenticated with role "Contract Observer"
    When I attempt to create a contract from template "Service Agreement Template"
    Then the request is denied with an authorization error

  Scenario: Contract Creator can only create contracts for authorized parties
    Given I am authenticated with role "Contract Creator"
    And I am authorized to create contracts involving party "Acme Corp"
    When I create a contract from template "Service Agreement Template"
    And I specify party "Acme Corp" as a contract party
    Then the contract is created successfully
    And the contract is associated with party "Acme Corp"

  Scenario: Contract Creator cannot create contracts involving unauthorized parties
    Given I am authenticated with role "Contract Creator"
    And I am not authorized to create contracts with party "RestrictedVendor Inc"
    When I attempt to create a contract involving party "RestrictedVendor Inc"
    Then the request is denied with an "Not authorized to create contracts with this party" error
    And the contract creation is prevented
    And the attempt is logged

  Scenario: Created contract is accessible only to authorized parties
    Given I am authenticated with role "Contract Creator"
    And I have created contract "Service Agreement" with parties "Acme Corp" and "TechVendor Inc"
    When a representative of party "Acme Corp" attempts to access the contract
    Then the contract is accessible and visible
    And when a representative of unrelated party "UnrelatedCorp" attempts to access the contract
    Then the access is denied with a "Not authorized to access this contract" error

  Scenario: Unauthorized party cannot access created contract
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is created with parties "Acme Corp" and "TechVendor Inc"
    And I do not have authorization for either party
    When I attempt to access contract "Service Agreement"
    Then the request is denied with an "Access denied - unauthorized for contract parties" error
    And the access denial is logged with timestamp
