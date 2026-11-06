import { describe, expect, it } from "vitest";
import {
  BLUE_SEQUENTIAL, ORANGE_SEQUENTIAL, DIVERGING, ramp,
  sequentialScale, divergingScale,
} from "./palette";

describe("sequential ramps", () => {
  it("has 13 steps and hex values", () => {
    expect(BLUE_SEQUENTIAL).toHaveLength(13);
    expect(ORANGE_SEQUENTIAL).toHaveLength(13);
    for (const c of [...BLUE_SEQUENTIAL, ...ORANGE_SEQUENTIAL]) {
      expect(c).toMatch(/^#[0-9a-f]{6}$/);
    }
  });

  it("is monotonically darker from light to dark (blue ramp, validated steps)", () => {
    const lum = (hex: string) => {
      const n = parseInt(hex.slice(1), 16);
      const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };
    for (let i = 1; i < BLUE_SEQUENTIAL.length; i++) {
      expect(lum(BLUE_SEQUENTIAL[i])).toBeLessThanOrEqual(lum(BLUE_SEQUENTIAL[i - 1]) + 0.5);
    }
    expect(lum(BLUE_SEQUENTIAL[12])).toBeLessThan(lum(BLUE_SEQUENTIAL[0]) / 3);
  });

  it("orange ramp is distinct from the blue ramp", () => {
    for (let i = 0; i < 13; i++) {
      expect(ORANGE_SEQUENTIAL[i]).not.toBe(BLUE_SEQUENTIAL[i]);
    }
  });

  it("ramp() interpolates endpoints exactly", () => {
    const r = ramp("#ffffff", "#000000", 5);
    expect(r[0]).toBe("#ffffff");
    expect(r[4]).toBe("#000000");
    expect(r).toHaveLength(5);
  });
});

describe("diverging ramp (coal direction)", () => {
  it("has 13 steps with a neutral midpoint", () => {
    for (const mode of ["light", "dark"] as const) {
      const steps = DIVERGING[mode];
      expect(steps).toHaveLength(13);
      // midpoint is the skill's neutral gray for that mode
      expect(steps[6]).toBe(mode === "light" ? "#f0efec" : "#383835");
    }
  });

  it("blue pole is cool, red pole is warm", () => {
    const channel = (hex: string, i: number) =>
      parseInt(hex.slice(1 + i * 2, 3 + i * 2), 16);
    const light = DIVERGING.light;
    expect(channel(light[0], 2)).toBeGreaterThan(channel(light[0], 0)); // blue: B > R
    expect(channel(light[12], 0)).toBeGreaterThan(channel(light[12], 2)); // red: R > B
  });
});

describe("scales", () => {
  it("sequentialScale maps min/mid/max to first/mid/last step", () => {
    const s = sequentialScale(BLUE_SEQUENTIAL, 0, 100);
    expect(s.color(0)).toBe(BLUE_SEQUENTIAL[0]);
    expect(s.color(100)).toBe(BLUE_SEQUENTIAL[12]);
    // out-of-range clamps, never throws
    expect(s.color(-50)).toBe(BLUE_SEQUENTIAL[0]);
    expect(s.color(150)).toBe(BLUE_SEQUENTIAL[12]);
  });

  it("divergingScale maps sign to hue and clamps", () => {
    const s = divergingScale("light", 10);
    expect(s.color(0)).toBe("#f0efec");
    expect(s.color(-10)).toBe(DIVERGING.light[0]);
    expect(s.color(10)).toBe(DIVERGING.light[12]);
    expect(s.color(-99)).toBe(DIVERGING.light[0]);
    expect(s.color(99)).toBe(DIVERGING.light[12]);
    // symmetric: +5 and -5 are equidistant from the midpoint
    expect(DIVERGING.light.indexOf(s.color(5))).toBe(
      DIVERGING.light.length - 1 - DIVERGING.light.indexOf(s.color(-5)),
    );
  });
});
