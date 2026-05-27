[← Validation & Acceptance Criteria](10_validation_acceptance_criteria.md) · [↑ Table of Contents](../README.md) · [Appendices →](12_appendices.md)

---

## 11. Requirements Traceability Matrix

|Req ID|Component|Interface/API|Test Case|
|---|---|---|---|
|FR-ACM-01|Asset Crawler + Mapper: Harvest Initiation|OAI-PMH, DCAT / Linked Data, arbitrary Query languages as supported by remote catalogues via HTTP endpoints|Initiate simple harvesting operation of remote catalogue(s).|
|FR-ACM-02|Asset Crawler: Harvest Scope|arbitrary Query languages as supported by remote catalogues via HTTP endpoints|Conduct several harvesting operations with varying definitions.|
|FR-ACM-03|Asset Crawler: Asset Lifecycle|–|Harvest remote catalogue and validate different lifecycle settings, namely (1) versioning and (2) deletion.|
|FR-ACM-04|Asset Crawler + Mapper: Asset Linking|–|Harvest remote catalogue and show the linking and lifecycle handling of original and transformed asset.|
|FR-ACM-05|Asset Crawler: Referenced Assets|URLs, DIDs|Retrieve a remote asset from a catalogue C₁ that contains links to another catalogue C₂.|
|FR-SR-01|Schema Registry: Schema Storing|–|Upload a remote schema to the Schema Registry and validate it is not accessible from local catalogue for internal purposes, such as validating assets.|
|FR-SR-02|Schema Registry: Mapping Strategy|–|Harvest a remote catalogue using different transformation strategies; details to be validated per strategy.|
|FR-SR-03|Schema Registry: Prompt Storage|–|Create a new AI prompt for a mapping between two schemas; basic lifecycle.| 
|FR-SR-04|Schema Registry: Prompt Templates|–|See FR-SR-05|
|FR-SR-05|Schema Registry: AI-Driven Transformation|–|Perform a harvesting operation on a remote catalogue using AI-driven transformation. Do this with varying LLM parameters.|
|FR-SR-06|Schema Registry: RDF Transformation Definition|–|See FR-SR-07|
|FR-SR-08|Schema Registry: Transformation Fallback|–|Showcase automatic fallback on deterministic RDF mapping, when AIdriven transformation is unsuccessful.|
|FR-SR-09|Schema Registry: Transformation Audit|CSV, JSON|Store the record of a mapping in an immutable way, then query and export it.|
|FR-SR-10|Schema Registry: Prompt Testing|–|Showcase UI that enables the testing of prompts.|
|FR-SR-11|Schema Registry: LLM Configuration|–|Create and store a LLM configuration in the Schema Registry.|
|FR-SR-12|Schema Registry: Multi Model Support|–|Perform a harvesting operation on a remote catalogue with multi-model provider support enabled.|
|FR-SR-13|Schema Registry: Batch Transformation|–|Change the prompt, transformation strategy or error correction and show that the already existing assets are transformed accordingly.|
|FR-CR-01|Catalogue Registry: Configure Catalogue|–|Perform a harvesting operation for each of the required communication protocols.|
|FR-CR-02|Catalogue Registry: Configure Types|URIs|Create and store a mapping of asset types from a remote to a local schema. Then perform a harvesting operations showcasing the correct mapping from remote to local assets.|
|FR-CR-03|Catalogue Registry: API Mapping|OpenAPI|Configure a mapping from an asset type to a API request and perform a harvesting operation utilizing this mapping.|
|FR-AC-01|Access Control: User Roles|–|Showcase the different User Roles by performing CRUD operations for the Asset Crawler, Schema Registry and Catalogue Registry. These should fail, if the user does not have the correct role.|
|FR-GI-01|General: Discoverable Catalogue|RFC 9279|Show that the local catalogue exposes its machine-readable API documentation in a discoverable way according to [RFC.9279].|

---

[← Validation & Acceptance Criteria](10_validation_acceptance_criteria.md) · [↑ Table of Contents](../README.md) · [Appendices →](12_appendices.md)

