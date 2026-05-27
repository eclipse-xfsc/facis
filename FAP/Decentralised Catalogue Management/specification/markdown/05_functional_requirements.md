[← Conceptual Architecture](04_conceptual_architecture.md) · [↑ Table of Contents](../README.md) · [Technical Architecture →](06_technical_architecture.md)

---

## 5. Functional Requirements

### 5.1 Asset Crawler + Mapper

#### FR-ACM-01 Initiating a Harvest

*Priority:* MUST HAVE  
*Description:*   
There MUST be a dedicated endpoint via which an authorized user can initiate the harvest of one or more remote catalogues with the following arguments:  
- a reference to one, or more, or all remote catalogues, as registered in the Catalogue Registry according to FR-CR-01,  
- a harvest scope, specified as a one-off argument or as a reference to a pre-configured harvest scope according to FR-ACM-02,
- whether schema mapping is to be performed.


Errors that prevent the harvest from being executed MUST be logged; these include

- the remote catalogue not being available, or
- the remote catalogue not being able to interpret the harvest scope, e.g., not being able to interpret the given query.


Each harvested asset MUST be imported into the local catalogue, jointly with the following provenance metadata:

- The unique identifier of the asset in the remote catalogue, if available
- A reference to a metadata record about the harvest, including

    -  The unique identifier of the remote catalogue in the Catalogue Registry
    -  The date and time of the harvest
    -  The scope of the harvest according to FR-ACM-02.


If schema mapping is to be performed, the transformation configured in the Catalogue Registry for the respective remote catalogue MUST be applied to each harvested asset as specified in FR-SR-05 for the AI-driven transformation, in FR-SR-07 for the deterministic RDF mapping, or in FR-SR-08 for the hybrid strategy. The result of a successful mapping MUST be stored as an asset linked to the originally imported asset according to FR-ACM-04; errors encountered during the mapping MUST be logged. The audit trail of the transformation (cf. FR-SR-09) MUST be stored as additional provenance metadata.

*Acceptance criteria:*
1. Set up a Catalogue Registry with 2 remote catalogues C₁ and C₂.
2. Execute the harvesting of
    - a. C₁,
    - b. C₁ and C₂, and, after having updated assets in both C₁ and C₂,
    - c. all of the stored remote catalogues (i.e., here, once more C₁ and C₂).
3. After each of (2a.), (2b.) and (2c.), query the local catalogue showing that the harvested assets are now stored in the local catalogue and that their metadata contain all the provenance information defined in this requirement.


*Notes:*

- The user MAY schedule recurring harvests by external mechanisms such as cron, which invoke the endpoint in defined intervals.
- After initiation, a harvest will run unattended, not expecting the user to intervene. Instead, the user MAY study the log and provenance metadata resulting from a requested harvest.
- It may be beyond the control of the Asset Crawler or Mapper whether, in the local catalogue, an imported asset may use the same identifier that it had in the remote catalogue. Especially for the case where this is not possible, we record that identifier separately.
- Schema mapping is not part of the acceptance criterion of this FR, as its correct implementation is validated by the acceptance criteria for the respective FRs for the Schema Registry.


#### FR-ACM-02 Harvest Scope

*Priority:* MUST HAVE  
*Description:* The user MUST be able to specify what should be harvested from a remote catalogue:
1. All assets of the given remote catalogue
2. All assets of a given type, as specified in FR-CR-02
3. As a generalization of (2.), if supported by the remote catalogue, only those assets that match a given query
4. All assets that have changed since a given date and time
5. All assets that have ever been imported from the given remote catalogue
6. All assets that were imported from the given remote catalogue in the last harvest (according to FR-ACM-01)
7. For (5.) and (6.), the variation MUST be supported to additionally include any new assets in the remote catalogue, as in (4.)
8. All assets in the scope of the last harvest (including, e.g., beyond (6.), new assets of the type specified according to (2.)).


