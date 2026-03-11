export default {
  name: "AccessInfoModal",
  template: "#tpl-access-info-modal",
  props: {
    visible: { type: Boolean, default: false }
  },
  emits: ["close"]
};
