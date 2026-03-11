export default {
  name: "ManageMenu",
  template: "#tpl-manage-menu",
  props: {
    manageMenu: { type: Object, required: true }
  },
  emits: ["close", "delete-user", "edit-user"]
};
