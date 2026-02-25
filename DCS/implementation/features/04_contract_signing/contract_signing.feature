@UC-04-01 @FR-CWE-19 @FR-CWE-26 @FR-SM-13 @FR-SM-16 @FR-SM-07 @FR-SM-14
Feature: Contract Signing
  Contract Signers review contracts in a secure viewer and apply
  legally binding digital signatures with identity and PoA credentials.

  Scenario: Sign contract in secure viewer
    Given I am authenticated with role "Contract Signer"
    And contract "Service Agreement" is in "Approved" status
    When I open contract "Service Agreement" in the secure viewer
    And I apply my digital signature to contract "Service Agreement"
    Then a signed artifact is produced
    And the contract status is updated to "Signed"
    And the signing action is logged with timestamp and signer ID

  Scenario: Signature includes identity and PoA credentials
    Given I am authenticated with role "Contract Signer"
    And I hold a valid identity credential issued by a recognized authority
    And I hold a valid PoA credential for organization "Acme Corp"
    When I apply my digital signature to contract "Service Agreement"
    Then the signature binds my identity credential
    And the signature binds my PoA credential

  Scenario: Signing interface supports wallet integration
    Given I am authenticated with role "Contract Signer"
    And I have a configured digital wallet
    And contract "Service Agreement" is in "Approved" status
    When I open the signing interface for contract "Service Agreement"
    Then the interface integrates with my wallet for signature operations
    And the interface displays my pending signer tasks

  Scenario: Signature workflow enforces signing order
    Given I am authenticated with role "Contract Manager"
    And contract "Multi-Party Agreement" requires sequential signatures
    And signer "Alice" must sign before signer "Bob"
    When signer "Bob" attempts to sign before signer "Alice"
    Then the request is denied
    And I receive error "Signing order dependency not met"

  Scenario: Signature workflow enforces deadlines
    Given I am authenticated with role "Contract Signer"
    And contract "Time-Bound Agreement" has a signing deadline that has passed
    When I attempt to apply my digital signature to contract "Time-Bound Agreement"
    Then the request is denied
    And I receive error "Signing deadline has expired"

  Scenario: Multi-signer contract tracks completion in real time
    Given I am authenticated with role "Contract Manager"
    And contract "Partnership Agreement" requires signatures from 3 parties
    And 2 of 3 signatures have been collected
    When I view signing status for contract "Partnership Agreement"
    Then I see 2 signatures completed and 1 pending
    And I see timestamps for each completed signature

  Scenario: Digital signature applied via signing service
    Given I am authenticated with role "Contract Signer"
    And contract "Service Agreement" is in "Approved" status
    When I apply my digital signature via the signing service
    Then the system ensures secure key usage
    And signature integrity is validated upon signing

  Scenario: Cannot sign unapproved contract
    Given I am authenticated with role "Contract Signer"
    And contract "Draft Agreement" is in "Draft" status
    When I attempt to apply my digital signature to contract "Draft Agreement"
    Then the request is denied
    And I receive error "Contract must be approved before signing"

  Scenario: Unauthorized role cannot sign contracts
    Given I am authenticated with role "Contract Observer"
    And contract "Service Agreement" is in "Approved" status
    When I attempt to apply my digital signature to contract "Service Agreement"
    Then the request is denied with an authorization error

  # FR-SM-02: Support for PAdES, JAdES, and CAdES Signatures
  Scenario: Select PAdES signature format for PDF contract
    Given I am authenticated with role "Contract Signer"
    And contract "PDF Agreement" is in "Approved" status
    And contract "PDF Agreement" is in PDF format
    When I select signature format "PAdES"
    And I apply my digital signature to contract "PDF Agreement"
    Then the signature is applied in PAdES format
    And the signed PDF is legally recognized

  Scenario: Select JAdES signature format for JSON contract
    Given I am authenticated with role "Contract Signer"
    And contract "JSON API Agreement" is in "Approved" status
    And contract "JSON API Agreement" is in JSON format
    When I select signature format "JAdES"
    And I apply my digital signature to contract "JSON API Agreement"
    Then the signature is applied in JAdES format
    And the signed JSON is interoperable across systems

  Scenario: Select CAdES signature format for CMS structure
    Given I am authenticated with role "Contract Signer"
    And contract "CMS Structured Agreement" is in "Approved" status
    And contract "CMS Structured Agreement" uses CMS structure
    When I select signature format "CAdES"
    And I apply my digital signature to contract "CMS Structured Agreement"
    Then the signature is applied in CAdES format
    And the signed CMS structure is compliant

  Scenario: System suggests appropriate signature format based on document type
    Given I am authenticated with role "Contract Signer"
    And contract "Auto-Format Agreement" is in "Approved" status
    When I open the signing interface for contract "Auto-Format Agreement"
    Then the system suggests the appropriate signature format
    And I can override the suggestion if needed

  # FR-SM-01: Signature Level Selection (SES/AES/QES)
  Scenario: Select Simple Electronic Signature (SES) level
    Given I am authenticated with role "Contract Signer"
    And contract "Low-Risk Agreement" is in "Approved" status
    And contract "Low-Risk Agreement" permits SES signatures
    When I select signature level "SES"
    And I apply my digital signature
    Then a Simple Electronic Signature is applied
    And the signature level is recorded in the contract metadata

  Scenario: Select Advanced Electronic Signature (AES) level
    Given I am authenticated with role "Contract Signer"
    And contract "Standard Agreement" is in "Approved" status
    And contract "Standard Agreement" requires at least AES
    When I select signature level "AES"
    And I apply my digital signature with identity verification
    Then an Advanced Electronic Signature is applied
    And the signer identity is uniquely linked to the signature

  Scenario: Select Qualified Electronic Signature (QES) level
    Given I am authenticated with role "Contract Signer"
    And contract "High-Value Agreement" is in "Approved" status
    And contract "High-Value Agreement" requires QES
    When I select signature level "QES"
    And I apply my digital signature using a qualified signature creation device
    Then a Qualified Electronic Signature is applied
    And the signature has legal equivalence to a handwritten signature

  Scenario: Contract requirements enforce minimum signature level
    Given I am authenticated with role "Contract Signer"
    And contract "Regulated Agreement" requires minimum signature level "QES"
    When I attempt to sign with signature level "AES"
    Then the request is denied
    And I receive error "Contract requires Qualified Electronic Signature (QES)"

  # FR-SM-27: PDF/A Format Export
  Scenario: Export signed contract in PDF/A format
    Given I am authenticated with role "Contract Manager"
    And contract "Archive Ready Agreement" has been signed
    When I export contract "Archive Ready Agreement" in PDF/A format
    Then I receive a PDF/A compliant document
    And the PDF/A includes embedded metadata
    And the PDF/A includes signature containers

  Scenario: PDF/A export meets long-term archival requirements
    Given I am authenticated with role "Archive Manager"
    And contract "Long-Term Agreement" has been signed
    When I export contract "Long-Term Agreement" in PDF/A-3 format
    Then the exported PDF meets ISO 19005-3 requirements
    And the PDF is suitable for regulatory archival

  Scenario: PDF/A export includes all contract attachments
    Given I am authenticated with role "Contract Manager"
    And contract "Bundled Agreement" has attachments
    When I export contract "Bundled Agreement" in PDF/A format
    Then the PDF/A includes all attachments as embedded files
    And each attachment maintains its original format integrity

  # FR-SM-08: Persisted Contract Signing Summary
  Scenario: Signing summary is persisted with VC embedding
    Given I am authenticated with role "Contract Signer"
    And contract "Summary Agreement" has been signed by all parties
    When the system generates the signing summary
    Then the summary includes all signer credentials as VCs
    And the VCs are embedded in the contract record

  Scenario: Signing summary is embedded in PDF/A-3 document
    Given I am authenticated with role "Contract Manager"
    And contract "Embedded Summary Agreement" has a signing summary
    When I export the contract in PDF/A-3 format
    Then the signing summary is embedded in the PDF
    And the embedded summary is machine-readable

  Scenario: Signer with correct role can retrieve and sign designated contract
    Given I am authenticated with role "Contract Signer"
    And I am designated as a signatory for contract "Service Agreement"
    And contract "Service Agreement" is in "Approved" status
    When I retrieve contract "Service Agreement" for signing
    Then the contract is accessible in the secure viewer
    And I can apply my digital signature to the contract
    And the retrieval and signing action is logged

  Scenario: Signer not designated for contract cannot retrieve it
    Given I am authenticated with role "Contract Signer"
    And I am not designated as a signatory for contract "Service Agreement"
    When I attempt to retrieve contract "Service Agreement"
    Then the request is denied with a "Not a designated signatory for this contract" error
    And the access denial is logged

  Scenario: Contract enforces distinct role for each signatory
    Given I am authenticated with role "Contract Manager"
    And contract "Multi-Party Agreement" is in "Approved" status
    And contract "Multi-Party Agreement" requires "Procurement Officer" at position 1
    And contract "Multi-Party Agreement" requires "Finance Director" at position 2
    When I view the signing requirements for contract "Multi-Party Agreement"
    Then the required role for position 1 is "Procurement Officer"
    And the required role for position 2 is "Finance Director"
    And signing order is enforced with credential verification

  Scenario: Signatory cannot sign contract if role credentials do not match
    Given I am authenticated with role "Contract Signer"
    And I hold a PoA credential from "Authority X"
    And I am designated as a signatory for contract "Restricted Agreement"
    And contract "Restricted Agreement" requires PoA credential from "Authority Y"
    When I attempt to sign contract "Restricted Agreement"
    Then the request is denied with a "Credential issuer does not match contract requirement" error
    And the credential mismatch is logged
    And the contract remains unsigned

