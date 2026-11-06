import type { CountryYearFile, UsStateYearFile, UsAggregatesFile } from "../data/types";
import type { GeoMapping } from "../data/geo";

export const COUNTRY_YEAR: CountryYearFile = {
  grain: "iso3 x year",
  n: 4,
  records: [
    {
      iso3: "USA", name: "United States", continent: "North America", year: 2023,
      ember: {
        demand: 4200, generation: 4100, clean: 2100, fossil: 2000, renewable: 1400,
        wind_solar: 900, clean_share: 51.2, net_imports: null, ci: 380, emissions: 1500,
        demand_change: 20, clean_change: 50, fossil_change: -30, has_previous_year: 1,
        growth_status: "clean_growth_met_or_exceeded_demand_growth",
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
        wind_solar: 950, clean_share: 51.8, net_imports: null, ci: 372, emissions: 1490,
        demand_change: 50, clean_change: 50, fossil_change: 0, has_previous_year: 1,
        growth_status: "clean_growth_met_or_exceeded_demand_growth",
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
        wind_solar: 2500, clean_share: 56.2, net_imports: null, ci: 220, emissions: 2000,
        demand_change: 100, clean_change: 200, fossil_change: -50, has_previous_year: 1,
        growth_status: "clean_growth_met_or_exceeded_demand_growth",
      },
      ei: {
        elect: 9100, coal_gen: 5500, gas_gen: 300, nuclear_gen: 450, ren_gen: 2850,
        wind: 1000, solar: 900, hydro: 900, coal_prod_mt: 4700, coal_tes_ej: 90,
        tes_ej: 300, co2_mtco2: 30000, pop: 1420,
      },
      coal_share: 60.4, ei_available: true, zero_generation: false, ci_precision_limited: false,
    },
    {
      iso3: "DEU", name: "Germany", continent: "Europe", year: 2024,
      ember: {
        demand: 480, generation: 475, clean: 280, fossil: 195, renewable: 200,
        wind_solar: 140, clean_share: 58.9, net_imports: null, ci: 180, emissions: 90,
        demand_change: -5, clean_change: 10, fossil_change: -15, has_previous_year: 1,
        growth_status: "demand_not_growing",
      },
      ei: {
        elect: 478, coal_gen: 80, gas_gen: 140, nuclear_gen: 0, ren_gen: 240,
        wind: 120, solar: 80, hydro: 40, coal_prod_mt: null, coal_tes_ej: null,
        tes_ej: 12, co2_mtco2: 600, pop: 84,
      },
      coal_share: 16.7, ei_available: true, zero_generation: false, ci_precision_limited: false,
    },
  ],
};

export const US_STATE: UsStateYearFile = {
  grain: "state x year x base-sector",
  sectors: {
    1: "Electric Utility",
    2: "IPP Non-CHP",
    3: "IPP CHP",
    8: "Commercial and Institutional",
    9: "Coke Plants",
    10: "Other Industrial",
  },
  n: 7,
  records: [
    { state: "TX", state_name: "Texas", year: 2023, sector: 1, sector_name: "Electric Utility", consumption: 30e6, receipts: 31e6, stocks: 9e6, price: 80, heat_btu_lb: 19900, heat_unit: "Btu/lb", sulfur_pct: 1.4, ash_pct: 9.9 },
    { state: "TX", state_name: "Texas", year: 2024, sector: 1, sector_name: "Electric Utility", consumption: 40e6, receipts: 41e6, stocks: 10e6, price: 90, heat_btu_lb: 20000, heat_unit: "Btu/lb", sulfur_pct: 1.5, ash_pct: 10 },
    { state: "TX", state_name: "Texas", year: 2024, sector: 2, sector_name: "IPP Non-CHP", consumption: 5e6, receipts: 5e6, stocks: 1e6, price: 95, heat_btu_lb: 20100, heat_unit: "Btu/lb", sulfur_pct: 1.6, ash_pct: 10.1 },
    // Non-power sector so "all base sectors" (48e6) != "electric power"
    // (1+2+3 = 45e6) - lets the panel test verify sector-scoped summation.
    { state: "TX", state_name: "Texas", year: 2024, sector: 8, sector_name: "Commercial and Institutional", consumption: 3e6, receipts: 3.2e6, stocks: 0.5e6, price: 100, heat_btu_lb: null, heat_unit: null, sulfur_pct: null, ash_pct: null },
    { state: "TX", state_name: "Texas", year: 2025, sector: 1, sector_name: "Electric Utility", consumption: 42e6, receipts: 42.5e6, stocks: 10.5e6, price: 97, heat_btu_lb: 20050, heat_unit: "Btu/lb", sulfur_pct: 1.5, ash_pct: 10 },
    { state: "OH", state_name: "Ohio", year: 2024, sector: 1, sector_name: "Electric Utility", consumption: 20e6, receipts: 20.5e6, stocks: 6e6, price: 85, heat_btu_lb: 15000, heat_unit: "GJ/tonne scale (assumed)", sulfur_pct: 1.1, ash_pct: 12 },
    { state: "AK", state_name: "Alaska", year: 2024, sector: 1, sector_name: "Electric Utility", consumption: null, receipts: null, stocks: null, price: null, heat_btu_lb: null, heat_unit: null, sulfur_pct: null, ash_pct: null },
  ],
};

export const US_AGGREGATES: UsAggregatesFile = {
  grain: "location x year x aggregate-sector",
  n: 4,
  records: [
    { location: "US", location_name: "United States", location_type: "us_total", year: 2023, sector: 98, sector_name: "Electric Power", consumption: 120e6, receipts: 121e6, price: 82 },
    { location: "US", location_name: "United States", location_type: "us_total", year: 2024, sector: 98, sector_name: "Electric Power", consumption: 130e6, receipts: 131e6, price: 92 },
    { location: "US", location_name: "United States", location_type: "us_total", year: 2025, sector: 98, sector_name: "Electric Power", consumption: 145e6, receipts: 146e6, price: 95 },
    { location: "90", location_name: "Pacific", location_type: "pacific_region", year: 2024, sector: 98, sector_name: "Electric Power", consumption: 25e6, receipts: 25.5e6, price: 90 },
  ],
};

export const GEO: GeoMapping = {
  numeric_to_alpha3: {
    "840": "USA",
    "156": "CHN",
    "276": "DEU",
  },
  name_to_alpha3: {},
};

/** Stub `fetch` to serve the fixture payloads. */
export function fetchStub(): (input: RequestInfo | URL) => Promise<Response> {
  return async (input) => {
    const url = String(input);
    let body: unknown;
    if (url.includes("country_year")) body = COUNTRY_YEAR;
    else if (url.includes("us_state_year")) body = US_STATE;
    else if (url.includes("us_aggregates")) body = US_AGGREGATES;
    else body = GEO;
    return {
      ok: true,
      status: 200,
      json: async () => body,
    } as Response;
  };
}
