import { getAccessInitial } from "../utils/formatters.js";

export default {
  name: "AdminToolsView",
  template: "#tpl-admin-tools-view",
  props: {
    currentAdminTab: { type: String, default: "accessControl" },
    usersPagination: { type: Object, required: true },
    pagination: { type: Object, required: true },
    pageWindowFn: { type: Function, required: true },
  },
  emits: [
    "update:currentAdminTab", "open-invite-modal", "open-manage-menu",
    "open-access-info", "page-change"
  ],
  methods: {
    getAccessInitial,
    setPage(key, page) {
      this.$emit("page-change", { key, page });
    }
  }
};
