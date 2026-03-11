(() => {
  // src/services/uibuilder.service.js
  var mockUsers = [
    {
      uniqueId: "u1",
      profile: { firstName: "Alice", lastName: "Schmidt" },
      email: "alice@example.com",
      status: "Active",
      access: ["local_catalogue", "catalogue_registry", "schema_registry", "admin_tools", "harvester"]
    },
    {
      uniqueId: "u2",
      profile: { firstName: "Bob", lastName: "Mueller" },
      email: "bob@example.com",
      status: "Active",
      access: ["local_catalogue", "catalogue_registry"]
    },
    {
      uniqueId: "u3",
      profile: { firstName: "Clara", lastName: "Fischer" },
      email: "clara@example.com",
      status: "Invited",
      access: ["local_catalogue", "schema_registry", "harvester"]
    }
  ];
  var mockCatalogs = [
    {
      uniqueId: "rc1",
      catalog: {
        catalogId: "rc1",
        catalogName: "SensorML Europe",
        owner: "EU Sensors Consortium",
        strategy: "deterministic",
        baseEndpoint: "https://api.sensorml-eu.org/sparql",
        enabled: true
      }
    },
    {
      uniqueId: "rc2",
      catalog: {
        catalogId: "rc2",
        catalogName: "DCAT-AP Germany",
        owner: "GovData.de",
        strategy: "ai",
        baseEndpoint: "https://govdata.de/ckan/api",
        enabled: true
      }
    },
    {
      uniqueId: "rc3",
      catalog: {
        catalogId: "rc3",
        catalogName: "OGC Observations",
        owner: "OGC Foundation",
        strategy: "hybrid",
        baseEndpoint: "https://ogc.org/api/observations",
        enabled: false
      }
    }
  ];
  var msgCallbacks = [];
  var _isMock = false;
  function dispatchMsg(msg) {
    setTimeout(() => {
      msgCallbacks.forEach((cb) => {
        try {
          cb(msg);
        } catch (e) {
          console.error("[facis-service] callback error:", e);
        }
      });
    }, 150);
  }
  function createMockResponder(msg) {
    if (!msg) return;
    if (msg.type === "getDashboard") {
      dispatchMsg({
        payload: {
          type: "getDashboard",
          response: {
            action: "getDashboard",
            status: "success",
            userAccess: ["local_catalogue", "catalogue_registry", "schema_registry", "admin_tools", "harvester"],
            userPermissions: {
              local_catalogue: { read: true, create: false, update: false, delete: false },
              catalogue_registry: { read: true, create: true, update: true, delete: true },
              schema_registry: { read: true, create: true, update: true, delete: true },
              harvester: { read: true, create: true, update: true, delete: false },
              admin_tools: { read: true, create: true, update: true, delete: true }
            }
          }
        }
      });
    }
    if (msg.type === "getCatalogRegistry") {
      dispatchMsg({
        payload: {
          response: {
            action: "getCatalogRegistry",
            status: "success",
            catalogs: mockCatalogs
          }
        }
      });
    }
    if (msg.type === "getAdminTools") {
      dispatchMsg({
        type: "getAdminTools",
        response: { status: "success", users: mockUsers }
      });
    }
    if (msg.type === "inviteUser") {
      dispatchMsg({
        payload: {
          data: msg.data,
          response: {
            action: "inviteUser",
            status: "success",
            uniqueId: "mock-" + Date.now()
          }
        }
      });
    }
    if (msg.type === "registerRemoteCatalog") {
      dispatchMsg({
        payload: {
          response: {
            action: "registerRemoteCatalog",
            status: "success",
            uniqueId: "mock-rc-" + Date.now()
          }
        }
      });
    }
    if (msg.type === "updateRemoteCatalog") {
      dispatchMsg({
        payload: {
          data: msg.data,
          response: {
            action: "updateRemoteCatalog",
            status: "success"
          }
        }
      });
    }
    if (msg.type === "logOut") {
      console.log("[facis-service] Logout requested (no redirect in preview)");
    }
  }
  var mockAdapter = {
    start() {
      console.log("[facis-service] mock start()");
    },
    send(msg) {
      console.log("[facis-service] mock send():", JSON.stringify(msg, null, 2));
      createMockResponder(msg);
    },
    onChange(prop, cb) {
      if (prop === "msg" && typeof cb === "function") {
        msgCallbacks.push(cb);
      }
    },
    get(prop) {
      if (prop === "clientId") return "mock-client-001";
      return void 0;
    },
    set() {
    },
    eventSend() {
    }
  };
  var uibuilderService = {
    init() {
      if (window.uibuilder) {
        _isMock = false;
        console.log("[facis-service] Using real uibuilder");
      } else {
        _isMock = true;
        window.uibuilder = mockAdapter;
        console.log("[facis-service] Mock uibuilder activated");
      }
    },
    onMessage(handler) {
      if (_isMock) {
        msgCallbacks.push(handler);
      } else {
        window.uibuilder.onChange("msg", handler);
      }
    },
    send(msg) {
      window.uibuilder.send(msg);
    },
    start() {
      window.uibuilder.start();
    },
    get(prop) {
      return window.uibuilder.get(prop);
    },
    isMock() {
      return _isMock;
    }
  };

  // src/state/store.js
  function createStoreData() {
    return {
      currentPage: "localCatalogue",
      currentTab: "localCatalogue",
      currentSchemaTab: "localSchema",
      currentAdminTab: "accessControl",
      // Modals
      isViewModal: false,
      manageUserModal: false,
      currentViewTab: "Overview",
      isInviteModal: false,
      showRegisterRemoteCatalogModal: false,
      isRegisterSchemaEditModal: false,
      isRegisterSchemaNewModal: false,
      showHarvestWizard: false,
      showAccessInformation: false,
      // Invite form
      inviteForm: {
        firstName: "",
        lastName: "",
        email: "",
        role: "Searcher",
        expiresIn: "30 Days",
        altRole: "",
        message: "You have been invited to join the federated catalogue system.",
        selectedAccess: ["Local Catalogue"]
      },
      // Manage user form
      manageForm: {
        firstName: "",
        lastName: "",
        email: "",
        role: "Searcher",
        selectedRoles: ["Local Catalogue"],
        expiresIn: "30 Days",
        altRole: "",
        message: ""
      },
      // Remote catalog form
      editingRemoteCatalogId: null,
      isEditingRemoteCatalog: false,
      remoteCatalogForm: {
        catalogId: "",
        catalogName: "",
        owner: "",
        protocol: "Query interface",
        baseEndpoint: "",
        mimeType: "application/sparql-results+json",
        queryEndpoint: "",
        queryLanguages: "",
        // OAI-PMH fields
        metadataPrefix: "oai_dc",
        setSpec: "",
        resumptionToken: false,
        // DCAT fields
        dcatCatalogUri: "",
        linkedDataEndpoint: "",
        contentNegotiation: "application/ld+json",
        strategy: "none",
        promptId: "",
        llmConfigId: "",
        namespacesToPreserve: "",
        shaclShapeId: "",
        auth: "none",
        trustAnchor: "",
        enabled: true
      },
      // Pagination
      pagination: {
        catalog: { page: 1, perPage: 5 },
        schema: { page: 1, perPage: 5 },
        remoteSchema: { page: 1, perPage: 5 },
        catalogsRegister: { page: 1, perPage: 5 },
        users: { page: 1, perPage: 5 },
        harvest: { page: 1, perPage: 5 },
        mapping: { page: 1, perPage: 5 },
        harvestWizard: { page: 1, perPage: 5 }
      },
      // Manage menu
      manageMenu: {
        open: false,
        x: 0,
        y: 0,
        stage: "root",
        userId: null,
        anchorEl: null
      },
      roles: ["Harvester", "Catalog Admin", "Schema Admin", "Administrator", "Searcher"],
      // Schema form
      registerSchemaForm: {
        name: "",
        format: "SHACL",
        catalogSearch: "",
        remoteCatalogs: ["DCAT-AP.de", "OGC SensorML"],
        namespaces: ["ex:", "dcat:", "dct:"],
        version: "",
        sourceUrl: "",
        summaryTab: "SHACL"
      },
      schemaSummaries: {
        Parsed: `Targets: dcat:Distribution, ex:GeoDataset
Required Properties: dct:title, dct:dataset

Classes: dcat:Dataset (class), dcat:Distribution (lclass)
Properties: dcat:mediaType, dcat:spatial

Terms: ex:dataset - http://example.org/dataset, dcat:dataset
IRIs: ex - http://example.org/, dcat - http://www.w3.org/ns/dcat#`,
        SHACL: `@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct:  <http://purl.org/dc/terms/> .

:CatalogueShape a sh:NodeShape ;
  sh:targetClass dcat:Catalogue ;
  sh:property [
    sh:path dcat:dataset ;
    sh:minCount 1 ;
    sh:node :DatasetShape ;
  ] .

:DatasetShape a sh:NodeShape ;
  sh:targetClass dcat:Dataset ;
  sh:property [
    sh:path dct:identifier ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path dct:title ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path dct:publisher ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path dcat:distribution ;
    sh:node :DistributionShape ;
    sh:minCount 0 ;
  ] .

:DistributionShape a sh:NodeShape ;
  sh:targetClass dcat:Distribution ;
  sh:property [
    sh:path dcat:accessURL ;
    sh:nodeKind sh:IRI ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path dcat:mediaType ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] .`,
        Vocab: `# RDF vocab output placeholder (ttl)
@prefix ex: <http://example.org/> .
ex:Dataset a ex:Class .
ex:publisher a ex:Property .`,
        JSONLD: `{
  "@context": {
    "dcat": "http://www.w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/"
  }
}`
      },
      // Asset Detail Panel (Milestone 1)
      showAssetDetailPanel: false,
      assetDetailRow: null,
      isEditingAsset: false,
      assetEditForm: {
        assets: "",
        type: "",
        name: "",
        domain: "",
        integrationStatus: "Active"
      },
      showDeleteAssetConfirm: false,
      deleteAssetTargetId: null,
      // Selections
      selectedRows: [],
      selectedMappingRows: [],
      auditSearch: "",
      // Transformation / validation data
      transformationSummary: [
        "Schema harmonization",
        "Domain enrichment",
        "Attribute normalization",
        "Additional rules applied...",
        "Recursive timestamp update (Enabled)",
        "Harvested data items: 18,564",
        "Transformation issues resolved: 1,013"
      ],
      validation: {
        status: "Passed",
        minorWarnings: 52,
        criticalErrors: 2
      },
      auditMini: [
        { id: 1, level: "Info", step: "Schemas Harmonized", timestamp: "2026-09-02 10:32 (UTC)" }
      ],
      auditRows: [
        { id: 1, rule: "Recursive Time Updates", level: "Info", step: "Schemas Harmonized", timestamp: "2026-06-02 10:32 (UTC)", assetId: "sensor-asset-001", catalogueId: "SensorML", promptVersion: "1.0", status: "Success" },
        { id: 2, rule: "Schemas Harmonized", level: "Warning", step: "Schemas Harmonized", timestamp: "2026-09-02 10:32 (UTC)", assetId: "dataset-energy-042", catalogueId: "DCAT-AP.de", promptVersion: "2.0", status: "Warning" },
        { id: 3, rule: "Null value issues fixed", level: "Error", step: "Schemas Harmonized", timestamp: "2026-09-02 10:32 (UTC)", assetId: "service-api-007", catalogueId: "OGC SensorML", promptVersion: "1.0", status: "Error" },
        { id: 4, rule: "Namespace prefix mapped", level: "Info", step: "RDF Mapping", timestamp: "2026-09-01 14:20 (UTC)", assetId: "sensor-asset-001", catalogueId: "SensorML", promptVersion: "", status: "Success" },
        { id: 5, rule: "AI fallback triggered", level: "Warning", step: "Hybrid Mapping", timestamp: "2026-08-28 09:15 (UTC)", assetId: "dataset-energy-042", catalogueId: "DCAT-AP.de", promptVersion: "1.0", status: "Warning" }
      ],
      // Audit trail filters (FR-SR-09)
      auditFilters: {
        assetId: "",
        catalogueId: "",
        promptVersion: "",
        status: "",
        dateFrom: "",
        dateTo: ""
      },
      // JSON diff data
      originalJsonLines: [
        { text: "{", changeType: null },
        { text: '  "identifier": "sensor-asset-001",', changeType: null },
        { text: '  "catalogue": "SensorML",', changeType: null },
        { text: '  "updateTime": "2026-02-09T10:32:18Z",', changeType: null },
        { text: '  "temperature": 22.5,', changeType: null },
        { text: '  "humidity": 60,', changeType: null },
        { text: '  "airQualityIndex": 42,', changeType: null },
        { text: '  "status": "active",', changeType: null },
        { text: '  "owner": {', changeType: null },
        { text: '    "name": "Local Organization",', changeType: null },
        { text: '    "contact": "support@am.com"', changeType: null },
        { text: "  },", changeType: null },
        { text: '  "location": {', changeType: null },
        { text: '    "latitude": 40.7128,', changeType: null },
        { text: '    "longitude": -74.006', changeType: null },
        { text: "  },", changeType: null },
        { text: '  "tags": [', changeType: null },
        { text: '    "sensor-network",', changeType: null },
        { text: '    "environmental-monitoring",', changeType: null },
        { text: '    "asset-safety"', changeType: null },
        { text: "  ],", changeType: null },
        { text: '  "metrics": {', changeType: null },
        { text: '    "batteryLevel": 87,', changeType: null },
        { text: '    "signalStrength": -71,', changeType: null },
        { text: '    "lastHeartbeat": "2026-02-09T10:30:01Z"', changeType: null },
        { text: "  }", changeType: null },
        { text: "}", changeType: null }
      ],
      localJsonLines: [
        { text: "{", changeType: null },
        { text: '  "identifier": "sensor-asset-001",', changeType: null },
        { text: '  "catalogue": "SensorML",', changeType: null },
        { text: '  "updated_at": "2026-02-09T10:32:18Z",', changeType: "updated" },
        { text: '  "snisn_temperature": 22.5,', changeType: "updated" },
        { text: '  "snisn_humidity": 60,', changeType: "updated" },
        { text: '  "ai-generated-field-1": "deterministic_fallback",', changeType: "new" },
        { text: '  "status": "active",', changeType: null },
        { text: '  "owner": {', changeType: null },
        { text: '    "name": "Local Organization",', changeType: null },
        { text: '    "contact_email": "support@am.com"', changeType: "updated" },
        { text: "  },", changeType: null },
        { text: '  "location": null,', changeType: "deleted" },
        { text: '  "domain_tags": [', changeType: null },
        { text: '    "asset-safety",', changeType: null },
        { text: '    "environmental-monitoring",', changeType: null },
        { text: '    "sensor-network"', changeType: null },
        { text: "  ],", changeType: null },
        { text: '  "metrics": {', changeType: "new" },
        { text: '    "batteryLevel": 87,', changeType: "new" },
        { text: '    "signalStrength": -71,', changeType: "new" },
        { text: '    "lastHeartbeat": "2026-02-09T10:30:01Z",', changeType: "new" },
        { text: '    "harvestRunId": "run-2026-02-09-001"', changeType: "new" },
        { text: "  },", changeType: "new" },
        { text: '  "airQualityIndex": null', changeType: "deleted" },
        { text: "}", changeType: null }
      ],
      // Search and filters
      searchText: "",
      filters: {
        catalog: "",
        type: "",
        domain: "",
        status: ""
      },
      // Data
      allCatalogsRaw: [],
      tableRows: [],
      schemaRegistry: [
        { id: 1, schema: "DCAT-AP.de", catalogs: 3, localMapping: "Service, Data Product", versioning: "v1.0", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Federated" },
        { id: 2, schema: "Data Specifications", catalogs: 2, localMapping: "Dataset (1)", versioning: "v1.1", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Federated" },
        { id: 3, schema: "OGC SensorML", catalogs: 1, localMapping: "Asset + Safety", versioning: "v1.0", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Federated" },
        { id: 4, schema: "Xxx Taxonomy", catalogs: 1, localMapping: null, versioning: "v2.0", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Untrusted" }
      ],
      remoteSchema: [
        { id: 1, schema: "ISO 19115-1", catalogs: 5, localMapping: "Dataset (2)", versioning: "v2.0", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Federated" },
        { id: 2, schema: "schema.org Dataset", catalogs: 7, localMapping: "Dataset (5)", versioning: "v1.0", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Federated" },
        { id: 3, schema: "OpenAPI Specification", catalogs: 3, localMapping: "Service, Data Product", versioning: "v1.1", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Federated" },
        { id: 4, schema: "W3C PROV-O", catalogs: 2, localMapping: "Asset + Safety", versioning: "v2.0", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Federated" },
        { id: 5, schema: "SKOS Concept Scheme", catalogs: 1, localMapping: null, versioning: "v1.0", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Untrusted" },
        { id: 6, schema: "INSPIRE Metadata", catalogs: 4, localMapping: "Dataset (4)", versioning: "v1.1", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Federated" },
        { id: 7, schema: "DCAT", catalogs: 8, localMapping: "Service, Data Product", versioning: "v2.0", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Federated" },
        { id: 8, schema: "OGC Observations & Measurements", catalogs: 2, localMapping: "Asset + Safety", versioning: "v1.0", versionOptions: ["v1.0", "v1.1", "v2.0"], trustLevel: "Federated" }
      ],
      catalogsTable: [],
      // Asset Type Registry
      assetTypes: [
        { id: 1, name: "Dataset", description: "A collection of related data records", icon: "dataset" },
        { id: 2, name: "Service", description: "An API or web service endpoint", icon: "service" },
        { id: 3, name: "Document", description: "A document or report artifact", icon: "document" },
        { id: 4, name: "Software Release", description: "A versioned software package or release", icon: "software" },
        { id: 5, name: "Compliance Artifact", description: "A regulatory or compliance record", icon: "compliance" }
      ],
      assetTypeForm: { id: null, name: "", description: "", icon: "dataset" },
      isEditingAssetType: false,
      showAssetTypeForm: false,
      currentCatalogRegistryTab: "catalogues",
      // Prompt Management (FR-SR-03, FR-SR-04)
      prompts: [
        {
          id: "prompt-001",
          version: "1.0",
          status: "active",
          sourceSchema: "OGC SensorML",
          targetSchema: "DCAT-AP.de",
          template: "Transform the following {SOURCE_SCHEMA} asset into a valid {TARGET_SCHEMA} record.\n\nSource asset:\n{SOURCE_ASSET}\n\nExamples:\n{EXAMPLES}\n\nConstraints:\n{CONSTRAINTS}",
          examples: "Input: SensorML observation \u2192 Output: DCAT Dataset with dct:title, dcat:distribution",
          constraints: "All output must validate against the target SHACL shape. Preserve original identifiers.",
          createdAt: "2026-01-15",
          updatedAt: "2026-02-01"
        },
        {
          id: "prompt-002",
          version: "2.0",
          status: "draft",
          sourceSchema: "ISO 19115-1",
          targetSchema: "DCAT-AP.de",
          template: "Map the ISO 19115-1 metadata record to DCAT-AP.de format.\n\nSource:\n{SOURCE_ASSET}\n\nTarget schema:\n{TARGET_SCHEMA}\n\nExamples:\n{EXAMPLES}",
          examples: "MD_Metadata \u2192 dcat:Dataset with mandatory dct:identifier, dct:title",
          constraints: "Preserve spatial extent. Map CI_ResponsibleParty to dct:publisher.",
          createdAt: "2026-02-10",
          updatedAt: "2026-02-10"
        },
        {
          id: "prompt-003",
          version: "1.0",
          status: "deprecated",
          sourceSchema: "schema.org Dataset",
          targetSchema: "DCAT-AP.de",
          template: "Convert schema.org Dataset to {TARGET_SCHEMA}.\n\nInput:\n{SOURCE_ASSET}",
          examples: "",
          constraints: "Use dct:title for schema:name. Map schema:distribution to dcat:distribution.",
          createdAt: "2025-11-20",
          updatedAt: "2026-01-05"
        }
      ],
      showPromptModal: false,
      isEditingPrompt: false,
      promptForm: {
        id: null,
        version: "1.0",
        status: "draft",
        sourceSchema: "",
        targetSchema: "",
        template: "",
        examples: "",
        constraints: ""
      },
      promptFormError: "",
      promptSearch: "",
      // LLM Configuration (FR-SR-11)
      llmConfigs: [
        {
          id: "llm-001",
          name: "GPT-4o Production",
          provider: "OpenAI",
          model: "gpt-4o",
          temperature: 0.2,
          maxTokens: 4096,
          timeout: 30,
          status: "active",
          createdAt: "2026-01-10",
          updatedAt: "2026-02-15"
        },
        {
          id: "llm-002",
          name: "Claude Staging",
          provider: "Anthropic",
          model: "claude-3.5-sonnet",
          temperature: 0.3,
          maxTokens: 8192,
          timeout: 60,
          status: "active",
          createdAt: "2026-02-01",
          updatedAt: "2026-02-20"
        },
        {
          id: "llm-003",
          name: "Mistral Dev",
          provider: "Mistral",
          model: "mistral-large",
          temperature: 0.5,
          maxTokens: 2048,
          timeout: 45,
          status: "inactive",
          createdAt: "2025-12-05",
          updatedAt: "2026-01-18"
        }
      ],
      showLlmConfigModal: false,
      isEditingLlmConfig: false,
      llmConfigForm: {
        id: null,
        name: "",
        provider: "OpenAI",
        model: "",
        temperature: 0.3,
        maxTokens: 4096,
        timeout: 30,
        status: "active"
      },
      llmConfigSearch: "",
      llmConfigError: "",
      // Prompt Testing (FR-SR-10)
      promptTestSelectedPrompt: "",
      promptTestSelectedLlm: "",
      promptTestSampleInput: "",
      promptTestRunning: false,
      promptTestResult: "",
      promptTestError: "",
      promptTestShowResolved: false,
      promptTestCases: [
        {
          id: "tc-001",
          name: "SensorML to DCAT basic",
          promptId: "prompt-001",
          llmConfigId: "llm-001",
          sampleInput: '{\n  "@type": "SensorML",\n  "identifier": "sensor-abc-123",\n  "name": "Temperature Sensor Berlin",\n  "description": "Outdoor temperature monitoring station"\n}',
          expectedOutput: "",
          lastResult: '{\n  "@type": "dcat:Dataset",\n  "dct:title": "Temperature Sensor Berlin",\n  "dct:identifier": "sensor-abc-123",\n  "dct:description": "Outdoor temperature monitoring station"\n}',
          lastRunAt: "2026-02-20"
        }
      ],
      showTestCaseModal: false,
      isEditingTestCase: false,
      testCaseForm: {
        id: null,
        name: "",
        promptId: "",
        llmConfigId: "",
        sampleInput: "",
        expectedOutput: ""
      },
      users: [],
      harvestRecords: [
        { id: 1, sourceCatalogue: "SensorML", tool: "Mobil-X Crawler", harvestDate: "Today, 12:58 pm", assetsAdded: "+12", duration: "3 mins ago", result: "Warning" },
        { id: 2, sourceCatalogue: "SensorML", tool: "SensorML Harvester", harvestDate: "Today, 11:00 am", assetsAdded: "+275", duration: "1 hours ago", result: "Success" },
        { id: 3, sourceCatalogue: "SensorML", tool: "CrowdSense Harvester", harvestDate: "Yesterday, 2:58 pm", assetsAdded: "+113", duration: "1 day ago", result: "Error" }
      ],
      mappingRows: [
        { id: 1, remoteCatalogue: "DCAT-AP.de", remoteSchema: "Data Service Entity 1.0", remoteSchemaMeta: "", transformationStrategy: "Deterministic RDF", promptsCount: 2, shaclCount: 3 },
        { id: 2, remoteCatalogue: "DCAT-AP.de", remoteSchema: "Energy Product 1.0", remoteSchemaMeta: "5", transformationStrategy: " AI-driven", promptsCount: 1, shaclCount: 2 },
        { id: 3, remoteCatalogue: "OGC SensorML", remoteSchema: "Dataset Schema", remoteSchemaMeta: "v1", transformationStrategy: "Deterministic RDF", promptsCount: 2, shaclCount: 3 },
        { id: 4, remoteCatalogue: "OGC SensorML", remoteSchema: "Mobility Data", remoteSchemaMeta: "Mobility 0.3 Data Service", transformationStrategy: "Hybrid AI Mapping", promptsCount: 0, shaclCount: 0 }
      ],
      // Resize
      resizeTimer: null,
      userAccess: [],
      // Granular per-area CRUD permissions (FR-AC-01)
      userPermissions: {
        local_catalogue: { read: true, create: true, update: true, delete: true },
        catalogue_registry: { read: true, create: true, update: true, delete: true },
        schema_registry: { read: true, create: true, update: true, delete: true },
        harvester: { read: true, create: true, update: true, delete: true },
        admin_tools: { read: true, create: true, update: true, delete: true }
      },
      // Harvest wizard
      harvestWizardStep: 1,
      harvestWizardSearch: "",
      harvestWizardRows: [],
      harvestWizardSelected: [],
      harvestWizardSelectedRows: [],
      harvestWizardRowsBase: [],
      // Remote catalog pending state
      pendingRemoteCatalog: null,
      isRegisteringRemoteCatalog: false,
      registerRemoteCatalogError: "",
      originalRemoteCatalogForm: null,
      isUpdatingRemoteCatalog: false,
      updateRemoteCatalogError: "",
      pendingUpdateRemoteCatalogId: null,
      // Harvest scope
      harvestScope: {
        selected: [],
        typeValue: "",
        queryValue: "",
        fromDate: "",
        toDate: "",
        includeNewAssets: false,
        schemaMappingEnabled: false,
        resolveReferences: false
      },
      // Lifecycle mapping
      lifecycleMapping: {
        performSchemaMapping: true,
        updateHandling: "version",
        deletionHandling: "remove",
        resolveReferences: true
      },
      // Harvest error log (FR-ACM-01)
      harvestLog: [
        { id: 1, catalogue: "SensorML", level: "Error", message: "Remote catalogue unavailable \u2014 connection timed out after 30 s", timestamp: "2026-02-09 11:02 (UTC)" },
        { id: 2, catalogue: "DCAT-AP.de", level: "Warning", message: "Scope 'changed_between' not interpretable by remote \u2014 fell back to full harvest", timestamp: "2026-02-09 11:04 (UTC)" },
        { id: 3, catalogue: "OGC SensorML", level: "Info", message: "Harvest completed successfully \u2014 275 assets imported", timestamp: "2026-02-09 11:05 (UTC)" },
        { id: 4, catalogue: "SensorML", level: "Error", message: "Schema mapping failed for 3 assets \u2014 SHACL validation errors", timestamp: "2026-02-09 11:06 (UTC)" }
      ],
      showHarvestLog: false,
      // Provenance metadata per imported asset (FR-ACM-01)
      harvestProvenance: [
        { assetId: "sensor-asset-001", catalogue: "SensorML", harvestRunId: "run-2026-02-09-001", harvestedAt: "2026-02-09T11:05:00Z", strategy: "Deterministic RDF", promptVersion: null, schemaSource: "OGC SensorML v1.0", originalChecksum: "sha256:a1b2c3d4" },
        { assetId: "dataset-energy-042", catalogue: "DCAT-AP.de", harvestRunId: "run-2026-02-09-001", harvestedAt: "2026-02-09T11:05:12Z", strategy: "AI-driven", promptVersion: "1.0", schemaSource: "DCAT-AP.de v2.0", originalChecksum: "sha256:e5f6a7b8" },
        { assetId: "service-api-007", catalogue: "OGC SensorML", harvestRunId: "run-2026-02-09-001", harvestedAt: "2026-02-09T11:05:18Z", strategy: "Hybrid", promptVersion: "2.0", schemaSource: "ISO 19115-1 v2.0", originalChecksum: "sha256:c9d0e1f2" }
      ],
      overviewToggles: {
        catalogsSelectedEnabled: true,
        mappingStrategiesEnabled: true
      },
      // Batch Re-transformation (FR-SR-13)
      showBatchRetransformModal: false,
      batchRetransform: {
        trigger: "prompt_change",
        // prompt_change | strategy_change | llm_change | manual
        scope: "all",
        // all | catalogue | query
        catalogueFilter: "",
        queryFilter: "",
        dryRun: true,
        status: "idle",
        // idle | running | completed | cancelled | error
        progress: 0,
        totalAssets: 0,
        processedAssets: 0,
        successCount: 0,
        errorCount: 0,
        skippedCount: 0,
        startedAt: "",
        completedAt: "",
        errors: []
      },
      batchRetransformHistory: [
        { id: "br-001", trigger: "Prompt updated (prompt-001 v1.0\u2192v1.1)", scope: "All assets", dryRun: false, total: 275, success: 270, errors: 5, skipped: 0, startedAt: "2026-02-20 14:30", completedAt: "2026-02-20 14:42", status: "completed" },
        { id: "br-002", trigger: "LLM config changed (llm-001)", scope: "Catalogue: SensorML", dryRun: true, total: 120, success: 118, errors: 2, skipped: 0, startedAt: "2026-02-18 09:15", completedAt: "2026-02-18 09:22", status: "completed" }
      ],
      // Multi-Model Provider Support (FR-SR-12)
      llmProviders: [
        { id: "prov-001", name: "OpenAI", type: "openai", apiEndpoint: "https://api.openai.com/v1", models: ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"], isDefault: true, precedence: 1, status: "active", createdAt: "2026-01-05" },
        { id: "prov-002", name: "Anthropic", type: "anthropic", apiEndpoint: "https://api.anthropic.com/v1", models: ["claude-3.5-sonnet", "claude-3-opus", "claude-3-haiku"], isDefault: false, precedence: 2, status: "active", createdAt: "2026-01-10" },
        { id: "prov-003", name: "Local Ollama", type: "ollama", apiEndpoint: "http://localhost:11434/api", models: ["llama3", "mistral", "codellama"], isDefault: false, precedence: 3, status: "inactive", createdAt: "2026-02-01" }
      ],
      showProviderModal: false,
      isEditingProvider: false,
      providerForm: {
        id: null,
        name: "",
        type: "openai",
        apiEndpoint: "",
        models: "",
        isDefault: false,
        precedence: 1,
        status: "active"
      },
      providerFormError: "",
      providerSearch: "",
      // ── Milestone 2: Schema & Mapping Workflows ─────────────
      // Local Schema create modal
      showCreateLocalSchemaModal: false,
      isEditingLocalSchema: false,
      editingLocalSchemaId: null,
      localSchemaForm: {
        schema: "",
        format: "SHACL",
        catalogs: 1,
        localMapping: "",
        versioning: "v1.0",
        trustLevel: "Federated"
      },
      showDeleteSchemaConfirm: false,
      deleteSchemaTargetId: null,
      // Schema version diff
      showSchemaDiffPanel: false,
      schemaDiffRow: null,
      schemaDiffVersionA: "",
      schemaDiffVersionB: "",
      // Add Mapping modal
      showAddMappingModal: false,
      isEditingMapping: false,
      editingMappingId: null,
      addMappingForm: {
        remoteCatalogue: "",
        remoteSchema: "",
        remoteSchemaMeta: "",
        transformationStrategy: "Deterministic RDF",
        promptsCount: 0,
        shaclCount: 0
      },
      // ── Milestone 3: Harvester Live Operations ──────────────
      // Harvest run detail view
      showHarvestRunDetail: false,
      harvestRunDetailData: null,
      // Live harvest progress
      activeHarvest: {
        running: false,
        catalogueName: "",
        progress: 0,
        totalAssets: 0,
        processedAssets: 0,
        successCount: 0,
        errorCount: 0,
        status: "idle",
        startedAt: "",
        errors: []
      },
      _harvestInterval: null,
      // Test Connection feedback
      testConnectionResult: {
        status: "",
        message: "",
        latency: 0
      },
      isTestingConnection: false,
      // Mapping View/Edit detail panel
      showMappingDetailPanel: false,
      mappingDetailRow: null,
      isEditingMappingDetail: false,
      mappingDetailEditForm: {
        remoteCatalogue: "",
        remoteSchema: "",
        remoteSchemaMeta: "",
        transformationStrategy: "Deterministic RDF"
      },
      // ── Milestone 5: Global UX & Safety ────────────────────────
      toasts: [],
      _toastCounter: 0,
      confirmDialog: {
        visible: false,
        title: "",
        message: "",
        confirmLabel: "Delete",
        onConfirm: null
      },
      showDeleteRemoteCatalogConfirm: false,
      deleteRemoteCatalogTargetId: null,
      // ── Milestone 4: Admin Tools & Monitoring ──────────────────
      // Monitoring dashboard
      monitoringMetrics: {
        systemUptime: "99.7%",
        avgResponseTime: "245ms",
        totalHarvestsToday: 12,
        failedHarvestsToday: 1,
        activeConnections: 8,
        queuedJobs: 3,
        diskUsage: "42%",
        memoryUsage: "67%"
      },
      monitoringEvents: [
        { id: 1, type: "info", source: "Harvester", message: "Scheduled harvest completed for SensorML", timestamp: "2026-03-05 12:58 (UTC)" },
        { id: 2, type: "warning", source: "Schema Mapper", message: "SHACL validation returned 3 minor warnings for DCAT-AP.de batch", timestamp: "2026-03-05 12:45 (UTC)" },
        { id: 3, type: "error", source: "Remote Catalogue", message: "Connection to OGC SensorML endpoint timed out after 30s", timestamp: "2026-03-05 12:30 (UTC)" },
        { id: 4, type: "info", source: "System", message: "Automatic backup completed successfully", timestamp: "2026-03-05 12:00 (UTC)" },
        { id: 5, type: "info", source: "Auth", message: "User 'admin@facis.eu' logged in", timestamp: "2026-03-05 11:45 (UTC)" },
        { id: 6, type: "warning", source: "LLM Provider", message: "OpenAI rate limit approached \u2014 85% of quota used", timestamp: "2026-03-05 11:30 (UTC)" },
        { id: 7, type: "info", source: "Harvester", message: "275 assets imported from DCAT-AP.de", timestamp: "2026-03-05 11:00 (UTC)" },
        { id: 8, type: "error", source: "Schema Mapper", message: "LLM transformation failed for 2 assets \u2014 timeout exceeded", timestamp: "2026-03-05 10:30 (UTC)" }
      ],
      monitoringEventFilter: "all",
      monitoringAuditSearch: "",
      // Service status
      serviceStatus: [
        { name: "Harvest Engine", status: "operational", lastCheck: "2 min ago" },
        { name: "Schema Mapper", status: "operational", lastCheck: "1 min ago" },
        { name: "LLM Gateway", status: "degraded", lastCheck: "5 min ago" },
        { name: "SPARQL Endpoint", status: "operational", lastCheck: "3 min ago" },
        { name: "Remote Catalogue Proxy", status: "operational", lastCheck: "1 min ago" }
      ],
      // User profile
      showUserProfile: false,
      userProfile: {
        name: "Admin User",
        email: "admin@facis.eu",
        role: "Administrator",
        organization: "Facis DCM",
        lastLogin: "2026-03-05 11:45 (UTC)",
        memberSince: "2025-09-01",
        sessionsToday: 3
      },
      passwordForm: {
        currentPassword: "",
        newPassword: "",
        confirmPassword: ""
      },
      passwordFormError: "",
      passwordFormSuccess: "",
      // Access map
      accessMap: {
        "Local Catalogue": "local_catalogue",
        "Catalogue Registry": "catalogue_registry",
        "Schema Registry": "schema_registry",
        "Harvest": "harvester",
        "Admin Tools": "admin_tools"
      }
    };
  }

  // src/utils/formatters.js
  function statusClass(status) {
    if (status === "Active") return "green";
    if (status === "Warning") return "yellow";
    if (status === "Error") return "red";
    return "gray";
  }
  function trustClass(level) {
    if (level === "Hybrid AI Mapping") return "green";
    if (level === "Deterministic RDF") return "yellow";
    if (level === "AI-driven") return "blue";
    return "gray";
  }
  function roleClass(role) {
    if (role === "Harvester") return "blue";
    if (role === "Schema Admin") return "green";
    if (role === "Administrator") return "red";
    return "gray";
  }
  function resultClass(result) {
    if (result === "Success") return "green";
    if (result === "Warning") return "yellow";
    if (result === "Error") return "red";
    return "gray";
  }
  function logPillClass(level) {
    if (level === "Info") return "blue";
    if (level === "Warning") return "yellow";
    if (level === "Error") return "red";
    return "gray";
  }
  function namespaceClass(ns) {
    const v = String(ns || "").trim().toLowerCase();
    if (v === "ex:" || v === "ex") return "green";
    if (v === "dcat:" || v === "dcat") return "blue";
    if (v === "dct:" || v === "dct") return "yellow";
    return "gray";
  }
  function strategyPillClass(strategy) {
    const v = String(strategy || "").toLowerCase();
    if (v.includes("deterministic")) return "yellow";
    if (v.includes("hybrid")) return "green";
    if (v.includes("ai")) return "blue";
    return "gray";
  }
  function strategyLabel(code) {
    const m = {
      none: "None",
      ai: "AI-driven",
      hybrid: "Hybrid AI Mapping",
      deterministic: "Deterministic RDF"
    };
    return m[code] || code || "None";
  }
  function getAccessInitial(key) {
    const map = {
      local_catalogue: "L",
      catalogue_registry: "C",
      schema_registry: "S",
      admin_tools: "A",
      harvester: "H"
    };
    return map[key] || "?";
  }

  // src/utils/helpers.js
  function getCookie(name) {
    const value = "; " + document.cookie;
    const parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  }
  function normalizeText(v) {
    return String(v ?? "").toLowerCase().trim();
  }
  function normalizeFilter(val) {
    if (!val) return "";
    if (val === "All") return "";
    return val;
  }
  function paginate(list, page, perPage) {
    const total = list.length;
    const startIndex = (page - 1) * perPage;
    const endIndex = startIndex + perPage;
    return {
      total,
      totalPages: Math.ceil(total / perPage),
      rows: list.slice(startIndex, endIndex),
      showingStart: total === 0 ? 0 : startIndex + 1,
      showingEnd: Math.min(endIndex, total)
    };
  }
  function matchValue(value, needle) {
    if (!needle) return null;
    if (value == null) return null;
    const t = typeof value;
    if (t === "string" || t === "number" || t === "boolean") {
      const s = String(value);
      return normalizeText(s).includes(needle) ? s : null;
    }
    if (Array.isArray(value)) {
      for (const v of value) {
        const r = matchValue(v, needle);
        if (r != null) return r;
      }
      return null;
    }
    if (t === "object") {
      for (const v of Object.values(value)) {
        const r = matchValue(v, needle);
        if (r != null) return r;
      }
      return null;
    }
    return null;
  }
  function getCatalogAssets(catalogItem) {
    const a = catalogItem?.assets;
    const out = [];
    if (Array.isArray(a?.documents)) out.push(...a.documents);
    if (Array.isArray(a?.parts)) out.push(...a.parts);
    else if (a?.parts && typeof a.parts === "object") out.push(a.parts);
    if (Array.isArray(a?.items)) out.push(...a.items);
    if (Array.isArray(a)) out.push(...a);
    return out;
  }
  function getAssetTitle(asset) {
    return asset?.title || asset?.name || asset?.label || asset?.identifier || asset?.assetId || asset?.id || asset?.uri || asset?.url || asset?.meta?.title || asset?.metadata?.title || "-";
  }
  function assetMatchesQuery(asset, needle) {
    return matchValue(asset, needle) != null;
  }
  function getChangedFields(oldObj, newObj) {
    const patch = {};
    const keys = /* @__PURE__ */ new Set([
      ...Object.keys(oldObj || {}),
      ...Object.keys(newObj || {})
    ]);
    keys.forEach((k) => {
      if (oldObj?.[k] !== newObj?.[k]) patch[k] = newObj?.[k];
    });
    return patch;
  }
  function parseJsonLine(text) {
    const match = text.match(/^(\s*)"([^"]+)"\s*:\s*"([^"]*)"(.*)$/);
    if (!match) return null;
    return {
      indent: match[1],
      key: match[2],
      value: match[3],
      suffix: match[4]
    };
  }

  // src/modals/ViewModal.js
  var ViewModal_default = {
    name: "ViewModal",
    template: "#tpl-view-modal",
    props: {
      visible: { type: Boolean, default: false },
      currentViewTab: { type: String, default: "Overview" },
      transformationSummary: { type: Array, default: () => [] },
      validation: { type: Object, default: () => ({}) },
      auditMini: { type: Array, default: () => [] },
      auditRows: { type: Array, default: () => [] },
      auditSearch: { type: String, default: "" },
      auditFilters: { type: Object, default: () => ({}) },
      originalJsonLines: { type: Array, default: () => [] },
      localJsonLines: { type: Array, default: () => [] }
    },
    emits: [
      "close",
      "update:currentViewTab",
      "update:auditSearch",
      "update:auditFilters",
      "export-audit",
      "clear-audit-filters"
    ],
    computed: {
      filteredAuditMini() {
        const q = this.auditSearch.trim().toLowerCase();
        if (!q) return this.auditMini;
        return this.auditMini.filter(
          (r) => (r.level || "").toLowerCase().includes(q) || (r.step || "").toLowerCase().includes(q) || (r.timestamp || "").toLowerCase().includes(q)
        );
      },
      filteredAuditRows() {
        const f = this.auditFilters || {};
        return this.auditRows.filter((row) => {
          if (f.assetId && !(row.assetId || "").toLowerCase().includes(f.assetId.toLowerCase())) return false;
          if (f.catalogueId && (row.catalogueId || "") !== f.catalogueId) return false;
          if (f.promptVersion && (row.promptVersion || "") !== f.promptVersion) return false;
          if (f.status && (row.status || "") !== f.status) return false;
          if (f.dateFrom) {
            const rowDate = (row.timestamp || "").slice(0, 10);
            if (rowDate < f.dateFrom) return false;
          }
          if (f.dateTo) {
            const rowDate = (row.timestamp || "").slice(0, 10);
            if (rowDate > f.dateTo) return false;
          }
          return true;
        });
      },
      auditCatalogueOptions() {
        const set = /* @__PURE__ */ new Set();
        this.auditRows.forEach((r) => {
          if (r.catalogueId) set.add(r.catalogueId);
        });
        return Array.from(set).sort();
      },
      auditPromptVersionOptions() {
        const set = /* @__PURE__ */ new Set();
        this.auditRows.forEach((r) => {
          if (r.promptVersion) set.add(r.promptVersion);
        });
        return Array.from(set).sort();
      },
      auditStatusOptions() {
        const set = /* @__PURE__ */ new Set();
        this.auditRows.forEach((r) => {
          if (r.status) set.add(r.status);
        });
        return Array.from(set).sort();
      },
      hasActiveFilters() {
        const f = this.auditFilters || {};
        return !!(f.assetId || f.catalogueId || f.promptVersion || f.status || f.dateFrom || f.dateTo);
      }
    },
    methods: {
      logPillClass,
      parseJsonLine,
      updateFilter(key, value) {
        this.$emit("update:auditFilters", { ...this.auditFilters, [key]: value });
      },
      exportAudit(format) {
        this.$emit("export-audit", format);
      }
    }
  };

  // src/modals/InviteModal.js
  var InviteModal_default = {
    name: "InviteModal",
    template: "#tpl-invite-modal",
    props: {
      visible: { type: Boolean, default: false },
      inviteForm: { type: Object, required: true }
    },
    emits: ["close", "send-invite", "update:inviteForm"],
    computed: {
      canSendInvite() {
        const f = this.inviteForm;
        return f.firstName.trim() && f.lastName.trim() && f.email.trim() && f.role && f.expiresIn;
      }
    }
  };

  // src/modals/ManageUserModal.js
  var ManageUserModal_default = {
    name: "ManageUserModal",
    template: "#tpl-manage-user-modal",
    props: {
      visible: { type: Boolean, default: false },
      manageForm: { type: Object, required: true }
    },
    emits: ["close", "send-manage"],
    computed: {
      canSendManageUser() {
        const m = this.manageForm;
        return m.firstName.trim() && m.lastName.trim() && m.email.trim() && m.selectedRoles.length > 0 && m.expiresIn;
      }
    }
  };

  // src/modals/RegisterCatalogModal.js
  var RegisterCatalogModal_default = {
    name: "RegisterCatalogModal",
    template: "#tpl-register-catalog-modal",
    props: {
      visible: { type: Boolean, default: false },
      remoteCatalogForm: { type: Object, required: true },
      isEditingRemoteCatalog: { type: Boolean, default: false },
      isSavingRemoteCatalog: { type: Boolean, default: false },
      registerRemoteCatalogError: { type: String, default: "" },
      updateRemoteCatalogError: { type: String, default: "" },
      isTestingConnection: { type: Boolean, default: false },
      testConnectionResult: { type: Object, default: () => ({ status: "", message: "", latency: 0 }) }
    },
    emits: ["close", "save", "test-connection"]
  };

  // src/modals/SchemaModal.js
  var SchemaModal_default = {
    name: "SchemaModal",
    template: "#tpl-schema-modal",
    props: {
      visible: { type: Boolean, default: false },
      modalTitle: { type: String, default: "Register Remote Schema" },
      registerSchemaForm: { type: Object, required: true },
      schemaSummaries: { type: Object, default: () => ({}) }
    },
    emits: ["close", "save", "remove-catalog", "add-catalog"],
    computed: {
      currentSummaryText() {
        const t = this.registerSchemaForm.summaryTab;
        return this.schemaSummaries[t] || "";
      },
      filteredRemoteCatalogs() {
        const q = (this.registerSchemaForm.catalogSearch || "").toLowerCase().trim();
        if (!q) return this.registerSchemaForm.remoteCatalogs;
        return this.registerSchemaForm.remoteCatalogs.filter((c) => c.toLowerCase().includes(q));
      }
    },
    methods: {
      namespaceClass
    }
  };

  // src/modals/HarvestWizardModal.js
  var HarvestWizardModal_default = {
    name: "HarvestWizardModal",
    template: "#tpl-harvest-wizard-modal",
    props: {
      visible: { type: Boolean, default: false },
      harvestWizardStep: { type: Number, default: 1 },
      harvestWizardSearch: { type: String, default: "" },
      harvestWizardPagination: { type: Object, required: true },
      harvestWizardSelectedRows: { type: Array, default: () => [] },
      isWizardAllSelected: { type: Boolean, default: false },
      pagination: { type: Object, required: true },
      pageWindowFn: { type: Function, required: true },
      harvestScope: { type: Object, required: true },
      lifecycleMapping: { type: Object, required: true },
      wizardSelectedCount: { type: Number, default: 0 },
      overviewScopeLines: { type: Array, default: () => [] },
      overviewLifecycleLines: { type: Array, default: () => [] },
      overviewMappingCounts: { type: Object, default: () => ({}) },
      isAllAssetsSelected: { type: Boolean, default: false },
      showIncludeNewAssetsToggle: { type: Boolean, default: false }
    },
    emits: [
      "close",
      "next-step",
      "prev-step",
      "start-harvest",
      "update:harvestWizardSearch",
      "update:harvestWizardSelectedRows",
      "update:harvestWizardStep",
      "run-wizard-search",
      "toggle-wizard-select-all",
      "toggle-scope-option",
      "toggle-lifecycle-card",
      "page-change"
    ],
    methods: {
      setPage(key, page) {
        this.$emit("page-change", { key, page });
      }
    }
  };

  // src/modals/AccessInfoModal.js
  var AccessInfoModal_default = {
    name: "AccessInfoModal",
    template: "#tpl-access-info-modal",
    props: {
      visible: { type: Boolean, default: false }
    },
    emits: ["close"]
  };

  // src/modals/ManageMenu.js
  var ManageMenu_default = {
    name: "ManageMenu",
    template: "#tpl-manage-menu",
    props: {
      manageMenu: { type: Object, required: true }
    },
    emits: ["close", "delete-user", "edit-user"]
  };

  // src/main.js
  uibuilderService.init();
  var { createApp, toRaw } = Vue;
  var app = createApp({
    data() {
      return createStoreData();
    },
    computed: {
      catalogPagination() {
        return paginate(this.tableRows, this.pagination.catalog.page, this.pagination.catalog.perPage);
      },
      schemaPagination() {
        return paginate(this.schemaRegistry, this.pagination.schema.page, this.pagination.schema.perPage);
      },
      remoteSchemaPagination() {
        return paginate(this.remoteSchema, this.pagination.remoteSchema.page, this.pagination.remoteSchema.perPage);
      },
      mappingPagination() {
        return paginate(this.mappingRows, this.pagination.mapping.page, this.pagination.mapping.perPage);
      },
      catalogsRegisterPagination() {
        const tableRows = this.catalogsTable.map((c) => ({
          id: c.id || c.uniqueId,
          catalogName: c.catalogName,
          ownerContact: c.owner,
          transformationStrategy: strategyLabel(c.strategy),
          accessUrl: c.baseEndpoint,
          enabled: !!c.enabled,
          _catalog: c
        }));
        return paginate(tableRows, this.pagination.catalogsRegister.page, this.pagination.catalogsRegister.perPage);
      },
      usersPagination() {
        return paginate(this.users, this.pagination.users.page, this.pagination.users.perPage);
      },
      harvestPagination() {
        return paginate(this.harvestRecords, this.pagination.harvest.page, this.pagination.harvest.perPage);
      },
      harvestWizardPagination() {
        return paginate(this.harvestWizardRows, this.pagination.harvestWizard.page, this.pagination.harvestWizard.perPage);
      },
      isWizardAllSelected() {
        const ids = this.harvestWizardRows.map((r) => r.id);
        if (!ids.length) return false;
        return ids.every((id) => this.harvestWizardSelectedRows.includes(id));
      },
      canSendInvite() {
        const f = this.inviteForm;
        return f.firstName.trim() && f.lastName.trim() && f.email.trim() && f.role && f.expiresIn;
      },
      canSendManageUser() {
        const m = this.manageForm;
        return m.firstName.trim() && m.lastName.trim() && m.email.trim() && m.selectedRoles.length > 0 && m.expiresIn;
      },
      currentSummaryText() {
        return this.schemaSummaries[this.registerSchemaForm.summaryTab] || "";
      },
      filteredRemoteCatalogs() {
        const q = (this.registerSchemaForm.catalogSearch || "").toLowerCase().trim();
        if (!q) return this.registerSchemaForm.remoteCatalogs;
        return this.registerSchemaForm.remoteCatalogs.filter((c) => c.toLowerCase().includes(q));
      },
      filteredPrompts() {
        const q = (this.promptSearch || "").trim().toLowerCase();
        if (!q) return this.prompts;
        return this.prompts.filter(
          (p) => (p.id || "").toLowerCase().includes(q) || (p.sourceSchema || "").toLowerCase().includes(q) || (p.targetSchema || "").toLowerCase().includes(q) || (p.status || "").toLowerCase().includes(q)
        );
      },
      promptTemplateParts() {
        const tpl = this.promptForm.template || "";
        const parts = [];
        const regex = /(\{SOURCE_ASSET\}|\{SOURCE_SCHEMA\}|\{TARGET_SCHEMA\}|\{EXAMPLES\}|\{CONSTRAINTS\})/g;
        let last = 0;
        let match;
        while ((match = regex.exec(tpl)) !== null) {
          if (match.index > last) parts.push({ text: tpl.slice(last, match.index), isVar: false });
          parts.push({ text: match[1], isVar: true });
          last = regex.lastIndex;
        }
        if (last < tpl.length) parts.push({ text: tpl.slice(last), isVar: false });
        return parts;
      },
      filteredLlmConfigs() {
        const q = (this.llmConfigSearch || "").trim().toLowerCase();
        if (!q) return this.llmConfigs;
        return this.llmConfigs.filter(
          (c) => (c.id || "").toLowerCase().includes(q) || (c.name || "").toLowerCase().includes(q) || (c.provider || "").toLowerCase().includes(q) || (c.model || "").toLowerCase().includes(q) || (c.status || "").toLowerCase().includes(q)
        );
      },
      resolvedPromptPreview() {
        if (!this.promptTestSelectedPrompt || !this.promptTestSampleInput) return "";
        const p = this.prompts.find((x) => x.id === this.promptTestSelectedPrompt);
        if (!p) return "";
        let tpl = p.template || "";
        tpl = tpl.replace(/\{SOURCE_ASSET\}/g, this.promptTestSampleInput);
        tpl = tpl.replace(/\{SOURCE_SCHEMA\}/g, p.sourceSchema || "");
        tpl = tpl.replace(/\{TARGET_SCHEMA\}/g, p.targetSchema || "");
        tpl = tpl.replace(/\{EXAMPLES\}/g, p.examples || "");
        tpl = tpl.replace(/\{CONSTRAINTS\}/g, p.constraints || "");
        return tpl;
      },
      filteredAuditMini() {
        const q = this.auditSearch.trim().toLowerCase();
        if (!q) return this.auditMini;
        return this.auditMini.filter(
          (r) => (r.level || "").toLowerCase().includes(q) || (r.step || "").toLowerCase().includes(q) || (r.timestamp || "").toLowerCase().includes(q)
        );
      },
      filteredMonitoringEvents() {
        const f = this.monitoringEventFilter;
        const q = (this.monitoringAuditSearch || "").trim().toLowerCase();
        let events = this.monitoringEvents;
        if (f !== "all") events = events.filter((e) => e.type === f);
        if (q) events = events.filter(
          (e) => (e.source || "").toLowerCase().includes(q) || (e.message || "").toLowerCase().includes(q) || (e.timestamp || "").toLowerCase().includes(q)
        );
        return events;
      },
      catalogOptions() {
        const set = /* @__PURE__ */ new Set();
        for (const item of this.allCatalogsRaw) {
          const v = item?.catalog?.catalogId;
          if (v) set.add(String(v));
        }
        return Array.from(set).sort();
      },
      typeOptions() {
        const set = /* @__PURE__ */ new Set();
        for (const item of this.allCatalogsRaw) {
          const docs = item?.assets?.documents || [];
          for (const d of docs) {
            if (d?.format) set.add(String(d.format));
          }
        }
        return Array.from(set).sort();
      },
      domainOptions() {
        const set = /* @__PURE__ */ new Set();
        for (const item of this.allCatalogsRaw) {
          const v = item?.catalog?.publisher?.website;
          if (v) set.add(String(v));
        }
        return Array.from(set).sort();
      },
      statusOptions() {
        return ["Active", "Warning", "Error"];
      },
      pageWindow() {
        return (key, size = 5) => {
          const p = this.pagination[key].page;
          const total = this[`${key}Pagination`]?.totalPages || 1;
          const start = Math.min(p, Math.max(1, total - size + 1));
          const end = Math.min(total, start + size - 1);
          const pages = [];
          for (let i = start; i <= end; i++) pages.push(i);
          return pages;
        };
      },
      isSavingRemoteCatalog() {
        return this.isRegisteringRemoteCatalog || this.isUpdatingRemoteCatalog;
      },
      inverseAccessMap() {
        const inv = {};
        Object.entries(this.accessMap || {}).forEach(([label, key]) => {
          inv[key] = label;
        });
        return inv;
      },
      wizardSelectedCatalogRows() {
        const set = new Set(this.harvestWizardSelectedRows);
        return (this.tableRows || []).filter((r) => set.has(r.id));
      },
      wizardSelectedCount() {
        return this.wizardSelectedCatalogRows.length;
      },
      overviewScopeLines() {
        const s = this.harvestScope || {};
        const selected = Array.isArray(s.selected) ? s.selected : [];
        const lines = [];
        const has = (k) => selected.includes(k);
        if (has("all_assets")) return ["All assets in the remote catalogue"];
        if (has("by_type")) lines.push(`All assets of type: ${s.typeValue || "-"}`);
        if (has("matching_query")) lines.push(`Assets matching a query: ${s.queryValue || "-"}`);
        if (has("ever_imported")) lines.push("All assets ever imported from that remote catalogue");
        if (has("last_harvest")) lines.push("Assets imported in the last harvest");
        if (has("changed_between")) {
          lines.push(`Assets changed between: ${s.fromDate || "-"} \u2192 ${s.toDate || "-"}`);
        }
        if (has("last_harvest_scope")) lines.push("All assets in scope of last harvest");
        if ((has("ever_imported") || has("last_harvest")) && !!s.includeNewAssets) {
          lines.push("Include any new assets in remote catalogue");
        }
        return lines.length ? lines : ["\u2014 No scope selected"];
      },
      overviewLifecycleLines() {
        const l = this.lifecycleMapping;
        const updateText = l.updateHandling === "version" ? "Update Handling: Create new version" : "Update Handling: Create new catalog for new assets";
        const deletionText = l.deletionHandling === "remove" ? "Deletion Handling: Remove deleted assets" : "Deletion Handling: Retain copy of old assets";
        const lines = [updateText, deletionText];
        return lines;
      },
      overviewMappingCounts() {
        const rows = Array.isArray(this.catalogsTable) ? this.catalogsTable : [];
        const counts = { ai: 0, hybrid: 0, deterministic: 0, none: 0 };
        rows.forEach((r) => {
          const st = r.strategy || r.transformationStrategy || "none";
          if (st === "ai" || st === "AI-driven") counts.ai++;
          else if (st === "hybrid" || st === "Hybrid") counts.hybrid++;
          else if (st === "deterministic" || st === "Deterministic RDF") counts.deterministic++;
          else counts.none++;
        });
        return counts;
      },
      isAllAssetsSelected() {
        return this.harvestScope.selected.includes("all_assets");
      },
      showIncludeNewAssetsToggle() {
        const s = this.harvestScope.selected;
        return s.includes("last_harvest") || s.includes("ever_imported");
      }
    },
    watch: {
      isViewModal(val) {
        document.body.style.overflow = val ? "hidden" : "";
      },
      isInviteModal(v) {
        document.body.style.overflow = v ? "hidden" : "";
      },
      currentPage(newPage) {
        if (newPage === "catalogueRegistry") {
          uibuilderService.send({
            type: "getCatalogRegistry",
            auth: { userToken: getCookie("userToken"), clientId: getCookie("uibuilder-client-id") }
          });
        }
        if (newPage === "adminTools") {
          uibuilderService.send({
            type: "getAdminTools",
            auth: { userToken: getCookie("userToken"), clientId: getCookie("uibuilder-client-id") }
          });
        }
      }
    },
    methods: {
      // ── Formatters (delegated) ─────────────────────────────────
      statusClass,
      trustClass,
      roleClass,
      resultClass,
      logPillClass,
      namespaceClass,
      strategyPillClass,
      strategyLabel,
      getAccessInitial,
      parseJsonLine,
      // ── Helpers ────────────────────────────────────────────────
      getCookie,
      hasAccess(key) {
        return this.userAccess.includes(key);
      },
      canRead(area) {
        return !!(this.userPermissions[area] && this.userPermissions[area].read);
      },
      canCreate(area) {
        return !!(this.userPermissions[area] && this.userPermissions[area].create);
      },
      canUpdate(area) {
        return !!(this.userPermissions[area] && this.userPermissions[area].update);
      },
      canDelete(area) {
        return !!(this.userPermissions[area] && this.userPermissions[area].delete);
      },
      // ── Pagination ─────────────────────────────────────────────
      paginate,
      handlePageChange(evt) {
        this.pagination[evt.key].page = evt.page;
      },
      setPerPageByViewport() {
        const h = window.innerHeight;
        let perPage;
        if (h < 800) perPage = 4;
        else if (h < 900) perPage = 6;
        else if (h < 1e3) perPage = 8;
        else perPage = 10;
        Object.keys(this.pagination).forEach((key) => {
          const p = this.pagination[key];
          if (p.perPage !== perPage) {
            p.perPage = perPage;
            const total = this.getTotalFor(key);
            const totalPages = Math.max(1, Math.ceil(total / p.perPage));
            if (p.page > totalPages) p.page = totalPages;
          }
        });
      },
      getTotalFor(key) {
        switch (key) {
          case "catalog":
            return this.tableRows.length;
          case "schema":
            return this.schemaRegistry.length;
          case "catalogsRegister":
            return this.catalogsTable.length;
          case "users":
            return this.users.length;
          case "harvest":
            return this.harvestRecords.length;
          default:
            return 0;
        }
      },
      onResize() {
        clearTimeout(this.resizeTimer);
        this.resizeTimer = setTimeout(() => this.setPerPageByViewport(), 150);
      },
      // ── Local Catalogue ────────────────────────────────────────
      async loadLocalCatalogs() {
        try {
          const res = await fetch("./local_catalogs_20.json");
          const data = await res.json();
          this.allCatalogsRaw = Array.isArray(data?.catalogs) ? data.catalogs : [];
          this.applySearchResults(this.allCatalogsRaw);
        } catch (err) {
          console.error("Failed to load local_catalogs_20.json:", err);
        }
      },
      applySearchResults(rawList) {
        this.pagination.catalog.page = 1;
        this.tableRows = rawList.map((item, i) => ({
          id: i + 1,
          assets: item?.assets?.parts?.title ?? "-",
          type: item?.assets?.documents?.[0]?.format ?? "-",
          name: item?.vehicles?.[0]?.brand ?? "-",
          domain: item?.catalog?.publisher?.website ?? "-",
          updated: item?.catalog?.updatedAt ?? "-",
          integrationStatus: "Active"
        }));
      },
      runSearch() {
        const q = normalizeText(this.searchText);
        const fCatalog = normalizeFilter(this.filters.catalog);
        const fType = normalizeFilter(this.filters.type);
        const fDomain = normalizeFilter(this.filters.domain);
        const fStatus = normalizeFilter(this.filters.status);
        if (!q) {
          const filteredRaw = this.allCatalogsRaw.filter((item) => {
            if (fCatalog && String(item?.catalog?.catalogId) !== String(fCatalog)) return false;
            if (fDomain && String(item?.catalog?.publisher?.website) !== String(fDomain)) return false;
            if (fType) {
              const docs = item?.assets?.documents || [];
              if (!docs.some((d) => String(d?.format) === String(fType))) return false;
            }
            if (fStatus && "Active" !== fStatus) return false;
            return true;
          });
          this.applySearchResults(filteredRaw);
          this.pagination.catalog.page = 1;
          return;
        }
        const rows = [];
        this.allCatalogsRaw.forEach((item, catalogIndex) => {
          if (fCatalog && String(item?.catalog?.catalogId) !== String(fCatalog)) return;
          if (fDomain && String(item?.catalog?.publisher?.website) !== String(fDomain)) return;
          const assets = getCatalogAssets(item);
          const filteredAssets = !fType ? assets : assets.filter((a) => !a?.format || String(a?.format) === String(fType));
          filteredAssets.forEach((asset, assetIndex) => {
            if (!assetMatchesQuery(asset, q)) return;
            rows.push({
              id: `c${catalogIndex}-a${assetIndex}`,
              assets: getAssetTitle(asset),
              type: asset?.format ?? (item?.assets?.documents?.[0]?.format ?? "-"),
              name: item?.vehicles?.[0]?.brand ?? "-",
              domain: item?.catalog?.publisher?.website ?? "-",
              updated: item?.catalog?.updatedAt ?? "-",
              integrationStatus: "Active"
            });
          });
        });
        this.tableRows = rows;
        this.pagination.catalog.page = 1;
      },
      clearFilters() {
        this.searchText = "";
        this.filters = { catalog: "", type: "", domain: "", status: "" };
        this.pagination.catalog.page = 1;
        this.runSearch();
      },
      // ── Asset Detail Panel (Milestone 1) ──────────────────────
      openAssetDetail(row) {
        this.assetDetailRow = { ...row };
        this.isEditingAsset = false;
        this.showAssetDetailPanel = true;
      },
      closeAssetDetail() {
        this.showAssetDetailPanel = false;
        this.assetDetailRow = null;
        this.isEditingAsset = false;
      },
      startEditAsset() {
        if (!this.assetDetailRow) return;
        this.assetEditForm = {
          assets: this.assetDetailRow.assets,
          type: this.assetDetailRow.type,
          name: this.assetDetailRow.name,
          domain: this.assetDetailRow.domain,
          integrationStatus: this.assetDetailRow.integrationStatus
        };
        this.isEditingAsset = true;
      },
      cancelEditAsset() {
        this.isEditingAsset = false;
      },
      saveEditAsset() {
        if (!this.assetDetailRow) return;
        const idx = this.tableRows.findIndex((r) => r.id === this.assetDetailRow.id);
        if (idx !== -1) {
          const updated = { ...this.tableRows[idx], ...this.assetEditForm, updated: (/* @__PURE__ */ new Date()).toISOString().slice(0, 10) };
          this.tableRows.splice(idx, 1, updated);
          this.assetDetailRow = { ...updated };
        }
        this.isEditingAsset = false;
        this.addToast("success", "Asset updated.");
      },
      deleteAsset(id) {
        this.tableRows = this.tableRows.filter((r) => r.id !== id);
        this.selectedRows = this.selectedRows.filter((x) => x !== id);
        if (this.assetDetailRow && this.assetDetailRow.id === id) {
          this.closeAssetDetail();
        }
        this.addToast("success", "Asset deleted.");
      },
      confirmDeleteAsset(id) {
        this.showConfirm("Delete Asset", "Are you sure you want to delete this asset? This action cannot be undone.", "Delete", () => this.deleteAsset(id));
      },
      archiveAsset(id) {
        const idx = this.tableRows.findIndex((r) => r.id === id);
        if (idx !== -1) {
          this.tableRows.splice(idx, 1, { ...this.tableRows[idx], integrationStatus: "Archived" });
          if (this.assetDetailRow && this.assetDetailRow.id === id) {
            this.assetDetailRow = { ...this.tableRows[idx] };
          }
        }
        this.addToast("success", "Asset archived.");
      },
      // ── Bulk Actions (Milestone 1) ─────────────────────────────
      bulkDeleteAssets() {
        if (!this.selectedRows.length) return;
        const count = this.selectedRows.length;
        this.showConfirm("Delete Assets", `Are you sure you want to delete ${count} selected asset${count > 1 ? "s" : ""}? This action cannot be undone.`, "Delete", () => {
          this.tableRows = this.tableRows.filter((r) => !this.selectedRows.includes(r.id));
          if (this.assetDetailRow && this.selectedRows.includes(this.assetDetailRow.id)) {
            this.closeAssetDetail();
          }
          this.selectedRows = [];
          this.addToast("success", `${count} asset${count > 1 ? "s" : ""} deleted.`);
        });
      },
      bulkChangeStatus(status) {
        if (!this.selectedRows.length) return;
        const set = new Set(this.selectedRows);
        this.tableRows = this.tableRows.map((r) => set.has(r.id) ? { ...r, integrationStatus: status } : r);
        this.selectedRows = [];
      },
      bulkExportAssets() {
        if (!this.selectedRows.length) return;
        const set = new Set(this.selectedRows);
        const rows = this.tableRows.filter((r) => set.has(r.id));
        const headers = ["ID", "Assets", "Type", "Name", "Domain", "Updated", "Integration Status"];
        const csvRows = rows.map((r) => [r.id, r.assets, r.type, r.name, r.domain, r.updated, r.integrationStatus].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(","));
        const content = [headers.join(","), ...csvRows].join("\n");
        const blob = new Blob([content], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "assets-export.csv";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      },
      toggleSelectAll(e) {
        if (e.target.checked) {
          this.selectedRows = this.catalogPagination.rows.map((r) => r.id);
        } else {
          this.selectedRows = [];
        }
      },
      // ── Catalog Registry ───────────────────────────────────────
      toggleCatalogEnabled(id, e) {
        const c = this.catalogsTable.find((x) => x.id === id);
        if (c) c.enabled = !!e.target.checked;
      },
      openRegisterRemoteCatalogModal() {
        this.isEditingRemoteCatalog = false;
        this.editingRemoteCatalogId = null;
        this.remoteCatalogForm = {
          catalogId: "",
          catalogName: "",
          owner: "",
          protocol: "Query interface",
          baseEndpoint: "",
          mimeType: "application/sparql-results+json",
          queryEndpoint: "",
          queryLanguages: "",
          metadataPrefix: "oai_dc",
          setSpec: "",
          resumptionToken: false,
          dcatCatalogUri: "",
          linkedDataEndpoint: "",
          contentNegotiation: "application/ld+json",
          strategy: "none",
          promptId: "",
          llmConfigId: "",
          namespacesToPreserve: "",
          shaclShapeId: "",
          auth: "none",
          trustAnchor: "",
          enabled: true
        };
        this.showRegisterRemoteCatalogModal = true;
      },
      openEditRemoteCatalog(row) {
        this.isEditingRemoteCatalog = true;
        this.editingRemoteCatalogId = row.id;
        this.remoteCatalogForm = JSON.parse(JSON.stringify(row));
        this.originalRemoteCatalogForm = JSON.parse(JSON.stringify(row));
        this.showRegisterRemoteCatalogModal = true;
      },
      closeRegisterRemoteCatalogModal() {
        this.showRegisterRemoteCatalogModal = false;
      },
      testRemoteCatalogConnection() {
        this.isTestingConnection = true;
        this.testConnectionResult = { status: "", message: "", latency: 0 };
        const start = Date.now();
        setTimeout(() => {
          const latency = Date.now() - start;
          const endpoint = this.remoteCatalogForm.baseEndpoint || "";
          if (!endpoint.trim()) {
            this.testConnectionResult = { status: "error", message: "No endpoint URL provided.", latency: 0 };
          } else {
            this.testConnectionResult = { status: "success", message: `Connection successful to ${endpoint}`, latency };
          }
          this.isTestingConnection = false;
        }, 800 + Math.random() * 700);
      },
      registerRemoteCatalog() {
        const payload = JSON.parse(JSON.stringify(this.remoteCatalogForm));
        this.registerRemoteCatalogError = "";
        this.isRegisteringRemoteCatalog = true;
        this.pendingRemoteCatalog = payload;
        uibuilderService.send({
          type: "registerRemoteCatalog",
          auth: { userToken: getCookie("userToken"), clientId: getCookie("uibuilder-client-id") },
          data: payload
        });
      },
      saveRemoteCatalog() {
        const current = JSON.parse(JSON.stringify(this.remoteCatalogForm));
        if (this.isEditingRemoteCatalog && this.editingRemoteCatalogId != null) {
          const old = this.originalRemoteCatalogForm || {};
          const patch = getChangedFields(old, current);
          if (Object.keys(patch).length === 0) {
            this.closeRegisterRemoteCatalogModal();
            return;
          }
          this.isUpdatingRemoteCatalog = true;
          this.updateRemoteCatalogError = "";
          this.pendingUpdateRemoteCatalogId = this.editingRemoteCatalogId;
          uibuilderService.send({
            type: "updateRemoteCatalog",
            auth: { userToken: getCookie("userToken"), clientId: getCookie("uibuilder-client-id") },
            data: { uniqueId: this.editingRemoteCatalogId, patch }
          });
          return;
        }
        this.registerRemoteCatalog();
      },
      // ── Admin Tools ────────────────────────────────────────────
      openManageMenu(e, user) {
        const el = e.currentTarget;
        const r = el.getBoundingClientRect();
        this.manageMenu = {
          open: true,
          stage: "root",
          userId: user.uniqueId,
          anchorEl: el,
          x: r.left,
          y: r.bottom + 8
        };
        this.$nextTick(() => this.fixMenuOverflow());
      },
      closeManageMenu() {
        this.manageMenu = { open: false, x: 0, y: 0, stage: "root", userId: null, anchorEl: null };
      },
      fixMenuOverflow() {
        const menu = document.querySelector(".manage-menu");
        if (!menu) return;
        const mr = menu.getBoundingClientRect();
        if (mr.right > window.innerWidth - 12) this.manageMenu.x -= mr.right - (window.innerWidth - 12);
        if (mr.bottom > window.innerHeight - 12) this.manageMenu.y -= mr.bottom - (window.innerHeight - 12);
      },
      updateMenuPosition() {
        if (!this.manageMenu.open || !this.manageMenu.anchorEl) return;
        const r = this.manageMenu.anchorEl.getBoundingClientRect();
        this.manageMenu.x = r.left;
        this.manageMenu.y = r.bottom + 8;
        this.fixMenuOverflow();
      },
      deleteUser(userId) {
        const user = this.users.find((u) => String(u.uniqueId) === String(userId));
        const name = user?.name || "this user";
        this.closeManageMenu();
        this.showConfirm("Delete User", `Are you sure you want to delete "${name}"? This action cannot be undone.`, "Delete", () => {
          this.users = this.users.filter((u) => String(u.uniqueId) !== String(userId));
          this.addToast("success", "User deleted successfully.");
        });
      },
      openManageUserModal() {
        const userId = this.manageMenu.userId;
        const user = this.users.find((u) => String(u.uniqueId) === String(userId));
        if (!user) return;
        const nameParts = (user.name || "").split(" ");
        this.manageForm.firstName = nameParts[0] || "";
        this.manageForm.lastName = nameParts.slice(1).join(" ") || "";
        this.manageForm.email = user.email || "";
        const accessKeys = Array.isArray(user.access) ? user.access : [];
        const labels = accessKeys.map((k) => this.inverseAccessMap?.[k]).filter(Boolean);
        if (!labels.includes("Local Catalogue")) labels.unshift("Local Catalogue");
        this.manageForm.selectedRoles = labels;
        this.manageForm.expiresIn = user.expiresIn || "30 Days";
        this.manageForm.altRole = "";
        this.manageForm.message = "";
        this.manageUserModal = true;
        this.manageMenu.open = false;
      },
      closeManageUserModal() {
        this.manageUserModal = false;
        this.manageForm.selectedRoles = ["Local Catalogue"];
      },
      sendManageUser() {
        const userId = this.manageMenu.userId;
        const user = this.users.find((u) => String(u.uniqueId) === String(userId));
        if (user) {
          user.name = `${this.manageForm.firstName} ${this.manageForm.lastName}`.trim();
          user.email = this.manageForm.email;
          const accessKeys = (this.manageForm.selectedRoles || []).map((label) => this.accessMap[label] || label);
          if (!accessKeys.includes("local_catalogue")) accessKeys.unshift("local_catalogue");
          user.access = accessKeys;
          user.expiresIn = this.manageForm.expiresIn || user.expiresIn;
        }
        this.manageUserModal = false;
        this.manageForm.selectedRoles = ["Local Catalogue"];
        this.addToast("success", "User updated successfully.");
      },
      // ── Invite ─────────────────────────────────────────────────
      closeInviteModal() {
        this.isInviteModal = false;
        this.resetInviteForm();
      },
      sendInvite() {
        const raw = toRaw(this.inviteForm);
        const { role, altRole, firstName, lastName, selectedAccess, ...rest } = raw;
        const mappedAccess = (selectedAccess || []).map((label) => this.accessMap[label] || label);
        const data = { profile: { firstName, lastName }, ...rest, access: mappedAccess };
        uibuilderService.send({
          type: "inviteUser",
          auth: { userToken: getCookie("userToken") },
          data
        });
        this.isInviteModal = false;
        this.resetInviteForm();
        this.addToast("success", "Invitation sent successfully.");
      },
      resetInviteForm() {
        this.inviteForm = {
          firstName: "",
          lastName: "",
          email: "",
          role: "Searcher",
          expiresIn: "30 Days",
          altRole: "",
          message: "You have been invited to join the federated catalogue system.",
          selectedAccess: ["Local Catalogue"]
        };
      },
      // ── Schema Modals ──────────────────────────────────────────
      openRegisterSchemaEditModal() {
        this.isRegisterSchemaEditModal = true;
      },
      openRegisterSchemaNewModal() {
        this.isRegisterSchemaNewModal = true;
      },
      closeRegisterSchemaNewModal() {
        this.isRegisterSchemaNewModal = false;
      },
      closeRegisterSchemaEditModal() {
        this.isRegisterSchemaEditModal = false;
      },
      removeRemoteCatalog(name) {
        this.registerSchemaForm.remoteCatalogs = this.registerSchemaForm.remoteCatalogs.filter((x) => x !== name);
      },
      addFirstCatalogFromSearch() {
        const q = (this.registerSchemaForm.catalogSearch || "").trim();
        if (!q) return;
        const exists = this.registerSchemaForm.remoteCatalogs.some((x) => x.toLowerCase() === q.toLowerCase());
        if (!exists) this.registerSchemaForm.remoteCatalogs.push(q);
        this.registerSchemaForm.catalogSearch = "";
      },
      saveRegisterSchemaNew() {
        this.closeRegisterSchemaNewModal();
      },
      saveRegisterSchemaEdit() {
        this.closeRegisterSchemaEditModal();
      },
      // ── Asset Type Registry ──────────────────────────────────────
      openAssetTypeForm() {
        this.isEditingAssetType = false;
        this.assetTypeForm = { id: null, name: "", description: "", icon: "dataset" };
        this.showAssetTypeForm = true;
      },
      editAssetType(at) {
        this.isEditingAssetType = true;
        this.assetTypeForm = { id: at.id, name: at.name, description: at.description, icon: at.icon };
        this.showAssetTypeForm = true;
      },
      cancelAssetTypeForm() {
        this.showAssetTypeForm = false;
        this.assetTypeForm = { id: null, name: "", description: "", icon: "dataset" };
        this.isEditingAssetType = false;
      },
      saveAssetType() {
        if (!this.assetTypeForm.name) return;
        if (this.isEditingAssetType && this.assetTypeForm.id != null) {
          const idx = this.assetTypes.findIndex((t) => t.id === this.assetTypeForm.id);
          if (idx !== -1) {
            this.assetTypes.splice(idx, 1, { ...this.assetTypeForm });
          }
        } else {
          const maxId = this.assetTypes.reduce((m, t) => Math.max(m, t.id), 0);
          this.assetTypes.push({ ...this.assetTypeForm, id: maxId + 1 });
        }
        this.cancelAssetTypeForm();
        this.addToast("success", this.isEditingAssetType ? "Asset type updated." : "Asset type created.");
      },
      deleteAssetType(id) {
        const at = this.assetTypes.find((t) => t.id === id);
        this.showConfirm("Delete Asset Type", `Are you sure you want to delete "${at?.name || "this type"}"?`, "Delete", () => {
          this.assetTypes = this.assetTypes.filter((t) => t.id !== id);
          this.addToast("success", "Asset type deleted.");
        });
      },
      // ── Prompt Management (FR-SR-03, FR-SR-04) ─────────────────
      openPromptModal() {
        this.isEditingPrompt = false;
        this.promptFormError = "";
        this.promptForm = {
          id: null,
          version: "1.0",
          status: "draft",
          sourceSchema: "",
          targetSchema: "",
          template: "",
          examples: "",
          constraints: ""
        };
        this.showPromptModal = true;
      },
      openEditPrompt(p) {
        this.isEditingPrompt = true;
        this.promptFormError = "";
        this.promptForm = { ...p };
        this.showPromptModal = true;
      },
      closePromptModal() {
        this.showPromptModal = false;
        this.promptFormError = "";
      },
      savePrompt() {
        if (!this.promptForm.sourceSchema || !this.promptForm.targetSchema || !this.promptForm.template) return;
        if (this.promptForm.status === "active") {
          const conflict = this.prompts.find(
            (p) => p.status === "active" && p.sourceSchema === this.promptForm.sourceSchema && p.targetSchema === this.promptForm.targetSchema && p.id !== this.promptForm.id
          );
          if (conflict) {
            this.promptFormError = `Only one active prompt allowed per source-target pair. "${conflict.id}" is already active for ${conflict.sourceSchema} \u2192 ${conflict.targetSchema}.`;
            return;
          }
        }
        const now = (/* @__PURE__ */ new Date()).toISOString().slice(0, 10);
        if (this.isEditingPrompt && this.promptForm.id) {
          const idx = this.prompts.findIndex((p) => p.id === this.promptForm.id);
          if (idx !== -1) {
            this.prompts.splice(idx, 1, { ...this.promptForm, updatedAt: now });
          }
        } else {
          const id = this.promptForm.id || `prompt-${String(Date.now()).slice(-6)}`;
          this.prompts.push({ ...this.promptForm, id, createdAt: now, updatedAt: now });
        }
        this.closePromptModal();
        this.addToast("success", this.isEditingPrompt ? "Prompt updated." : "Prompt created.");
      },
      deletePrompt(id) {
        this.showConfirm("Delete Prompt", `Are you sure you want to delete prompt "${id}"?`, "Delete", () => {
          this.prompts = this.prompts.filter((p) => p.id !== id);
          this.addToast("success", "Prompt deleted.");
        });
      },
      changePromptStatus(prompt, newStatus) {
        if (newStatus === "active") {
          const conflict = this.prompts.find(
            (p) => p.status === "active" && p.sourceSchema === prompt.sourceSchema && p.targetSchema === prompt.targetSchema && p.id !== prompt.id
          );
          if (conflict) {
            this.promptFormError = `Cannot activate: "${conflict.id}" is already active for ${conflict.sourceSchema} \u2192 ${conflict.targetSchema}.`;
            return;
          }
        }
        const idx = this.prompts.findIndex((p) => p.id === prompt.id);
        if (idx !== -1) {
          this.prompts.splice(idx, 1, { ...this.prompts[idx], status: newStatus, updatedAt: (/* @__PURE__ */ new Date()).toISOString().slice(0, 10) });
        }
      },
      insertVariable(variable) {
        const ta = this.$refs.promptTemplateArea;
        if (!ta) {
          this.promptForm.template += variable;
          return;
        }
        const start = ta.selectionStart;
        const end = ta.selectionEnd;
        const val = this.promptForm.template;
        this.promptForm.template = val.slice(0, start) + variable + val.slice(end);
        this.$nextTick(() => {
          ta.selectionStart = ta.selectionEnd = start + variable.length;
          ta.focus();
        });
      },
      promptStatusClass(status) {
        switch (status) {
          case "active":
            return "green";
          case "draft":
            return "blue";
          case "deprecated":
            return "yellow";
          case "archived":
            return "gray";
          default:
            return "gray";
        }
      },
      // ── LLM Configuration (FR-SR-11) ─────────────────────────
      openLlmConfigModal() {
        this.isEditingLlmConfig = false;
        this.llmConfigError = "";
        this.llmConfigForm = {
          id: null,
          name: "",
          provider: "OpenAI",
          model: "",
          temperature: 0.3,
          maxTokens: 4096,
          timeout: 30,
          status: "active"
        };
        this.showLlmConfigModal = true;
      },
      openEditLlmConfig(cfg) {
        this.isEditingLlmConfig = true;
        this.llmConfigError = "";
        this.llmConfigForm = { ...cfg };
        this.showLlmConfigModal = true;
      },
      closeLlmConfigModal() {
        this.showLlmConfigModal = false;
        this.llmConfigError = "";
      },
      saveLlmConfig() {
        if (!this.llmConfigForm.name || !this.llmConfigForm.model) return;
        const now = (/* @__PURE__ */ new Date()).toISOString().slice(0, 10);
        if (this.isEditingLlmConfig && this.llmConfigForm.id) {
          const idx = this.llmConfigs.findIndex((c) => c.id === this.llmConfigForm.id);
          if (idx !== -1) {
            this.llmConfigs.splice(idx, 1, { ...this.llmConfigForm, updatedAt: now });
          }
        } else {
          const id = this.llmConfigForm.id || `llm-${String(Date.now()).slice(-6)}`;
          this.llmConfigs.push({ ...this.llmConfigForm, id, createdAt: now, updatedAt: now });
        }
        this.closeLlmConfigModal();
        this.addToast("success", this.isEditingLlmConfig ? "LLM config updated." : "LLM config created.");
      },
      deleteLlmConfig(id) {
        const cfg = this.llmConfigs.find((c) => c.id === id);
        this.showConfirm("Delete LLM Configuration", `Are you sure you want to delete "${cfg?.name || id}"?`, "Delete", () => {
          this.llmConfigs = this.llmConfigs.filter((c) => c.id !== id);
          this.addToast("success", "LLM configuration deleted.");
        });
      },
      llmProviderClass(provider) {
        switch (provider) {
          case "OpenAI":
            return "green";
          case "Anthropic":
            return "blue";
          case "Mistral":
            return "yellow";
          case "Google":
            return "blue";
          case "Azure OpenAI":
            return "green";
          default:
            return "gray";
        }
      },
      // ── Prompt Testing (FR-SR-10) ─────────────────────────────
      runPromptTest() {
        if (!this.promptTestSelectedPrompt || !this.promptTestSelectedLlm || !this.promptTestSampleInput) return;
        this.promptTestRunning = true;
        this.promptTestResult = "";
        this.promptTestError = "";
        const prompt = this.prompts.find((p) => p.id === this.promptTestSelectedPrompt);
        const llmCfg = this.llmConfigs.find((c) => c.id === this.promptTestSelectedLlm);
        setTimeout(() => {
          try {
            let input;
            try {
              input = JSON.parse(this.promptTestSampleInput);
            } catch (e) {
              input = this.promptTestSampleInput;
            }
            const result = {
              "@type": "dcat:Dataset",
              "dct:title": input.name || input.title || "Transformed Record",
              "dct:identifier": input.identifier || input.id || "generated-id",
              "dct:description": input.description || "",
              "dcat:theme": prompt ? prompt.targetSchema : "",
              "_meta": {
                "llmProvider": llmCfg ? llmCfg.provider : "",
                "model": llmCfg ? llmCfg.model : "",
                "temperature": llmCfg ? llmCfg.temperature : 0,
                "promptVersion": prompt ? prompt.version : "",
                "timestamp": (/* @__PURE__ */ new Date()).toISOString()
              }
            };
            this.promptTestResult = JSON.stringify(result, null, 2);
          } catch (err) {
            this.promptTestError = "Transformation failed: " + err.message;
          }
          this.promptTestRunning = false;
        }, 1500 + Math.random() * 1e3);
      },
      openSaveTestCaseModal() {
        this.isEditingTestCase = false;
        this.testCaseForm = {
          id: null,
          name: "",
          promptId: this.promptTestSelectedPrompt || "",
          llmConfigId: this.promptTestSelectedLlm || "",
          sampleInput: this.promptTestSampleInput || "",
          expectedOutput: ""
        };
        this.showTestCaseModal = true;
      },
      openEditTestCase(tc) {
        this.isEditingTestCase = true;
        this.testCaseForm = { ...tc };
        this.showTestCaseModal = true;
      },
      closeTestCaseModal() {
        this.showTestCaseModal = false;
      },
      saveTestCase() {
        if (!this.testCaseForm.name) return;
        if (this.isEditingTestCase && this.testCaseForm.id) {
          const idx = this.promptTestCases.findIndex((t) => t.id === this.testCaseForm.id);
          if (idx !== -1) {
            this.promptTestCases.splice(idx, 1, { ...this.testCaseForm });
          }
        } else {
          const id = `tc-${String(Date.now()).slice(-6)}`;
          this.promptTestCases.push({ ...this.testCaseForm, id, lastResult: "", lastRunAt: "" });
        }
        this.closeTestCaseModal();
      },
      deleteTestCase(id) {
        this.showConfirm("Delete Test Case", "Are you sure you want to delete this test case?", "Delete", () => {
          this.promptTestCases = this.promptTestCases.filter((t) => t.id !== id);
          this.addToast("success", "Test case deleted.");
        });
      },
      loadTestCase(tc) {
        this.promptTestSelectedPrompt = tc.promptId;
        this.promptTestSelectedLlm = tc.llmConfigId;
        this.promptTestSampleInput = tc.sampleInput;
        this.promptTestResult = tc.lastResult || "";
        this.promptTestError = "";
      },
      // ── Batch Re-transformation (FR-SR-13) ─────────────────
      openBatchRetransformModal() {
        this.batchRetransform = {
          trigger: "prompt_change",
          scope: "all",
          catalogueFilter: "",
          queryFilter: "",
          dryRun: true,
          status: "idle",
          progress: 0,
          totalAssets: 0,
          processedAssets: 0,
          successCount: 0,
          errorCount: 0,
          skippedCount: 0,
          startedAt: "",
          completedAt: "",
          errors: []
        };
        this.showBatchRetransformModal = true;
      },
      closeBatchRetransformModal() {
        if (this.batchRetransform.status === "running") return;
        this.showBatchRetransformModal = false;
      },
      startBatchRetransform() {
        const b = this.batchRetransform;
        b.status = "running";
        b.progress = 0;
        b.processedAssets = 0;
        b.successCount = 0;
        b.errorCount = 0;
        b.skippedCount = 0;
        b.errors = [];
        b.startedAt = (/* @__PURE__ */ new Date()).toISOString().replace("T", " ").slice(0, 16);
        b.completedAt = "";
        const total = b.scope === "all" ? 275 : b.scope === "catalogue" ? 120 : 50;
        b.totalAssets = total;
        this._batchInterval = setInterval(() => {
          if (b.status !== "running") {
            clearInterval(this._batchInterval);
            return;
          }
          const step = Math.ceil(total / 20);
          b.processedAssets = Math.min(total, b.processedAssets + step);
          b.progress = Math.round(b.processedAssets / total * 100);
          if (b.processedAssets > total * 0.6 && b.errorCount === 0) {
            b.errorCount = Math.ceil(total * 0.02);
            b.errors.push({ assetId: "asset-err-001", message: "SHACL validation failed", timestamp: (/* @__PURE__ */ new Date()).toISOString().slice(0, 19) });
            b.errors.push({ assetId: "asset-err-002", message: "LLM timeout exceeded", timestamp: (/* @__PURE__ */ new Date()).toISOString().slice(0, 19) });
          }
          b.successCount = b.processedAssets - b.errorCount;
          if (b.processedAssets >= total) {
            clearInterval(this._batchInterval);
            b.status = "completed";
            b.progress = 100;
            b.completedAt = (/* @__PURE__ */ new Date()).toISOString().replace("T", " ").slice(0, 16);
            const triggerLabels = { prompt_change: "Prompt changed", strategy_change: "Strategy changed", llm_change: "LLM config changed", manual: "Manual trigger" };
            const scopeLabels = { all: "All assets", catalogue: `Catalogue: ${b.catalogueFilter || "\u2014"}`, query: `Query: ${b.queryFilter || "\u2014"}` };
            this.batchRetransformHistory.unshift({
              id: `br-${String(Date.now()).slice(-6)}`,
              trigger: triggerLabels[b.trigger] || b.trigger,
              scope: scopeLabels[b.scope] || b.scope,
              dryRun: b.dryRun,
              total: b.totalAssets,
              success: b.successCount,
              errors: b.errorCount,
              skipped: b.skippedCount,
              startedAt: b.startedAt,
              completedAt: b.completedAt,
              status: "completed"
            });
          }
        }, 400);
      },
      cancelBatchRetransform() {
        if (this._batchInterval) clearInterval(this._batchInterval);
        this.batchRetransform.status = "cancelled";
        this.batchRetransform.completedAt = (/* @__PURE__ */ new Date()).toISOString().replace("T", " ").slice(0, 16);
      },
      batchTriggerLabel(t) {
        return { prompt_change: "Prompt Change", strategy_change: "Strategy Change", llm_change: "LLM Config Change", manual: "Manual" }[t] || t;
      },
      // ── Multi-Model Provider (FR-SR-12) ──────────────────────
      openProviderModal() {
        this.isEditingProvider = false;
        this.providerFormError = "";
        this.providerForm = { id: null, name: "", type: "openai", apiEndpoint: "", models: "", isDefault: false, precedence: this.llmProviders.length + 1, status: "active" };
        this.showProviderModal = true;
      },
      openEditProvider(p) {
        this.isEditingProvider = true;
        this.providerFormError = "";
        this.providerForm = { ...p, models: Array.isArray(p.models) ? p.models.join(", ") : p.models };
        this.showProviderModal = true;
      },
      closeProviderModal() {
        this.showProviderModal = false;
        this.providerFormError = "";
      },
      saveProvider() {
        if (!this.providerForm.name || !this.providerForm.apiEndpoint) return;
        const now = (/* @__PURE__ */ new Date()).toISOString().slice(0, 10);
        const models = typeof this.providerForm.models === "string" ? this.providerForm.models.split(",").map((m) => m.trim()).filter(Boolean) : this.providerForm.models;
        if (this.isEditingProvider && this.providerForm.id) {
          const idx = this.llmProviders.findIndex((p) => p.id === this.providerForm.id);
          if (idx !== -1) {
            this.llmProviders.splice(idx, 1, { ...this.providerForm, models, updatedAt: now });
          }
        } else {
          const id = `prov-${String(Date.now()).slice(-6)}`;
          this.llmProviders.push({ ...this.providerForm, id, models, createdAt: now });
        }
        if (this.providerForm.isDefault) {
          this.llmProviders.forEach((p) => {
            if (p.id !== (this.providerForm.id || this.llmProviders[this.llmProviders.length - 1].id)) p.isDefault = false;
          });
        }
        this.closeProviderModal();
        this.addToast("success", this.isEditingProvider ? "Provider updated." : "Provider created.");
      },
      deleteProvider(id) {
        const prov = this.llmProviders.find((p) => p.id === id);
        this.showConfirm("Delete Provider", `Are you sure you want to delete "${prov?.name || id}"?`, "Delete", () => {
          this.llmProviders = this.llmProviders.filter((p) => p.id !== id);
          this.addToast("success", "Provider deleted.");
        });
      },
      moveProviderUp(id) {
        const idx = this.llmProviders.findIndex((p) => p.id === id);
        if (idx <= 0) return;
        const item = this.llmProviders.splice(idx, 1)[0];
        this.llmProviders.splice(idx - 1, 0, item);
        this.llmProviders.forEach((p, i) => {
          p.precedence = i + 1;
        });
      },
      moveProviderDown(id) {
        const idx = this.llmProviders.findIndex((p) => p.id === id);
        if (idx < 0 || idx >= this.llmProviders.length - 1) return;
        const item = this.llmProviders.splice(idx, 1)[0];
        this.llmProviders.splice(idx + 1, 0, item);
        this.llmProviders.forEach((p, i) => {
          p.precedence = i + 1;
        });
      },
      providerTypeClass(type) {
        switch (type) {
          case "openai":
            return "green";
          case "anthropic":
            return "blue";
          case "ollama":
            return "yellow";
          case "azure":
            return "green";
          case "google":
            return "blue";
          default:
            return "gray";
        }
      },
      // ── Audit Trail Export & Filters (FR-SR-09) ──────────────
      exportAuditTrail(format) {
        const rows = this.auditRows;
        let content, filename, mimeType;
        if (format === "csv") {
          const headers = ["ID", "Rule", "Level", "Step", "Asset ID", "Catalogue", "Prompt Version", "Status", "Timestamp"];
          const csvRows = rows.map((r) => [r.id, r.rule, r.level, r.step, r.assetId || "", r.catalogueId || "", r.promptVersion || "", r.status || "", r.timestamp].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(","));
          content = [headers.join(","), ...csvRows].join("\n");
          filename = "audit-trail.csv";
          mimeType = "text/csv";
        } else {
          content = JSON.stringify(rows, null, 2);
          filename = "audit-trail.json";
          mimeType = "application/json";
        }
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      },
      clearAuditFilters() {
        this.auditFilters = { assetId: "", catalogueId: "", promptVersion: "", status: "", dateFrom: "", dateTo: "" };
      },
      // ── Local Schema CRUD (Milestone 2) ──────────────────────
      openCreateLocalSchemaModal() {
        this.isEditingLocalSchema = false;
        this.editingLocalSchemaId = null;
        this.localSchemaForm = { schema: "", format: "SHACL", catalogs: 1, localMapping: "", versioning: "v1.0", trustLevel: "Federated" };
        this.showCreateLocalSchemaModal = true;
      },
      openEditLocalSchema(row) {
        this.isEditingLocalSchema = true;
        this.editingLocalSchemaId = row.id;
        this.localSchemaForm = { schema: row.schema, format: "SHACL", catalogs: row.catalogs, localMapping: row.localMapping || "", versioning: row.versioning, trustLevel: row.trustLevel };
        this.showCreateLocalSchemaModal = true;
      },
      closeCreateLocalSchemaModal() {
        this.showCreateLocalSchemaModal = false;
      },
      saveLocalSchema() {
        if (!this.localSchemaForm.schema) return;
        const now = (/* @__PURE__ */ new Date()).toISOString().slice(0, 10);
        if (this.isEditingLocalSchema && this.editingLocalSchemaId != null) {
          const idx = this.schemaRegistry.findIndex((s) => s.id === this.editingLocalSchemaId);
          if (idx !== -1) {
            this.schemaRegistry.splice(idx, 1, {
              ...this.schemaRegistry[idx],
              schema: this.localSchemaForm.schema,
              catalogs: this.localSchemaForm.catalogs,
              localMapping: this.localSchemaForm.localMapping || null,
              versioning: this.localSchemaForm.versioning,
              trustLevel: this.localSchemaForm.trustLevel
            });
          }
        } else {
          const maxId = this.schemaRegistry.reduce((m, s) => Math.max(m, s.id), 0);
          this.schemaRegistry.push({
            id: maxId + 1,
            schema: this.localSchemaForm.schema,
            catalogs: this.localSchemaForm.catalogs,
            localMapping: this.localSchemaForm.localMapping || null,
            versioning: this.localSchemaForm.versioning,
            versionOptions: ["v1.0", "v1.1", "v2.0"],
            trustLevel: this.localSchemaForm.trustLevel
          });
        }
        this.showCreateLocalSchemaModal = false;
        this.addToast("success", this.isEditingLocalSchema ? "Schema updated." : "Schema created.");
      },
      confirmDeleteSchema(id) {
        const schema = this.schemaRegistry.find((s) => s.id === id);
        this.showConfirm("Delete Schema", `Are you sure you want to delete "${schema?.schema || "this schema"}"? This action cannot be undone.`, "Delete", () => {
          this.schemaRegistry = this.schemaRegistry.filter((s) => s.id !== id);
          this.addToast("success", "Schema deleted.");
        });
      },
      // ── Schema Version Diff (Milestone 2) ─────────────────────
      openSchemaDiff(row) {
        this.schemaDiffRow = { ...row };
        this.schemaDiffVersionA = row.versionOptions?.[0] || "v1.0";
        this.schemaDiffVersionB = row.versioning || row.versionOptions?.[1] || "v1.1";
        this.showSchemaDiffPanel = true;
      },
      closeSchemaDiff() {
        this.showSchemaDiffPanel = false;
        this.schemaDiffRow = null;
      },
      getSchemaDiffContent(version) {
        const base = this.schemaDiffRow?.schema || "Schema";
        const diffs = {
          "v1.0": `@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct:  <http://purl.org/dc/terms/> .

:DatasetShape a sh:NodeShape ;
  sh:targetClass dcat:Dataset ;
  sh:property [
    sh:path dct:title ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path dct:identifier ;
    sh:minCount 1 ;
  ] .`,
          "v1.1": `@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct:  <http://purl.org/dc/terms/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

:DatasetShape a sh:NodeShape ;
  sh:targetClass dcat:Dataset ;
  sh:property [
    sh:path dct:title ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path dct:identifier ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path dcat:distribution ;
    sh:node :DistributionShape ;
  ] .`,
          "v2.0": `@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dct:  <http://purl.org/dc/terms/> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

:DatasetShape a sh:NodeShape ;
  sh:targetClass dcat:Dataset ;
  sh:property [
    sh:path dct:title ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
  ] ;
  sh:property [
    sh:path dct:identifier ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path dcat:distribution ;
    sh:node :DistributionShape ;
    sh:minCount 0 ;
  ] ;
  sh:property [
    sh:path dct:publisher ;
    sh:node :AgentShape ;
    sh:minCount 1 ;
  ] .`
        };
        return diffs[version] || `# ${base} \u2014 ${version}
# No content available for this version.`;
      },
      // ── Add Mapping Modal (Milestone 2) ───────────────────────
      openAddMappingModal() {
        this.isEditingMapping = false;
        this.editingMappingId = null;
        this.addMappingForm = { remoteCatalogue: "", remoteSchema: "", remoteSchemaMeta: "", transformationStrategy: "Deterministic RDF", promptsCount: 0, shaclCount: 0 };
        this.showAddMappingModal = true;
      },
      closeAddMappingModal() {
        this.showAddMappingModal = false;
      },
      saveAddMapping() {
        if (!this.addMappingForm.remoteCatalogue || !this.addMappingForm.remoteSchema) return;
        if (this.isEditingMapping && this.editingMappingId != null) {
          const idx = this.mappingRows.findIndex((r) => r.id === this.editingMappingId);
          if (idx !== -1) {
            this.mappingRows.splice(idx, 1, { ...this.mappingRows[idx], ...this.addMappingForm });
          }
        } else {
          const maxId = this.mappingRows.reduce((m, r) => Math.max(m, r.id), 0);
          this.mappingRows.push({ id: maxId + 1, ...this.addMappingForm });
        }
        this.showAddMappingModal = false;
        this.addToast("success", this.isEditingMapping ? "Mapping updated." : "Mapping created.");
      },
      // ── Mapping View/Edit Detail (Milestone 2) ────────────────
      openMappingViewEdit(row) {
        this.mappingDetailRow = { ...row };
        this.isEditingMappingDetail = false;
        this.showMappingDetailPanel = true;
      },
      closeMappingDetail() {
        this.showMappingDetailPanel = false;
        this.mappingDetailRow = null;
        this.isEditingMappingDetail = false;
      },
      startEditMappingDetail() {
        if (!this.mappingDetailRow) return;
        this.mappingDetailEditForm = {
          remoteCatalogue: this.mappingDetailRow.remoteCatalogue,
          remoteSchema: this.mappingDetailRow.remoteSchema,
          remoteSchemaMeta: this.mappingDetailRow.remoteSchemaMeta,
          transformationStrategy: this.mappingDetailRow.transformationStrategy
        };
        this.isEditingMappingDetail = true;
      },
      cancelEditMappingDetail() {
        this.isEditingMappingDetail = false;
      },
      saveEditMappingDetail() {
        if (!this.mappingDetailRow) return;
        const idx = this.mappingRows.findIndex((r) => r.id === this.mappingDetailRow.id);
        if (idx !== -1) {
          const updated = { ...this.mappingRows[idx], ...this.mappingDetailEditForm };
          this.mappingRows.splice(idx, 1, updated);
          this.mappingDetailRow = { ...updated };
        }
        this.isEditingMappingDetail = false;
      },
      openMappingPrompts(row) {
        this.openMappingViewEdit(row);
      },
      openMappingShacl(row) {
        this.openMappingViewEdit(row);
      },
      // ── Mapping ────────────────────────────────────────────────
      toggleAllMappingRows(e) {
        this.selectedMappingRows = e.target.checked ? this.mappingPagination.rows.map((r) => r.id) : [];
      },
      removeMappingRow(id) {
        const row = this.mappingRows.find((r) => r.id === id);
        this.showConfirm("Delete Mapping", `Are you sure you want to delete the mapping for "${row?.remoteCatalogue || "this mapping"}"?`, "Delete", () => {
          this.mappingRows = this.mappingRows.filter((r) => r.id !== id);
          this.selectedMappingRows = this.selectedMappingRows.filter((x) => x !== id);
          if (this.mappingDetailRow && this.mappingDetailRow.id === id) {
            this.closeMappingDetail();
          }
          this.addToast("success", "Mapping deleted.");
        });
      },
      // ── Harvest Wizard ─────────────────────────────────────────
      openHarvestWizard() {
        this.showHarvestWizard = true;
        this.harvestWizardStep = 1;
        this.harvestWizardSearch = "";
        this.harvestWizardSelectedRows = [];
        this.harvestScope.schemaMappingEnabled = false;
        this.harvestScope.resolveReferences = false;
        this.pagination.harvestWizard.page = 1;
        this.harvestWizardRowsBase = this.allCatalogsRaw.map((item, idx) => ({
          id: item?.id ?? idx + 1,
          catalog: item?.catalog?.catalogId ?? "-",
          type: item?.assets?.documents?.[0]?.format ?? "-",
          name: item?.vehicles?.[0]?.brand ?? "-",
          domain: item?.catalog?.publisher?.website ?? "-",
          updated: item?.catalog?.updatedAt ?? "-",
          integrationStatus: "Active",
          __raw: item
        }));
        this.harvestWizardRows = [...this.harvestWizardRowsBase];
      },
      closeHarvestWizard() {
        this.showHarvestWizard = false;
        this.harvestWizardStep = 1;
      },
      nextHarvestWizardStep() {
        this.harvestWizardStep = Math.min(4, this.harvestWizardStep + 1);
      },
      prevHarvestWizardStep() {
        this.harvestWizardStep = Math.max(1, this.harvestWizardStep - 1);
      },
      runHarvestWizardSearch() {
        const q = normalizeText(this.harvestWizardSearch);
        const filteredRaw = this.allCatalogsRaw.filter((item) => normalizeText(JSON.stringify(item)).includes(q));
        this.harvestWizardRows = filteredRaw.map((item, i) => ({
          id: item?.id ?? i + 1,
          catalog: item?.catalog?.catalogId ?? "-",
          type: item?.assets?.documents?.[0]?.format ?? "-",
          name: item?.vehicles?.[0]?.brand ?? "-",
          domain: item?.catalog?.publisher?.website ?? "-",
          updated: item?.catalog?.updatedAt ?? "-",
          integrationStatus: "Active"
        }));
        this.pagination.harvestWizard.page = 1;
      },
      toggleWizardSelectAll(e) {
        this.harvestWizardSelectedRows = e.target.checked ? this.harvestWizardRows.map((r) => r.id) : [];
      },
      toggleScopeOption(key) {
        const s = this.harvestScope.selected;
        if (key === "all_assets") {
          this.harvestScope.selected = s.includes("all_assets") ? [] : ["all_assets"];
          return;
        }
        if (s.includes("all_assets")) return;
        this.harvestScope.selected = s.includes(key) ? s.filter((x) => x !== key) : [...s, key];
        if (!this.showIncludeNewAssetsToggle) this.harvestScope.includeNewAssets = false;
      },
      toggleLifecycleCard(key) {
        if (this.lifecycleMapping && key in this.lifecycleMapping) {
          this.lifecycleMapping[key] = !this.lifecycleMapping[key];
        }
      },
      startHarvest() {
        console.log("START HARVEST payload:", {
          selectedCatalogRowIds: [...this.harvestWizardSelectedRows],
          harvestScope: { ...this.harvestScope },
          lifecycleMapping: { ...this.lifecycleMapping },
          overviewToggles: { ...this.overviewToggles }
        });
        this.closeHarvestWizard();
        this.startLiveHarvest();
      },
      // ── Harvest Run Detail (Milestone 3) ──────────────────────
      openHarvestRunDetail(run) {
        this.harvestRunDetailData = {
          ...run,
          assets: [
            { id: "asset-001", title: "SensorML Observation Record", status: "Success", duration: "1.2s", error: null },
            { id: "asset-002", title: "Temperature Sensor Dataset", status: "Success", duration: "0.8s", error: null },
            { id: "asset-003", title: "Geolocation Service Metadata", status: "Warning", duration: "2.1s", error: "SHACL minor validation warning" },
            { id: "asset-004", title: "Air Quality Measurements", status: "Error", duration: "4.5s", error: "Schema mapping failed \u2014 missing required field dct:identifier" },
            { id: "asset-005", title: "Traffic Flow Data Product", status: "Success", duration: "0.6s", error: null },
            { id: "asset-006", title: "Energy Consumption Report", status: "Success", duration: "1.0s", error: null }
          ]
        };
        this.showHarvestRunDetail = true;
      },
      closeHarvestRunDetail() {
        this.showHarvestRunDetail = false;
        this.harvestRunDetailData = null;
      },
      // ── Live Harvest Progress (Milestone 3) ───────────────────
      startLiveHarvest() {
        const h = this.activeHarvest;
        h.running = true;
        h.status = "running";
        h.catalogueName = "SensorML";
        h.progress = 0;
        h.processedAssets = 0;
        h.successCount = 0;
        h.errorCount = 0;
        h.errors = [];
        h.startedAt = (/* @__PURE__ */ new Date()).toISOString().replace("T", " ").slice(0, 16);
        const total = 120;
        h.totalAssets = total;
        if (this._harvestInterval) clearInterval(this._harvestInterval);
        this._harvestInterval = setInterval(() => {
          if (h.status !== "running") {
            clearInterval(this._harvestInterval);
            return;
          }
          const step = Math.ceil(total / 15);
          h.processedAssets = Math.min(total, h.processedAssets + step);
          h.progress = Math.round(h.processedAssets / total * 100);
          if (h.processedAssets > total * 0.7 && h.errorCount === 0) {
            h.errorCount = 3;
            h.errors = [
              { assetId: "asset-err-01", message: "SHACL validation failed", timestamp: (/* @__PURE__ */ new Date()).toISOString().slice(0, 19) },
              { assetId: "asset-err-02", message: "Missing required field dct:title", timestamp: (/* @__PURE__ */ new Date()).toISOString().slice(0, 19) },
              { assetId: "asset-err-03", message: "LLM timeout exceeded (30s)", timestamp: (/* @__PURE__ */ new Date()).toISOString().slice(0, 19) }
            ];
          }
          h.successCount = h.processedAssets - h.errorCount;
          if (h.processedAssets >= total) {
            clearInterval(this._harvestInterval);
            h.status = "completed";
            h.progress = 100;
            h.running = false;
            this.harvestRecords.unshift({
              id: Date.now(),
              sourceCatalogue: h.catalogueName,
              tool: "Live Harvester",
              harvestDate: "Just now",
              assetsAdded: `+${h.successCount}`,
              duration: "Just completed",
              result: h.errorCount > 0 ? "Warning" : "Success"
            });
          }
        }, 500);
      },
      pauseHarvest() {
        if (this.activeHarvest.status === "running") {
          this.activeHarvest.status = "paused";
          this.activeHarvest.running = false;
          if (this._harvestInterval) clearInterval(this._harvestInterval);
        }
      },
      resumeHarvest() {
        if (this.activeHarvest.status === "paused") {
          this.activeHarvest.status = "running";
          this.activeHarvest.running = true;
          const h = this.activeHarvest;
          const total = h.totalAssets;
          this._harvestInterval = setInterval(() => {
            if (h.status !== "running") {
              clearInterval(this._harvestInterval);
              return;
            }
            const step = Math.ceil(total / 15);
            h.processedAssets = Math.min(total, h.processedAssets + step);
            h.progress = Math.round(h.processedAssets / total * 100);
            h.successCount = h.processedAssets - h.errorCount;
            if (h.processedAssets >= total) {
              clearInterval(this._harvestInterval);
              h.status = "completed";
              h.progress = 100;
              h.running = false;
            }
          }, 500);
        }
      },
      cancelHarvest() {
        if (this._harvestInterval) clearInterval(this._harvestInterval);
        this.activeHarvest.status = "cancelled";
        this.activeHarvest.running = false;
      },
      // ── Toast Notifications (Milestone 5) ──────────────────────
      addToast(type, message, duration = 4e3) {
        const id = ++this._toastCounter;
        this.toasts.push({ id, type, message });
        setTimeout(() => this.dismissToast(id), duration);
      },
      dismissToast(id) {
        this.toasts = this.toasts.filter((t) => t.id !== id);
      },
      // ── Confirmation Dialog (Milestone 5) ────────────────────
      showConfirm(title, message, confirmLabel, onConfirm) {
        this.confirmDialog = { visible: true, title, message, confirmLabel: confirmLabel || "Delete", onConfirm };
      },
      cancelConfirm() {
        this.confirmDialog = { visible: false, title: "", message: "", confirmLabel: "Delete", onConfirm: null };
      },
      executeConfirm() {
        if (typeof this.confirmDialog.onConfirm === "function") {
          this.confirmDialog.onConfirm();
        }
        this.cancelConfirm();
      },
      // ── Delete Remote Catalogue (Milestone 5) ────────────────
      confirmDeleteRemoteCatalog(id) {
        const cat = this.catalogsTable.find((c) => String(c.id) === String(id) || String(c.uniqueId) === String(id));
        const name = cat?.catalogName || cat?.catalogId || "this catalogue";
        this.showConfirm(
          "Delete Remote Catalogue",
          `Are you sure you want to delete "${name}"? This action cannot be undone.`,
          "Delete",
          () => this.deleteRemoteCatalog(id)
        );
      },
      deleteRemoteCatalog(id) {
        this.catalogsTable = this.catalogsTable.filter((c) => String(c.id) !== String(id) && String(c.uniqueId) !== String(id));
        this.addToast("success", "Remote catalogue deleted successfully.");
      },
      // ── Monitoring Log Export (Milestone 4) ─────────────────────
      exportMonitoringLog(format) {
        const rows = this.filteredMonitoringEvents;
        let content, filename, mimeType;
        if (format === "csv") {
          const headers = ["ID", "Level", "Source", "Message", "Timestamp"];
          const csvRows = rows.map((r) => [r.id, r.type, r.source, r.message, r.timestamp].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(","));
          content = [headers.join(","), ...csvRows].join("\n");
          filename = "monitoring-events.csv";
          mimeType = "text/csv";
        } else {
          content = JSON.stringify(rows, null, 2);
          filename = "monitoring-events.json";
          mimeType = "application/json";
        }
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        this.addToast("success", `Event log exported as ${format.toUpperCase()}.`);
      },
      // ── Password Change (Milestone 4) ─────────────────────────
      changePassword() {
        this.passwordFormError = "";
        this.passwordFormSuccess = "";
        if (this.passwordForm.newPassword.length < 8) {
          this.passwordFormError = "New password must be at least 8 characters.";
          return;
        }
        if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
          this.passwordFormError = "Passwords do not match.";
          return;
        }
        setTimeout(() => {
          this.passwordFormSuccess = "Password updated successfully.";
          this.passwordForm = { currentPassword: "", newPassword: "", confirmPassword: "" };
          this.addToast("success", "Password changed successfully.");
        }, 600);
      },
      // ── Access Info ─────────────────────────────────────────────
      openAccessInformation() {
        this.showAccessInformation = true;
      },
      closeAccessInformation() {
        this.showAccessInformation = false;
      },
      // ── Logout ──────────────────────────────────────────────────
      logout() {
        uibuilderService.send({
          type: "logOut",
          auth: { userToken: getCookie("userToken"), clientId: getCookie("uibuilder-client-id") }
        });
      }
    },
    mounted() {
      uibuilderService.start();
      uibuilderService.send({
        type: "getDashboard",
        auth: { userToken: getCookie("userToken"), clientId: getCookie("uibuilder-client-id") }
      });
      uibuilderService.onMessage((msg) => {
        console.log(msg);
        const payload = msg?.payload ?? msg;
        const resp = payload?.response ?? msg?.response;
        if (resp?.action === "registerRemoteCatalog") {
          this.isRegisteringRemoteCatalog = false;
          if (resp.status === "success") {
            const newItem = this.pendingRemoteCatalog;
            this.pendingRemoteCatalog = null;
            const remoteCatalogId = resp.uniqueId || msg?.response?.uniqueId;
            const row = { ...newItem, uniqueId: remoteCatalogId, id: remoteCatalogId };
            const idx = this.catalogsTable.findIndex((x) => String(x.id) === String(remoteCatalogId));
            if (idx !== -1) this.catalogsTable.splice(idx, 1, row);
            else this.catalogsTable.unshift(row);
            this.pagination.catalogsRegister.page = 1;
            this.closeRegisterRemoteCatalogModal();
            this.addToast("success", "Remote catalogue registered successfully.");
          } else {
            this.registerRemoteCatalogError = resp?.message || "Register remote catalog failed";
            this.addToast("error", this.registerRemoteCatalogError);
          }
        }
        if (payload.state === "notLoggedIn") {
          window.location.href = "/asal-asal/login";
        }
        if (payload?.type === "getDashboard") {
          this.userAccess = payload?.response?.userAccess || [];
          if (payload?.response?.userPermissions) {
            this.userPermissions = payload.response.userPermissions;
          }
          const pageAccessMap = {
            localCatalogue: "local_catalogue",
            catalogueRegistry: "catalogue_registry",
            schemaRegistry: "schema_registry",
            harvester: "harvester",
            adminTools: "admin_tools"
          };
          const currentAccessKey = pageAccessMap[this.currentPage];
          if (currentAccessKey && !this.hasAccess(currentAccessKey)) {
            const fallback = Object.entries(pageAccessMap).find(([, ak]) => this.hasAccess(ak));
            this.currentPage = fallback ? fallback[0] : "";
          }
        }
        if (resp?.action === "getCatalogRegistry" && resp.status === "success") {
          const catalogs = Array.isArray(resp.catalogs) ? resp.catalogs : [];
          this.catalogsTable = catalogs.map((item) => ({
            uniqueId: item.uniqueId,
            id: item.uniqueId,
            ...item.catalog || {}
          }));
          this.pagination.catalogsRegister.page = 1;
        }
        if (resp?.action === "updateRemoteCatalog") {
          this.isUpdatingRemoteCatalog = false;
          if (resp?.status === "success") {
            const id = msg?.data?.uniqueId;
            const patch = msg?.data?.patch || {};
            const idx = this.catalogsTable.findIndex((c) => String(c.uniqueId) === String(id));
            if (idx !== -1) this.catalogsTable.splice(idx, 1, { ...this.catalogsTable[idx], ...patch });
            this.closeRegisterRemoteCatalogModal();
            this.addToast("success", "Remote catalogue updated successfully.");
          } else {
            this.updateRemoteCatalogError = resp?.message || "Update failed";
          }
        }
        if (resp?.action === "inviteUser" && resp?.status === "success") {
          const sent = payload?.data ?? msg?.data ?? {};
          const firstName = sent?.profile?.firstName ?? sent?.firstName ?? "";
          const lastName = sent?.profile?.lastName ?? sent?.lastName ?? "";
          const uid = resp?.uniqueId ?? msg?.response?.uniqueId ?? payload?.response?.uniqueId;
          const accessKeys = Array.isArray(sent?.access) ? sent.access : [];
          const newUser = {
            uniqueId: uid,
            name: `${firstName} ${lastName}`.trim(),
            avatar: "./img/avatar-16.jpg",
            email: sent?.email ?? "",
            access: accessKeys,
            status: "Invited",
            expiresIn: sent?.expiresIn ?? "30 Days"
          };
          let idx = uid ? this.users.findIndex((u) => String(u.uniqueId) === String(uid)) : -1;
          if (idx === -1 && newUser.email) idx = this.users.findIndex((u) => String(u.email) === String(newUser.email));
          if (idx !== -1) this.users.splice(idx, 1, newUser);
          else this.users.unshift(newUser);
          this.pagination.users.page = 1;
        }
        if (msg?.type === "getAdminTools" && msg?.response?.status === "success") {
          const list = msg.response.users || [];
          this.users = list.map((u, i) => {
            const uid = u.uniqueId ?? u.id ?? u._id ?? String(i);
            return {
              ...u,
              uniqueId: uid,
              name: `${u.profile?.firstName ?? ""} ${u.profile?.lastName ?? ""}`.trim() || u.name || u.email || "\u2014",
              avatar: u.avatar || "./img/avatar-16.jpg",
              email: u.email || "\u2014",
              status: u.status || (u.invited ? "Invited" : "Active")
            };
          });
        }
        if (resp?.action === "logOut" && resp?.status === "success") {
          window.location.href = "/asal-asal/login";
          document.cookie = "userToken=; path=/; max-age=0";
        }
      });
      this.setPerPageByViewport();
      window.addEventListener("resize", this.onResize);
      this.loadLocalCatalogs();
      window.addEventListener("scroll", this.updateMenuPosition, true);
      window.addEventListener("resize", this.updateMenuPosition);
    },
    beforeUnmount() {
      window.removeEventListener("resize", this.onResize);
      window.removeEventListener("scroll", this.updateMenuPosition, true);
      window.removeEventListener("resize", this.updateMenuPosition);
    }
  });
  app.component("view-modal", ViewModal_default);
  app.component("invite-modal", InviteModal_default);
  app.component("manage-user-modal", ManageUserModal_default);
  app.component("register-catalog-modal", RegisterCatalogModal_default);
  app.component("schema-modal", SchemaModal_default);
  app.component("harvest-wizard-modal", HarvestWizardModal_default);
  app.component("access-info-modal", AccessInfoModal_default);
  app.component("manage-menu", ManageMenu_default);
  app.mount("#app");
})();
