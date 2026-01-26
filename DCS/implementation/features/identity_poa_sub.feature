# UC-14: Identity & Proof of Authority - Sub Use Cases
Feature: Identity and Authorization Management - Detailed Sub Processes
  ## This feature ensures required identity and proof-of-authority credentials
  ## are retrieved and verified before contract signing or execution.
  As a security officer
  I want to manage identity credentials and proof of authority
  So that only authorized signers can execute contracts

  # UC-14-01 – Retrieve Identity & PoA Credentials
  Scenario: Credential verification and session binding
    Given a Contract Signatory or System Signatory is authenticated for signing a contract
    And required identity and PoA credentials are not yet bound to the user session
    When the signer initiates the signing process for a contract
    Then the system should:
      | Action                    | Result              |
      | Missing Credentials       | Trigger retrieval   |
      | Verify Chain              | Certificate valid   |
      | Check Status              | Not revoked         |
      | Grant Authorization       | On success          |
      | Block on Failure          | Deny with reason    |
    And all events should be logged for audit
