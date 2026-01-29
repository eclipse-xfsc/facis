# UC-15: Access Rights Revocation - Sub Use Cases
Feature: Access Rights and Signature Revocation - Detailed Sub Processes
  As an Auditor or Compliance Officer
  I want the system to detect when signer credentials are revoked using the XFSC Revocation List
  So that affected contracts are marked revoked/non-compliant, revocation is logged, and related access rights are invalidated until re-signing

  # UC-15-01 – Revoke Access Rights & Signatures
  Scenario: System enforces revocation for a contract signed with revoked credentials
  Given a contract exists that was signed by a Contract Signer
  And the signer’s credentials are listed as revoked in the XFSC Revocation List
  When the system validates the signer’s credential status
  Then the system should:
    | Action             | Result           |
    | Detect Revocation  | Via status list  |
    | Mark State         | "revoked"        |
    | Withdraw Rights    | Immediate effect |
    | Create Audit Entry | Compliance log   |
    | Require Re-signing | If needed        |
  And affected contracts should be flagged if configured
