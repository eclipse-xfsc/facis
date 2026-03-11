export default {
  name: "HarvesterView",
  template: "#tpl-harvester-view",
  props: {
    pagination: { type: Object, required: true },
    catalogsRegisterPagination: { type: Object, required: true },
    pageWindowFn: { type: Function, required: true },
  },
  emits: ["open-harvest-wizard", "page-change"],
  methods: {
    setPage(key, page) {
      this.$emit("page-change", { key, page });
    }
  }
};
