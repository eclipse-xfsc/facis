import { trustClass } from "../utils/formatters.js";

export default {
  name: "CatalogueRegistryView",
  template: "#tpl-catalogue-registry-view",
  props: {
    catalogsRegisterPagination: { type: Object, required: true },
    pagination: { type: Object, required: true },
    pageWindowFn: { type: Function, required: true },
  },
  emits: [
    "open-register-modal", "edit-catalog", "toggle-catalog-enabled", "page-change"
  ],
  methods: {
    trustClass,
    setPage(key, page) {
      this.$emit("page-change", { key, page });
    }
  }
};
