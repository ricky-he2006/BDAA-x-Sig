/**
 * Energy Atlas color system.
 *
 * Categorical slots and the blue sequential ramp are the dataviz skill's
 * validated default palette (steps 100–700, light + dark). The orange
 * sequential ramp is derived at load time by OKLab interpolation between a
 * near-surface warm tint and a deep orange-brown, anchored on the categorical
 * orange hue; the dev script `scripts/check_palette.mjs` regenerates and
 * validator-checks every step. Diverging coal-direction: blue <-> red with a
 * neutral gray midpoint (skill-specified), equal steps per arm.
 */

export type Mode = "light" | "dark";

export const SURFACE: Record<Mode, string> = {
  light: "#fcfcfb",
  dark: "#1a1a19",
};

export const PAGE: Record<Mode, string> = {
  light: "#f9f9f7",
  dark: "#0d0d0d",
};

export const INK: Record<Mode, { primary: string; secondary: string; muted: string; grid: string; panel: string; panelBorder: string }> = {
  light: {
    primary: "#0b0b0b",
    secondary: "#52514e",
    muted: "#85847f",
    grid: "#e8e7e2",
    panel: "#ffffff",
    panelBorder: "#e3e2dc",
  },
  dark: {
    primary: "#f0efec",
    secondary: "#c3c2b7",
    muted: "#8f8f88",
    grid: "#2c2c2a",
    panel: "#1f1f1e",
    panelBorder: "#343432",
  },
};

export const CATEGORICAL: Record<Mode, string[]> = {
  light: ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"],
  dark: ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"],
};

/** Blue sequential ramp, dataviz-validated steps 100 (light) -> 700 (dark). */
export const BLUE_SEQUENTIAL: string[] = [
  "#cde2fb", // 100
  "#b7d3f6", // 150
  "#9ec5f4", // 200
  "#86b6ef", // 250
  "#6da7ec", // 300
  "#5598e7", // 350
  "#3987e5", // 400
  "#2a78d6", // 450
  "#256abf", // 500
  "#1c5cab", // 550
  "#184f95", // 600
  "#104281", // 650
  "#0d366b", // 700
];

/* ---------------- OKLab interpolation ---------------- */

type Rgb = [number, number, number];

function hexToRgb(hex: string): Rgb {
  const h = hex.replace("#", "");
  return [
    parseInt(h.slice(0, 2), 16) / 255,
    parseInt(h.slice(2, 4), 16) / 255,
    parseInt(h.slice(4, 6), 16) / 255,
  ];
}

function rgbToHex(r: Rgb): string {
  const c = (x: number) =>
    Math.max(0, Math.min(255, Math.round(x * 255)))
      .toString(16)
      .padStart(2, "0");
  return `#${c(r[0])}${c(r[1])}${c(r[2])}`;
}