*Acceptance criteria:*
1. Set up one remote catalogue, which is capable of being harvested in all ways defined in this requirement, and which contains two assets A₁ and A₂ with last change dates 2025-02-15 and 2025-05-28.
2. Harvest the remote catalogue once in ways (1.), (2.), (3.), and (4.) defined above, specifying the date 2025-03-29.
3. In the remote catalogue, update asset A₂ and create a third asset A₃, having the same type as A₁.
4. Harvest the remote catalogue once more in ways (5.), (6.), and (7.) defined above.
5. After each harvest specified in acceptance criteria steps (2.) and (4.), show that the assets stored in the local catalogue match the given harvesting parameters, then revert the catalogue to the state before that harvest.


#### FR-ACM-03 Lifecycle of Imported Assets

*Priority:* MUST HAVE  
*Description:* Upon initiating a harvest, the user MUST be able to define how the lifecycle of remote assets should be reflected locally, i.e.:

- Whether a new version of a remote asset should be realized as a new version of the corresponding local asset, if it exists, or whether a separate local asset should be created,
- Whether the deletion of a remote asset should result in the deletion of the local asset, or whether the local copy should be retained.


*Acceptance criteria:*
1. Set up a remote catalogue with one asset. Harvest that asset.
2. Update the asset in the remote catalogue. Then, execute two harvesting processes with different settings of the remote asset lifecycle parameter:

    - a. For the first execution, a separate asset should be created in the local catalogue.
    - b. For the second execution, the existing asset in the local catalogue should be updated with a new version.
3. Delete the asset in the remote catalogue, and once more execute two harvesting processes with different settings of the remote asset lifecycle parameter.

    - a. For the first execution, the local catalogue should remain unchanged 
    - b. For the second execution, the corresponding asset in the local catalogue

should be removed.
4. After each step, run a query to demonstrate that the local catalogue has the intended state.


*Note:*

As it is NOT REQUIRED to implement a publish/subscribe mechanism, by which the local catalogue might be notified of the deletion of an asset in a remote catalogue, the only way to find out that an asset has been deleted is that it does not occur in subsequent harvests anymore.

#### FR-ACM-04 Linked Assets

*Priority:* MUST HAVE  
*Description:*
To ensure that, for any asset imported from a remote catalogue, both its original form and the transformed form resulting from schema mapping remain accessible, both forms MUST be stored in the local catalogue in a way that does not cause conflicts, i.e.:

- As the result of a regular query, the local catalogue MUST only return the transformed asset, unless explicitly asked for the original asset before transformation.
- Throughout the lifecycle of the imported asset (cf. FR-ACM-03), both the original form and the transformed form must be handled together.


Depending on the local catalogue’s implementation, this functionality MAY be realized by keeping the original form of an imported asset in a separate namespace of the asset store, or by only keeping the transformed form in the asset store and encoding the original form into special metadata. 

*Acceptance criteria:*
1. Run a harvest with successful schema mapping according to FR-ACM-01, which results in at least one asset imported.
2. Demonstrate queries that handle both the original form and the transformed form of the imported asset correctly, i.e.:

    - a. Run a regular query that demonstrates that only information about the transformed form of the asset is considered.
    - b. Run a query that explicitly asks for the original asset.
3. Demonstrate that the lifecycle of both the original form and the transformed form is handled correctly, i.e.:

    - a. Update the asset in the remote catalogue, re-run the harvest of step (1.), ensuring that the updated asset is imported into the local catalogue. Demonstrate that there are new versions of both the original form and the transformed form of the asset.
    - b. Delete the asset from the local catalogue. Demonstrate that both the original form and the transformed form have been deleted.


#### FR-ACM-05 Crawling References

*Priority:* MUST HAVE  
*Description:*
For the case that assets of one remote catalogue C₁ reference assets stored in another catalogue C₂ (e.g., hierarchical service dependencies), the Asset Crawler MUST be configurable to automatically resolve such links during a harvest, or not. The following reference types MUST be supported:

