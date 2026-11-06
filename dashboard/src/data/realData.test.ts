/**
 * Validates the ACTUAL generated JSON in dashboard/public/data/ (the files
 * the app fetches at runtime), not fixtures. Guards the NaN-fix: missing
 * values must arrive as `null`, real zeros must stay `0`, and no non-finite
 * number may be present. These tests fail if a stale or corrupt JSON file is
 * committed / served.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import type {
  CountryYearFile, UsStateYearFile, UsAggregatesFile,
} from "./types";

// vitest runs with cwd = the dashboard root, so public/data resolves directly.
function load<T>(name: string): T {
  const p = resolve(process.cwd(), "public", "data", name);
  return JSON.parse(readFileSync(p, "utf-8")) as T;
}

/** Recursively assert no NaN / +/-Infinity anywhere in a parsed structure. */
function assertFinite(v: unknown, path = "root"): void {
  if (Array.isArray(v)) {
    v.forEach((x, i) => assertFinite(x, `${path}[${i}]`));
  } else if (v && typeof v === "object") {
    for (const [k, x] of Object.entries(v as Record<string, unknown>)) {
      assertFinite(x, `${path}.${k}`);
    }
  } else if (typeof v === "number") {
    expect(Number.isFinite(v), `${path} is not finite`).toBe(true);
  }
}

describe("generated public/data JSON", () => {
  it("country_year.json: no non-finite values; missing EI -> null", () => {
    const f = load<CountryYearFile>("country_year.json");
    assertFinite(f);
    expect(f.n).toBe(f.records.length);
    // Countries with no EI variables must have null coal_share and null ei.
    const noEi = f.records.filter(r => !r.ei_available);
    expect(noEi.length).toBeGreaterThan(0);
    for (const r of noEi) {
      expect(r.coal_share).toBeNull();
      for (const v of Object.values(r.ei)) expect(v).toBeNull();
    }
    // Ember block: a real reported value and a missing one must coexist.
    const withCi = f.records.find(r => r.ember.ci != null);
    expect(withCi).toBeTruthy();
    const noCi = f.records.find(r => r.ember.ci == null);
    expect(noCi).toBeTruthy();
  });

  it("us_state_year.json: missing price/stocks are null, real zero kept", () => {
    const f = load<UsStateYearFile>("us_state_year.json");
    assertFinite(f);
    // A missing price (null) with a real, non-zero consumption alongside.
    const ak3 = f.records.find(r => r.state === "AK" && r.year === 2020 && r.sector === 3);
    expect(ak3).toBeTruthy();
    expect(ak3!.price).toBeNull();              // missing -> null, not 0
    expect(ak3!.consumption).toBe(220848);     // real value preserved
    // A reported price must be a real number.
    const ak1 = f.records.find(r => r.state === "AK" && r.year === 2020 && r.sector === 1);
    expect(ak1!.price).toBeCloseTo(49.26);
    // A real zero consumption must survive as exactly 0, with null price.
    const ca3 = f.records.find(r => r.state === "CA" && r.year === 2020 && r.sector === 3);
    expect(ca3).toBeTruthy();
    expect(ca3!.consumption).toBe(0);
    expect(ca3!.price).toBeNull();
  });

  it("us_aggregates.json: missing 2021 US price is null, neighbors intact", () => {
    const f = load<UsAggregatesFile>("us_aggregates.json");
    assertFinite(f);
    const g = (y: number, s: number) =>
      f.records.find(r => r.location === "US" && r.year === y && r.sector === s);
    expect(g(2020, 98)!.price).toBeCloseTo(36.13);
    expect(g(2021, 98)!.price).toBeNull();
    expect(g(2022, 98)!.price).toBeCloseTo(44.5);
  });

  it("geo.json: parses and has the two mapping tables", () => {
    const f = load<{ numeric_to_alpha3: Record<string, string>;
                     name_to_alpha3: Record<string, string> }>("geo.json");
    expect(Object.keys(f.numeric_to_alpha3).length).toBeGreaterThan(0);
    expect(Object.keys(f.name_to_alpha3).length).toBeGreaterThan(0);
    assertFinite(f);
  });
});
