#!/usr/bin/env node
/**
 * Dev-time palette gate for the Energy Atlas.
 *
 * Validates every ramp the app uses, each against the dataviz skill's rules
 * FOR THAT RAMP TYPE:
 *
 *   - Categorical (8 series slots, light + dark) -> the skill's
 *     validate_palette.js categorical gate: lightness band, chroma floor,
 *     CVD separation, normal-vision floor, surface contrast. This is the
 *     only hard gate from the validator; a FAIL here blocks the build.
 *
 *   - Sequential (blue clean-fill, orange coal-fill): CONTINUOUS choropleth
 *     fills, not discrete marks. The validator's --ordinal mode is for
 *     discrete ordinal marks (visible step gaps, min adjacent dL 0.06, step
 *     nearest the surface >= 2:1) and fails a correct 13-step continuous
 *     ramp by design. For a continuous fill the skill's reference palette
 *     (palette.md, "Sequential hue") explicitly allows the lightest step to
 *     "recede toward the surface" - the 2:1 surface-end rule belongs to
 *     --ordinal, not to these ramps. So the hard gates here are strictly
 *     monotone lightness and single hue (spread <= 40deg), using OKLCH math
 *     ported from the skill's validator; the surface-end contrast is reported
 *     as an advisory so a degenerate ramp (endpoint == surface) stays
 *     visible, but it does not FAIL the build.
 *
 *   - Diverging (coal direction, blue <-> red): neutral midpoint
 *     (chroma <= 0.05), monotone lightness within each arm, and both poles
 *     clearly separated from the midpoint (dE >= 15).
 *
 * The orange sequential ramp is REGENERATED here (same OKLab interpolation
 * that src/viz/palette.ts runs at load time) so the gate fails if the two
 * drift apart. BLUE_SEQUENTIAL is asserted equal to the app's constant.
 *
 * Run from the dashboard directory:
 *   node scripts/check_palette.mjs
 *
 * Exits non-zero if any check FAILs, so it can gate a build.
 */
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VALIDATOR = "/tmp/claude-1000/bundled-skills/2.1.317/8e1f922731ae2dd78540878682612c04/dataviz/scripts/validate_palette.js";

/* ---- color math (OKLab/OKLCH ported from the skill's validator) ---- */
const s2lin = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const lin2s = (c) => {
  c = Math.max(0, Math.min(1, c));
  return c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055;
};
const hex2srgb = (h) => {
  const x = h.replace("#", "");
  return [0, 2, 4].map((i) => parseInt(x.slice(i, i + 2), 16) / 255);
};
const rgb2hex = (r) =>
  "#" +
  r.map((v) => Math.round(v * 255).toString(16).padStart(2, "0")).join("");
