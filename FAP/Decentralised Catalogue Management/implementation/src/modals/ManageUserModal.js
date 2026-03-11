export default {
  name: "ManageUserModal",
  template: "#tpl-manage-user-modal",
  props: {
    visible: { type: Boolean, default: false },
    manageForm: { type: Object, required: true },
  },
  emits: ["close", "send-manage"],
  computed: {
    canSendManageUser() {
      const m = this.manageForm;
      return m.firstName.trim() && m.lastName.trim() && m.email.trim() && m.selectedRoles.length > 0 && m.expiresIn;
    }
  }
};
