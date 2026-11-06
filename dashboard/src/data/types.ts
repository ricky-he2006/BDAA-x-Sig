/** Types mirroring the JSON exports in dashboard/public/data/. */

export interface EmberBlock {
  demand: number | null;
  generation: number | null;
  clean: number | null;
  fossil: number | null;
  renewable: number | null;
  wind_solar: number | null;
  clean_share: number | null;
  net_imports: number | null;
  ci: number | null;
  emissions: number | null;
  demand_change: number | null;
  clean_change: number | null;
  fossil_change: number | null;
  has_previous_year: number;
  growth_status: string | null;
}

export interface EiBlock {
  elect: number | null;
  coal_gen: number | null;
  gas_gen: number | null;
  nuclear_gen: number | null;
  ren_gen: number | null;
  wind: number | null;
  solar: number | null;
  hydro: number | null;
  coal_prod_mt: number | null;
  coal_tes_ej: number | null;
  tes_ej: number | null;
  co2_mtco2: number | null;
  pop: number | null;
}

export interface CountryYear {
  iso3: string;
  name: string;
  continent: string;
  year: number;
  ember: EmberBlock;
  ei: EiBlock;
  coal_share: number | null;
  ei_available: boolean;
  ember_available?: boolean;
  zero_generation: boolean;
  ci_precision_limited: boolean;
}

export interface CountryYearFile {
  grain: string;
  n: number;
  records: CountryYear[];
  ei_world?: EiWorldYear[];
  coverage?: CoverageYear[];
  sources?: SourceFile[];
}

export interface EiWorldYear {
  year: number;
  coal_generation_twh: number;
  total_generation_twh: number;
  coal_production_mt: number;
  coal_tes_ej: number;
  coal_share_pct: number;
}
export interface CoverageYear {
  year: number;
  ember_countries: number;
  ei_countries: number;
  ei_coal_countries: number;
}
export interface SourceFile { file: string; sha256: string; url: string }

export interface UsStateYear {
  state: string;
  state_name: string;
  year: number;
  sector: number;
  sector_name: string;
  consumption: number | null;
  receipts: number | null;
  stocks: number | null;
  price: number | null;
  heat_btu_lb: number | null;
  heat_unit: string | null;
  sulfur_pct: number | null;
  ash_pct: number | null;
}

export interface UsStateYearFile {
  grain: string;
  sectors: Record<number, string>;
  n: number;
  records: UsStateYear[];
}

export interface UsAggregate {
  location: string;
  location_name: string;
  location_type: string;
  year: number;
  sector: number;
  sector_name: string;
  consumption: number | null;
  receipts: number | null;
  price: number | null;
}

export interface UsAggregatesFile {
  grain: string;
  n: number;
  records: UsAggregate[];
}

export type LayerKey =
  | "clean_gen"
  | "clean_share"
  | "renewable"
  | "demand"
  | "coal_gen"
  | "coal_share"
  | "coal_prod"
  | "coal_tes"
  | "ci";

export type ViewKey = "world" | "us" | "research" | "data";

// Plain number[] (not `as const`): it feeds echarts' mutable xAxis.data and
// YEARS.indexOf(year) with a `number`, both of which a readonly literal tuple
// would reject. It is only ever read as a list, never narrowed to a literal.
export const YEARS: number[] = [2020, 2021, 2022, 2023, 2024, 2025];

export const LAYERS: Record<
  LayerKey,
  { label: string; unit: string; source: string; sequential: "blue" | "orange" | "red" }
> = {
  clean_gen: { label: "Clean electricity generation", unit: "TWh", source: "Ember", sequential: "blue" },
  clean_share: { label: "Clean electricity share", unit: "%", source: "Ember", sequential: "blue" },
  renewable: { label: "Renewable generation", unit: "TWh", source: "Ember", sequential: "blue" },
  demand: { label: "Electricity demand", unit: "TWh", source: "Ember", sequential: "blue" },
  coal_gen: { label: "Coal-fired generation", unit: "TWh", source: "Energy Institute", sequential: "red" },
  coal_share: { label: "Coal share of generation", unit: "%", source: "Energy Institute", sequential: "red" },
  coal_prod: { label: "Coal production", unit: "Mt", source: "Energy Institute", sequential: "red" },
  coal_tes: { label: "Coal energy supply (TES)", unit: "EJ", source: "Energy Institute", sequential: "red" },
  ci: { label: "Carbon intensity", unit: "gCO2e/kWh", source: "Ember", sequential: "blue" },
};

/** The coal and clean presentation metrics; raw source fields remain available for audit. */
export const PRESENTATION_LAYERS: LayerKey[] = ["clean_share", "clean_gen", "coal_share", "coal_gen", "coal_prod", "coal_tes"];
