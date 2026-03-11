/**
 * main.js — Dashboard entry point
 *
 * Mounts the Vue 3 app, registers all components,
 * and wires the FACIS service to the store.
 */

import { uibuilderService } from "./services/uibuilder.service.js";
import { createStoreData } from "./state/store.js";
import {
  statusClass, trustClass, roleClass, resultClass, logPillClass,
  namespaceClass, strategyPillClass, strategyLabel, getAccessInitial
} from "./utils/formatters.js";
import {
  getCookie, normalizeText, normalizeFilter, paginate, deepIncludes,
  matchValue, getCatalogAssets, getAssetTitle, assetMatchesQuery,
  getChangedFields, parseJsonLine
} from "./utils/helpers.js";

// Components
import AppSidebar from "./components/Sidebar.js";
import AppTopbar from "./components/Topbar.js";
import StatCard from "./components/StatCard.js";
import TableStatusbar from "./components/TableStatusbar.js";
import DashboardLayout from "./layouts/DashboardLayout.js";

// Views
import LocalCatalogueView from "./views/LocalCatalogueView.js";
import CatalogueRegistryView from "./views/CatalogueRegistryView.js";
import SchemaRegistryView from "./views/SchemaRegistryView.js";
import AdminToolsView from "./views/AdminToolsView.js";
import HarvesterView from "./views/HarvesterView.js";

// Modals
import ViewModal from "./modals/ViewModal.js";
import InviteModal from "./modals/InviteModal.js";
import ManageUserModal from "./modals/ManageUserModal.js";
import RegisterCatalogModal from "./modals/RegisterCatalogModal.js";
import SchemaModal from "./modals/SchemaModal.js";
import HarvestWizardModal from "./modals/HarvestWizardModal.js";
import AccessInfoModal from "./modals/AccessInfoModal.js";
import ManageMenu from "./modals/ManageMenu.js";

// ─── Initialise FACIS service ────────────────────────────────────
uibuilderService.init();

// ─── Create Vue app ──────────────────────────────────────────────
const { createApp, toRaw } = Vue;

