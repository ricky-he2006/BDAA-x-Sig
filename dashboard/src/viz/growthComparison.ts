import type { CountryYear } from "../data/types";
import type { DataBundle } from "../data/loader";
import { percentChange } from "./researchMetrics";

export interface GrowthYear { year: number; clean: number; demand: number; coal: number }
export interface GrowthChange {
  year: number; clean: number; demand: number; coal: number;
  coalPct: number | null; coveredPct: number | null;
}
const reported = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);

/** Require all three plotted measures in every year, so membership never drives a trend. */
export function matchedGrowthCountries(data: Pick<DataBundle, "countryByIso">, years: number[]) {
  return [...data.countryByIso.entries()].filter(([, records]) => years.every(year => {
    const r = records.get(year);
    return r != null && r.ember_available !== false &&
      [r.ember.clean, r.ember.demand, r.ei.coal_gen].every(reported);
  }));
}

export function growthTotals(countries: [string, Map<number, CountryYear>][], years: number[]): GrowthYear[] {
  if (!countries.length) return [];
  return years.map(year => ({ year,
    clean: countries.reduce((sum, [, records]) => sum + records.get(year)!.ember.clean!, 0),
    demand: countries.reduce((sum, [, records]) => sum + records.get(year)!.ember.demand!, 0),
    coal: countries.reduce((sum, [, records]) => sum + records.get(year)!.ei.coal_gen!, 0),
  }));
}

export function growthChanges(totals: GrowthYear[]): GrowthChange[] {
  return totals.slice(1).flatMap((row, index) => {
    const previous = totals[index];
    if (row.year !== previous.year + 1) return [];
    const demand = row.demand - previous.demand, clean = row.clean - previous.clean;
    return [{ year: row.year, clean, demand, coal: row.coal - previous.coal,
      coalPct: percentChange(previous.coal, row.coal), coveredPct: demand > 0 ? clean / demand * 100 : null }];
  });
}
