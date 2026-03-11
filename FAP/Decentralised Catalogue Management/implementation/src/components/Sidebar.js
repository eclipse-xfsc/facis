export default {
  name: "AppSidebar",
  template: "#tpl-sidebar",
  props: {
    currentPage: { type: String, required: true },
    userAccess: { type: Array, default: () => [] }
  },
  emits: ["navigate", "logout"],
  methods: {
    hasAccess(key) {
      return this.userAccess.includes(key);
    }
  }
};
