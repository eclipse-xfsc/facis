import { statusClass, resultClass } from "../utils/formatters.js";
import { normalizeText, normalizeFilter, getCatalogAssets, getAssetTitle, assetMatchesQuery } from "../utils/helpers.js";

export default {
  name: "LocalCatalogueView",
  template: "#tpl-local-catalogue-view",
  props: {
    tableRows: { type: Array, default: () => [] },
    catalogPagination: { type: Object, required: true },
    harvestPagination: { type: Object, required: true },
    pagination: { type: Object, required: true },
    currentTab: { type: String, default: "localCatalogue" },
    searchText: { type: String, default: "" },
    filters: { type: Object, required: true },
    catalogOptions: { type: Array, default: () => [] },
    typeOptions: { type: Array, default: () => [] },
    domainOptions: { type: Array, default: () => [] },
    statusOptions: { type: Array, default: () => [] },
    selectedRows: { type: Array, default: () => [] },
    harvestRecords: { type: Array, default: () => [] },
    pageWindowFn: { type: Function, required: true },
  },
  emits: [
    "update:currentTab", "update:searchText", "update:filters", "update:selectedRows",
    "run-search", "clear-filters", "open-view-modal", "page-change"
  ],
  methods: {
    statusClass,
    resultClass,
    setPage(key, page) {
      this.$emit("page-change", { key, page });
    }
  }
};
