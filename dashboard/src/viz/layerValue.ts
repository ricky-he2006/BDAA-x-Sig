/**
 * Map a selected layer to a numeric value for a country-year, and to the
 * coal-change outline metric. All values are null-preserving: a null means
 * "not reported" and is rendered as no-fill (never as zero).
 */
import type { CountryYear, LayerKey } from "../data/types";
import type { DataBundle } from "../data/loader";
import { prevYear } from "../state/AppState";

export function layerValue(layer: LayerKey, cy: CountryYear | undefined): number | null {
  if (!cy) return null;
  switch (layer) {
    case "clean_gen":
      return cy.ember.clean;
    case "clean_share":
      return cy.ember.clean_share;
    case "renewable":
      return cy.ember.renewable;
    case "demand":
      return cy.ember.demand;
    case "coal_gen":
      return cy.ei.coal_gen;
    case "coal_share":
      return cy.coal_share;
    case "coal_prod":
      return cy.ei.coal_prod_mt;
    case "coal_tes":
      return cy.ei.coal_tes_ej;
    case "ci":
      return cy.ember.ci;
  }
}

/**
 * Coal-fired generation change vs previous year (TWh). Requires both years to
 * be present in EI; otherwise null (never assume zero).
 */
export function coalChangeTWh(
  bundle: DataBundle,
  iso3: string,
  year: number,
): number | null {
  const m = bundle.countryByIso.get(iso3);
  if (!m) return null;
  const cy = m.get(year);
  const py = prevYear(year);
  if (!cy || py == null) return null;
  const pcy = m.get(py);
  if (!pcy || cy.ei.coal_gen == null || pcy.ei.coal_gen == null) return null;
  return cy.ei.coal_gen - pcy.ei.coal_gen;
}

/** Symmetric bound for the diverging coal-change scale: max |delta| over the year. */
export function coalChangeBound(
  bundle: DataBundle,
  iso3s: Iterable<string>,
  year: number,
): number {
  let max = 0;
  for (const iso of iso3s) {
    const d = coalChangeTWh(bundle, iso, year);
    if (d != null && Math.abs(d) > max) max = Math.abs(d);
  }
  return max;
}

/** [min, max] of a layer over the given iso3s for a year (nulls excluded). */
export function layerDomain(
  bundle: DataBundle,
  layer: LayerKey,
  iso3s: Iterable<string>,
  year: number,
): [number, number] | null {
  let min = Infinity;
  let max = -Infinity;
  for (const iso of iso3s) {
    const v = layerValue(layer, bundle.countryByIso.get(iso)?.get(year));
    if (v == null) continue;
    if (v < min) min = v;
    if (v > max) max = v;
  }
  if (!Number.isFinite(min)) return null;
  return [min, max];
}

/** True if the value would render at a ramp extreme (for clamped-legend notes). */
export function isClamped(v: number, [min, max]: [number, number]): boolean {
  return v <= min || v >= max;
}
