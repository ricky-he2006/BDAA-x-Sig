import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { loadData, buildBundle, stateConsumption } from "./loader";
import type {
  CountryYearFile, UsStateYearFile, UsAggregatesFile,
} from "./types";

const cyFile: CountryYearFile = {
  grain: "iso3 x year",
  n: 3,
  records: [
    {
      iso3: "USA", name: "United States", continent: "North America", year: 2023,
      ember: {
        demand: 4200, generation: 4100, clean: 2100, fossil: 2000, renewable: 1400,
        wind_solar: 900, clean_share: 51.2, net_imports: null, ci: 380,
        emissions: 1500, demand_change: 20, clean_change: 50, fossil_change: -30,
        has_previous_year: 1, growth_status: "clean_growth_met_or_exceeded_demand_growth",
      },
      ei: {
        elect: 4150, coal_gen: 1000, gas_gen: 1600, nuclear_gen: 700, ren_gen: 850,
        wind: 500, solar: 250, hydro: 100, coal_prod_mt: 500, coal_tes_ej: 20,
        tes_ej: 100, co2_mtco2: 5000, pop: 335,
      },
      coal_share: 24.1, ei_available: true, zero_generation: false, ci_precision_limited: false,
    },
    {
      iso3: "USA", name: "United States", continent: "North America", year: 2024,
      ember: {
        demand: 4250, generation: 4150, clean: 2150, fossil: 2000, renewable: 1450,
        wind_solar: 950, clean_share: 51.8, net_imports: null, ci: 372,
        emissions: 1500, demand_change: 50, clean_change: 50, fossil_change: 0,
        has_previous_year: 1, growth_status: "clean_growth_met_or_exceeded_demand_growth",
      },
      ei: {
        elect: 4200, coal_gen: 980, gas_gen: 1620, nuclear_gen: 700, ren_gen: 900,
        wind: 520, solar: 260, hydro: 120, coal_prod_mt: 510, coal_tes_ej: 21,
        tes_ej: 102, co2_mtco2: 5050, pop: 340,
      },
      coal_share: 23.3, ei_available: true, zero_generation: false, ci_precision_limited: false,
    },
    {
      iso3: "CHN", name: "China", continent: "Asia", year: 2024,
      ember: {
        demand: 9000, generation: 8900, clean: 5000, fossil: 3900, renewable: 3500,
        wind_solar: 2500, clean_share: 56.2, net_imports: null, ci: 220,
        emissions: 2000, demand_change: 100, clean_change: 200, fossil_change: -50,
        has_previous_year: 1, growth_status: "clean_growth_met_or_exceeded_demand_growth",
      },
      ei: {
        elect: 9100, coal_gen: 5500, gas_gen: 300, nuclear_gen: 450, ren_gen: 2850,
        wind: 1000, solar: 900, hydro: 900, coal_prod_mt: 4700, coal_tes_ej: 90,
        tes_ej: 300, co2_mtco2: 30000, pop: 1420,
      },
      coal_share: 60.4, ei_available: true, zero_generation: false, ci_precision_limited: false,
    },
  ],
};

const usFile: UsStateYearFile = {
  grain: "state x year x base-sector",
  sectors: { 1: "Electric Utility", 2: "IPP Non-CHP", 3: "IPP CHP", 8: "Commercial and Institutional", 9: "Coke Plants", 10: "Other Industrial" },
  n: 4,
  records: [
    { state: "TX", state_name: "Texas", year: 2024, sector: 1, sector_name: "Electric Utility", consumption: 40e6, receipts: 41e6, stocks: 10e6, price: 90, heat_btu_lb: 20000, heat_unit: "Btu/lb", sulfur_pct: 1.5, ash_pct: 10 },
    { state: "TX", state_name: "Texas", year: 2024, sector: 2, sector_name: "IPP Non-CHP", consumption: 5e6, receipts: 5e6, stocks: 1e6, price: 95, heat_btu_lb: 20100, heat_unit: "Btu/lb", sulfur_pct: 1.6, ash_pct: 10.1 },
    { state: "TX", state_name: "Texas", year: 2023, sector: 1, sector_name: "Electric Utility", consumption: 30e6, receipts: 31e6, stocks: 9e6, price: 80, heat_btu_lb: 19900, heat_unit: "Btu/lb", sulfur_pct: 1.4, ash_pct: 9.9 },
    { state: "AK", state_name: "Alaska", year: 2024, sector: 1, sector_name: "Electric Utility", consumption: null, receipts: null, stocks: null, price: null, heat_btu_lb: null, heat_unit: null, sulfur_pct: null, ash_pct: null },
  ],
};

const aggFile: UsAggregatesFile = {
  grain: "location x year x aggregate-sector",
  n: 1,
  records: [
    { location: "US", location_name: "United States", location_type: "us_total", year: 2024, sector: 98, sector_name: "Electric Power", consumption: 130e6, receipts: 131e6, price: 92 },
  ],
};

const geoFile = {
  numeric_to_alpha3: { "840": "USA", "156": "CHN" },
  name_to_alpha3: {},
};

function mockFetch() {
  const handler = (url: string) => {
    let body: unknown;
    if (url.includes("country_year")) body = cyFile;
    else if (url.includes("us_state_year")) body = usFile;
    else if (url.includes("us_aggregates")) body = aggFile;
    else body = geoFile;
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve(body),
    } as Response);
  };
  return vi.fn(handler);
}

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch());
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("loadData", () => {
  it("builds the bundle with expected structure", async () => {
    const bundle = await loadData();
    expect(bundle.countryByIso.get("USA")?.get(2024)?.ember.clean_share).toBeCloseTo(51.8);
    expect(bundle.countryByIso.get("CHN")?.get(2024)?.ei.coal_gen).toBe(5500);
    expect(bundle.countryNames.get("USA")).toBe("United States");
    expect(bundle.stateByCode.get("TX")?.get(2024)).toHaveLength(2);
    expect(bundle.stateNames.get("TX")).toBe("Texas");
    expect(bundle.usAggregates).toHaveLength(1);
    expect(bundle.geo.matchFeature("840", "United States of America")).toBe("USA");
  });

  it("surfaces a failed fetch as an error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({ ok: false, status: 500, json: async () => ({}) })),
    );
    await expect(loadData()).rejects.toThrow(/failed to load/);
  });

  it("rejects duplicate observations, stale record counts and overlapping state sectors", () => {
    expect(() => buildBundle({ ...cyFile, n: 4, records: [...cyFile.records, cyFile.records[0]] }, usFile, aggFile, geoFile)).toThrow(/Duplicate country/);
    expect(() => buildBundle({ ...cyFile, n: 99 }, usFile, aggFile, geoFile)).toThrow(/count/);
    expect(() => buildBundle(cyFile, { ...usFile, records: usFile.records.map((r, i) => i === 0 ? { ...r, sector: 98 } : r) }, aggFile, geoFile)).toThrow(/state sector/);
  });
});

describe("stateConsumption (loader helper)", () => {
  it("sums base sectors and returns null when nothing is reported", () => {
    const mk = (consumption: number | null) => ({
      state: "TX", state_name: "Texas", year: 2024, sector: 1, sector_name: "Electric Utility",
      consumption, receipts: null, stocks: null, price: null, heat_btu_lb: null,
      heat_unit: null, sulfur_pct: null, ash_pct: null,
    });
    expect(stateConsumption([mk(40e6), mk(5e6), mk(null)])).toBe(45e6);
    expect(stateConsumption([])).toBeNull();
    expect(stateConsumption(undefined)).toBeNull();
    expect(stateConsumption([mk(null)])).toBeNull();
  });
});