- URLs (Linked Data style)
- DIDs [DID] 

*Acceptance criteria:*
1. Set up two Catalogues C₁ and C₂ with one asset each, A₁ and A₂, both of type dcat:Resource. A₁ references, via dcat:qualifiedRelation / dcat:Relationship, to A₂.
2. Demonstrate two harvests from C₁:

    - a. One in which only A₁ is retrieved
    - b. One in which A₂ is retrieved as well, because the link to C₂/A₂ is crawled.


### 5.2 Schema Registry

#### FR-SR-01 Storing Remote Schemas

*Priority:* MUST HAVE  
*Description:*
The Schema Registry MUST provide the possibility to store, for reference, any remote schemas that the local catalogue’s administrator has become aware of. These schemas MUST be kept separately from the schemas used by the local catalogue for validating local assets. For each schema, the following metadata SHALL be maintained: the unique ID(s) of those remote catalogues in the Catalogue Registry (cf. FR-CR-01), in which this schema is used

*Acceptance criteria:*
1. Set up a schema-aware local catalogue with one schema.
2. Upload one “remote schema” S to the Schema Registry. It is NOT REQUIRED to actually run a remote catalogue for this demonstration.
3. Demonstrate that, from the local catalogue, schema S is not accessible for purposes that schemas are typically used for, e.g., validating assets.


*Notes:*

- The rationale for keeping the remote schemas separately from the local schemas is that local assets are not necessarily valid against the remote schemas and vice versa.
- The rationale for emphasizing the separation of local and remote schemas is that the Schema Registry MAY be realized by storing schemas in a schema-aware local catalogue, but they MUST NOT interfere with the schemas regularly stored there.
- The Asset Crawler + Mapper is NOT REQUIRED to harvest schemas from a remote catalogue, as state-of-the-art catalogues do not typically expose their schemas. Nevertheless, there are exceptions, such as the XFSC Federated Catalogue [FC.CCF.SRS].


#### FR-SR-02 Transformation Strategy Selection

*Priority:* MUST HAVE  
*Description:*  
For each remote catalogue, one of the following transformation strategies MUST be configurable:

- AI-Driven: LLM transforms asset using prompts
- Deterministic RDF: schema-selective RDF Mapping
- Hybrid: first try AI, but fallback to RDF on failure


The selected strategy MUST be configured in the Catalogue Registry (cf. FR-CR-01). Changing the strategy for one remote catalogue MUST affect subsequent harvests from that remote catalogue but MUST NOT affect previously imported versions of assets from that remote catalogue.

*Acceptance criteria:*
1. Configure two remote catalogues, each with a different transformation strategy.
2. For one remote catalogue C₁, change the strategy.
3. Harvest assets from C₁; demonstrate that the new strategy is being applied according to the acceptance criteria for the respective FR(s).


#### FR-SR-03 Prompt Storage as Versioned Assets

*Priority:* MUST HAVE   
*Description:*  
Prompts to guide the AI-driven transformations of catalogue assets MUST be stored in Schema Registry as versioned assets with the following information:

- ID (UUID)
- version (major.minor.patch)
- status (draft/active/deprecated/archived)
- source schema ID (foreign key to remote schema, cf. FR-SR-01) and target schema ID (foreign key to local schema).
- prompt template ID (foreign key to prompt text with variable placeholders, cf. FR-SR04)
- examples (substituting the {EXAMPLES} prompt template variable with a concrete example for few-shot learning, e.g., showing how to transform complex data structures)
- constraints (substituting the {CONSTRAINTS} prompt template variable with a concrete textual specification of transformation rules, e.g., indicating that some metadata terms should, or should not, be mapped to their closest DCAT matches)
- created at, modified at (timestamps)
- author (string)

The constraint MUST be enforced that there can only be one active prompt per source-target schema pair.