const app = createApp({
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
      const tableRows = this.catalogsTable.map(c => ({
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
      const ids = this.harvestWizardRows.map(r => r.id);
      if (!ids.length) return false;
      return ids.every(id => this.harvestWizardSelectedRows.includes(id));
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
      return this.registerSchemaForm.remoteCatalogs.filter(c => c.toLowerCase().includes(q));
    },
    filteredPrompts() {
      const q = (this.promptSearch || "").trim().toLowerCase();
      if (!q) return this.prompts;
      return this.prompts.filter(p =>
        (p.id || "").toLowerCase().includes(q) ||
        (p.sourceSchema || "").toLowerCase().includes(q) ||
        (p.targetSchema || "").toLowerCase().includes(q) ||
        (p.status || "").toLowerCase().includes(q)
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
      return this.llmConfigs.filter(c =>
        (c.id || "").toLowerCase().includes(q) ||
        (c.name || "").toLowerCase().includes(q) ||
        (c.provider || "").toLowerCase().includes(q) ||
        (c.model || "").toLowerCase().includes(q) ||
        (c.status || "").toLowerCase().includes(q)
      );
    },
    resolvedPromptPreview() {
      if (!this.promptTestSelectedPrompt || !this.promptTestSampleInput) return "";
      const p = this.prompts.find(x => x.id === this.promptTestSelectedPrompt);
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
      return this.auditMini.filter(r =>
        (r.level || "").toLowerCase().includes(q) ||
        (r.step || "").toLowerCase().includes(q) ||
        (r.timestamp || "").toLowerCase().includes(q)
      );
    },
    filteredMonitoringEvents() {
      const f = this.monitoringEventFilter;
      const q = (this.monitoringAuditSearch || "").trim().toLowerCase();
      let events = this.monitoringEvents;
      if (f !== "all") events = events.filter(e => e.type === f);
      if (q) events = events.filter(e =>
        (e.source || "").toLowerCase().includes(q) ||
        (e.message || "").toLowerCase().includes(q) ||
        (e.timestamp || "").toLowerCase().includes(q)
      );
      return events;
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
          if (d?.format) set.add(String(d.format));
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
      const updateText = l.updateHandling === "version"
        ? "Update Handling: Create new version"
        : "Update Handling: Create new catalog for new assets";
      const deletionText = l.deletionHandling === "remove"
        ? "Deletion Handling: Remove deleted assets"
        : "Deletion Handling: Retain copy of old assets";
      const lines = [updateText, deletionText];
      return lines;
    },
    overviewMappingCounts() {
      const rows = Array.isArray(this.catalogsTable) ? this.catalogsTable : [];
      const counts = { ai: 0, hybrid: 0, deterministic: 0, none: 0 };
      rows.forEach(r => {
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
    },
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
    statusClass, trustClass, roleClass, resultClass, logPillClass,
    namespaceClass, strategyPillClass, strategyLabel, getAccessInitial,
    parseJsonLine,

    // ── Helpers ────────────────────────────────────────────────
    getCookie,
    hasAccess(key) { return this.userAccess.includes(key); },
    canRead(area)   { return !!(this.userPermissions[area] && this.userPermissions[area].read); },
    canCreate(area) { return !!(this.userPermissions[area] && this.userPermissions[area].create); },
    canUpdate(area) { return !!(this.userPermissions[area] && this.userPermissions[area].update); },
    canDelete(area) { return !!(this.userPermissions[area] && this.userPermissions[area].delete); },

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
        default: return 0;
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
        const filteredRaw = this.allCatalogsRaw.filter(item => {
          if (fCatalog && String(item?.catalog?.catalogId) !== String(fCatalog)) return false;
          if (fDomain && String(item?.catalog?.publisher?.website) !== String(fDomain)) return false;
          if (fType) {
            const docs = item?.assets?.documents || [];
            if (!docs.some(d => String(d?.format) === String(fType))) return false;
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
        const filteredAssets = !fType ? assets : assets.filter(a => !a?.format || String(a?.format) === String(fType));
        filteredAssets.forEach((asset, assetIndex) => {
          if (!assetMatchesQuery(asset, q)) return;
          rows.push({
            id: `c${catalogIndex}-a${assetIndex}`,
            assets: getAssetTitle(asset),
            type: asset?.format ?? (item?.assets?.documents?.[0]?.format ?? "-"),
            name: item?.vehicles?.[0]?.brand ?? "-",
            domain: item?.catalog?.publisher?.website ?? "-",
            updated: item?.catalog?.updatedAt ?? "-",
            integrationStatus: "Active",
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
        integrationStatus: this.assetDetailRow.integrationStatus,
      };
      this.isEditingAsset = true;
    },
    cancelEditAsset() {
      this.isEditingAsset = false;
    },
    saveEditAsset() {
      if (!this.assetDetailRow) return;
      const idx = this.tableRows.findIndex(r => r.id === this.assetDetailRow.id);
      if (idx !== -1) {
        const updated = { ...this.tableRows[idx], ...this.assetEditForm, updated: new Date().toISOString().slice(0, 10) };
        this.tableRows.splice(idx, 1, updated);
        this.assetDetailRow = { ...updated };
      }
      this.isEditingAsset = false;
      this.addToast("success", "Asset updated.");
    },
    deleteAsset(id) {
      this.tableRows = this.tableRows.filter(r => r.id !== id);
      this.selectedRows = this.selectedRows.filter(x => x !== id);
      if (this.assetDetailRow && this.assetDetailRow.id === id) {
        this.closeAssetDetail();
      }
      this.addToast("success", "Asset deleted.");
    },
    confirmDeleteAsset(id) {
      this.showConfirm("Delete Asset", "Are you sure you want to delete this asset? This action cannot be undone.", "Delete", () => this.deleteAsset(id));
    },
    archiveAsset(id) {
      const idx = this.tableRows.findIndex(r => r.id === id);
      if (idx !== -1) {
        this.tableRows.splice(idx, 1, { ...this.tableRows[idx], integrationStatus: 'Archived' });
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
      this.showConfirm("Delete Assets", `Are you sure you want to delete ${count} selected asset${count > 1 ? 's' : ''}? This action cannot be undone.`, "Delete", () => {
        this.tableRows = this.tableRows.filter(r => !this.selectedRows.includes(r.id));
        if (this.assetDetailRow && this.selectedRows.includes(this.assetDetailRow.id)) {
          this.closeAssetDetail();
        }
        this.selectedRows = [];
        this.addToast("success", `${count} asset${count > 1 ? 's' : ''} deleted.`);
      });
    },
    bulkChangeStatus(status) {
      if (!this.selectedRows.length) return;
      const set = new Set(this.selectedRows);
      this.tableRows = this.tableRows.map(r => set.has(r.id) ? { ...r, integrationStatus: status } : r);
      this.selectedRows = [];
    },
    bulkExportAssets() {
      if (!this.selectedRows.length) return;
      const set = new Set(this.selectedRows);
      const rows = this.tableRows.filter(r => set.has(r.id));
      const headers = ["ID", "Assets", "Type", "Name", "Domain", "Updated", "Integration Status"];
      const csvRows = rows.map(r => [r.id, r.assets, r.type, r.name, r.domain, r.updated, r.integrationStatus].map(v => `"${String(v).replace(/"/g, '""')}"`).join(","));
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
        this.selectedRows = this.catalogPagination.rows.map(r => r.id);
      } else {
        this.selectedRows = [];
      }
    },

    // ── Catalog Registry ───────────────────────────────────────
    toggleCatalogEnabled(id, e) {
      const c = this.catalogsTable.find(x => x.id === id);
      if (c) c.enabled = !!e.target.checked;
    },
    openRegisterRemoteCatalogModal() {
      this.isEditingRemoteCatalog = false;
      this.editingRemoteCatalogId = null;
      this.remoteCatalogForm = {
        catalogId: "", catalogName: "", owner: "",
        protocol: "Query interface", baseEndpoint: "",
        mimeType: "application/sparql-results+json",
        queryEndpoint: "", queryLanguages: "",
        metadataPrefix: "oai_dc", setSpec: "", resumptionToken: false,
        dcatCatalogUri: "", linkedDataEndpoint: "", contentNegotiation: "application/ld+json",
        strategy: "none", promptId: "", llmConfigId: "",
        namespacesToPreserve: "", shaclShapeId: "",
        auth: "none", trustAnchor: "", enabled: true,
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
        data: payload,
      });
    },
    saveRemoteCatalog() {
      const current = JSON.parse(JSON.stringify(this.remoteCatalogForm));
      if (this.isEditingRemoteCatalog && this.editingRemoteCatalogId != null) {
        const old = this.originalRemoteCatalogForm || {};
        const patch = getChangedFields(old, current);
        if (Object.keys(patch).length === 0) { this.closeRegisterRemoteCatalogModal(); return; }
        this.isUpdatingRemoteCatalog = true;
        this.updateRemoteCatalogError = "";
        this.pendingUpdateRemoteCatalogId = this.editingRemoteCatalogId;
        uibuilderService.send({
          type: "updateRemoteCatalog",
          auth: { userToken: getCookie("userToken"), clientId: getCookie("uibuilder-client-id") },
          data: { uniqueId: this.editingRemoteCatalogId, patch },
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
        open: true, stage: "root", userId: user.uniqueId,
        anchorEl: el, x: r.left, y: r.bottom + 8
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
      if (mr.right > window.innerWidth - 12) this.manageMenu.x -= (mr.right - (window.innerWidth - 12));
      if (mr.bottom > window.innerHeight - 12) this.manageMenu.y -= (mr.bottom - (window.innerHeight - 12));
    },
    updateMenuPosition() {
      if (!this.manageMenu.open || !this.manageMenu.anchorEl) return;
      const r = this.manageMenu.anchorEl.getBoundingClientRect();
      this.manageMenu.x = r.left;
      this.manageMenu.y = r.bottom + 8;
      this.fixMenuOverflow();
    },
    deleteUser(userId) {
      const user = this.users.find(u => String(u.uniqueId) === String(userId));
      const name = user?.name || "this user";
      this.closeManageMenu();
      this.showConfirm("Delete User", `Are you sure you want to delete "${name}"? This action cannot be undone.`, "Delete", () => {
        this.users = this.users.filter(u => String(u.uniqueId) !== String(userId));
        this.addToast("success", "User deleted successfully.");
      });
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
      const labels = accessKeys.map(k => this.inverseAccessMap?.[k]).filter(Boolean);
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
      const user = this.users.find(u => String(u.uniqueId) === String(userId));
      if (user) {
        user.name = `${this.manageForm.firstName} ${this.manageForm.lastName}`.trim();
        user.email = this.manageForm.email;
        const accessKeys = (this.manageForm.selectedRoles || []).map(label => this.accessMap[label] || label);
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
      const mappedAccess = (selectedAccess || []).map(label => this.accessMap[label] || label);
      const data = { profile: { firstName, lastName }, ...rest, access: mappedAccess };
      uibuilderService.send({
        type: "inviteUser",
        auth: { userToken: getCookie("userToken") },
        data,
      });
      this.isInviteModal = false;
      this.resetInviteForm();
      this.addToast("success", "Invitation sent successfully.");
    },
    resetInviteForm() {
      this.inviteForm = {
        firstName: "", lastName: "", email: "",
        role: "Searcher", expiresIn: "30 Days", altRole: "",
        message: "You have been invited to join the federated catalogue system.",
        selectedAccess: ["Local Catalogue"],
      };
    },

    // ── Schema Modals ──────────────────────────────────────────
    openRegisterSchemaEditModal() { this.isRegisterSchemaEditModal = true; },
    openRegisterSchemaNewModal() { this.isRegisterSchemaNewModal = true; },
    closeRegisterSchemaNewModal() { this.isRegisterSchemaNewModal = false; },
    closeRegisterSchemaEditModal() { this.isRegisterSchemaEditModal = false; },
    removeRemoteCatalog(name) {
      this.registerSchemaForm.remoteCatalogs = this.registerSchemaForm.remoteCatalogs.filter(x => x !== name);
    },
    addFirstCatalogFromSearch() {
      const q = (this.registerSchemaForm.catalogSearch || "").trim();
      if (!q) return;
      const exists = this.registerSchemaForm.remoteCatalogs.some(x => x.toLowerCase() === q.toLowerCase());
      if (!exists) this.registerSchemaForm.remoteCatalogs.push(q);
      this.registerSchemaForm.catalogSearch = "";
    },
    saveRegisterSchemaNew() { this.closeRegisterSchemaNewModal(); },
    saveRegisterSchemaEdit() { this.closeRegisterSchemaEditModal(); },

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
        const idx = this.assetTypes.findIndex(t => t.id === this.assetTypeForm.id);
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
      const at = this.assetTypes.find(t => t.id === id);
      this.showConfirm("Delete Asset Type", `Are you sure you want to delete "${at?.name || 'this type'}"?`, "Delete", () => {
        this.assetTypes = this.assetTypes.filter(t => t.id !== id);
        this.addToast("success", "Asset type deleted.");
      });
    },

    // ── Prompt Management (FR-SR-03, FR-SR-04) ─────────────────
    openPromptModal() {
      this.isEditingPrompt = false;
      this.promptFormError = "";
      this.promptForm = {
        id: null, version: "1.0", status: "draft",
        sourceSchema: "", targetSchema: "",
        template: "", examples: "", constraints: "",
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

      // Enforce: only one active prompt per source-target pair
      if (this.promptForm.status === "active") {
        const conflict = this.prompts.find(p =>
          p.status === "active" &&
          p.sourceSchema === this.promptForm.sourceSchema &&
          p.targetSchema === this.promptForm.targetSchema &&
          p.id !== this.promptForm.id
        );
        if (conflict) {
          this.promptFormError = `Only one active prompt allowed per source-target pair. "${conflict.id}" is already active for ${conflict.sourceSchema} → ${conflict.targetSchema}.`;
          return;
        }
      }

      const now = new Date().toISOString().slice(0, 10);
      if (this.isEditingPrompt && this.promptForm.id) {
        const idx = this.prompts.findIndex(p => p.id === this.promptForm.id);
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
        this.prompts = this.prompts.filter(p => p.id !== id);
        this.addToast("success", "Prompt deleted.");
      });
    },
    changePromptStatus(prompt, newStatus) {
      // Enforce: only one active per source-target pair
      if (newStatus === "active") {
        const conflict = this.prompts.find(p =>
          p.status === "active" &&
          p.sourceSchema === prompt.sourceSchema &&
          p.targetSchema === prompt.targetSchema &&
          p.id !== prompt.id
        );
        if (conflict) {
          this.promptFormError = `Cannot activate: "${conflict.id}" is already active for ${conflict.sourceSchema} → ${conflict.targetSchema}.`;
          return;
        }
      }
      const idx = this.prompts.findIndex(p => p.id === prompt.id);
      if (idx !== -1) {
        this.prompts.splice(idx, 1, { ...this.prompts[idx], status: newStatus, updatedAt: new Date().toISOString().slice(0, 10) });
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
        case "active": return "green";
        case "draft": return "blue";
        case "deprecated": return "yellow";
        case "archived": return "gray";
        default: return "gray";
      }
    },

    // ── LLM Configuration (FR-SR-11) ─────────────────────────
    openLlmConfigModal() {
      this.isEditingLlmConfig = false;
      this.llmConfigError = "";
      this.llmConfigForm = {
        id: null, name: "", provider: "OpenAI", model: "",
        temperature: 0.3, maxTokens: 4096, timeout: 30, status: "active",
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
      const now = new Date().toISOString().slice(0, 10);
      if (this.isEditingLlmConfig && this.llmConfigForm.id) {
        const idx = this.llmConfigs.findIndex(c => c.id === this.llmConfigForm.id);
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
      const cfg = this.llmConfigs.find(c => c.id === id);
      this.showConfirm("Delete LLM Configuration", `Are you sure you want to delete "${cfg?.name || id}"?`, "Delete", () => {
        this.llmConfigs = this.llmConfigs.filter(c => c.id !== id);
        this.addToast("success", "LLM configuration deleted.");
      });
    },
    llmProviderClass(provider) {
      switch (provider) {
        case "OpenAI": return "green";
        case "Anthropic": return "blue";
        case "Mistral": return "yellow";
        case "Google": return "blue";
        case "Azure OpenAI": return "green";
        default: return "gray";
      }
    },

    // ── Prompt Testing (FR-SR-10) ─────────────────────────────
    runPromptTest() {
      if (!this.promptTestSelectedPrompt || !this.promptTestSelectedLlm || !this.promptTestSampleInput) return;
      this.promptTestRunning = true;
      this.promptTestResult = "";
      this.promptTestError = "";
      const prompt = this.prompts.find(p => p.id === this.promptTestSelectedPrompt);
      const llmCfg = this.llmConfigs.find(c => c.id === this.promptTestSelectedLlm);
      // Simulate dry-run with resolved template
      setTimeout(() => {
        try {
          let input;
          try { input = JSON.parse(this.promptTestSampleInput); } catch (e) { input = this.promptTestSampleInput; }
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
              "timestamp": new Date().toISOString(),
            }
          };
          this.promptTestResult = JSON.stringify(result, null, 2);
        } catch (err) {
          this.promptTestError = "Transformation failed: " + err.message;
        }
        this.promptTestRunning = false;
      }, 1500 + Math.random() * 1000);
    },
    openSaveTestCaseModal() {
      this.isEditingTestCase = false;
      this.testCaseForm = {
        id: null,
        name: "",
        promptId: this.promptTestSelectedPrompt || "",
        llmConfigId: this.promptTestSelectedLlm || "",
        sampleInput: this.promptTestSampleInput || "",
        expectedOutput: "",
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
        const idx = this.promptTestCases.findIndex(t => t.id === this.testCaseForm.id);
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
        this.promptTestCases = this.promptTestCases.filter(t => t.id !== id);
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
        trigger: "prompt_change", scope: "all", catalogueFilter: "", queryFilter: "",
        dryRun: true, status: "idle", progress: 0, totalAssets: 0, processedAssets: 0,
        successCount: 0, errorCount: 0, skippedCount: 0, startedAt: "", completedAt: "", errors: [],
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
      b.startedAt = new Date().toISOString().replace("T", " ").slice(0, 16);
      b.completedAt = "";
      const total = b.scope === "all" ? 275 : b.scope === "catalogue" ? 120 : 50;
      b.totalAssets = total;
      this._batchInterval = setInterval(() => {
        if (b.status !== "running") { clearInterval(this._batchInterval); return; }
        const step = Math.ceil(total / 20);
        b.processedAssets = Math.min(total, b.processedAssets + step);
        b.progress = Math.round((b.processedAssets / total) * 100);
        // simulate some errors
        if (b.processedAssets > total * 0.6 && b.errorCount === 0) {
          b.errorCount = Math.ceil(total * 0.02);
          b.errors.push({ assetId: "asset-err-001", message: "SHACL validation failed", timestamp: new Date().toISOString().slice(0, 19) });
          b.errors.push({ assetId: "asset-err-002", message: "LLM timeout exceeded", timestamp: new Date().toISOString().slice(0, 19) });
        }
        b.successCount = b.processedAssets - b.errorCount;
        if (b.processedAssets >= total) {
          clearInterval(this._batchInterval);
          b.status = "completed";
          b.progress = 100;
          b.completedAt = new Date().toISOString().replace("T", " ").slice(0, 16);
          const triggerLabels = { prompt_change: "Prompt changed", strategy_change: "Strategy changed", llm_change: "LLM config changed", manual: "Manual trigger" };
          const scopeLabels = { all: "All assets", catalogue: `Catalogue: ${b.catalogueFilter || "—"}`, query: `Query: ${b.queryFilter || "—"}` };
          this.batchRetransformHistory.unshift({
            id: `br-${String(Date.now()).slice(-6)}`,
            trigger: triggerLabels[b.trigger] || b.trigger,
            scope: scopeLabels[b.scope] || b.scope,
            dryRun: b.dryRun,
            total: b.totalAssets, success: b.successCount, errors: b.errorCount, skipped: b.skippedCount,
            startedAt: b.startedAt, completedAt: b.completedAt, status: "completed",
          });
        }
      }, 400);
    },
    cancelBatchRetransform() {
      if (this._batchInterval) clearInterval(this._batchInterval);
      this.batchRetransform.status = "cancelled";
      this.batchRetransform.completedAt = new Date().toISOString().replace("T", " ").slice(0, 16);
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
      const now = new Date().toISOString().slice(0, 10);
      const models = typeof this.providerForm.models === "string"
        ? this.providerForm.models.split(",").map(m => m.trim()).filter(Boolean)
        : this.providerForm.models;
      if (this.isEditingProvider && this.providerForm.id) {
        const idx = this.llmProviders.findIndex(p => p.id === this.providerForm.id);
        if (idx !== -1) {
          this.llmProviders.splice(idx, 1, { ...this.providerForm, models, updatedAt: now });
        }
      } else {
        const id = `prov-${String(Date.now()).slice(-6)}`;
        this.llmProviders.push({ ...this.providerForm, id, models, createdAt: now });
      }
      // Handle default: only one can be default
      if (this.providerForm.isDefault) {
        this.llmProviders.forEach(p => { if (p.id !== (this.providerForm.id || this.llmProviders[this.llmProviders.length - 1].id)) p.isDefault = false; });
      }
      this.closeProviderModal();
      this.addToast("success", this.isEditingProvider ? "Provider updated." : "Provider created.");
    },
    deleteProvider(id) {
      const prov = this.llmProviders.find(p => p.id === id);
      this.showConfirm("Delete Provider", `Are you sure you want to delete "${prov?.name || id}"?`, "Delete", () => {
        this.llmProviders = this.llmProviders.filter(p => p.id !== id);
        this.addToast("success", "Provider deleted.");
      });
    },
    moveProviderUp(id) {
      const idx = this.llmProviders.findIndex(p => p.id === id);
      if (idx <= 0) return;
      const item = this.llmProviders.splice(idx, 1)[0];
      this.llmProviders.splice(idx - 1, 0, item);
      this.llmProviders.forEach((p, i) => { p.precedence = i + 1; });
    },
    moveProviderDown(id) {
      const idx = this.llmProviders.findIndex(p => p.id === id);
      if (idx < 0 || idx >= this.llmProviders.length - 1) return;
      const item = this.llmProviders.splice(idx, 1)[0];
      this.llmProviders.splice(idx + 1, 0, item);
      this.llmProviders.forEach((p, i) => { p.precedence = i + 1; });
    },
    providerTypeClass(type) {
      switch (type) {
        case "openai": return "green";
        case "anthropic": return "blue";
        case "ollama": return "yellow";
        case "azure": return "green";
        case "google": return "blue";
        default: return "gray";
      }
    },

    // ── Audit Trail Export & Filters (FR-SR-09) ──────────────
    exportAuditTrail(format) {
      const rows = this.auditRows;
      let content, filename, mimeType;
      if (format === "csv") {
        const headers = ["ID", "Rule", "Level", "Step", "Asset ID", "Catalogue", "Prompt Version", "Status", "Timestamp"];
        const csvRows = rows.map(r => [r.id, r.rule, r.level, r.step, r.assetId || "", r.catalogueId || "", r.promptVersion || "", r.status || "", r.timestamp].map(v => `"${String(v).replace(/"/g, '""')}"`).join(","));
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
      const now = new Date().toISOString().slice(0, 10);
      if (this.isEditingLocalSchema && this.editingLocalSchemaId != null) {
        const idx = this.schemaRegistry.findIndex(s => s.id === this.editingLocalSchemaId);
        if (idx !== -1) {
          this.schemaRegistry.splice(idx, 1, {
            ...this.schemaRegistry[idx],
            schema: this.localSchemaForm.schema,
            catalogs: this.localSchemaForm.catalogs,
            localMapping: this.localSchemaForm.localMapping || null,
            versioning: this.localSchemaForm.versioning,
            trustLevel: this.localSchemaForm.trustLevel,
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
          trustLevel: this.localSchemaForm.trustLevel,
        });
      }
      this.showCreateLocalSchemaModal = false;
      this.addToast("success", this.isEditingLocalSchema ? "Schema updated." : "Schema created.");
    },
    confirmDeleteSchema(id) {
      const schema = this.schemaRegistry.find(s => s.id === id);
      this.showConfirm("Delete Schema", `Are you sure you want to delete "${schema?.schema || 'this schema'}"? This action cannot be undone.`, "Delete", () => {
        this.schemaRegistry = this.schemaRegistry.filter(s => s.id !== id);
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
      // Mock diff content per version
      const base = this.schemaDiffRow?.schema || "Schema";
      const diffs = {
        "v1.0": `@prefix dcat: <http://www.w3.org/ns/dcat#> .\n@prefix dct:  <http://purl.org/dc/terms/> .\n\n:DatasetShape a sh:NodeShape ;\n  sh:targetClass dcat:Dataset ;\n  sh:property [\n    sh:path dct:title ;\n    sh:minCount 1 ;\n  ] ;\n  sh:property [\n    sh:path dct:identifier ;\n    sh:minCount 1 ;\n  ] .`,
        "v1.1": `@prefix dcat: <http://www.w3.org/ns/dcat#> .\n@prefix dct:  <http://purl.org/dc/terms/> .\n@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .\n\n:DatasetShape a sh:NodeShape ;\n  sh:targetClass dcat:Dataset ;\n  sh:property [\n    sh:path dct:title ;\n    sh:datatype xsd:string ;\n    sh:minCount 1 ;\n  ] ;\n  sh:property [\n    sh:path dct:identifier ;\n    sh:datatype xsd:string ;\n    sh:minCount 1 ;\n  ] ;\n  sh:property [\n    sh:path dcat:distribution ;\n    sh:node :DistributionShape ;\n  ] .`,
        "v2.0": `@prefix dcat: <http://www.w3.org/ns/dcat#> .\n@prefix dct:  <http://purl.org/dc/terms/> .\n@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .\n@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n\n:DatasetShape a sh:NodeShape ;\n  sh:targetClass dcat:Dataset ;\n  sh:property [\n    sh:path dct:title ;\n    sh:datatype xsd:string ;\n    sh:minCount 1 ;\n    sh:maxCount 1 ;\n  ] ;\n  sh:property [\n    sh:path dct:identifier ;\n    sh:datatype xsd:string ;\n    sh:minCount 1 ;\n  ] ;\n  sh:property [\n    sh:path dcat:distribution ;\n    sh:node :DistributionShape ;\n    sh:minCount 0 ;\n  ] ;\n  sh:property [\n    sh:path dct:publisher ;\n    sh:node :AgentShape ;\n    sh:minCount 1 ;\n  ] .`,
      };
      return diffs[version] || `# ${base} — ${version}\n# No content available for this version.`;
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
        const idx = this.mappingRows.findIndex(r => r.id === this.editingMappingId);
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
        transformationStrategy: this.mappingDetailRow.transformationStrategy,
      };
      this.isEditingMappingDetail = true;
    },
    cancelEditMappingDetail() {
      this.isEditingMappingDetail = false;
    },
    saveEditMappingDetail() {
      if (!this.mappingDetailRow) return;
      const idx = this.mappingRows.findIndex(r => r.id === this.mappingDetailRow.id);
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
      this.selectedMappingRows = e.target.checked ? this.mappingPagination.rows.map(r => r.id) : [];
    },
    removeMappingRow(id) {
      const row = this.mappingRows.find(r => r.id === id);
      this.showConfirm("Delete Mapping", `Are you sure you want to delete the mapping for "${row?.remoteCatalogue || 'this mapping'}"?`, "Delete", () => {
        this.mappingRows = this.mappingRows.filter(r => r.id !== id);
        this.selectedMappingRows = this.selectedMappingRows.filter(x => x !== id);
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
    closeHarvestWizard() { this.showHarvestWizard = false; this.harvestWizardStep = 1; },
    nextHarvestWizardStep() { this.harvestWizardStep = Math.min(4, this.harvestWizardStep + 1); },
    prevHarvestWizardStep() { this.harvestWizardStep = Math.max(1, this.harvestWizardStep - 1); },
    runHarvestWizardSearch() {
      const q = normalizeText(this.harvestWizardSearch);
      const filteredRaw = this.allCatalogsRaw.filter(item => normalizeText(JSON.stringify(item)).includes(q));
      this.harvestWizardRows = filteredRaw.map((item, i) => ({
        id: item?.id ?? i + 1,
        catalog: item?.catalog?.catalogId ?? "-",
        type: item?.assets?.documents?.[0]?.format ?? "-",
        name: item?.vehicles?.[0]?.brand ?? "-",
        domain: item?.catalog?.publisher?.website ?? "-",
        updated: item?.catalog?.updatedAt ?? "-",
        integrationStatus: "Active",
      }));
      this.pagination.harvestWizard.page = 1;
    },
    toggleWizardSelectAll(e) {
      this.harvestWizardSelectedRows = e.target.checked ? this.harvestWizardRows.map(r => r.id) : [];
    },
    toggleScopeOption(key) {
      const s = this.harvestScope.selected;
      if (key === "all_assets") {
        this.harvestScope.selected = s.includes("all_assets") ? [] : ["all_assets"];
        return;
      }
      if (s.includes("all_assets")) return;
      this.harvestScope.selected = s.includes(key) ? s.filter(x => x !== key) : [...s, key];
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
          { id: "asset-004", title: "Air Quality Measurements", status: "Error", duration: "4.5s", error: "Schema mapping failed — missing required field dct:identifier" },
          { id: "asset-005", title: "Traffic Flow Data Product", status: "Success", duration: "0.6s", error: null },
          { id: "asset-006", title: "Energy Consumption Report", status: "Success", duration: "1.0s", error: null },
        ],
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
      h.startedAt = new Date().toISOString().replace("T", " ").slice(0, 16);
      const total = 120;
      h.totalAssets = total;
      if (this._harvestInterval) clearInterval(this._harvestInterval);
      this._harvestInterval = setInterval(() => {
        if (h.status !== "running") { clearInterval(this._harvestInterval); return; }
        const step = Math.ceil(total / 15);
        h.processedAssets = Math.min(total, h.processedAssets + step);
        h.progress = Math.round((h.processedAssets / total) * 100);
        if (h.processedAssets > total * 0.7 && h.errorCount === 0) {
          h.errorCount = 3;
          h.errors = [
            { assetId: "asset-err-01", message: "SHACL validation failed", timestamp: new Date().toISOString().slice(0, 19) },
            { assetId: "asset-err-02", message: "Missing required field dct:title", timestamp: new Date().toISOString().slice(0, 19) },
            { assetId: "asset-err-03", message: "LLM timeout exceeded (30s)", timestamp: new Date().toISOString().slice(0, 19) },
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
            result: h.errorCount > 0 ? "Warning" : "Success",
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
          if (h.status !== "running") { clearInterval(this._harvestInterval); return; }
          const step = Math.ceil(total / 15);
          h.processedAssets = Math.min(total, h.processedAssets + step);
          h.progress = Math.round((h.processedAssets / total) * 100);
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
    addToast(type, message, duration = 4000) {
      const id = ++this._toastCounter;
      this.toasts.push({ id, type, message });
      setTimeout(() => this.dismissToast(id), duration);
    },
    dismissToast(id) {
      this.toasts = this.toasts.filter(t => t.id !== id);
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
      const cat = this.catalogsTable.find(c => String(c.id) === String(id) || String(c.uniqueId) === String(id));
      const name = cat?.catalogName || cat?.catalogId || "this catalogue";
      this.showConfirm(
        "Delete Remote Catalogue",
        `Are you sure you want to delete "${name}"? This action cannot be undone.`,
        "Delete",
        () => this.deleteRemoteCatalog(id)
      );
    },
    deleteRemoteCatalog(id) {
      this.catalogsTable = this.catalogsTable.filter(c => String(c.id) !== String(id) && String(c.uniqueId) !== String(id));
      this.addToast("success", "Remote catalogue deleted successfully.");
    },

    // ── Monitoring Log Export (Milestone 4) ─────────────────────
    exportMonitoringLog(format) {
      const rows = this.filteredMonitoringEvents;
      let content, filename, mimeType;
      if (format === "csv") {
        const headers = ["ID", "Level", "Source", "Message", "Timestamp"];
        const csvRows = rows.map(r => [r.id, r.type, r.source, r.message, r.timestamp].map(v => `"${String(v).replace(/"/g, '""')}"`).join(","));
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
      a.href = url; a.download = filename;
      document.body.appendChild(a); a.click();
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
      // Simulate password change
      setTimeout(() => {
        this.passwordFormSuccess = "Password updated successfully.";
        this.passwordForm = { currentPassword: "", newPassword: "", confirmPassword: "" };
        this.addToast("success", "Password changed successfully.");
      }, 600);
    },

    // ── Access Info ─────────────────────────────────────────────
    openAccessInformation() { this.showAccessInformation = true; },
    closeAccessInformation() { this.showAccessInformation = false; },

    // ── Logout ──────────────────────────────────────────────────
    logout() {
      uibuilderService.send({
        type: "logOut",
        auth: { userToken: getCookie("userToken"), clientId: getCookie("uibuilder-client-id") }
      });
    },
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
          const idx = this.catalogsTable.findIndex(x => String(x.id) === String(remoteCatalogId));
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
        this.catalogsTable = catalogs.map(item => ({
          uniqueId: item.uniqueId, id: item.uniqueId, ...(item.catalog || {})
        }));
        this.pagination.catalogsRegister.page = 1;
      }

      if (resp?.action === "updateRemoteCatalog") {
        this.isUpdatingRemoteCatalog = false;
        if (resp?.status === "success") {
          const id = msg?.data?.uniqueId;
          const patch = msg?.data?.patch || {};
          const idx = this.catalogsTable.findIndex(c => String(c.uniqueId) === String(id));
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
          expiresIn: sent?.expiresIn ?? "30 Days",
        };
        let idx = uid ? this.users.findIndex(u => String(u.uniqueId) === String(uid)) : -1;
        if (idx === -1 && newUser.email) idx = this.users.findIndex(u => String(u.email) === String(newUser.email));
        if (idx !== -1) this.users.splice(idx, 1, newUser);
        else this.users.unshift(newUser);
        this.pagination.users.page = 1;
      }

      if (msg?.type === "getAdminTools" && msg?.response?.status === "success") {
        const list = msg.response.users || [];
        this.users = list.map((u, i) => {
          const uid = u.uniqueId ?? u.id ?? u._id ?? String(i);
          return {
            ...u, uniqueId: uid,
            name: (`${u.profile?.firstName ?? ""} ${u.profile?.lastName ?? ""}`).trim() || u.name || u.email || "\u2014",
            avatar: u.avatar || "./img/avatar-16.jpg",
            email: u.email || "\u2014",
            status: u.status || (u.invited ? "Invited" : "Active"),
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
  },
});

// ─── Component definitions are available for future use ──────────
// When migrating HTML to use component tags (e.g. <app-sidebar>),
// uncomment the relevant app.component() call below.
//
// app.component("app-sidebar", AppSidebar);
// app.component("app-topbar", AppTopbar);
// app.component("stat-card", StatCard);
// app.component("table-statusbar", TableStatusbar);
// app.component("dashboard-layout", DashboardLayout);
// app.component("local-catalogue-view", LocalCatalogueView);
// app.component("catalogue-registry-view", CatalogueRegistryView);
// app.component("schema-registry-view", SchemaRegistryView);
// app.component("admin-tools-view", AdminToolsView);
// app.component("harvester-view", HarvesterView);
app.component("view-modal", ViewModal);
app.component("invite-modal", InviteModal);
app.component("manage-user-modal", ManageUserModal);
app.component("register-catalog-modal", RegisterCatalogModal);
app.component("schema-modal", SchemaModal);
app.component("harvest-wizard-modal", HarvestWizardModal);
app.component("access-info-modal", AccessInfoModal);
app.component("manage-menu", ManageMenu);

// ─── Mount ───────────────────────────────────────────────────────
app.mount("#app");
