@UC-07-02 @FR-CSA-02 @FR-PACM-04
Feature: Contract Permissions and Access Management
  Contract Managers configure access control rules for stored contracts.
  The system enforces role-based access and logs all access attempts.

  Scenario: Configure access permissions for stored contract
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is stored in the archive
    When I configure access permissions for contract "Service Agreement"
    Then the access control rules are updated
    And the change is logged with actor identity and timestamp
    And restrictions are immediately enforced

  Scenario: Grant role access to archived contract
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is stored in the archive
    When I grant role "Legal Officer" access to contract "Service Agreement"
    Then users with role "Legal Officer" can retrieve the contract
    And the permission grant is logged

  Scenario: Revoke role access to archived contract
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" is stored in the archive
    And role "External Reviewer" has access to contract "Service Agreement"
    When I revoke access for role "External Reviewer" to contract "Service Agreement"
    Then users with role "External Reviewer" can no longer retrieve the contract
    And the permission revocation is logged

  Scenario: Authorized role retrieves archived contract
    Given I am authenticated with role "Legal Officer"
    And contract "Service Agreement" is stored in the archive
    And role "Legal Officer" has access to contract "Service Agreement"
    When I retrieve contract "Service Agreement" from the archive
    Then the contract is returned
    And the access is logged

  Scenario: Unauthorized access attempt is denied and logged
    Given I am authenticated with role "Contract Observer"
    And contract "Confidential Agreement" is stored in the archive
    And role "Contract Observer" does not have access to contract "Confidential Agreement"
    When I attempt to retrieve contract "Confidential Agreement"
    Then the request is denied
    And the unauthorized access attempt is logged

  Scenario: Per-party access restrictions for multi-party contracts
    Given I am authenticated with role "Contract Manager"
    And contract "Partnership Agreement" has sections for "Alpha Corp" and "Beta Inc"
    When I configure per-party access for contract "Partnership Agreement"
    Then "Alpha Corp" users can only access their assigned sections
    And "Beta Inc" users can only access their assigned sections

  Scenario: Access to audit logs restricted by role
    Given I am authenticated with role "Auditor"
    When I access audit logs for contract "Service Agreement"
    Then the audit logs are returned
    And my access is logged with justification

  Scenario: Unauthorized role cannot access audit logs
    Given I am authenticated with role "Contract Observer"
    When I attempt to access audit logs for contract "Service Agreement"
    Then the request is denied
    And the unauthorized access attempt is blocked and logged

  Scenario: Unauthorized role cannot configure permissions
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is stored in the archive
    When I attempt to configure access permissions for contract "Service Agreement"
    Then the request is denied with an authorization error