*Acceptance criteria:*
1. In the Schema Registry, create a prompt P₁ for mapping between a source schema Sₛ and a target schema Sₜ.
2. Create a new version of this prompt, making it active, and deprecating the initial version.
3. Demonstrate that both the new version and the initial version can be retrieved.
4. Create a new prompt P₂ for mapping between Sₛ and Sₜ. Try to make it active. Expect the operation to fail.
5. Delete the prompt.


#### FR-SR-04 Prompt Templates and Variables

*Priority:* MUST HAVE   
*Description:*  
Templates for prompts (cf. FR-SR-03) MUST be stored as versioned assets with the following information:

- ID (UUID)
- version (major.minor.patch)
- text


Prompt templates MUST support the following variable placeholders:

- {SOURCE_ASSET} – Complete remote asset (harvested from the remote catalogue)
- {SOURCE_SCHEMA} – Remote schema definition (retrieved from the Schema Registry)
- {TARGET_SCHEMA} – Local schema definition (retrieved from the local catalogue)

In addition, prompt templates MUST support the following optional variable placeholders: • {EXAMPLES} – Optional example transformations (specified in the prompt that

instantiates this template according to FR-SR-03)

• {CONSTRAINTS} – Optional transformation rules (specified in the prompt that instantiates this template according to FR-SR-03)

These variables are intended to be substituted at runtime before sending the prompt to the LLM (cf. FR-SR-05).

Acceptance criteria: None for this FR on its own, but the correct implementation of this FR will be validated via FR-SR-05.

#### FR-SR-05 AI-Driven Transformation Execution

*Priority:* MUST HAVE   
*Description:*  
The AI Driven schema mapping, which is triggered during a harvest when referenced by the respective remote catalogue configuration (cf. FR-CR-01) MUST follow this execution pipeline:
1. Retrieve active prompt from Schema Registry (cf. FR-SR-03)
2. Substitute template variables (cf. FR-SR-04)
3. Send to the complete prompt to the LLM Parse the LLM’s response.
4. Validate the output against the local schema.
5. Store the result including, in case of successful validation, the transformed asset, and the following metadata:
    -  prompt version,
    -  model used,
    -  timestamp,
    -  duration,
    -  status,
    -  errors.


*Acceptance criteria:*
1. Configure a remote catalogue with AI-driven transformation.
2. Perform a harvesting operation.
3. Show that the result conforms to the local schema.
4. Query the metadata to show that the selected LLM parameters were correctly set.
5. Repeat steps (2.) to (4.) with varying LLM parameters and show that they impact the result and show that prompts with missing values for the {EXAMPLES} and {CONSTRAINTS} variables in prompt templates are handled without errors.
6. Perform a harvesting operation that enforces a timeout.
7. Show that the failures are correctly logged.


