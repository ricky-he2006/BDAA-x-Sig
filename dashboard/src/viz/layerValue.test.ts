import { describe, expect, it } from "vitest";
import {
  layerValue, layerDomain, coalChangeTWh, coalChangeBound,
} from "./layerValue";
import type { CountryYear } from "../data/types";
import type { DataBundle } from "../data/loader";

function cy(partial: {
  clean_share?: number | null;
  demand?: number | null;
  renewable?: number | null;
  coal_gen?: number | null;
}): CountryYear {
  return {
    iso3: "TEST",
    name: "Testland",
    continent: "Test",
    year: 2024,
    ember: {
      demand: partial.demand ?? null,
      generation: null, clean: null, fossil: null,
      renewable: partial.renewable ?? null, wind_solar: null,
      clean_share: partial.clean_share ?? null, net_imports: null, ci: null,
      emissions: null, demand_change: null, clean_change: null, fossil_change: null,
      has_previous_year: 1, growth_status: null,
    },
    ei: {
      elect: null, coal_gen: partial.coal_gen ?? null, gas_gen: null,
      nuclear_gen: null, ren_gen: null, wind: null, solar: null, hydro: null,
      coal_prod_mt: null, coal_tes_ej: null, tes_ej: null, co2_mtco2: null, pop: null,
    },
    coal_share: null, ei_available: partial.coal_gen != null,
    zero_generation: false, ci_precision_limited: false,
  };
}

function bundle(
  years: Record<number, Partial<Parameters<typeof cy>[0]>>,
): DataBundle {
  const m = new Map<number, CountryYear>();
  for (const [y, v] of Object.entries(years)) {
    if (v) m.set(Number(y), cy(v));
  }
  return {
    countryByIso: new Map([["TEST", m]]),
    countryNames: new Map([["TEST", "Testland"]]),
    geo: {} as DataBundle["geo"],
    stateByCode: new Map(),
    stateNames: new Map(),
    sectors: {},
    usAggregates: [], eiWorld: [], coverage: [], sources: [],
  };
}

describe("layerValue", () => {
  it("reads the right block per layer key", () => {
    const c = cy({ clean_share: 42, demand: 1000, renewable: 300, coal_gen: 250 });
    expect(layerValue("clean_share", c)).toBe(42);
    expect(layerValue("demand", c)).toBe(1000);
    expect(layerValue("renewable", c)).toBe(300);
    expect(layerValue("coal_gen", c)).toBe(250);
    expect(layerValue("ci", c)).toBeNull(); // not set
  });

  it("returns null for a missing country-year (never invents data)", () => {
    expect(layerValue("clean_share", undefined)).toBeNull();
  });
});

describe("coalChangeTWh", () => {
  it("is the difference of two reported EI values", () => {
    const b = bundle({
      2023: { coal_gen: 300 },
      2024: { coal_gen: 250 },
    });
    expect(coalChangeTWh(b, "TEST", 2024)).toBe(-50);
  });

  it("is null when either year is missing (never assumes zero)", () => {
    const b = bundle({ 2024: { coal_gen: 250 } });
    expect(coalChangeTWh(b, "TEST", 2024)).toBeNull();
    const b2 = bundle({
      2023: {},
      2024: { coal_gen: 250 },
    });
    expect(coalChangeTWh(b2, "TEST", 2024)).toBeNull();
  });

  it("is null at the first year of the series", () => {
    const b = bundle({ 2020: { coal_gen: 300 } });
    expect(coalChangeTWh(b, "TEST", 2020)).toBeNull();
  });
});

describe("layerDomain / coalChangeBound", () => {
  it("excludes nulls and returns null when no values exist", () => {
    const b = bundle({
      2024: { clean_share: 42, coal_gen: 250 },
    });
    expect(layerDomain(b, "clean_share", ["TEST"], 2024)).toEqual([42, 42]);
    expect(layerDomain(b, "demand", ["TEST"], 2024)).toBeNull();
    expect(coalChangeBound(b, ["TEST"], 2024)).toBe(0);
  });

  it("coalChangeBound is the max abs delta", () => {
    const b = bundle({
      2023: { coal_gen: 100 },
      2024: { coal_gen: 40 },
    });
    expect(coalChangeBound(b, ["TEST"], 2024)).toBe(60);
  });
});
