const { createApp } = Vue;

createApp({
    data() {
        return {
            currentPage: "localCatalogue",
            currentTab: "localCatalogue",
            currentSchemaTab: "localSchema",
            currentAdminTab: "accessControl",
            isViewModal: false,
            manageUserModal: false,
            currentViewTab: "Overview",
            isInviteModal: false,
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
            showRegisterRemoteCatalogModal: false,
            editingRemoteCatalogId: null,
            isEditingRemoteCatalog: false,
            remoteCatalogForm: {
              catalogId: "",
              catalogName: "",
              owner: "",
              protocol: "Query interface",
              baseEndpoint: "",
              mimeType: "application/sparql-results+json",
        
              // query interface settings
              queryEndpoint: "",
              queryLanguages: "",
        
              // schema mapping
              strategy: "none",
              promptId: "",
              llmConfigId: "",
              namespacesToPreserve: "",
              shaclShapeId: "",
        
              // advanced
              auth: "none",
              trustAnchor: "",
              enabled: true,
            },
                    
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
            manageMenu: {
              open: false,
              x: 0,
              y: 0,
              stage: "root",
              userId: null,
              anchorEl: null
            },
            roles: ["Harvester", "Catalog Admin", "Schema Admin", "Administrator", "Searcher"],
            isRegisterSchemaEditModal: false,
            isRegisterSchemaNewModal: false,
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
            
            # A remote rule set that says:
            # A DCAT Catalogue must have at least 1 dataset.
            # Each Dataset must have identifier + title + publisher.
            # Each Distribution must have accessURL and mediaType.
            
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






        
            selectedRows: [],
            auditSearch: "",

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
              {
                id: 1,
                level: "Info",
                step: "Schemas Harmonized",
                timestamp: "2026-09-02 10:32 (UTC)"
              }
            ],
            
            auditRows: [
              {
                id: 1,
                rule: "Recursive Time Updates",
                level: "Info",
                step: "Schemas Harmonized",
                timestamp: "2026-06-02 10:32 (UTC)"
              },
              {
                id: 2,
                rule: "Schemas Harmonized",
                level: "Warning",
                step: "Schemas Harmonized",
                timestamp: "2026-09-02 10:32 (UTC)"
              },
              {
                id: 3,
                rule: "Null value issues fixed",
                level: "Error",
                step: "Schemas Harmonized",
                timestamp: "2026-09-02 10:32 (UTC)"
              }
            ],
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
            
              // updated
              { text: '  "updated_at": "2026-02-09T10:32:18Z",', changeType: "updated" },
            
              // updated
              { text: '  "snisn_temperature": 22.5,', changeType: "updated" },
              { text: '  "snisn_humidity": 60,', changeType: "updated" },
            
              // new
              { text: '  "ai-generated-field-1": "deterministic_fallback",', changeType: "new" },
            
              { text: '  "status": "active",', changeType: null },
            
              { text: '  "owner": {', changeType: null },
              { text: '    "name": "Local Organization",', changeType: null },
            
              // updated
              { text: '    "contact_email": "support@am.com"', changeType: "updated" },
              { text: "  },", changeType: null },
            
              { text: '  "location": null,', changeType: "deleted" },
            
              { text: '  "domain_tags": [', changeType: null },
              { text: '    "asset-safety",', changeType: null },
              { text: '    "environmental-monitoring",', changeType: null },
              { text: '    "sensor-network"', changeType: null },
              { text: "  ],", changeType: null },
            
              // new
              { text: '  "metrics": {', changeType: "new" },
              { text: '    "batteryLevel": 87,', changeType: "new" },
              { text: '    "signalStrength": -71,', changeType: "new" },
              { text: '    "lastHeartbeat": "2026-02-09T10:30:01Z",', changeType: "new" },
              { text: '    "harvestRunId": "run-2026-02-09-001"', changeType: "new" },
              { text: "  },", changeType: "new" },
            
              // deleted
              { text: '  "airQualityIndex": null', changeType: "deleted" },
            
              { text: "}", changeType: null }
            ],



        
            searchText: "",
            filters: {
              catalog: "",
              type: "",
              domain: "",
              status: ""
            },
        
            allCatalogsRaw: [],
        
            tableRows: [],
            schemaRegistry: [
              {
                id: 1,
                schema: "DCAT-AP.de",
                catalogs: 3,
                localMapping: "Service, Data Product",
                versioning: "v1.0",
                versionOptions: ["v1.0", "v1.1", "v2.0"],
                trustLevel: "Federated"
              },
              {
                id: 2,
                schema: "Data Specifications",
                catalogs: 2,
                localMapping: "Dataset (1)",
                versioning: "v1.1",
                versionOptions: ["v1.0", "v1.1", "v2.0"],
                trustLevel: "Federated"
              },
              {
                id: 3,
                schema: "OGC SensorML",
                catalogs: 1,
                localMapping: "Asset + Safety",
                versioning: "v1.0",
                versionOptions: ["v1.0", "v1.1", "v2.0"], 
                trustLevel: "Federated"
              },
              {
                id: 4,
                schema: "Xxx Taxonomy",
                catalogs: 1,
                localMapping: null,
                versioning: "v2.0",
                versionOptions: ["v1.0", "v1.1", "v2.0"],
                trustLevel: "Untrusted"
              }
            ],
            remoteSchema:[
              {
                id: 1,
                schema: "ISO 19115-1",
                catalogs: 5,
                localMapping: "Dataset (2)",
                versioning: "v2.0",
                versionOptions: ["v1.0", "v1.1", "v2.0"],
                trustLevel: "Federated"
              },
              {
                id: 2,
                schema: "schema.org Dataset",
                catalogs: 7,
                localMapping: "Dataset (5)",
                versioning: "v1.0",
                versionOptions: ["v1.0", "v1.1", "v2.0"],
                trustLevel: "Federated"
              },
              {
                id: 3,
                schema: "OpenAPI Specification",
                catalogs: 3,
                localMapping: "Service, Data Product",
                versioning: "v1.1",
                versionOptions: ["v1.0", "v1.1", "v2.0"],
                trustLevel: "Federated"
              },
              {
                id: 4,
                schema: "W3C PROV-O",
                catalogs: 2,
                localMapping: "Asset + Safety",
                versioning: "v2.0",
                versionOptions: ["v1.0", "v1.1", "v2.0"],
                trustLevel: "Federated"
              },
              {
                id: 5,
                schema: "SKOS Concept Scheme",
                catalogs: 1,
                localMapping: null,
                versioning: "v1.0",
                versionOptions: ["v1.0", "v1.1", "v2.0"],
                trustLevel: "Untrusted"
              },
              {
                id: 6,
                schema: "INSPIRE Metadata",
                catalogs: 4,
                localMapping: "Dataset (4)",
                versioning: "v1.1",
                versionOptions: ["v1.0", "v1.1", "v2.0"],
                trustLevel: "Federated"
              },
              {
                id: 7,
                schema: "DCAT",
                catalogs: 8,
                localMapping: "Service, Data Product",
                versioning: "v2.0",
                versionOptions: ["v1.0", "v1.1", "v2.0"],
                trustLevel: "Federated"
              },
              {
                id: 8,
                schema: "OGC Observations & Measurements",
                catalogs: 2,
                localMapping: "Asset + Safety",
                versioning: "v1.0",
                versionOptions: ["v1.0", "v1.1", "v2.0"],
                trustLevel: "Federated"
              }
            ],

            catalogsTable: [],

            users: [],
            
            harvestRecords: [
              {
                id: 1,
                sourceCatalogue: "SensorML",
                tool: "Mobil-X Crawler",
                harvestDate: "Today, 12:58 pm",
                assetsAdded: "+12",
                duration: "3 mins ago",
                result: "Warning"
              },
              {
                id: 2,
                sourceCatalogue: "SensorML",
                tool: "SensorML Harvester",
                harvestDate: "Today, 11:00 am",
                assetsAdded: "+275",
                duration: "1 hours ago",
                result: "Success"
              },
              {
                id: 3,
                sourceCatalogue: "SensorML",
                tool: "CrowdSense Harvester",
                harvestDate: "Yesterday, 2:58 pm",
                assetsAdded: "+113",
                duration: "1 day ago",
                result: "Error"
              }
            ],
            mappingRows: [
              {
                id: 1,
                remoteCatalogue: "DCAT-AP.de",
                remoteSchema: "Data Service Entity 1.0",
                remoteSchemaMeta: "",
                transformationStrategy: "Deterministic RDF",
                promptsCount: 2,
                shaclCount: 3
              },
              {
                id: 2,
                remoteCatalogue: "DCAT-AP.de",
                remoteSchema: "Energy Product 1.0",
                remoteSchemaMeta: "5",
                transformationStrategy: " AI-driven",
                promptsCount: 1,
                shaclCount: 2
              },
              {
                id: 3,
                remoteCatalogue: "OGC SensorML",
                remoteSchema: "Dataset Schema",
                remoteSchemaMeta: "v1",
                transformationStrategy: "Deterministic RDF",
                promptsCount: 2,
                shaclCount: 3
              },
              {
                id: 4,
                remoteCatalogue: "OGC SensorML",
                remoteSchema: "Mobility Data",
                remoteSchemaMeta: "Mobility 0.3 Data Service",
                transformationStrategy: "Hybrid AI Mapping",
                promptsCount: 0,
                shaclCount: 0
              }
            ],
            selectedMappingRows: [],

            resizeTimer: null,
            userAccess: [],
            showHarvestWizard: false,
            harvestWizardStep: 1,
            
            harvestWizardSearch: "",
            harvestWizardRows: [],
            harvestWizardSelected: [], 
            harvestWizardSelectedRows: [],  // ids
            
            pendingRemoteCatalog: null,
            isRegisteringRemoteCatalog: false,
            registerRemoteCatalogError: "",
            harvestScope: {
              // all_assets | by_type | ever_imported | last_harvest | matching_query | changed_between
              selected: [],
            
              // inputs
              typeValue: "",
              queryValue: "",
            
              // only for changed_between
              fromDate: "",
              toDate: "",
            
              // switch (conditional)
              includeNewAssets: false,
            },

            lifecycleMapping: {
              performSchemaMapping: true,
              updateHandling: "version",    // "version" | "newCatalog"
              deletionHandling: "remove",   // "remove" | "retain"
              resolveReferences: true
            },
            lifecycleMapping: {
              performSchemaMapping: true,
              updateHandling: "version",    // "version" | "newCatalog"
              deletionHandling: "remove",   // "remove" | "retain"
              resolveReferences: true
            },
            overviewToggles: {
              catalogsSelectedEnabled: true,
              mappingStrategiesEnabled: true
            },
            
            harvestWizardRowsBase: [],
            harvestWizardRows: [],
            showAccessInformation: false,

            originalRemoteCatalogForm: null, 
            isUpdatingRemoteCatalog: false,
            updateRemoteCatalogError: "",
            pendingUpdateRemoteCatalogId: null,
            
            accessMap: {
              "Local Catalogue": "local_catalogue",
              "Catalogue Registry": "catalogue_registry",
              "Schema Registry": "schema_registry",
              "Harvest": "harvester",
              "Admin Tools": "admin_tools",
            }, //hossein

        };
    },
    computed: {
        catalogPagination() {
          return this.paginate(this.tableRows, this.pagination.catalog.page, this.pagination.catalog.perPage);
        },
        schemaPagination() {
          return this.paginate(this.schemaRegistry, this.pagination.schema.page, this.pagination.schema.perPage);
        },
        remoteSchemaPagination() {
          return this.paginate(this.remoteSchema, this.pagination.remoteSchema.page, this.pagination.remoteSchema.perPage);
        },
        mappingPagination() {
          return this.paginate(
            this.mappingRows,
            this.pagination.mapping.page,
            this.pagination.mapping.perPage
          );
        },
        catalogsRegisterPagination() {
            const tableRows = this.catalogsTable.map(c => ({
              id: c.id || c.uniqueId,
        
              // columns used by your final table html:
              catalogName: c.catalogName,
              ownerContact: c.owner,
              transformationStrategy: this.strategyLabel(c.strategy),
              accessUrl: c.baseEndpoint,
              enabled: !!c.enabled,
        
              // keep pointer data if needed
              _catalog: c
            }));
        
            return this.paginate(tableRows, this.pagination.catalogsRegister.page, this.pagination.catalogsRegister.perPage);
        },
        usersPagination() {
          return this.paginate(this.users, this.pagination.users.page, this.pagination.users.perPage);
        },
        harvestPagination() {
          return this.paginate(this.harvestRecords, this.pagination.harvest.page, this.pagination.harvest.perPage);
        },
        harvestWizardPagination() {
            return this.paginate(
              this.harvestWizardRows,
              this.pagination.harvestWizard.page,
              this.pagination.harvestWizard.perPage
            );
        },
        isWizardAllSelectedOnPage() {
          const ids = this.harvestWizardPagination.rows.map(r => r.id);
          if (!ids.length) return false;
          return ids.every(id => this.harvestWizardSelectedRows.includes(id));
        },

        
        isHarvestWizardAllPageSelected() {
            const pageKeys = this.harvestWizardPagination.rows.map(r => r._key);
            if (!pageKeys.length) return false;
            return pageKeys.every(k => this.harvestWizardSelected.includes(k));
        },

        filteredAuditMini() {
          const q = this.auditSearch.trim().toLowerCase();
          if (!q) return this.auditMini;
        
          return this.auditMini.filter(r =>
            (r.level || "").toLowerCase().includes(q) ||
            (r.step || "").toLowerCase().includes(q) ||
            (r.timestamp || "").toLowerCase().includes(q)
          );
        },
        catalogOptions() {
            const set = new Set();
            for (const item of this.allCatalogsRaw) {
              const v = item?.catalog?.catalogId;
              if (v) set.add(String(v));
            }
            return Array.from(set).sort();
        },
        
        typeOptions() {
            const set = new Set();
            for (const item of this.allCatalogsRaw) {
              const docs = item?.assets?.documents || [];
              for (const d of docs) {
                const v = d?.format;
                if (v) set.add(String(v));
              }
            }
            return Array.from(set).sort();
        },
        
        domainOptions() {
            const set = new Set();
            for (const item of this.allCatalogsRaw) {
              const v = item?.catalog?.publisher?.website;
              if (v) set.add(String(v));
            }
            return Array.from(set).sort();
        },
        
        statusOptions() {
            return ["Active", "Warning", "Error"];
        },
        canSendInvite() {
              const f = this.inviteForm;
              return (
                f.firstName.trim() &&
                f.lastName.trim() &&
                f.email.trim() &&
                f.role &&
                f.expiresIn
              );
        },
        pageWindow() {
              return (key, size = 5) => {
                const p = this.pagination[key].page;
                const total = this[`${key}Pagination`].totalPages || 1;
            
                const start = Math.min(p, Math.max(1, total - size + 1));
                const end = Math.min(total, start + size - 1);
            
                const pages = [];
                for (let i = start; i <= end; i++) pages.push(i);
                return pages;
              };
        },
        currentSummaryText() {
              const t = this.registerSchemaForm.summaryTab;
              return this.schemaSummaries[t] || "";
        },
            
        filteredRemoteCatalogs() {
              const q = (this.registerSchemaForm.catalogSearch || "").toLowerCase().trim();
              if (!q) return this.registerSchemaForm.remoteCatalogs;
              return this.registerSchemaForm.remoteCatalogs.filter(c => c.toLowerCase().includes(q));
        },
          
        canSendManageUser(){
            const m = this.manageForm;
            return (
                m.firstName.trim() &&
                m.lastName.trim() &&
                m.email.trim() &&
                m.selectedRoles.length > 0 &&
                m.expiresIn
            );
        },
        wizardSelectedCatalogRows() {
          const set = new Set(this.harvestWizardSelectedRows);
          return (this.tableRows || []).filter(r => set.has(r.id));
        },
        
        wizardSelectedCount() {
          return this.wizardSelectedCatalogRows.length;
        },
        
        overviewScopeLines() {
          const s = this.harvestScope || {};
          const selected = Array.isArray(s.selected) ? s.selected : [];
          const lines = [];
        
          const has = (k) => selected.includes(k);
        
          if (has("all_assets")) {
            return ["All assets in the remote catalogue"];
          }
        
          if (has("by_type")) {
            lines.push(`All assets of type: ${s.typeValue || "-"}`);
          }
        
          if (has("matching_query")) {
            lines.push(`Assets matching a query: ${s.queryValue || "-"}`);
          }
        
          if (has("ever_imported")) {
            lines.push("All assets ever imported from that remote catalogue");
          }
        
          if (has("last_harvest")) {
            lines.push("Assets imported in the last harvest");
          }
        
          // Rule 3: changed_between => from ... to ...
          if (has("changed_between")) {
            const from = s.fromDate || "-";
            const to = s.toDate || "-";
            lines.push(`Assets changed between: ${from} → ${to}`);
          }
        
          const canIncludeNew = has("ever_imported") || has("last_harvest");
          if (canIncludeNew && !!s.includeNewAssets) {
            lines.push("Include any new assets in remote catalogue");
          }
        
          return lines.length ? lines : ["— No scope selected"];
        },


        
        overviewLifecycleLines() {
          const l = this.lifecycleMapping;
        
          const updateText =
            l.updateHandling === "version"
              ? "Update Handling: Create new version"
              : "Update Handling: Create new catalog for new assets";
        
          const deletionText =
            l.deletionHandling === "remove"
              ? "Deletion Handling: Remove deleted assets"
              : "Deletion Handling: Retain copy of old assets";
        
          const lines = [updateText, deletionText];
        
          if (l.resolveReferences) lines.push("Resolve References");
        
          return lines;
        },
        
        overviewMappingCounts() {
          const rows = Array.isArray(this.catalogsTable) ? this.catalogsTable : [];
        
          const counts = { ai: 0, hybrid: 0, deterministic: 0, none: 0 };
        
          rows.forEach(r => {
            const st = (r.strategy || r.transformationStrategy || "none");
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
        },
        
        canSelectMulti() {
          return !this.isAllAssetsSelected;
        },
        
        isWizardAllSelected() {
          const ids = this.harvestWizardRows.map(r => r.id);
          if (!ids.length) return false;
          return ids.every(id => this.harvestWizardSelectedRows.includes(id));
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
        },//hossein

    },
    watch: {
      isViewModal(val) {
        if (val) {
          document.body.style.overflow = "hidden";
        } else {
          document.body.style.overflow = "";
        }
      },
      isInviteModal(v){
        document.body.style.overflow = v ? "hidden" : "";
      },
      isRegisterSchemaModal(v){
        document.body.style.overflow = v ? "hidden" : "";
      },
      currentPage(newPage) {
        if (newPage === "catalogueRegistry") {
          uibuilder.send({
            type: "getCatalogRegistry",
            auth: {
              userToken: this.getCookie("userToken"),
              clientId: this.getCookie("uibuilder-client-id"),
            }
          });
    
          console.log("📤 Sent getRemoteCatalogs request");
        }
        if (newPage === "adminTools") {
          uibuilder.send({
            type: "getAdminTools",
            auth: {
              userToken: this.getCookie("userToken"),
              clientId: this.getCookie("uibuilder-client-id"),
            }
          });
    
          console.log("📤 Sent getUsers request");
        }
      } //hossein
    
    },
    methods: {
        getCookie: function (name) {
            let value = "; " + document.cookie;
            let parts = value.split("; " + name + "=");
            if (parts.length == 2) return parts.pop().split(";").shift();
          },
    
        statusClass(status) {
          if (status === "Active") return "green";
          if (status === "Warning") return "yellow";
          if (status === "Error") return "red";
          return "gray";
        },
        setPerPageByViewport() {
          const h = window.innerHeight;
        
          let perPage;
          if (h < 800) perPage = 4;
          else if (h < 900) perPage = 6;
          else if (h < 1000) perPage = 8;
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
            case "catalog": return this.tableRows.length;
            case "schema": return this.schemaRegistry.length;
            case "catalogsRegister": return this.catalogsTable.length;
            case "users": return this.users.length;
            case "harvest": return this.harvestRecords.length;
            case "remoteRegistry": return this.remoteRegistryRows.length;
            default: return 0;
          }
        },
        paginate(list, page, perPage) {
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
        },





    
        onResize() {
          clearTimeout(this.resizeTimer);
          this.resizeTimer = setTimeout(() => {
            this.setPerPageByViewport();
          }, 150);
        },
        trustClass(level) {
          if (level === "Hybrid AI Mapping") return "green";
          if (level === "Deterministic RDF") return "yellow";
          if (level === "AI-driven") return "blue";
          return "gray";
        },
        roleClass(role) {
            if (role === "Harvester") return "blue";
            if (role === "Schema Admin") return "green";
            if (role === "Administrator") return "red";
            return "gray";
        },
        resultClass(result) {
          if (result === "Success") return "green";
          if (result === "Warning") return "yellow";
          if (result === "Error") return "red";
          return "gray";
        },
        logPillClass(level) {
          if (level === "Info") return "blue";
          if (level === "Warning") return "yellow";
          if (level === "Error") return "red";
          return "gray";
        },
        namespaceClass(ns) {
          const v = String(ns || "").trim().toLowerCase();
        
          if (v === "ex:" || v === "ex") return "green";
          if (v === "dcat:" || v === "dcat") return "blue";
          if (v === "dct:" || v === "dct") return "yellow";
        
          return "gray"; // fallback
        },


        parseJsonLine(text) {
            const match = text.match(/^(\s*)"([^"]+)"\s*:\s*"([^"]*)"(.*)$/);
        
            if (!match) return null;
        
            return {
              indent: match[1],
              key: match[2],
              value: match[3],
              suffix: match[4]
            };
        },
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

        
        mapLocalCatalogsToTableRows(data) {
          const catalogs = Array.isArray(data?.catalogs) ? data.catalogs : [];
        
          return catalogs.map((item, i) => {
            const catalogId = item?.assets?.parts?.title ?? "-";
            const domain = item?.catalog?.publisher?.website ?? "-";
            const updatedAt = item?.catalog?.updatedAt ?? "-";
        
            // type -> assets.documents.format
            const firstDocFormat = item?.assets?.documents?.[0]?.format ?? "-";
        
            // name -> vehicles.brand
            const firstBrand = item?.vehicles?.[0]?.brand ?? "-";
        
            return {
              id: i + 1,
              assets: catalogId,
              type: firstDocFormat,
              name: firstBrand,
              domain: domain,
              updated: updatedAt,
              integrationStatus: "Active"
            };
          });
        },
        runSearch() {
          const q = this.normalizeText(this.searchText);
        
          const fCatalog = this.normalizeFilter(this.filters.catalog);
          const fType    = this.normalizeFilter(this.filters.type);
          const fDomain  = this.normalizeFilter(this.filters.domain);
          const fStatus  = this.normalizeFilter(this.filters.status);
        
          if (!q) {
            const filteredRaw = this.allCatalogsRaw.filter(item => {
              if (fCatalog) {
                const catalogId = item?.catalog?.catalogId;
                if (String(catalogId) !== String(fCatalog)) return false;
              }
        
              if (fDomain) {
                const domain = item?.catalog?.publisher?.website;
                if (String(domain) !== String(fDomain)) return false;
              }
        
              if (fType) {
                const docs = item?.assets?.documents || [];
                const hasType = docs.some(d => String(d?.format) === String(fType));
                if (!hasType) return false;
              }
        
              if (fStatus) {
                const status = "Active";
                if (status !== fStatus) return false;
              }
        
              return true;
            });
        
            this.applySearchResults(filteredRaw);
            this.pagination.catalog.page = 1;
            return;
          }
        
          const rows = [];
        
          this.allCatalogsRaw.forEach((item, catalogIndex) => {
            if (fCatalog) {
              const catalogId = item?.catalog?.catalogId;
              if (String(catalogId) !== String(fCatalog)) return;
            }
        
            if (fDomain) {
              const domain = item?.catalog?.publisher?.website;
              if (String(domain) !== String(fDomain)) return;
            }
        
            const assets = this.getCatalogAssets(item);
        
            const filteredAssets = !fType
              ? assets
              : assets.filter(a => !a?.format || String(a?.format) === String(fType));
        
            filteredAssets.forEach((asset, assetIndex) => {
              if (!this.assetMatchesQuery(asset, q)) return;
        
              rows.push({
                id: `c${catalogIndex}-a${assetIndex}`, // unique
        
                assets: this.getAssetTitle(asset),
        
                type: asset?.format ?? (item?.assets?.documents?.[0]?.format ?? "-"),
                name: item?.vehicles?.[0]?.brand ?? "-",
                domain: item?.catalog?.publisher?.website ?? "-",
                updated: item?.catalog?.updatedAt ?? "-",
                integrationStatus: "Active",
        
                __rawCatalog: item,
                __rawAsset: asset
              });
            });
          });
        
          this.tableRows = rows;
          this.pagination.catalog.page = 1;
        },

        matchValue(value, needle) {
          if (!needle) return null;
          if (value == null) return null;
        
          const t = typeof value;
        
          if (t === "string" || t === "number" || t === "boolean") {
            const s = String(value);
            return this.normalizeText(s).includes(needle) ? s : null;
          }
        
          if (Array.isArray(value)) {
            for (const v of value) {
              const r = this.matchValue(v, needle);
              if (r != null) return r;
            }
            return null;
          }
        
          if (t === "object") {
            for (const v of Object.values(value)) {
              const r = this.matchValue(v, needle);
              if (r != null) return r;
            }
            return null;
          }
        
          return null;
        },


        getCatalogAssets(catalogItem) {
          const a = catalogItem?.assets;
          const out = [];
        
          // documents[]
          if (Array.isArray(a?.documents)) out.push(...a.documents);
        
          if (Array.isArray(a?.parts)) out.push(...a.parts);
          else if (a?.parts && typeof a.parts === "object") out.push(a.parts);
        
          // items[]
          if (Array.isArray(a?.items)) out.push(...a.items);
        
          if (Array.isArray(a)) out.push(...a);
        
        
          return out;
        },

        
        getAssetTitle(asset) {
          return (
            asset?.title ||
            asset?.name ||
            asset?.label ||
            asset?.identifier ||
            asset?.assetId ||
            asset?.id ||
            asset?.uri ||
            asset?.url ||
            asset?.meta?.title ||
            asset?.metadata?.title ||
            "-"
          );
        },

        
        assetMatchesQuery(asset, needle) {
          return this.matchValue(asset, needle) != null;
        },




        
        applySearchResults(rawList) {
          this.pagination.catalog.page = 1;
        
          this.tableRows = rawList.map((item, i) => {
            const catalogId = item?.assets?.parts?.title ?? "-";
            const domain    = item?.catalog?.publisher?.website ?? "-";
            const updatedAt = item?.catalog?.updatedAt ?? "-";
        
            const firstDocFormat = item?.assets?.documents?.[0]?.format ?? "-";
            const firstBrand     = item?.vehicles?.[0]?.brand ?? "-";
        
            return {
              id: i + 1,
              assets: catalogId,
              type: firstDocFormat,
              name: firstBrand,
              domain: domain,
              updated: updatedAt,
              integrationStatus: "Active"
            };
          });
        },
        
        normalizeFilter(val) {
          if (!val) return "";
          if (val === "All") return "";
          return val;
        },
        
        clearSearchAndFilters() {
          this.searchText = "";
          this.filters.catalog = "";
          this.filters.type = "";
          this.filters.domain = "";
          this.filters.status = "";
        
          this.applySearchResults(this.allCatalogsRaw);
        },
        normalizeText(v) {
          return String(v ?? "").toLowerCase().trim();
        },
        
        deepIncludes(value, needle) {
          // needle: already normalized lowercase
          if (!needle) return true;
        
          if (value == null) return false;
        
          // string/number/boolean
          const t = typeof value;
          if (t === "string" || t === "number" || t === "boolean") {
            return this.normalizeText(value).includes(needle);
          }
        
          // array
          if (Array.isArray(value)) {
            return value.some(v => this.deepIncludes(v, needle));
          }
        
          // object
          if (t === "object") {
            return Object.values(value).some(v => this.deepIncludes(v, needle));
          }
        
          return false;
        },
        closeInviteModal() {
          this.isInviteModal = false;
          this.resetInviteForm();
        }, //hossein
        sendInvite() {
          const raw = Vue.toRaw(this.inviteForm);
        
          const { role, altRole, firstName, lastName, selectedAccess, ...rest } = raw;
        
          const mappedAccess = (selectedAccess || []).map(
            label => this.accessMap[label] || label
          );
        
          const data = {
            profile: {
              firstName,
              lastName,
            },
            ...rest,
            access: mappedAccess,
          };
        
          uibuilder.send({
            type: "inviteUser",
            auth: {
              userToken: this.getCookie("userToken"),
            },
            data,
          });
        
          console.log("Invite payload:", data);
        
          this.isInviteModal = false;
          this.resetInviteForm();
        }, //hossein
        
        openManageMenu(e, user){
          const el = e.currentTarget;
          const r = el.getBoundingClientRect();
        
          this.manageMenu.open = true;
          this.manageMenu.stage = "root";
          this.manageMenu.userId = user.uniqueId;
          this.manageMenu.anchorEl = el;
        
          this.manageMenu.x = r.left;
          this.manageMenu.y = r.bottom + 8;
        
          this.$nextTick(() => this.fixMenuOverflow());
        },//hossein
        
        closeManageMenu(){
          this.manageMenu.open = false;
          this.manageMenu.userId = null;
          this.manageMenu.stage = "root";
          this.manageMenu.anchorEl = null;
        },
        
        fixMenuOverflow(){
          const menu = document.querySelector(".manage-menu");
          if (!menu) return;
        
          const mr = menu.getBoundingClientRect();
          const pad = 12;
        
          if (mr.right > window.innerWidth - pad) {
            this.manageMenu.x -= (mr.right - (window.innerWidth - pad));
          }
          if (mr.bottom > window.innerHeight - pad) {
            this.manageMenu.y -= (mr.bottom - (window.innerHeight - pad));
          }
        },
        
        updateMenuPosition(){
          if (!this.manageMenu.open || !this.manageMenu.anchorEl) return;
        
          const r = this.manageMenu.anchorEl.getBoundingClientRect();
          this.manageMenu.x = r.left;
          this.manageMenu.y = r.bottom + 8;
          this.fixMenuOverflow();
        },
        
        getUserRole(userId){
          const u = this.users.find(x => x.id === userId);
          return u ? u.role : "";
        },
        
        changeUserRole(userId, newRole){
          const u = this.users.find(x => x.id === userId);
          if (u) u.role = newRole;
          this.closeManageMenu();
        },
        
        deleteUser(userId) {
          this.users = this.users.filter(
            u => String(u.uniqueId) !== String(userId)
          );
        
          this.closeManageMenu();
          this.manageMenu.userId = null;
        }, //hossein
        
        openRegisterSchemaEditModal(){
          this.isRegisterSchemaEditModal = true;
        },
        openRegisterSchemaNewModal(){
          this.isRegisterSchemaNewModal = true;
        },
        closeRegisterSchemaNewModal(){
          this.isRegisterSchemaNewModal = false;
        },
        closeRegisterSchemaEditModal(){
          this.isRegisterSchemaEditModal = false;
        },
        removeRemoteCatalog(name){
          this.registerSchemaForm.remoteCatalogs =
            this.registerSchemaForm.remoteCatalogs.filter(x => x !== name);
        },
        addFirstCatalogFromSearch(){
          const q = (this.registerSchemaForm.catalogSearch || "").trim();
          if (!q) return;
        
          const exists = this.registerSchemaForm.remoteCatalogs.some(x => x.toLowerCase() === q.toLowerCase());
          if (!exists) this.registerSchemaForm.remoteCatalogs.push(q);
        
          this.registerSchemaForm.catalogSearch = "";
        },
        saveRegisterSchemaNew(){
          console.log("Register Remote Schema payload:", this.registerSchemaForm);
          this.closeRegisterSchemaNewModal();
        },
        saveRegisterSchemaEdit(){
          console.log("Register Remote Schema payload:", this.registerSchemaForm);
          this.closeRegisterSchemaEditModal();
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
        
            strategy: "none",
            promptId: "",
            llmConfigId: "",
            namespacesToPreserve: "",
            shaclShapeId: "",
        
            auth: "none",
            trustAnchor: "",
            enabled: true,
          };
        
          this.showRegisterRemoteCatalogModal = true;
        },
        toggleCatalogEnabled(id, e) {
          const c = this.catalogsTable.find(x => x.id === id);
          if (!c) return;
          c.enabled = !!e.target.checked;
        },
        strategyLabel(code) {
            const m = {
              none: "None",
              ai: "AI-driven",
              hybrid: "Hybrid AI Mapping",
              deterministic: "Deterministic RDF"
            };
            return m[code] || code || "None";
        },

        registerRemoteCatalog() {
          const payload = JSON.parse(JSON.stringify(this.remoteCatalogForm));
        
          this.registerRemoteCatalogError = "";
          this.isRegisteringRemoteCatalog = true;
          this.pendingRemoteCatalog = payload;
        
          uibuilder.send({
            type: "registerRemoteCatalog",
            auth: {
              userToken: this.getCookie("userToken"),
              clientId: this.getCookie("uibuilder-client-id"),
            },
            data: payload,
          });
        },



        editRemoteCatalog(row) {
          const found = this.catalogsTable.find(c => c.id === row.id);
          if (!found) return;
        
          this.isEditingRemoteCatalog = true;
          this.editingRemoteCatalogId = found.id;
        
          this.remoteCatalogForm = JSON.parse(JSON.stringify(found));
        
          this.showRegisterRemoteCatalogModal = true;
        },



        closeRegisterRemoteCatalogModal() {
            this.showRegisterRemoteCatalogModal = false;
        },
        
        testRemoteCatalogConnection() {
            // TODO: call API
            console.log("Testing connection...", this.remoteCatalogForm);
        },
        toggleAllMappingRows(e) {
          const checked = e.target.checked;
          if (checked) {
            this.selectedMappingRows = this.mappingPagination.rows.map(r => r.id);
          } else {
            this.selectedMappingRows = [];
          }
        },
        
        strategyPillClass(strategy) {
          const v = String(strategy || "").toLowerCase();
          if (v.includes("deterministic")) return "yellow";
          if (v.includes("hybrid")) return "green";
          if (v.includes("ai")) return "blue";
          return "gray";
        },
        
        openMappingPrompts(row) {
          console.log("Open prompts for:", row);
          // TODO: open prompts modal
        },
        
        openMappingShacl(row) {
          console.log("Open SHACL for:", row);
          // TODO: open SHACL modal
        },
        
        openMappingViewEdit(row) {
          console.log("View/Edit mapping:", row);
          // TODO: open mapping view/edit modal (prefill with row)
        },
        
        removeMappingRow(id) {
          this.mappingRows = this.mappingRows.filter(r => r.id !== id);
          this.selectedMappingRows = this.selectedMappingRows.filter(x => x !== id);
        },

        openManageUserModal() {
          const userId = this.manageMenu.userId;
        
          const user = this.users.find(u => String(u.uniqueId) === String(userId));
          if (!user) return;
        
          const nameParts = (user.name || "").split(" ");
          this.manageForm.firstName = nameParts[0] || "";
          this.manageForm.lastName = nameParts.slice(1).join(" ") || "";
          this.manageForm.email = user.email || "";
        
          const accessKeys = Array.isArray(user.access) ? user.access : [];
        
          const labels = accessKeys
            .map(k => this.inverseAccessMap?.[k])
            .filter(Boolean);
        
          if (!labels.includes("Local Catalogue")) labels.unshift("Local Catalogue");
        
          this.manageForm.selectedRoles = labels;
        
          this.manageForm.expiresIn = user.expiresIn || "30 Days";
          this.manageForm.altRole = "";
          this.manageForm.message = "";
        
          this.manageUserModal = true;
          this.manageMenu.open = false;
        }, //hossein

        closeManageUserModal(){
          this.manageUserModal = false;
          this.manageForm.selectedRoles = ["Local Catalogue"];
        },
        
        sendManageUser() {
          const userId = this.manageMenu.userId;
          const user = this.users.find(u => String(u.uniqueId) === String(userId));
        
          if (user) {
            user.name = `${this.manageForm.firstName} ${this.manageForm.lastName}`.trim();
            user.email = this.manageForm.email;
        
            // label -> access key
            const accessKeys = (this.manageForm.selectedRoles || []).map(
              label => this.accessMap[label] || label
            );
        
            if (!accessKeys.includes("local_catalogue")) {
              accessKeys.unshift("local_catalogue");
            }
        
            user.access = accessKeys;
            user.expiresIn = this.manageForm.expiresIn || user.expiresIn;
          }
        
          this.manageUserModal = false;
          this.manageForm.selectedRoles = ["Local Catalogue"];
        }, //hossein
        
        hasAccess(accessKey) {
            return this.userAccess.includes(accessKey);
        },
        openHarvestWizard() {
          this.showHarvestWizard = true;
          this.harvestWizardStep = 1;
        
          this.harvestWizardSearch = "";
          this.harvestWizardSelectedRows = [];
          this.pagination.harvestWizard.page = 1;
        
          this.harvestWizardRowsBase = this.allCatalogsRaw.map((item, idx) => ({
            id: item?.id ?? idx + 1,
            catalog: item?.catalog?.catalogId ?? "-",
            type: (item?.assets?.documents?.[0]?.format ?? "-"),
            name: (item?.vehicles?.[0]?.brand ?? "-"),
            domain: (item?.catalog?.publisher?.website ?? "-"),
            updated: (item?.catalog?.updatedAt ?? "-"),
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
          const q = this.normalizeText(this.harvestWizardSearch);
        
          const filteredRaw = this.allCatalogsRaw.filter(item => {
            const blob = JSON.stringify(item);
            return this.normalizeText(blob).includes(q);
          });
        
          this.harvestWizardRows = this.mapLocalCatalogsToTableRows({ catalogs: filteredRaw });
        
          this.pagination.harvestWizard.page = 1;
        },
        
        applyHarvestWizardRows(rawList) {
            this.pagination.harvestWizard.page = 1;
        
            this.harvestWizardRows = (rawList || []).map((item, i) => {
              const catalogue = item?.catalog?.catalogId ?? item?.catalog?.catalogName ?? `Catalogue ${i + 1}`;
        
              const description =
                item?.catalog?.publisher?.website ??
                item?.catalog?.publisher?.name ??
                item?.catalog?.description ??
                "-";
        
              const trustLevel = item?.catalog?.trustLevel ?? "Federated";
        
              const versioning =
                item?.catalog?.versioning ??
                item?.catalog?.version ??
                "0 / 0";
        
              const assetCount = Array.isArray(item?.assets?.documents) ? item.assets.documents.length : 0;
              const assets = `${assetCount} / ${assetCount}`;
        
              return {
                _key: String(item?.id ?? item?.catalog?.catalogId ?? i + 1),
                catalogue,
                description,
                trustLevel,
                versioning,
                assets,
                __raw: item
              };
            });
        },
        
       toggleWizardRow(id){
          const i = this.harvestWizardSelectedRows.indexOf(id);
          if (i === -1) this.harvestWizardSelectedRows.push(id);
          else this.harvestWizardSelectedRows.splice(i, 1);
        },
        
        toggleWizardSelectAll(e) {
          const checked = e.target.checked;
        
          if (checked) {
            this.harvestWizardSelectedRows = this.harvestWizardRows.map(r => r.id);
          } else {
            this.harvestWizardSelectedRows = [];
          }
        },
        
        setChangedSinceNow(){
          const d = new Date();
          const pad = (n) => String(n).padStart(2, "0");
          const yyyy = d.getFullYear();
          const mm = pad(d.getMonth() + 1);
          const dd = pad(d.getDate());
          const hh = pad(d.getHours());
          const mi = pad(d.getMinutes());
        
          this.harvestScope.changedSince = `${yyyy}-${mm}-${dd}T${hh}:${mi}`;
          this.harvestScope.mode = "changedSince";
        },
        startHarvest() {
          const payload = {
            selectedCatalogRowIds: [...this.harvestWizardSelectedRows],
            harvestScope: { ...this.harvestScope },
            lifecycleMapping: { ...this.lifecycleMapping },
            overviewToggles: { ...this.overviewToggles }
          };
        
          console.log("START HARVEST payload:", payload);
        
          // TODO: API call
          // fetch('/api/harvest', { method:'POST', body: JSON.stringify(payload) ... })
        
          this.closeHarvestWizard();
        },
        toggleScopeOption(key) {
              const s = this.harvestScope.selected;
            
              if (key === "all_assets") {
                if (s.includes("all_assets")) {
                  this.harvestScope.selected = [];
                } else {
                  this.harvestScope.selected = ["all_assets"];
                }
                return;
              }
            
              if (s.includes("all_assets")) return;
            
              if (s.includes(key)) {
                this.harvestScope.selected = s.filter(x => x !== key);
              } else {
                this.harvestScope.selected = [...s, key];
              }
            
              if (!this.showIncludeNewAssetsToggle) {
                this.harvestScope.includeNewAssets = false;
              }
        },

        saveRemoteCatalog() {
          const current = JSON.parse(JSON.stringify(this.remoteCatalogForm));
        
          // EDIT MODE
          if (this.isEditingRemoteCatalog && this.editingRemoteCatalogId != null) {
              const old = this.originalRemoteCatalogForm || {};
              const patch = this.getChangedFields(old, current);
            
              if (Object.keys(patch).length === 0) {
                this.closeRegisterRemoteCatalogModal();
                return;
              }
            
              this.isUpdatingRemoteCatalog = true;
              this.updateRemoteCatalogError = "";
              this.pendingUpdateRemoteCatalogId = this.editingRemoteCatalogId;
            
              uibuilder.send({
                type: "updateRemoteCatalog",
                auth: {
                  userToken: this.getCookie("userToken"),
                  clientId: this.getCookie("uibuilder-client-id"),
                },
                data: {
                  uniqueId: this.editingRemoteCatalogId,
                  patch,
                },
              });
            
              return;
            }
        
          // CREATE MODE
          this.registerRemoteCatalog();
        }, 
        
        clearFilters() {
            this.searchText = "";
        
            this.filters = {
              catalog: "",
              type: "",
              domain: "",
              status: "",
            };
        
            this.pagination.catalog.page = 1;
        
            this.runSearch(); 
        },

        openAccessInformation(){
            this.showAccessInformation = true;
        },
        closeAccessInformation(){
            this.showAccessInformation = false;
        },
        
        getChangedFields(oldObj, newObj) {
          const patch = {};
          const keys = new Set([
            ...Object.keys(oldObj || {}),
            ...Object.keys(newObj || {}),
          ]);
        
          keys.forEach((k) => {
            const a = oldObj?.[k];
            const b = newObj?.[k];
        
            if (a !== b) patch[k] = b;
          });
        
          return patch;
        }, 
        
        openEditRemoteCatalog(row) {
          this.isEditingRemoteCatalog = true;
          this.editingRemoteCatalogId = row.id;
        
          this.remoteCatalogForm = JSON.parse(JSON.stringify(row));
        
          this.originalRemoteCatalogForm = JSON.parse(JSON.stringify(row));
        
          this.showRegisterRemoteCatalogModal = true;
        }, 
        
        toggleLifecycleCard(key) {
          if (!this.lifecycleMapping || !(key in this.lifecycleMapping)) return;
          this.lifecycleMapping[key] = !this.lifecycleMapping[key];
        },
        
        getAccessInitial(key) {
          const map = {
            local_catalogue: "L",
            catalogue_registry: "C",
            schema_registry: "S",
            admin_tools: "A",
            harvester: "H",
          };
        
          return map[key] || "?";
        }, //hossein


        resetInviteForm() {
          this.inviteForm = {
            firstName: "",
            lastName: "",
            email: "",
            role: "Searcher",
            expiresIn: "30 Days",
            altRole: "",
            message: "You have been invited to join the federated catalogue system.",
            selectedAccess: ["Local Catalogue"],
          };
        }, //hossein
        
        logout(){
            uibuilder.send({
            type: "logOut",
            auth: {
              userToken: this.getCookie("userToken"),
              clientId: this.getCookie("uibuilder-client-id"),
            }
          });
        }

    },
    mounted() {
        
        
        uibuilder.start();
        uibuilder.send({
            type: 'getDashboard',
            auth: {
                userToken: this.getCookie('userToken'),
                clientId:this.getCookie('uibuilder-client-id')
            }
        });
        uibuilder.onChange("msg", (msg) => {
            console.log(msg)
            const payload = msg?.payload ?? msg;
            const resp = payload?.response ?? msg?.response;
            
            if (resp?.action === "registerRemoteCatalog") {
              this.isRegisteringRemoteCatalog = false;
            
              if (resp.status === "success") {
                const newItem = this.pendingRemoteCatalog;
                this.pendingRemoteCatalog = null;
            
                const remoteCatalogId = resp.uniqueId || msg?.response?.uniqueId;
            
                const row = {
                  ...newItem,
                  uniqueId: remoteCatalogId,
                  id: remoteCatalogId,
                };
            
                const idx = this.catalogsTable.findIndex(x => String(x.id) === String(remoteCatalogId));
                if (idx !== -1) this.catalogsTable.splice(idx, 1, row);
                else this.catalogsTable.unshift(row);
            
                this.pagination.catalogsRegister.page = 1;
                this.closeRegisterRemoteCatalogModal();
              } else {
                this.registerRemoteCatalogError =
                  resp?.message || "Register remote catalog failed";
              }
            }

        
            if(payload.state === "notLoggedIn"){
                window.location.href = "/asal-asal/login";
            }
        
            if (payload?.type === "getDashboard") {
              this.userAccess = payload?.response?.userAccess || [];
            
            if (
                (this.currentPage === "localCatalogue" && !this.hasAccess("local_catalogue")) ||
                (this.currentPage === "catalogueRegistry" && !this.hasAccess("catalogue_registry")) ||
                (this.currentPage === "schemaRegistry" && !this.hasAccess("schema_registry")) ||
                (this.currentPage === "harvester" && !this.hasAccess("harvester")) ||
                (this.currentPage === "adminTools" && !this.hasAccess("admin_tools"))
                ) {
                if (this.hasAccess("local_catalogue")) {
                  this.currentPage = "localCatalogue";
                } else if (this.hasAccess("catalogue_registry")) {
                  this.currentPage = "catalogueRegistry";
                } else if (this.hasAccess("schema_registry")) {
                  this.currentPage = "schemaRegistry";
                } else if (this.hasAccess("harvester")) {
                  this.currentPage = "harvester";
                } else if (this.hasAccess("admin_tools")) {
                  this.currentPage = "adminTools";
                } else {
                  this.currentPage = ""; 
                }
              }
            }
            
            if (resp?.action === "getCatalogRegistry") {
              if (resp.status === "success") {
                const catalogs = Array.isArray(resp.catalogs) ? resp.catalogs : [];
            
                this.catalogsTable = catalogs.map((item) => ({
                  uniqueId: item.uniqueId,
                  id: item.uniqueId,
                  ...(item.catalog || {}),
                }));
            
                this.pagination.catalogsRegister.page = 1;
              } else {
                console.error("getCatalogRegistry failed:", resp);
                this.catalogsTable = [];
              }
            }

            if (resp?.action === "updateRemoteCatalog") {
              const id = msg?.data?.uniqueId;
            
              this.isUpdatingRemoteCatalog = false;
            
              if (resp?.status === "success") {
                const patch = msg?.data?.patch || {};
            
                const idx = this.catalogsTable.findIndex(c => String(c.uniqueId) === String(id));
                if (idx !== -1) {
                  this.catalogsTable.splice(idx, 1, {
                    ...this.catalogsTable[idx],
                    ...patch,
                  });
                }
            
                this.closeRegisterRemoteCatalogModal();
            
                // alert("Catalog updated successfully ✅")
            
              } else {
                this.updateRemoteCatalogError = resp?.message || "Update failed ❌";
              }
            }
            
            // Invite User response handler
            if (resp?.action === "inviteUser") {
              if (resp?.status === "success") {
                const sent = payload?.data ?? msg?.data ?? {};
                const firstName = sent?.profile?.firstName ?? sent?.firstName ?? "";
                const lastName  = sent?.profile?.lastName  ?? sent?.lastName  ?? "";
            
                const uid =
                  resp?.uniqueId ??
                  msg?.response?.uniqueId ??
                  payload?.response?.uniqueId;
            
                const accessKeys = Array.isArray(sent?.access) ? sent.access : [];
            
                const newUser = {
                  uniqueId: uid,
                  name: `${firstName} ${lastName}`.trim(),
                  avatar: "./img/avatar-16.jpg",
                  email: sent?.email ?? "",
                  access: accessKeys,
                  status: "Invited",
                  expiresIn: sent?.expiresIn ?? "30 Days",
                };
            
                let idx = -1;
            
                if (uid) {
                  idx = this.users.findIndex(u => String(u.uniqueId) === String(uid));
                }
                if (idx === -1 && newUser.email) {
                  idx = this.users.findIndex(u => String(u.email) === String(newUser.email));
                }
            
                if (idx !== -1) this.users.splice(idx, 1, newUser);
                else this.users.unshift(newUser);
            
                this.pagination.users.page = 1;
              } else {
                console.error("inviteUser failed:", resp);
              }
            } //hossein

            if (msg?.type === "getAdminTools" && msg?.response?.status === "success") {
              console.log("Users from backend:", msg.response.users);
              const list = msg.response.users || [];
            
              this.users = list.map((u, i) => {
                const uid = u.uniqueId ?? u.id ?? u._id ?? String(i);
            
                return {
                  ...u,
                  uniqueId: uid,
                  name: (`${u.profile?.firstName ?? ""} ${u.profile?.lastName ?? ""}`).trim()
                        || u.name
                        || u.email
                        || "—",
                
                  avatar: u.avatar || "./img/avatar-16.jpg",
                  email: u.email || "—",
                  status: u.status || (u.invited ? "Invited" : "Active"),
                };
              });
            
              console.log("✅ Admin Tools users mapped:", Vue.toRaw(this.users));
            } //hossein
            
            if(resp?.action === "logOut" && resp?.status === "success"){
                window.location.href = "/asal-asal/login";
                document.cookie = "userToken=; path=/; max-age=0";
            }//hossein


        });

      this.setPerPageByViewport();
      window.addEventListener("resize", this.onResize);
      this.loadLocalCatalogs();
      window.addEventListener("scroll", this.updateMenuPosition, true);
      window.addEventListener("resize", this.updateMenuPosition);


    },
    beforeUnmount() {
      window.removeEventListener("resize", this.onResize);
      document.removeEventListener("click", this.closeAllMenus);
      window.removeEventListener("scroll", this.updateMenuPosition, true);
      window.removeEventListener("resize", this.updateMenuPosition);

    },
}).mount('#app');
