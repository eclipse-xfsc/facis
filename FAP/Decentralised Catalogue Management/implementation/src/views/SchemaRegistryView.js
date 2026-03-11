import { trustClass, strategyPillClass } from "../utils/formatters.js";

export default {
  name: "SchemaRegistryView",
  template: "#tpl-schema-registry-view",
  props: {
    currentSchemaTab: { type: String, default: "localSchema" },
    schemaPagination: { type: Object, required: true },
    remoteSchemaPagination: { type: Object, required: true },
    mappingPagination: { type: Object, required: true },
    pagination: { type: Object, required: true },
    selectedRows: { type: Array, default: () => [] },
    selectedMappingRows: { type: Array, default: () => [] },
    filters: { type: Object, required: true },
    pageWindowFn: { type: Function, required: true },
  },
  emits: [
    "update:currentSchemaTab", "update:selectedRows", "update:selectedMappingRows",
    "update:filters", "open-schema-new-modal", "open-schema-edit-modal",
    "toggle-all-mapping", "remove-mapping-row", "page-change"
  ],
  methods: {
    trustClass,
    strategyPillClass,
    setPage(key, page) {
      this.$emit("page-change", { key, page });
    }
  }
};
