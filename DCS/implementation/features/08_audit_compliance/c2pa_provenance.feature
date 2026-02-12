@UC-08 @DCS-OR-C2PA
Feature: C2PA Content & Lifecycle Credentials for PDF Contracts
  The system uses the C2PA (Coalition for Content Provenance and Authenticity) standard
  to record origin, edits, and lifecycle states of contract PDFs with tamper-evident
  Content Credentials supporting audit and compliance.

  Background:
    Given the DCS system is configured with C2PA manifest support
    And trusted issuer keys are anchored to the organization

  # DCS-OR-C2PA-001: Use of C2PA for Contract Provenance
  @DCS-OR-C2PA-001
  Scenario: Contract PDF includes valid C2PA manifest for provenance
    Given I am authenticated with role "Contract Manager"
    And contract "Service Agreement" has been signed
    When I retrieve the signed contract PDF for "Service Agreement"
    Then the PDF contains a valid C2PA manifest
    And the manifest records the contract origin
    And the manifest records all edits made to the contract

  @DCS-OR-C2PA-001
  Scenario: C2PA manifest is verifiable using standard tools
    Given I am authenticated with role "Auditor"
    And contract "Service Agreement" has a C2PA manifest
    When I validate the C2PA manifest using a verification tool
    Then the manifest passes validation
    And the provenance chain is intact

  # DCS-OR-C2PA-002: PDF Embedding and Incremental Updates
  @DCS-OR-C2PA-002
  Scenario: C2PA manifest is embedded in signed contract PDF
    Given I am authenticated with role "Contract Manager"
    And contract "Master Agreement" has been signed with legal signatures
    When the system embeds a C2PA manifest in the PDF
    Then the manifest is embedded within the PDF structure
    And the original legal signatures remain valid
    And the PDF passes signature verification

  @DCS-OR-C2PA-002
  Scenario: C2PA manifest supports remote linking
    Given I am authenticated with role "Contract Manager"
    And contract "Remote Manifest Agreement" has been signed
    When the system links a remote C2PA manifest to the PDF
    Then the PDF contains a reference to the remote manifest
    And the remote manifest is accessible via the link

  @DCS-OR-C2PA-002
  Scenario: Incremental PDF updates preserve existing signatures
    Given I am authenticated with role "Contract Manager"
    And contract "Amended Agreement" has existing legal signatures
    When the system appends a C2PA manifest update
    Then the update uses PDF incremental update mechanism
    And all existing signatures pass verification after the update

  # DCS-OR-C2PA-003: Contract Lifecycle Assertions
  @DCS-OR-C2PA-003
  Scenario Outline: C2PA manifest contains lifecycle state assertions
    Given I am authenticated with role "Contract Manager"
    And contract "Lifecycle Contract" has status "<status>"
    When I retrieve the C2PA manifest for contract "Lifecycle Contract"
    Then the manifest contains a lifecycle assertion with status "<status>"
    And the assertion includes contract_id
    And the assertion includes file_hash
    And the assertion includes reason
    And the assertion includes effective_at timestamp
    And the assertion includes authority
    And the assertion includes vc_id

    Examples:
      | status     |
      | draft      |
      | active     |
      | amended    |
      | suspended  |
      | terminated |
      | expired    |
      | replaced   |

  @DCS-OR-C2PA-003
  Scenario: C2PA manifest links to previous manifest for amended contracts
    Given I am authenticated with role "Contract Manager"
    And contract "Amended Contract" was previously active
    And contract "Amended Contract" has been amended
    When I retrieve the C2PA manifest for contract "Amended Contract"
    Then the manifest assertion includes prev_manifest_hash
    And the prev_manifest_hash matches the previous version's manifest

  # DCS-OR-C2PA-004: Verifiable Credential Binding
  @DCS-OR-C2PA-004
  Scenario: System issues W3C VC bound to contract status
    Given I am authenticated with role "Contract Manager"
    And contract "VC-Bound Agreement" has status "active"
    When the system issues a status VC for contract "VC-Bound Agreement"
    Then a W3C Verifiable Credential is issued
    And the VC binds to the contract_id
    And the VC binds to the file_hash
    And the VC includes status "active"
    And the VC includes reason and effective_at

  @DCS-OR-C2PA-004
  Scenario: C2PA manifest carries link to status VC
    Given I am authenticated with role "Auditor"
    And contract "VC-Linked Agreement" has an associated status VC
    When I retrieve the C2PA manifest for contract "VC-Linked Agreement"
    Then the manifest contains vc_id linking to the status VC
    And I can retrieve and verify the linked VC

  @DCS-OR-C2PA-004
  Scenario: C2PA manifest can embed VC copy
    Given I am authenticated with role "Contract Manager"
    And contract "Embedded VC Agreement" requires embedded credentials
    When the system embeds the status VC in the C2PA manifest
    Then the manifest contains a full copy of the VC
    And the embedded VC signature is valid

  # DCS-OR-C2PA-005: Status Publication and Revocation
  @DCS-OR-C2PA-005
  Scenario: Contract status is published to verifiable status list
    Given I am authenticated with role "Contract Manager"
    And contract "Published Agreement" has status "active"
    When the system publishes the contract status
    Then the status is published to Status List 2021
    And the status list entry is verifiable

  @DCS-OR-C2PA-005
  Scenario: Contract suspension is reflected in status list within 5 minutes
    Given I am authenticated with role "Contract Manager"
    And contract "Suspended Agreement" has status "active"
    When I suspend contract "Suspended Agreement"
    Then the status list is updated within 5 minutes
    And the status list reflects "suspended" status

  @DCS-OR-C2PA-005
  Scenario: Contract termination is reflected in status list in real time
    Given I am authenticated with role "Contract Manager"
    And contract "Terminated Agreement" has status "active"
    When I terminate contract "Terminated Agreement"
    Then the status list is updated in real time
    And the status list reflects "terminated" status

  # DCS-OR-C2PA-006: Verifier Behavior and UI
  @DCS-OR-C2PA-006
  Scenario Outline: Verifier displays correct status banner
    Given I am authenticated with role "Auditor"
    And contract "Status Banner Contract" has status "<status>"
    When I verify contract "Status Banner Contract" using the verifier
    Then the verifier checks PDF signatures
    And the verifier checks C2PA manifests
    And the verifier checks the VC signature
    And the verifier checks the status list
    And the verifier displays banner "<banner>"

    Examples:
      | status     | banner     |
      | draft      | Draft      |
      | active     | Active     |
      | suspended  | Suspended  |
      | terminated | Terminated |
      | replaced   | Replaced   |
      | expired    | Expired    |

  @DCS-OR-C2PA-006
  Scenario: Verifier shows clear error for invalid signatures
    Given I am authenticated with role "Auditor"
    And contract "Tampered Contract" has a broken signature
    When I verify contract "Tampered Contract" using the verifier
    Then the verifier displays an error banner
    And the error indicates signature validation failure

  # DCS-OR-C2PA-007: Trust Anchors and Delegation
  @DCS-OR-C2PA-007
  Scenario: Issuer keys are anchored to organization DID
    Given I am authenticated with role "System Administrator"
    When I inspect the C2PA issuer key configuration
    Then the issuer key is anchored to the organization DID
    And the DID contains LPID/eIDAS data

  @DCS-OR-C2PA-007
  Scenario: Status change delegation requires PoA credential
    Given I am authenticated with role "Contract Manager"
    And I hold a valid PoA credential for status changes
    When I change the status of contract "Delegated Agreement"
    Then my PoA credential is verified
    And the delegation chain is recorded in the manifest

  @DCS-OR-C2PA-007
  Scenario: Key rotation is supported
    Given I am authenticated with role "System Administrator"
    When I rotate the C2PA issuer key
    Then the new key is activated
    And the old key is marked for revocation
    And manifests signed with the new key are valid

  @DCS-OR-C2PA-007
  Scenario: Key revocation invalidates related manifests
    Given I am authenticated with role "System Administrator"
    And a C2PA issuer key has been compromised
    When I revoke the compromised key
    Then manifests signed with the revoked key show revocation warning
    And new manifests cannot be signed with the revoked key

  # DCS-OR-C2PA-008: Resilience to Metadata Stripping
  @DCS-OR-C2PA-008
  Scenario: Remote manifest exists for every contract
    Given I am authenticated with role "Contract Manager"
    And contract "Remote Backup Agreement" has a C2PA manifest
    When I query the remote manifest repository
    Then a remote manifest copy exists for contract "Remote Backup Agreement"

  @DCS-OR-C2PA-008
  Scenario: Verifier fetches remote manifest when embedded manifest is missing
    Given I am authenticated with role "Auditor"
    And contract "Stripped Manifest Contract" had its embedded manifest stripped
    When I verify contract "Stripped Manifest Contract" using the verifier
    Then the verifier fetches the remote manifest
    And the verification completes successfully using the remote manifest

  @DCS-OR-C2PA-008
  Scenario: Verification succeeds after embedded manifest stripping
    Given I am authenticated with role "Auditor"
    And I have a PDF copy of contract "Test Contract" with stripped metadata
    When I verify the stripped PDF using the verifier
    Then the verifier retrieves the remote manifest via contract identifier
    And the verification result is valid

  # DCS-OR-C2PA-009: Audit and Trusted Time
  @DCS-OR-C2PA-009
  Scenario: Lifecycle assertions are timestamped with RFC 3161
    Given I am authenticated with role "Contract Manager"
    And contract "Timestamped Agreement" has a lifecycle assertion
    When I retrieve the C2PA manifest for contract "Timestamped Agreement"
    Then the lifecycle assertion includes an RFC 3161 timestamp
    And the timestamp is from a trusted TSA

  @DCS-OR-C2PA-009
  Scenario: VC issuance events are timestamped
    Given I am authenticated with role "Auditor"
    And contract "Audited Agreement" has an associated status VC
    When I inspect the VC issuance record
    Then the issuance includes an RFC 3161 timestamp
    And the timestamp signature is valid

  @DCS-OR-C2PA-009
  Scenario: Audit log records all status changes
    Given I am authenticated with role "Auditor"
    And contract "Audit Trail Contract" has had multiple status changes
    When I retrieve the audit log for contract "Audit Trail Contract"
    Then the log contains entries for each status change
    And each entry includes who changed the status
    And each entry includes why the status was changed
    And the log is append-only and tamper-evident

  # DCS-OR-C2PA-010: Backward Compatibility with Legal Signatures
  @DCS-OR-C2PA-010
  Scenario: Adding C2PA manifest does not break legal signatures
    Given I am authenticated with role "Contract Manager"
    And contract "Legacy Signed Agreement" has valid legal signatures
    When the system adds a C2PA manifest to the PDF
    Then the legal signatures remain valid
    And the PDF passes signature validation before and after

  @DCS-OR-C2PA-010
  Scenario: Updating C2PA manifest preserves legal signatures
    Given I am authenticated with role "Contract Manager"
    And contract "Manifest Update Agreement" has legal signatures and a C2PA manifest
    When the system updates the C2PA manifest
    Then the legal signatures remain valid
    And the updated manifest is valid
    And the PDF passes both signature and C2PA validation

  @DCS-OR-C2PA-010
  Scenario: Verify backward compatibility across manifest versions
    Given I am authenticated with role "Auditor"
    And contract "Multi-Version Contract" has multiple C2PA manifest updates
    When I validate all versions of the contract PDF
    Then each version maintains valid legal signatures
    And each version has valid C2PA manifests
    And zero PDFs fail signature validation

