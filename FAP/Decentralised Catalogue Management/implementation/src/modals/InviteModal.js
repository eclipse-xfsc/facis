export default {
  name: "InviteModal",
  template: "#tpl-invite-modal",
  props: {
    visible: { type: Boolean, default: false },
    inviteForm: { type: Object, required: true },
  },
  emits: ["close", "send-invite", "update:inviteForm"],
  computed: {
    canSendInvite() {
      const f = this.inviteForm;
      return f.firstName.trim() && f.lastName.trim() && f.email.trim() && f.role && f.expiresIn;
    }
  }
};
