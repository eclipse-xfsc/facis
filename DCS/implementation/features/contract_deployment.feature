# UC-05: Contract Deployment
Feature: Contract Deployment
  As a Contract Manager
  I want to trigger contract deployments and monitor their status
  So that contracts are successfully deployed to target systems

  Scenario: Trigger contract deployment
    Given a contract "Acme NDA 2025" is in "Signed" status
    And a target system is configured for deployment
    When a Contract Manager submits the signed contract for deployment
    Then the system should:
      | Action                    | Details                               |
      | Trigger Deployment        | Outbound call is initiated            |
      | Generate Correlation ID   | Deployment correlation ID is created  |
      | Set Deployment Status     | Status is set to "In Progress"        |

  Scenario: Observe outbound deployment call
    Given a deployment is "In Progress" with a correlation ID
    When a Contract Manager observes the outbound deployment
    Then the system should:
      | Action                 | Details                               |
      | Show Correlation ID    | Correlation ID is visible             |
      | Payload                | Contract data                         |
      | Show Target System     | Target system is identified           |
      | Show Transfer State    | Sent/Pending/Acknowledged             |
      | Log Observation Event  | Observation is recorded for audit     |

  Scenario: Confirm deployment receipt
    Given a deployment is "In Progress" with a correlation ID
    When the target system acknowledges receipt
    Then the system should:
      | Action                    | Details                          |
      | Update Deployment Status  | Status is updated to "Deployed"  |
      | Record Correlation ID     | Correlation ID is stored         |
      | Archive Receipt           | Receipt/ack is archived          |
      | Store Completion Timestamp| Completion time is recorded      |
      | Log Receipt Confirmation  | Receipt confirmation is logged   |

  Scenario: Identify and query deployment failure
    Given a deployment attempt exists with a correlation ID
    When the target system does not confirm receipt
    Then the system should:
      | Action                 | Details                                 |
      | Set Deployment Status  | Status is updated to "Failed"           |
      | Retain Correlation ID  | Correlation ID remains available        |
      | Record Failure Reason  | Failure reason is recorded (if known)   |
      | Allow Status Query     | Failure can be retrieved by Contract ID |
      | Log Failure Event      | Failure is recorded for audit           |

  Scenario: View deployment status
    Given multiple contracts have been deployed
    When a Contract Manager checks deployment status
    Then all deployed contracts should show:
      | Field            | Value                 |
      | Contract ID      | Unique identifier     |
      | Status           | Deployed/Failed       |
      | Correlation ID   | Tracking identifier   |
      | Timestamp        | Deployment time       |

