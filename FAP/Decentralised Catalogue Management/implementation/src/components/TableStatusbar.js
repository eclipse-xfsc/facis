export default {
  name: "TableStatusbar",
  template: "#tpl-table-statusbar",
  props: {
    paginationKey: { type: String, required: true },
    pagination: { type: Object, required: true },
    computed: { type: Object, required: true },
    legend: { type: Array, default: () => [] }
  },
  emits: ["page-change"],
  computed: {
    pages() {
      const p = this.pagination;
      const total = this.computed.totalPages || 1;
      const size = 5;
      const start = Math.min(p.page, Math.max(1, total - size + 1));
      const end = Math.min(total, start + size - 1);
      const arr = [];
      for (let i = start; i <= end; i++) arr.push(i);
      return arr;
    }
  }
};
