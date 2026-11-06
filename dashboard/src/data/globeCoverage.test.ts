/**
 * Full-globe coverage test: exercises the EXACT chain the browser runs -
 *
 *   bundled world-atlas topology -> topojson feature() -> GeoMatcher
 *   (real public/data/geo.json) -> iso3 -> buildBundle (real generated
 *   JSON) -> layerValue / coalChangeTWh / layerDomain / scales
 *
 * Answers, for the data actually shipped:
 *   1. every globe feature resolves to a valid iso3 (or is a known
 *      no-id enclave that stays uncolored on purpose);
 *   2. every data country is either clickable on the globe, or is a
 *      microstate/territory with no 110m feature and is reachable via search
 *      (the exact set is pinned so a real country losing its feature fails);
 *   3. every country x year x layer value is a finite number or null -
 *      never NaN, never a throw;
 *   4. the color scales produce colors for the real domains;
 *   5. the US map: every state feature resolves via FIPS; states with no
 *      coal rows (MA, VT) render null (no data), never zero or NaN.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { beforeAll, describe, expect, it } from "vitest";
import { feature } from "topojson-client";
import worldTopo from "world-atlas/countries-110m.json";
import statesTopo from "us-atlas/states-albers-10m.json";
import { FIPS_TO_STATE } from "./geo";
import { buildBundle } from "./loader";
import type { DataBundle } from "./loader";
import { coalChangeTWh, layerDomain, layerValue } from "../viz/layerValue";
import { stateValue } from "../viz/stateValue";
import {
  BLUE_SEQUENTIAL, ORANGE_SEQUENTIAL, divergingScale, sequentialScale,
} from "../viz/palette";
import { LAYERS, YEARS, type LayerKey } from "./types";

type Raw = {
  properties?: { name?: string } | null;
  id?: string | number | null;
};
type Topo = { objects: { countries?: unknown; states?: unknown } };

function loadJson<T>(name: string): T {
  const p = resolve(process.cwd(), "public", "data", name);
  return JSON.parse(readFileSync(p, "utf-8")) as T;
}

function topoFeatures(topo: unknown, key: "countries" | "states"): Raw[] {
  const t = topo as Topo;
  const fc = feature(t, t.objects[key]) as unknown as { features: Raw[] };
  return fc.features;
}

let bundle: DataBundle;
let worldFeatures: Raw[];
let statesFeatures: Raw[];

function resolveIso(f: Raw): string | null {
  return bundle.geo.matchFeature(f.id ?? null, f.properties?.name ?? null);
}

// Built once for the whole suite (real files, real code).
beforeAll(() => {
  bundle = buildBundle(
    loadJson("country_year.json"),
    loadJson("us_state_year.json"),
    loadJson("us_aggregates.json"),
    loadJson("geo.json"),
  );
  worldFeatures = topoFeatures(worldTopo, "countries");
  statesFeatures = topoFeatures(statesTopo, "states");
});

describe("world globe: feature -> iso3 resolution", () => {
  it("bundled topology has the expected features; none resolve to a malformed iso3", () => {
    expect(worldFeatures.length).toBe(177);
    for (const f of worldFeatures) {
      const iso = resolveIso(f);
      if (iso != null) expect(iso, f.properties?.name).toMatch(/^[A-Z]{3}$/);
    }
  });

  it("every feature resolves to an iso3 except the two known no-id enclaves", () => {
    // N. Cyprus and Somaliland carry no ISO numeric id in the topology and the
    // dataset reports no generation for either, so they stay uncolored on
    // purpose. Everything else must resolve.
    const unresolved = worldFeatures
      .filter(f => resolveIso(f) == null)
      .map(f => f.properties?.name)
      .sort();
    expect(unresolved).toEqual(["N. Cyprus", "Somaliland"]);
  });

  it("major countries (incl. ones previously unmapped) resolve to the right iso3", () => {
    const byName = new Map(worldFeatures.map(f => [f.properties?.name, f]));
    const expectIso: [string, string][] = [
      ["United States of America", "USA"],
      ["China", "CHN"],
      ["India", "IND"],
      ["Germany", "DEU"],
      ["Indonesia", "IDN"],
      ["Brazil", "BRA"],
      ["Australia", "AUS"],
      ["Russia", "RUS"],
      ["Japan", "JPN"],
      ["France", "FRA"],
      ["United Kingdom", "GBR"],
      // formerly-mis-mapped (built from the incomplete EI numeric table):
      ["Afghanistan", "AFG"],
      ["Armenia", "ARM"],
      ["Benin", "BEN"],
      ["Cameroon", "CMR"],
      ["Ghana", "GHA"],
      ["Senegal", "SEN"],
      ["Kenya", "KEN"],
      ["Somalia", "SOM"],
      ["Mexico", "MEX"],
      ["Nigeria", "NGA"],
      ["South Korea", "KOR"],
      ["North Korea", "PRK"],
      ["Côte d'Ivoire", "CIV"],
      ["Dem. Rep. Congo", "COD"],
      ["Congo", "COG"],
      ["Bosnia and Herz.", "BIH"],
      ["Eq. Guinea", "GNQ"],
      ["Sri Lanka", "LKA"],
      ["Macedonia", "MKD"],
      ["Timor-Leste", "TLS"],
      ["eSwatini", "SWZ"],
      // data-code edge cases (the dataset keys these differently than ISO):
      ["Falkland Is.", "FLK"],
      ["Kosovo", "XKX"],
    ];
    for (const [name, iso] of expectIso) {
      const f = byName.get(name);
      expect(f, `feature for ${name} exists in topology`).toBeTruthy();
      expect(resolveIso(f!), name).toBe(iso);
    }
  });
});

describe("world globe: data -> globe coverage", () => {
  it("every data country is clickable on the globe, else is a known microstate (search-only)", () => {
    const isoOnGlobe = new Set<string>();
    for (const f of worldFeatures) {
      const iso = resolveIso(f);
      if (iso) isoOnGlobe.add(iso);
    }
    const allData = [...bundle.countryByIso.keys()];
    const searchOnly = allData.filter(iso => !isoOnGlobe.has(iso)).sort();

    // These 42 are all small island states / city-states / overseas
    // territories with no feature at 110m resolution. They remain reachable
    // via the search box. The exact set is pinned so any FUTURE regression
    // (a real country losing its globe feature) fails loudly rather than
    // quietly greying out.
    const EXPECTED_SEARCH_ONLY = [
      "ABW", "ASM", "ATG", "BHR", "BMU", "BRB", "COK", "COM", "CPV", "CYM",
      "DMA", "FRO", "GIB", "GLP", "GRD", "GUF", "GUM", "HKG", "KIR", "KNA",
      "LCA", "MAC", "MDV", "MLT", "MSR", "MTQ", "MUS", "NIU", "NRU", "PYF",
      "REU", "SGP", "SHN", "SPM", "STP", "SYC", "TCA", "TON", "VCT", "VGB",
      "VIR", "WSM",
    ].sort();
    expect(searchOnly, `data countries without a globe feature: ${searchOnly.join(", ")}`)
      .toEqual(EXPECTED_SEARCH_ONLY);

    // And every data country that IS on the globe has a display name for its
    // panel (clicking it must not show "Unknown").
    for (const iso of allData) {
      if (isoOnGlobe.has(iso)) {
        expect(bundle.countryNames.has(iso), iso).toBe(true);
      }
    }
  });
});

describe("world globe: values for every country x year x layer", () => {
  it("layerValue never throws or returns NaN for any country/year/layer", () => {
    const layers = Object.keys(LAYERS) as LayerKey[];
    let checked = 0;
    for (const [iso, byYear] of bundle.countryByIso) {
      for (const [year, rec] of byYear) {
        for (const layer of layers) {
          const v = layerValue(layer, rec);
          expect(v == null || Number.isFinite(v), `${iso} ${year} ${layer}`).toBe(true);
          checked++;
        }
        const d = coalChangeTWh(bundle, iso, year);
        expect(d == null || Number.isFinite(d), `${iso} ${year} coalDelta`).toBe(true);
      }
    }
    expect(checked).toBeGreaterThan(0);
  });

  it("every layer has a valid domain and scale for 2024 (mid-panel year)", () => {
    for (const layer of Object.keys(LAYERS) as LayerKey[]) {
      const domain = layerDomain(bundle, layer, bundle.countryByIso.keys(), 2024);
      expect(domain, `domain for ${layer}`).not.toBeNull();
      const [min, max] = domain!;
      expect(Number.isFinite(min)).toBe(true);
      expect(Number.isFinite(max)).toBe(true);
      expect(min).toBeLessThanOrEqual(max);
      const ramp = LAYERS[layer].sequential === "orange" ? ORANGE_SEQUENTIAL : BLUE_SEQUENTIAL;
      const scale = sequentialScale(ramp, min, max);
      const color = scale.color((min + max) / 2);
      expect(typeof color).toBe("string");
      expect(color.length).toBeGreaterThan(0);
    }
  });

  it("diverging coal-change scale colors real 2025 deltas", () => {
    // US rebounded in 2025 (positive delta), China fell (negative) - both
    // must color without throwing.
    const us = coalChangeTWh(bundle, "USA", 2025);
    const cn = coalChangeTWh(bundle, "CHN", 2025);
    expect(us).not.toBeNull();
    expect(cn).not.toBeNull();
    expect(us!).toBeGreaterThan(0);
    expect(cn!).toBeLessThan(0);
    const bound = Math.max(Math.abs(us!), Math.abs(cn!));
    for (const theme of ["light", "dark"] as const) {
      const s = divergingScale(theme, bound);
      expect(typeof s.color(us!)).toBe("string");
      expect(typeof s.color(cn!)).toBe("string");
      expect(typeof s.color(0)).toBe("string");
    }
  });

  it("2025 partial panel: countries without a 2025 record resolve to null, not NaN", () => {
    // Ember 2025 covers 91 of 213 countries: many iso3s lack a 2025 record.
    const missing2025 = [...bundle.countryByIso.keys()].filter(
      iso => !bundle.countryByIso.get(iso)!.has(2025),
    );
    expect(missing2025.length).toBeGreaterThan(0);
    for (const iso of missing2025.slice(0, 50)) {
      for (const layer of Object.keys(LAYERS) as LayerKey[]) {
        const v = layerValue(layer, bundle.countryByIso.get(iso)?.get(2025));
        expect(v, `${iso} ${layer}`).toBeNull();
      }
    }
  });
});

describe("US drill-down map: state feature -> state data", () => {
  it("every state feature resolves via FIPS to a known state code", () => {
    const codes = new Set(Object.values(FIPS_TO_STATE));
    for (const f of statesFeatures) {
      const fips = String(f.id);
      const st = FIPS_TO_STATE[fips];
      expect(st, `FIPS ${fips} (${f.properties?.name}) maps to a known state`).toBeTruthy();
      expect(codes.has(st!), fips).toBe(true);
    }
    expect(statesFeatures.length).toBeGreaterThanOrEqual(50);
  });

  it("stateValue is always finite or null (never NaN) for every state x year", () => {
    for (const st of Object.values(FIPS_TO_STATE)) {
      for (const y of YEARS) {
        const v = stateValue(bundle, st, y, "all");
        expect(v == null || Number.isFinite(v), `${st} ${y}`).toBe(true);
      }
    }
  });

  it("states with no coal rows (MA, VT) render null - no data, not zero", () => {
    for (const st of ["MA", "VT"]) {
      expect(bundle.stateByCode.has(st), st).toBe(false);
      for (const y of YEARS) {
        expect(stateValue(bundle, st, y, "all"), `${st} ${y}`).toBeNull();
      }
    }
  });

  it("DC has rows but EIA reports no consumption -> null every year, not zero", () => {
    // DC appears in the table (sector 8 rows) but every consumption is null,
    // so it must render as no-data, never as 0.
    expect(bundle.stateByCode.has("DC")).toBe(true);
    for (const y of YEARS) {
      expect(stateValue(bundle, "DC", y, "all"), `DC ${y}`).toBeNull();
    }
  });

  it("exactly the no-data states render receded; the other 49 have real values", () => {
    // MA, VT: no rows at all. DC: rows but no reported consumption.
    // Every other state reports coal consumption in at least one year.
    const hasAnyYear = Object.values(FIPS_TO_STATE).filter(st =>
      YEARS.some(y => stateValue(bundle, st, y, "all") != null),
    ).sort();
    const expected = Object.values(FIPS_TO_STATE)
      .filter(s => !["MA", "VT", "DC"].includes(s)).sort();
    expect(hasAnyYear, `states with usable coal data`).toEqual(expected);
    expect(hasAnyYear.length).toBe(49);
  });

  it("Hawaii reports real 2020-2022 values but none after 2022 (partial, not NaN)", () => {
    expect(stateValue(bundle, "HI", 2020, "all")!).toBeGreaterThan(0);
    expect(stateValue(bundle, "HI", 2022, "all")!).toBeGreaterThan(0);
    expect(stateValue(bundle, "HI", 2023, "all")).toBeNull();
    expect(stateValue(bundle, "HI", 2025, "all")).toBeNull();
  });

  it("Texas (largest state) has real 2024 consumption across base sectors", () => {
    const total = stateValue(bundle, "TX", 2024, "all");
    expect(total).not.toBeNull();
    expect(total!).toBeGreaterThan(1_000_000); // short tons
  });
});

describe("globe geometry sanity", () => {
  it("feature() produced sane counts for both bundled topologies", () => {
    expect(worldFeatures.length).toBe(177);
    expect(statesFeatures.length).toBeGreaterThanOrEqual(50);
  });

  it("YEARS covers 2020-2025 and every data year is selectable", () => {
    expect(YEARS).toEqual([2020, 2021, 2022, 2023, 2024, 2025]);
    const dataYears = new Set<number>();
    for (const byYear of bundle.countryByIso.values()) {
      for (const y of byYear.keys()) dataYears.add(y);
    }
    for (const y of dataYears) expect(YEARS).toContain(y);
  });
});
