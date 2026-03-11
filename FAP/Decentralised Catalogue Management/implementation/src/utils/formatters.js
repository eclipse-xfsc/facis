/**
 * Formatting and CSS-class utility functions.
 * Pure functions — no Vue dependency.
 */

export function statusClass(status) {
  if (status === "Active") return "green";
  if (status === "Warning") return "yellow";
  if (status === "Error") return "red";
  return "gray";
}

export function trustClass(level) {
  if (level === "Hybrid AI Mapping") return "green";
  if (level === "Deterministic RDF") return "yellow";
  if (level === "AI-driven") return "blue";
  return "gray";
}

export function roleClass(role) {
  if (role === "Harvester") return "blue";
  if (role === "Schema Admin") return "green";
  if (role === "Administrator") return "red";
  return "gray";
}

export function resultClass(result) {
  if (result === "Success") return "green";
  if (result === "Warning") return "yellow";
  if (result === "Error") return "red";
  return "gray";
}

export function logPillClass(level) {
  if (level === "Info") return "blue";
  if (level === "Warning") return "yellow";
  if (level === "Error") return "red";
  return "gray";
}

export function namespaceClass(ns) {
  const v = String(ns || "").trim().toLowerCase();
  if (v === "ex:" || v === "ex") return "green";
  if (v === "dcat:" || v === "dcat") return "blue";
  if (v === "dct:" || v === "dct") return "yellow";
  return "gray";
}

export function strategyPillClass(strategy) {
  const v = String(strategy || "").toLowerCase();
  if (v.includes("deterministic")) return "yellow";
  if (v.includes("hybrid")) return "green";
  if (v.includes("ai")) return "blue";
  return "gray";
}

export function strategyLabel(code) {
  const m = {
    none: "None",
    ai: "AI-driven",
    hybrid: "Hybrid AI Mapping",
    deterministic: "Deterministic RDF"
  };
  return m[code] || code || "None";
}

export function getAccessInitial(key) {
  const map = {
    local_catalogue: "L",
    catalogue_registry: "C",
    schema_registry: "S",
    admin_tools: "A",
    harvester: "H",
  };
  return map[key] || "?";
}
