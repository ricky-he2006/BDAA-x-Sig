import type {
  CountryYear, CountryYearFile, UsStateYear, UsStateYearFile,
  UsAggregatesFile,
  EiWorldYear, CoverageYear, SourceFile,
} from "./types";
import type { GeoMapping } from "./geo";
import { GeoMatcher } from "./geo";

export interface DataBundle {
  countryByIso: Map<string, Map<number, CountryYear>>;
  countryNames: Map<string, string>;
  /** world-atlas feature (id, name) -> iso3 or null. */
  geo: GeoMatcher;
  stateByCode: Map<string, Map<number, UsStateYear[]>>;
  stateNames: Map<string, string>;
  sectors: Record<number, string>;
  usAggregates: UsAggregatesFile["records"];
  eiWorld: EiWorldYear[];
  coverage: CoverageYear[];
  sources: SourceFile[];
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`failed to load ${path}: ${res.status}`);
  return (await res.json()) as T;
}

export async function loadData(): Promise<DataBundle> {
  const [cy, us, agg, geoRaw] = await Promise.all([
    fetchJson<CountryYearFile>("/data/country_year.json"),
    fetchJson<UsStateYearFile>("/data/us_state_year.json"),
    fetchJson<UsAggregatesFile>("/data/us_aggregates.json"),
    fetchJson<GeoMapping>("/data/geo.json"),
  ]);
  return buildBundle(cy, us, agg, geoRaw);
}

/**
 * Pure bundle construction (no I/O) - the exact mapping the app runs at
 * startup. Exported so tests can exercise it against the real generated
 * JSON files.
 */
export function buildBundle(
  cy: CountryYearFile,
  us: UsStateYearFile,
  agg: UsAggregatesFile,
  geoRaw: GeoMapping,
): DataBundle {
  // Fail visibly on stale counts or duplicate keys rather than silently
  // overwriting country/state observations in Maps.
  for (const [label, file, key] of [
    ["country", cy, (r: CountryYear) => `${r.iso3}:${r.year}`],
    ["state", us, (r: UsStateYear) => `${r.state}:${r.year}:${r.sector}`],
    ["aggregate", agg, (r: UsAggregatesFile["records"][number]) => `${r.location}:${r.year}:${r.sector}`],
  ] as const) {
    if (file.n !== file.records.length) throw new Error(`${label} record count does not match its manifest`);
    const keys = new Set<string>();
    for (const r of file.records) {
      const id = (key as (r: typeof file.records[number]) => string)(r);
      if (keys.has(id)) throw new Error(`Duplicate ${label} observation: ${id}`);
      keys.add(id);
    }
  }
  const countryByIso = new Map<string, Map<number, CountryYear>>();
  const countryNames = new Map<string, string>();
  for (const r of cy.records) {
    let m = countryByIso.get(r.iso3);
    if (!m) {
      m = new Map();
      countryByIso.set(r.iso3, m);
    }
    m.set(r.year, r);
    countryNames.set(r.iso3, r.name);
  }

  const stateByCode = new Map<string, Map<number, UsStateYear[]>>();
  const stateNames = new Map<string, string>();
  for (const r of us.records) {
    if (![1, 2, 3, 8, 9, 10].includes(r.sector)) throw new Error(`Overlapping or unsupported state sector: ${r.sector}`);
    let m = stateByCode.get(r.state);
    if (!m) {
      m = new Map();
      stateByCode.set(r.state, m);
    }
    const arr = m.get(r.year) ?? [];
    arr.push(r);
    m.set(r.year, arr);
    stateNames.set(r.state, r.state_name);
  }

  return {
    countryByIso,
    countryNames,
    geo: new GeoMatcher(geoRaw),
    stateByCode,
    stateNames,
    sectors: us.sectors,
    usAggregates: agg.records,
    eiWorld: cy.ei_world ?? [],
    coverage: cy.coverage ?? [],
    sources: cy.sources ?? [],
  };
}

/** Sum of base-sector (non-overlapping) consumption for a state-year. */
export function stateConsumption(yearRows: UsStateYear[] | undefined): number | null {
  if (!yearRows || yearRows.length === 0) return null;
  let s = 0;
  let any = false;
  for (const r of yearRows) {
    if (r.consumption != null) {
      s += r.consumption;
      any = true;
    }
  }
  return any ? s : null;
}
