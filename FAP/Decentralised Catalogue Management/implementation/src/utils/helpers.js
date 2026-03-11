/**
 * Data-processing helpers.
 * Pure functions — no Vue dependency.
 */

export function getCookie(name) {
  const value = "; " + document.cookie;
  const parts = value.split("; " + name + "=");
  if (parts.length === 2) return parts.pop().split(";").shift();
  return "";
}

export function normalizeText(v) {
  return String(v ?? "").toLowerCase().trim();
}

export function normalizeFilter(val) {
  if (!val) return "";
  if (val === "All") return "";
  return val;
}

export function paginate(list, page, perPage) {
  const total = list.length;
  const startIndex = (page - 1) * perPage;
  const endIndex = startIndex + perPage;
  return {
    total,
    totalPages: Math.ceil(total / perPage),
    rows: list.slice(startIndex, endIndex),
    showingStart: total === 0 ? 0 : startIndex + 1,
    showingEnd: Math.min(endIndex, total)
  };
}

export function pageWindow(paginationObj, computedPaginationFn, key, size) {
  size = size || 5;
  const p = paginationObj[key].page;
  const total = computedPaginationFn(key) || 1;
  const start = Math.min(p, Math.max(1, total - size + 1));
  const end = Math.min(total, start + size - 1);
  const pages = [];
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
}

export function deepIncludes(value, needle) {
  if (!needle) return true;
  if (value == null) return false;
  const t = typeof value;
  if (t === "string" || t === "number" || t === "boolean") {
    return normalizeText(value).includes(needle);
  }
  if (Array.isArray(value)) {
    return value.some(v => deepIncludes(v, needle));
  }
  if (t === "object") {
    return Object.values(value).some(v => deepIncludes(v, needle));
  }
  return false;
}

export function matchValue(value, needle) {
  if (!needle) return null;
  if (value == null) return null;
  const t = typeof value;
  if (t === "string" || t === "number" || t === "boolean") {
    const s = String(value);
    return normalizeText(s).includes(needle) ? s : null;
  }
  if (Array.isArray(value)) {
    for (const v of value) {
      const r = matchValue(v, needle);
      if (r != null) return r;
    }
    return null;
  }
  if (t === "object") {
    for (const v of Object.values(value)) {
      const r = matchValue(v, needle);
      if (r != null) return r;
    }
    return null;
  }
  return null;
}

export function getCatalogAssets(catalogItem) {
  const a = catalogItem?.assets;
  const out = [];
  if (Array.isArray(a?.documents)) out.push(...a.documents);
  if (Array.isArray(a?.parts)) out.push(...a.parts);
  else if (a?.parts && typeof a.parts === "object") out.push(a.parts);
  if (Array.isArray(a?.items)) out.push(...a.items);
  if (Array.isArray(a)) out.push(...a);
  return out;
}

export function getAssetTitle(asset) {
  return (
    asset?.title || asset?.name || asset?.label || asset?.identifier ||
    asset?.assetId || asset?.id || asset?.uri || asset?.url ||
    asset?.meta?.title || asset?.metadata?.title || "-"
  );
}

export function assetMatchesQuery(asset, needle) {
  return matchValue(asset, needle) != null;
}

export function getChangedFields(oldObj, newObj) {
  const patch = {};
  const keys = new Set([
    ...Object.keys(oldObj || {}),
    ...Object.keys(newObj || {}),
  ]);
  keys.forEach((k) => {
    if (oldObj?.[k] !== newObj?.[k]) patch[k] = newObj?.[k];
  });
  return patch;
}

export function parseJsonLine(text) {
  const match = text.match(/^(\s*)"([^"]+)"\s*:\s*"([^"]*)"(.*)$/);
  if (!match) return null;
  return {
    indent: match[1],
    key: match[2],
    value: match[3],
    suffix: match[4]
  };
}
