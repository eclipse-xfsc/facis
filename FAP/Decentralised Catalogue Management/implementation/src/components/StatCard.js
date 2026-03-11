export default {
  name: "StatCard",
  template: "#tpl-stat-card",
  props: {
    primary: { type: Boolean, default: false },
    number: { type: [String, Number], default: 0 },
    label: { type: String, default: "" },
    subtitle: { type: String, default: "" },
    iconType: { type: String, default: "" }
  }
};