const s2l = (c: number) => (c <= 0.04045 / 12.92 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const l2s = (c: number) => (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055);

/** sRGB -> OKLab (L, a, b). */
function rgbToLab(r: Rgb): Rgb {
  const [rl, gl, bl] = [s2l(r[0]), s2l(r[1]), s2l(r[2])];
  const l = 0.4122214708 * rl + 0.5363325363 * gl + 0.0514459929 * bl;
  const m = 0.2119034982 * rl + 0.6806995451 * gl + 0.1073969566 * bl;
  const s = 0.0883024619 * rl + 0.2817188376 * gl + 0.6299787005 * bl;
  const l_ = Math.cbrt(l), m_ = Math.cbrt(m), s_ = Math.cbrt(s);
  return [
    0.2104542553 * l_ + 0.793617785 * m_ - 0.0040720468 * s_,
    1.9779984951 * l_ - 2.428592205 * m_ + 0.4505937099 * s_,
    0.0259040321 * l_ + 0.7827717662 * m_ - 0.8086757663 * s_,
  ];
}

/** OKLab (L, a, b) -> sRGB, clamped to [0,1]. */
function labToRgb(lab: Rgb): Rgb {
  const [L, a, b] = lab;
  const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
  const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
  const s_ = L - 0.0894844775 * a - 1.291485548 * b;
  const l = l_ ** 3, m = m_ ** 3, s = s_ ** 3;
  return [
    Math.max(0, Math.min(1, 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s)),
    Math.max(0, Math.min(1, -1.2684380046 * l + 2.609757401 * m - 0.3413193964 * s)),
    Math.max(0, Math.min(1, -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s)),
  ].map(l2s) as Rgb;
}

function mixLab(from: Rgb, to: Rgb, t: number): Rgb {
  return [
    from[0] + (to[0] - from[0]) * t,
    from[1] + (to[1] - from[1]) * t,
    from[2] + (to[2] - from[2]) * t,
  ];
}

/** `steps` swatches, endpoints included. */
export function ramp(fromHex: string, toHex: string, steps: number): string[] {
  const from = rgbToLab(hexToRgb(fromHex));
  const to = rgbToLab(hexToRgb(toHex));
  return Array.from({ length: steps }, (_, i) =>
    rgbToHex(labToRgb(mixLab(from, to, i / (steps - 1)))),
  );
}

/**
 * Orange sequential ramp: near-surface warm tint -> deep orange-brown,
 * passing through the categorical orange hue. 13 steps to match BLUE_SEQUENTIAL.
 */
export const ORANGE_SEQUENTIAL: string[] = ramp("#fdeee2", "#832e07", 13);

/* ---------------- Diverging (coal direction) ---------------- */

const DIVERGING_MID: Record<Mode, string> = {
  light: "#f0efec",
  dark: "#383835",
};
const DIVERGING_BLUE: Record<Mode, string> = { light: "#2a78d6", dark: "#3987e5" };
const DIVERGING_RED: Record<Mode, string> = { light: "#e34948", dark: "#e66767" };

/**
 * 13-step diverging ramp for coal *direction*: index 6 = no change (neutral),
 * 0 = strongest decrease (blue), 12 = strongest increase (red).
 */
export function divergingRamp(mode: Mode): string[] {
  const blue = rgbToLab(hexToRgb(DIVERGING_BLUE[mode]));
  const mid = rgbToLab(hexToRgb(DIVERGING_MID[mode]));
  const red = rgbToLab(hexToRgb(DIVERGING_RED[mode]));
  const out: string[] = [];
  // Blue pole (index 0) -> neutral mid (index 6) -> red pole (index 12).
  // The first arm must run blue->mid in ascending index so index 6 lands on the
  // neutral; reversed, the array would put neutral at index 0 and divergingScale
  // (which maps v=0 -> index 6) would paint zero-change as the blue pole.
  for (let i = 0; i <= 6; i++) out.push(rgbToHex(labToRgb(mixLab(blue, mid, i / 6))));
  for (let i = 1; i <= 6; i++) out.push(rgbToHex(labToRgb(mixLab(mid, red, i / 6))));
  return out;
}

export const DIVERGING: Record<Mode, string[]> = {
  light: divergingRamp("light"),
  dark: divergingRamp("dark"),
};

/* ---------------- Scale helpers ---------------- */

export interface SequentialScale {
  ramp: string[];
  min: number;
  max: number;
  color: (v: number) => string;
  /** css linear-gradient for legend bars (left = min). */
  cssGradient: string;
}

export function sequentialScale(rampSteps: string[], min: number, max: number): SequentialScale {
  const span = max - min;
  const color = (v: number): string => {
    const t = span <= 0 ? 0.5 : Math.max(0, Math.min(1, (v - min) / span));
    return rampSteps[Math.round(t * (rampSteps.length - 1))];
  };
  return {
    ramp: rampSteps,
    min,
    max,
    color,
    cssGradient: `linear-gradient(to right, ${rampSteps.join(", ")})`,
  };
}

/**
 * Diverging scale over signed values: abs bound = symmetric range.
 * `bound` is the magnitude that maps to the extreme pole (e.g. max |delta|).
 */
export function divergingScale(mode: Mode, bound: number): {
  color: (v: number) => string;
  cssGradient: string;
  steps: string[];
} {
  const steps = DIVERGING[mode];
  const b = bound <= 0 ? 1 : bound;
  const color = (v: number): string => {
    const t = Math.max(-1, Math.min(1, v / b));
    return steps[Math.round((t + 1) / 2 * (steps.length - 1))];
  };
  return {
    color,
    cssGradient: `linear-gradient(to right, ${steps.join(", ")})`,
    steps,
  };
}
