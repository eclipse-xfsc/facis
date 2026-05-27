[← Background & Context](02_background_context.md) · [↑ Table of Contents](../README.md) · [Conceptual Architecture →](04_conceptual_architecture.md)

---

## 3. Scope & Boundaries

### 3.1 In Scope

- Unified search across distributed service catalogues.
- Interoperable service listings and metadata exchange.
- Catalogue changes resulting from Asset Crawling + Mapping processes (e.g., creating a new asset version, creating a new asset, or deleting an asset due to a remote deletion)
- Integration with ORCE to support lifecycle management features like deployment hooks and updates. Further on ORCE includes key functionality like UI Builder, Workflow Capabilities and seamless integration of boundary systems via REST API. ORCE is based on Node-[RED](https://nodered.org/) and includes all baseline functions as well.
- Integration with ICAM to ensure secure access to services and resources. XFSC delivers a full stack for Authentication and Authorization (e.g., Keycloak), Credential Manager for Organisations and Individuals as well as [Policy Engine](https://eclipse.dev/xfsc/traincd/traincd/) for specific rules.
- Support for cross-domain use cases, enabling service discovery across different administrative domains.


### 3.2 Out of Scope

- Direct edits or arbitrary updates to catalogue content outside the workflow of the Asset Crawler + Mapper.
- Publish/subscribe mechanisms beyond the XFSC Federated Catalogue’s existing interface with the Gaia-X Credential Event Service (CES), i.e., no implementation of the original optional requirements G-FR-07 and G-FR-08 [FC.CCF.SRS].
- Ontology alignment (applied to schemas)
- Enforcing a global, unified schema across all catalogues.
- Service instantiation or direct execution.
- Deep integration beyond metadata exchange and access control.

---

[← Background & Context](02_background_context.md) · [↑ Table of Contents](../README.md) · [Conceptual Architecture →](04_conceptual_architecture.md)

