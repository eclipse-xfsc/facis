import { namespaceClass } from "../utils/formatters.js";

export default {
  name: "SchemaModal",
  template: "#tpl-schema-modal",
  props: {
    visible: { type: Boolean, default: false },
    modalTitle: { type: String, default: "Register Remote Schema" },
    registerSchemaForm: { type: Object, required: true },
    schemaSummaries: { type: Object, default: () => ({}) },
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
      return this.registerSchemaForm.remoteCatalogs.filter(c => c.toLowerCase().includes(q));
    }
  },
  methods: {
    namespaceClass
  }
};
