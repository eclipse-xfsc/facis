export default {
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
    showIncludeNewAssetsToggle: { type: Boolean, default: false },
  },
  emits: [
    "close", "next-step", "prev-step", "start-harvest",
    "update:harvestWizardSearch", "update:harvestWizardSelectedRows",
    "update:harvestWizardStep",
    "run-wizard-search", "toggle-wizard-select-all",
    "toggle-scope-option", "toggle-lifecycle-card",
    "page-change"
  ],
  methods: {
    setPage(key, page) {
      this.$emit("page-change", { key, page });
    }
  }
};
