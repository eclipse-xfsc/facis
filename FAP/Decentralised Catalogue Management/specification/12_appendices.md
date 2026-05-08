[← Requirements Traceability Matrix](11_requirements_traceability_matrix.md) · [↑ Table of Contents](README.md)

---

## 12. Appendices

### Appendix A: Glossary

|Term|Full Name|Definition|
|---|---|---|
|CES|Gaia-X Credential Event Service|A common publication/subscription service that allows the Gaia-X catalogues of the GXDCH to be notified about new, updated, and revoked credentials [CES]|
|CRUD|Create, Read, Update, Delete|Four basic operations (actions) of persistent storage.|
|DID|Decentralized Identifier|W3C standard for decentralized digital identities [DID]|
|OAI-PMH|The Open Archives Initiative Protocol for Metadata Harvesting|A low-barrier mechanism for repository interoperability [OAI-PMH]|
|VC|Verifiable Credential|W3C standard for tamper-evident credentials [VCDM]|
|VP|Verifiable Presentation|Package of one or more VCs for presentation to verifier [VCDM]|


### Appendix B: References


|Reference ID|Description|Link|
|------------|-----------|----|
|[GX.CES]|Conceputal explenation, technical documentatio n, and highlevel specification of the Credential Event Service|https://gitlab.com/gaia-x/lab/credentials-events-service https://gaia-x.eu/gaia-x-and-catalogues/ https://docs.gaia-x.eu/technicalcommittee/architecturedocument/24.04/gx_services/#gaia-x-credential-eventservice-ces<br><br>|
|[DID]|Decentralized Identifiers (DIDs) v1.0|https://www.w3.org/TR/did-1.0/<br><br>|
|[FACIS.FCE.SR S]|SRS for the Federation Architecture for Composed Infrastructure Services (FACIS) Enhancement of XFSC Federated Catalogue|https://github.com/eclipsexfsc/docs/tree/main/federated-catalogue<br><br>|
|[FC.CCF.SRS]|SRS for the GXFS Federated Catalogue – Core Catalogue Features (FC.CCF)|https://www.gxfs.eu/download/1740/<br><br>|
|[OAI-PMH]|The Open Archives Initiative Protocol for Metadata Harvesting|https://www.openarchives.org/OAI/openarchivesprotoc ol.html<br><br>|
|[RFC.9727]|api-catalogue: A Well-Known URI and Link Relation to Help Discovery of APIs|https://datatracker.ietf.org/doc/rfc9727/<br><br>|
|[SPARQL]|W3C SPARQL 1.2 Query Language|https://www.w3.org/TR/sparql12-query/<br><br>|
|[VCDM]|Verifiable Credentials Data Model v2.0|https://www.w3.org/TR/vc-data-model-2.0/<br><br>|


### Appendix C: Possible Implementation of the Local Catalogue with the XFSCFederated Catalogue

The following table explains, for the relevant requirements affecting the local catalogue, how they MAY be realized using the XFSC Federated Catalogue [FC.CCF.SRS, FACIS.FCE.SRS].

|Functional Requirement|Related XFSC Federated Catalogue Requirement(s)|Comment|
|---|---|:---:|
|FR-ACM02|(unspecifie d but implement ed)|Regarding harvests performed by executing queries in a remote catalogue (case (3.) of FR-ACM-02), the XFSC Federated Catalogue has an (unspecified) feature for passing on incoming queries to “partner catalogues”. In contrast to the regular POST /query method, the /query/search endpoint runs a query not only in the internal graph database, but also sends it to configured “partner” catalogues:<br><br>• API definition: https://github.com/eclipse-xfsc/federatedcatalogue/blob/main/openapi/fc_openapi.yaml#L713<br><br>• Implementation: https://github.com/eclipsexfsc/federated-catalogue/blob/main/fc-serviceserver/src/main/java/eu/xfsc/fc/server/service/QueryService.java#L148<br><br>• Test: https://github.com/eclipse-xfsc/federatedcatalogue/blob/main/fc-serviceserver/src/test/java/eu/xfsc/fc/server/controller/DistributedQueryControllerTest.java|
|FR-ACM04|CAT-FR-[SF0](https://www.w3.org/TR/vocab-dcat-3/), CATFR-LM-04|The XFSC Federated Catalogue is prepared to store, aside any machine-readable asset, a human-readable representation, which is subject to the same lifecycle. This functionality MAY be extended to link the original form of an imported asset to its transformed form after schema mapping.|
|FR-SR-01|CAT-FR-[SF0](https://projects.eclipse.org/projects/technology.xfsc), -04, CAT-FRCO-05|The XFSC Federated Catalogue supports schema management including versioning. The validity of assets against schemas is not enforced; instead, the user decides what schemas assets should be validated again. Still, additional modifications will be required to store remote schemas separately from local schemas.|
|FR-SR-09|CAT-FRCO-02, -05|Using the XFSC Federated Catalogue as the local catalogue immediately satisfies the requirements for storing the result of validating an asset after schema mapping.|
|FR-CR-02|SD-Sch-01 SD-G-F-*|The XFSC Federated Catalogue features a schema storage and a graph database. Thus, it is possible to maintain the asset types as a dedicated ontology, or as a special named graph in the graph database, whichever suits better.|


### Appendix D: Change Log Template   
For future revisions, document changes using this format:


|Version|Date|Section|Change Description|
|---|---|---|---|
|[x.y]|[YYYY-MMDD]|[Section number/name]|[Brief description of change]|

---

[← Requirements Traceability Matrix](11_requirements_traceability_matrix.md) · [↑ Table of Contents](README.md)