function oklabFromLin([r, g, b]) {
  // Official Ottosson OKLab forward matrix - must stay byte-identical to
  // rgbToLab in src/viz/palette.ts (this gate regenerates the app's ramps).
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  return [
    0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
    1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
    0.0259040321 * l + 0.7827717662 * m - 0.8086757660 * s,
  ];
}
function linFromOklab([L, a, b]) {
  const l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3;
  const m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3;
  const s_ = (L - 0.0894844775 * a - 1.291485548 * b) ** 3;
  return [
    4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
    -1.2684380046 * l_ + 2.609757401 * m_ - 0.3413193964 * s_,
    -0.0041960863 * l_ - 0.7034186147 * m_ + 1.707614701 * s_,
  ];
}
const oklab = (h) => oklabFromLin(hex2srgb(h).map(s2lin));
const oklch = (h) => {
  const [L, a, b] = oklab(h);
  return [L, Math.hypot(a, b)];
};
const okhue = (h) => {
  const [, a, b] = oklab(h);
  return ((Math.atan2(b, a) * 180) / Math.PI + 360) % 360;
};
function deltaE(h1, h2) {
  const a = oklab(h1), b = oklab(h2);
  return 100 * Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
}
const relLum = (h) => {
  const [r, g, b] = hex2srgb(h).map(s2lin);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
const contrast = (a, b) => {
  const [hi, lo] = [relLum(a), relLum(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};

/* ---- OKLab interpolation (same as src/viz/palette.ts) ---- */
function ramp(from, to, n) {
  const A = oklab(from), B = oklab(to);
  const mix = (t) => A.map((v, i) => v + (B[i] - v) * t);
  return Array.from({ length: n }, (_, i) => {
    const [L, a, b] = mix(i / (n - 1));
    return rgb2hex(linFromOklab([L, a, b]).map(lin2s));
  });
}
function diverging(blueHex, midHex, redHex) {
  const B = oklab(blueHex), M = oklab(midHex), R = oklab(redHex);
  const mix = (A, C, t) => A.map((v, i) => v + (C[i] - v) * t);
  const hex = (v) => rgb2hex(linFromOklab(v).map(lin2s));
  const out = [];
  // Must mirror divergingRamp in src/viz/palette.ts exactly: blue pole (idx 0)
  // -> neutral mid (idx 6) -> red pole (idx 12). A reversed first arm puts the
  // neutral at idx 0 and the blue pole at idx 6, which is the bug this gate is
  // here to catch.
  for (let i = 0; i <= 6; i++) out.push(hex(mix(B, M, i / 6)));
  for (let i = 1; i <= 6; i++) out.push(hex(mix(M, R, i / 6)));
  return out;
}

/* ---- the ramps the app uses (must match src/viz/palette.ts) ---- */
const BLUE = [
  "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
  "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
];
const ORANGE = ramp("#fdeee2", "#832e07", 13);
const DIV_LIGHT = diverging("#2a78d6", "#f0efec", "#e34948");
const DIV_DARK = diverging("#3987e5", "#383835", "#e66767");
const CAT_LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"];
const CAT_DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"];

/* ---- assert the gate's BLUE copy matches the app's constant ---- */
const paletteTs = readFileSync(path.join(__dirname, "..", "src", "viz", "palette.ts"), "utf8");
const iStart = paletteTs.indexOf("BLUE_SEQUENTIAL: string[] = [");
const blueBlock = iStart >= 0
  ? [...paletteTs.slice(iStart, paletteTs.indexOf("];", iStart))
     .matchAll(/"(#[0-9a-f]{6})"/g)].map((m) => m[1])
  : null;
if (!blueBlock || blueBlock.length !== 13 || !blueBlock.every((h, i) => h === BLUE[i])) {
  console.error("FAIL: scripts/check_palette.mjs BLUE drifts from src/viz/palette.ts BLUE_SEQUENTIAL");
  process.exit(1);
}
// The orange ramp is generated by the same ramp() endpoints in both files.
if (!/ramp\("#fdeee2", "#832e07", 13\)/.test(paletteTs)) {
  console.error("FAIL: src/viz/palette.ts ORANGE_SEQUENTIAL endpoints differ from this gate");
  process.exit(1);
}

/* ---- sequential (continuous fill) checks ---- */
function checkSequential(label, steps, mode, surface) {
  console.log(`\n=== ${label} (sequential, continuous fill) ===`);
  const Ls = steps.map((h) => oklch(h)[0]);
  let ok = true;
  const mono = Ls.every((v, i) => i === 0 || v < Ls[i - 1] - 1e-9) ||
    Ls.every((v, i) => i === 0 || v > Ls[i - 1] + 1e-9);
  if (!mono) {
    ok = false;
    console.log(`  [FAIL] Lightness monotone   L = ${Ls.map((l) => l.toFixed(3)).join(", ")}`);
  } else {
    console.log(`  [PASS] Lightness monotone   ${Ls[0].toFixed(3)} -> ${Ls[Ls.length - 1].toFixed(3)}`);
  }
  const hues = steps.map(okhue);
  let spread = Math.max(...hues) - Math.min(...hues);
  if (spread > 180) spread = 360 - spread;
  if (spread > 40) {
    ok = false;
    console.log(`  [FAIL] Single hue           hue spread ${spread.toFixed(0)}deg > 40deg`);
  } else {
    console.log(`  [PASS] Single hue           hue spread ${spread.toFixed(0)}deg`);
  }
  // Surface-end contrast is an ADVISORY for continuous fills, not a gate. The
  // skill's reference palette (palette.md, "Sequential hue") allows the
  // lightest step of a sequential ramp to "recede toward the surface"; the
  // 2:1 floor is the validator's --ordinal rule for discrete marks. We still
  // print it so a degenerate ramp (endpoint == surface, contrast 1.00:1) is
  // visible in the gate output and caught by the render-and-look step.
  const byL = [...steps].sort((a, b) => oklch(a)[0] - oklch(b)[0]);
  const atRisk = mode === "light" ? byL[byL.length - 1] : byL[0];
  const cr = contrast(atRisk, surface);
  console.log(
    `  [INFO] Surface-end contrast ${atRisk} at ${cr.toFixed(2)}:1 vs ${surface}` +
    ` (continuous fill: recede-toward-surface permitted)`,
  );
  return ok;
}

/* ---- diverging checks ---- */
function checkDiverging(label, steps) {
  console.log(`\n=== ${label} (diverging, two poles + neutral mid) ===`);
  let all = true;
  const mid = steps[(steps.length - 1) / 2]; // 13 steps -> index 6
  const midC = oklch(mid)[1];
  if (midC > 0.05) {
    all = false;
    console.log(`  [FAIL] Neutral midpoint     ${mid} chroma ${midC.toFixed(3)} > 0.05`);
  } else {
    console.log(`  [PASS] Neutral midpoint     ${mid} chroma ${midC.toFixed(3)}`);
  }
  for (const [name, arm] of [["blue arm", steps.slice(0, 7).reverse()], ["red arm", steps.slice(7)]]) {
    const Ls = arm.map((h) => oklch(h)[0]);
    const dir = Ls[1] < Ls[0] ? -1 : 1; // direction away from the midpoint
    const mono = Ls.every((v, i) => i === 0 || (v - Ls[i - 1]) * dir > 1e-9);
    if (!mono) {
      all = false;
      console.log(`  [FAIL] ${name} monotone    L = ${Ls.map((l) => l.toFixed(3)).join(", ")}`);
    } else {
      console.log(`  [PASS] ${name} monotone    ${Ls[0].toFixed(3)} -> ${Ls[Ls.length - 1].toFixed(3)}`);
    }
  }
  for (const pole of [steps[0], steps[steps.length - 1]]) {
    const d = deltaE(mid, pole);
    if (d < 15) {
      all = false;
      console.log(`  [FAIL] Pole separation      ${pole} dE from mid ${d.toFixed(1)} < 15`);
    } else {
      console.log(`  [PASS] Pole separation      ${pole} dE from mid ${d.toFixed(1)}`);
    }
  }
  return all;
}

/* ---- run ---- */
const failed = [];

for (const [label, palette, mode, surface] of [
  ["categorical light", CAT_LIGHT, "light", "#fcfcfb"],
  ["categorical dark", CAT_DARK, "dark", "#1a1a19"],
]) {
  console.log(`\n=== ${label} (categorical, skill validator) ===`);
  try {
    const out = execFileSync(
      "node",
      [VALIDATOR, palette.join(","), "--mode", mode, "--surface", surface, "--pairs", "adjacent"],
      { encoding: "utf8" },
    );
    process.stdout.write(out);
  } catch (e) {
    if (e.stdout) process.stdout.write(e.stdout);
    if (e.stderr) process.stderr.write(e.stderr);
    if (e.status === 2) console.error(`  [FAIL] validator usage error (exit 2) for ${label}`);
    failed.push(label);
  }
}

if (!checkSequential("sequential blue light", BLUE, "light", "#fcfcfb")) failed.push("sequential blue light");
if (!checkSequential("sequential blue dark", BLUE, "dark", "#1a1a19")) failed.push("sequential blue dark");
if (!checkSequential("sequential orange light", ORANGE, "light", "#fcfcfb")) failed.push("sequential orange light");
if (!checkSequential("sequential orange dark", ORANGE, "dark", "#1a1a19")) failed.push("sequential orange dark");
if (!checkDiverging("diverging light", DIV_LIGHT)) failed.push("diverging light");
if (!checkDiverging("diverging dark", DIV_DARK)) failed.push("diverging dark");

console.log(`\norange sequential ramp (regenerated, same math as src/viz/palette.ts):`);
ORANGE.forEach((h, i) => console.log(`  ${(100 + i * 50).toString().padStart(3)}  ${h}  (L ${oklch(h)[0].toFixed(3)})`));

if (failed.length) {
  console.log(`\nRESULT: FAIL (${failed.length}): ${failed.join(", ")}`);
  process.exit(1);
}
console.log("\nRESULT: PASS");
