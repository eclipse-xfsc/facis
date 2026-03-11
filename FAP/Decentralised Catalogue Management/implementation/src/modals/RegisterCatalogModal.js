export default {
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
    testConnectionResult: { type: Object, default: () => ({ status: "", message: "", latency: 0 }) },
  },
  emits: ["close", "save", "test-connection"]
};
