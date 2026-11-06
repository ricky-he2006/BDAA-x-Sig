import type { CountryYear } from "../data/types";
import type { DataBundle } from "../data/loader";

export interface PanelTotal {
  year: number; countries: number; clean: number; fossil: number;
  generation: number; demand: number; windSolar: number;
}

/** Consistent source and membership, requiring all displayed metrics. */
export function emberPanel(data: DataBundle, years: number[]): PanelTotal[] {
  const picks = (r: CountryYear) => [r.ember.clean, r.ember.fossil, r.ember.generation, r.ember.demand, r.ember.wind_solar];
  const matched = [...data.countryByIso.values()].filter(m => years.every(y => {
    const r = m.get(y);
    return r != null && r.ember_available !== false && picks(r).every(v => v != null);
  }));
  return years.map(year => ({
    year, countries: matched.length,
    clean: matched.reduce((s, m) => s + m.get(year)!.ember.clean!, 0),
    fossil: matched.reduce((s, m) => s + m.get(year)!.ember.fossil!, 0),
    generation: matched.reduce((s, m) => s + m.get(year)!.ember.generation!, 0),
    demand: matched.reduce((s, m) => s + m.get(year)!.ember.demand!, 0),
    windSolar: matched.reduce((s, m) => s + m.get(year)!.ember.wind_solar!, 0),
  }));
}

export function percentChange(before: number | null | undefined, after: number | null | undefined): number | null {
  return before == null || after == null || before <= 0 ? null : (after / before - 1) * 100;
}