*Note:*  
 This requirement MAY be realized using a framework such as [LangChain](https://www.langchain.com/), which provides prompt template management, variable substitution, and multi-provider LLM integration.

#### FR-SR-06 Deterministic Schema-selective RDF Mapping

*Priority:* MUST HAVE  
*Description:*  
- The deterministic mapping of RDF assets from one schema to another schema assumes that a subset of the RDF triples in an asset imported from a remote catalogue constitute a valid asset in the local catalogue because both catalogues have a common understanding of a standard vocabulary, e.g., DCAT. Thus, it MUST be possible to configure the following:http://www.w3.org/ns/dcatNamespace(s) of metadata vocabularies to preserve (e.g., http://www.w3.org/ns/dcat#)

- Optional reference to a SHACL shape (stored as a schema in the local catalogue) to validate the retained triples.


Mark as incomplete if validation fails.

*Acceptance criteria:*

None for this FR on its own, but the correct implementation of this FR will be validated via FRSR-07.

#### FR-SR-07 Deterministic RDF Mapping Execution

*Priority:* MUST HAVE   
*Description:*  
The deterministic RDF schema mapping MUST follow this execution pipeline:
1. Parse RDF asset to triples
2. Retain all triples whose predicate is in one of the namespaces to be preserved; discard any other triples.
3. If a SHACL shape is configured, take the preserved triples as a data graph and validate it against the SHACL shape. In case of successful validation, or in case no SHACL shape was configured, keep the preserved triples as the transformed asset; otherwise raise an error.


*Acceptance criteria:*
1. Configure a remote catalogue to use deterministic RDF mapping:

    - a. with SHACL validation, and
    - b. without SHACL validation
2. In the remote catalogue, create one RDF asset A₁ that is valid against the given SHACL shape (after only retaining triples with predicates from the namespaces to be preserved), and another one A₂ that is not.
3. Perform a harvest from that catalogue.
4. Run a query against the result:


    - a. If SHACL validation is turned on, show that

        - A₁ was mapped by discarding triples from unknown namespaces, and
        - A₂ was not mapped.


    - b. If SHACL validation is turned off, show that both A₁ and A₂ were mapped by discarding triples from unknown namespaces.


*Note:*

Triples discarded during this transformation will not be part of the transformed asset and thus not queryable. However, they will remain accessible in the original form of the remote asset, which is also stored in the local catalogue according to FR-ACM-04.

#### FR-SR-08 Hybrid Mapping Strategy with Automatic Fallback

Priority: MAY HAVE Description:

There MAY be a hybrid mapping strategy, which falls back to the Deterministic RDF mapping (FR-SR-06, -07) in case the AI-Driven mapping is not successful for at least one of the following reasons:

- LLM timeout/network error,
- unparseable output,
- validation failure,
- rate limit.
1. The execution sequence is as follows: Attempt AI-Driven transformation
2. On failure, fall back to Deterministic RDF mapping.


*Acceptance criteria:*
1. Configure a remote catalogue.
2. Perform a harvesting operation using the AI-driven mode.
3. Set it up in a way that is not successful.
4. Verify from the logs that it has been attempted.
5. Demonstrate that the unsuccessful AI-driven mapping triggered the fallback, resulting in a deterministic RDF mapping.


#### FR-SR-09 Transformation Audit Trail

*Priority:* MUST HAVE   
*Description:* The Schema Registry MUST store a tamper-proof record per mapping, which is exportable as CSV and JSON. It MUST contain:

- transformation ID
- asset IDs (remote/local)
- catalogue ID
- timestamps
- strategy

    -  For AI: prompt ID and version
    -  For deterministic RDF: preserved namespaces


- results of schema validation
- status
- errors
- duration
- metadata about the validation as specified in the XFSC Federated Catalogue requirements CAT-FR-CO-02 and CAT-FR-CO-05 [FACIS.FCE.SRS].


Records SHOULD be queryable by:

- asset ID
- catalogue ID
- prompt version
- status
- date range


*Acceptance criteria:*
1. Set up a remote catalogue.
2. Perform a harvesting operation.
3. Show that a record of the mapping is stored in the Schema Registry.
4. Export the record once as CSV and once as JSON.
5. Show that it is not possible to store a modified version of the same record in the Schema Registry.
6. Show that it is possible to query the records by the parameters defined in this requirement.


#### FR-SR-10 Prompt Testing Interface

*Priority:* MUST HAVE   
*Description:*   
The Schema Registry MUST have a testing UI, which provides controls for:

- Prompt version selection
- Sample asset input
- Dry-run execution (no persistence)
- Output view and comparison For test cases, the following data SHOULD be stored with each prompt:
- sample input
- expected output
- description Acceptance criteria: In the UI, demonstrate the following functionality:
- It should be accessible from prompt management UI.
- It has a side-by-side source/result display.
- The run test cases can be saved and reused.
- It offers a setting to support batch testing.


#### FR-SR-11 LLM Configuration

*Priority:* MUST HAVE   
*Description:*  
The Schema Registry MUST support storing configurations of LLMs with the following parameters:

- ID (UUID)
- LLM provider (e.g., OpenAI, Anthropic, Ollama, custom)
- Model identifier
- Temperature
- Token limit
- Timeout


*Acceptance Criteria:*  
1. Create two different LLM configurations L₁ and L₂.
2. Set up two remote catalogues C₁ and C₂, each of which uses AI-driven transformation using L₁ and L₂, respectively.
3. Demonstrate the results of a harvest and the subsequent mapping of harvested assets. You MAY use different prompts that highlight the differences of the two LLMs.


#### FR-SR-12 Multi-Model Provider Support

*Priority:* MAY HAVE   
*Description:*  
The providers OpenAI, Anthropic, and Ollama SHOULD be supported, as well as custom endpoints. Per provider, it SHOULD be possible to configure the following options:

- endpoint URL
- authentication
- credentials (encrypted)
- model ID
- rate limits
- timeouts


It SHOULD be possible to reference a provider on each of the following levels:

- per prompt (by extending FR-SR-03)
- per catalogue (by extending FR-CR-01)
- as a global system default.


The model to be applied SHALL be selected according to the following precedence rule: prompt level > catalogue level > system level.

*Acceptance criteria:*

- Demonstrate a setup, in which multiple providers are configured simultaneously.
- Demonstrate the selection of a provider selection per prompt, per catalogue, and as a global system default.
- No code changes for provider selection.
- Demonstrate that credentials are stored encrypted.
- Demonstrate that rate limits are enforced.
- Demonstrate how usage is tracked per provider and per model.


#### FR-SR-13 Batch Re-transformation

*Priority:* MAY HAVE   
*Description:* It SHOULD be possible to have a re-transformation of previously imported assets triggered by any of the following events:

- changing the transformation strategy in a Catalogue Registry entry (cf. FR-CR-01),
- For AI-driven transformation: a new version of a prompt or of an LLM
- For deterministic RDF mapping: changes to the namespaces and target schema. The scope of assets, to which this re-transformation is applied, SHOULD be configurable:
- All assets
- All assets of a given type
- All assets harvested from (a) given remote catalogue(s) The lifecycle of assets according to FR-ACM-03 MUST be respected.


There SHOULD be a dry-run mode, and an interactive mode with progress tracking and the possibility to cancel. Acceptance criteria:

- Demonstrate the initiation of the interactive mode via a UI or an API call. o Show that the progress is visible during execution. o Cancel the execution.
- Original assets preserved (versioning).
- Asset lifecycle respected: show that their previous versions are still accessible.
- Show that a summary report has been generated.
- Demonstrate a failed re-transformation and how it is successfully re-tried after fixing the transformation configuration that caused the problem.
- Individual retry supported.


### 5.3 Catalogue Registry

#### FR-CR-01 Configure Remote Catalogues

*Priority:* MUST HAVE   
*Description:*  
It MUST be possible to configure remote catalogues, from which assets can be crawled, according to the following communication protocols / APIs:

- OAI-PMH
- DCAT as Linked Data: a URL that resolves to a dcat:Catalog
- Query interface: an endpoint to which a query is sent


For each such remote catalogue the configuration MUST include the following information:

- a unique identifier
- the identifier of communication protocol, as listed above
- in the case of communication with a query interface:

 the query endpoint(s)

 for each query endpoint, the supported query language(s)

- a MIME type identifying the expected result, e.g., application/sparql-results+json for a SPARQL result set in JSON format [SPARQL].


- the desired transformation strategy for schema mapping according to FR-SR-02, if any, and:


    - If the AI-driven or hybrid strategy is selected, the ID of an active stored prompt to guide the AI-driven transformation (cf. FR-SR-03) and of an LLM to execute the prompt (cf. FR-SR-11).

    - If the deterministic RDF mapping is selected, the namespace(s) of URIs to preserve and, optionally, the identifier of a SHACL shape in the local catalogue to validate the mapping result (cf. FR-SR-06).

*Acceptance criteria:*

For each of the three required communication protocols, demonstrate the harvest from a catalogue containing at least two assets according to FR-ACM-01. After each harvest, demonstrate its success by running an appropriate query to retrieve information from the assets harvested, then revert the asset store to the state before the harvest. This MAY be realized as three harvests from less than three catalogues, if one catalogue speaks more than one communication protocol.

#### FR-CR-02 Configure Asset Types

*Priority:* MUST HAVE  
*Description:*

There MUST be a registry of asset types that we would like to import to the local catalogue and and a mapping of asset types expected to be found in the remote catalogues onto these. The syntax of asset type identifiers (e.g., plain words or URIs of classes defined in an ontology) MAY vary based on the specification of the remote catalogue.

- In case the identifier of an asset differs between local and remote catalogue(s), the asset type registry MUST contain a mapping of each remote asset type identifier to the local type,
- In the case that an asset type is identified in the same way in the local catalogue and in all remote catalogues configured in the Catalogue Registry, it MUST be possible simply add the plain asset type identifier as an entry without an explicit mapping.


*Acceptance criteria:*  
Show the registry of asset types, containing both mappings and plain entries.

*Note:*

There is no standard way of obtaining the types of assets of remote catalogues. The local administrator MAY extract them from a harvest according to FR-ACM-01. Depending on the communication protocol spoken by the remote catalogue (cf. FR-CR-01), a harvest MAY include explicit type information; this is the case, e.g., with DCAT and SPARQL query results. For a remote catalogue with a query interface, it MAY alternatively be possible to query for all asset types. Another option is to consult the remote catalogue’s documentation.

#### FR-CR-03 Catalogue API Mapping

*Priority:* MAY HAVE   
*Description:*  
To enable the harvesting of assets from remote catalogues by type (case (2.) of FR-ACM-02) in a broader range of scenarios, mappings from asset types (defined according to FR-CR-02) to remote catalogue API requests MAY be pre-configured, e.g., mapping the asset type https://w3id.org/gaia-x/development#ServiceOffering to an API request like GET https://remote.catalogue/assets?type=ServiceDescription. Such API mappings SHOULD be AIdriven, as long as there is no deterministic implementation. The prompts for guiding API mappings SHOULD be managed like the prompts for schema mapping (cf. FR-SR-03), referencing, instead of schemas, the target remote catalogue according to FR-CR-01.

*Acceptance criteria:*
1. Set up a remote catalogue that has no query API.
2. In the local catalogue, define an asset type T and, if required for interoperability with the remote catalogue, a mapping to the remote asset type m(T).
3. In the remote catalogue, create an asset of type m(T).
4. Harvest the asset.
5. Query the local catalogue to demonstrate that the harvested asset has been imported.


### 5.4 Access Control

#### FR-AC-01 User Roles

*Priority:* MUST HAVE  
*Description:*  
It MUST be possible to define different User Roles, which allow or deny accessing the functionalities of one / some / all of the following:

- the Asset Crawler: initiation of a harvest (FR-ACM-01), Harvest Scope CRUD operations (FR-ACM-02), configuring lifecycle (FR-ACM-03) and crawling (FR-ACM-05) options
- CRUD operations in the Schema Registry (FR-SR-01, -03)
- CRUD operations in the Catalogue Registry (FR-CR-01, -02, and optionally -03).


*Acceptance criteria:*
1. For each of the permissions listed above, assign to a user a role that has, or does not have, the respective permission.
2. Demonstrate the user’s attempt of executing the respective action. Expect it to be denied when the user’s role has not been granted the necessary permission.


### 5.5 General Interoperability

#### FR-GI-01 Discoverable Local Catalogue API

*Priority:* MUST HAVE  
*Description:*  
The local catalogue MUST expose its machine-readable API documentation in a way that enables it to be discovered,according to [RFC.9279]. Acceptance criteria: Implement RFC 9279 in the XFSC Catalogue and demonstrate a request to /.well-known/apicatalog.

---

[← Conceptual Architecture](04_conceptual_architecture.md) · [↑ Table of Contents](../README.md) · [Technical Architecture →](06_technical_architecture.md)

