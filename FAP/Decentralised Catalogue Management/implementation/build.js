/**
 * build.js — Minimal build pipeline
 *
 * Bundles all source code from /src into exactly 3 files in /public:
 *   public/index.js   — all JS bundled (IIFE, Vue is a CDN global)
 *   public/index.css   — all CSS
 *   public/index.html  — copied from src/index.html
 *
 * Usage:
 *   node build.js          — one-shot build
 *   node build.js --watch  — rebuild on file changes
 */

import { build, context } from "esbuild";
import { copyFileSync, watchFile } from "fs";

const isWatch = process.argv.includes("--watch");

const copyHtml = () => {
  copyFileSync("src/index.html", "public/index.html");
  console.log("  public/index.html ← src/index.html");
};

const copyCss = () => {
  copyFileSync("src/styles.css", "public/index.css");
  console.log("  public/index.css  ← src/styles.css");
};

const buildOptions = {
  entryPoints: ["src/main.js"],
  bundle: true,
  format: "iife",
  outfile: "public/index.js",
  logLevel: "info",
  // Vue is loaded via CDN as a global — not bundled
  // The code references `Vue` as a global variable, esbuild leaves it as-is
};

if (isWatch) {
  const ctx = await context(buildOptions);
  await ctx.watch();
  console.log("[build] watching src/ for changes…");

  // Also watch index.html for changes
  watchFile("src/index.html", { interval: 500 }, () => {
    copyHtml();
  });
  watchFile("src/styles.css", { interval: 500 }, () => {
    copyCss();
  });

  copyHtml();
  copyCss();
} else {
  await build(buildOptions);
  copyHtml();
  copyCss();
  console.log("[build] done.");
}
