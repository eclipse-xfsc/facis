# UC-03: Contract Creation & Approval
Feature: Contract Creation, Negotiation, and Approval
  This feature covers the detailed sub-processes involved in contract creation, review, approval, and preparation for signing.

  Background:
    Given version control is enabled for contracts
    And audit logging is enabled for all contract operations

  Scenario: Create contract from approved template
    Given an approved contract template exists
    When a user with role "Contract Creator" creates a new contract from the approved template
    Then the system should:
      | Action                | Details                                   |
      | Issue Contract ID     | A unique Contract ID is generated         |
      | Create Draft Contract | Contract is created in "Draft"            |
      | Preserve Template     | The approved template remains unchanged   |
      | Log Creation Event    | Contract creation is recorded for audit   |

  Scenario: Edit contract metadata without affecting template
    Given a contract "Acme NDA 2025" exists in "Draft" status
    And the contract is based on an approved template
    When a Contract Creator updates the contract metadata
    Then the system should:
      | Action                   | Details                                       |
      | Update Contract Metadata | Contract metadata is updated                  |
      | Preserve Template        | The template content remains unchanged        |
      | Record Provenance        | Change actor and timestamp are recorded       |
      | Record Immutable Hash    | Updated contract state hash is recorded       |
      | Log Modification Event   | The metadata change is recorded for audit     |

  Scenario: Route draft contract for approval
    Given a contract "Acme NDA 2025" exists in "Draft" status
    When a Contract Creator submits the contract for approval
    Then the system should:
      | Action                 | Details                                   |
      | Create Approval Request| Contract is routed into approval workflow |
      | Update Contract Status | Status is updated for approval processing |
      | Lock Contract Content  | Contract content is locked for approval   |
      | Log Routing Event      | Approval routing is recorded for audit    |
