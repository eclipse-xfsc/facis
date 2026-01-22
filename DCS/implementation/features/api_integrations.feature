# UC-11: API & Integrations
Feature: API Integration and External Services
  As a Integration Manager
  I want to use APIs to manage contracts programmatically
  So that contract operations can be integrated into external systems

  Scenario: Create contract via API
    Given an approved contract template "temp-001" exists
    And the contract creation API is available
    When a POST request is made with:
      | Field           | Value              |
      | template_id     | temp-001           |
      | contract_name   | Acme NDA 2025      |
      | other_party     | Acme Corporation   |
      | start_date      | 2025-01-14         |
    Then the system should:
      | Action                 | Details                              |
      | Accept Request         | Contract creation request accepted   |
      | Return Contract ID     | A new Contract ID is returned        |
      | Create Contract Record | Contract is created with status "Draft" |

  Scenario: Sign contract via API
    Given a contract with ID "contract-001" exists in "Approved" status
    And the contract signing API is available
    When an API client submits a contract signing request for contract "contract-001"
    Then the system should:
      | Action                   | Details                              |
      | Accept Request           | Contract signing request accepted    |
      | Update Contract Status   | Contract status set to "Signed"      |
      | Store Signature Metadata | Signature information is recorded    |

  Scenario: Validate contract via API
    Given a contract with ID "contract-001" exists
    And the contract validation API is available
    When an API client submits a contract validation request for contract "contract-001"
    Then the system should:
      | Action                     | Details                              |
      | Accept Request             | Contract validation request accepted |
      | Perform Validation         | Contract validation is executed      |
      | Return Validation Result   | Validation outcome is returned       |

  Scenario: Inspect API responses
    Given the API client can call contract APIs to create, sign, and validate
    When the API client inspects responses from these API operations
    Then the system should:
      | Action                          | Details                                        |
      | Return Success Response         | API returns HTTP 2xx for successful calls      |
      | Return Validation Result        | Validation result is returned when requested   |
      | Provide Correlation Identifiers | Request/response correlation IDs are available |
      | Log API Request and Response    | Request/response logs include correlation IDs  |

  Scenario: Handle API validation errors
    Given an API client submits an invalid contract API request
    When the system performs request validation
    Then the system should:
      | Action               | Details                                  |
      | Reject Request       | Validation fails                         |
      | Return Error Result  | Validation error is returned             |
      | Log API Interaction  | Request and error response are logged with correlation ID |
