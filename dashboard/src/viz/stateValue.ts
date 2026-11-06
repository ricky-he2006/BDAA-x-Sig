/**
 * US state coal consumption by selected sector, from the processed
 * state x year x base-sector table. Base sectors only (1,2,3,8,9,10) are ever
 * summed — the EIA aggregate rows 94 (=2+3) and 98 (=1+2+3) are never added to
 * them, so there is no double counting.
 */
import type { DataBundle } from "../data/loader";
import type { UsStateYear } from "../data/types";
import type { UsSectorKey } from "../state/AppState";
import { FIPS_TO_STATE } from "../data/geo";

const POWER = [1, 2, 3];

export function sectorsFor(key: UsSectorKey): number[] {
  if (key === "all") return [1, 2, 3, 8, 9, 10];
  if (key === "power") return POWER;
  return [key];
}

/** Sum of consumption across the selected sector(s) for a state-year. Null if no row. */
export function stateConsumption(
  rows: UsStateYear[] | undefined,
  sector: UsSectorKey,
): number | null {
  if (!rows || rows.length === 0) return null;
  const want = new Set(sectorsFor(sector));
  let s = 0;
  let any = false;
  for (const r of rows) {
    if (!want.has(r.sector)) continue;
    if (r.consumption != null) {
      s += r.consumption;
      any = true;
    }
  }
  return any ? s : null;
}

/** Consumption for a state-year-sector selection, from the bundle. */
export function stateValue(
  bundle: DataBundle,
  state: string,
  year: number,
  sector: UsSectorKey,
): number | null {
  return stateConsumption(bundle.stateByCode.get(state)?.get(year), sector);
}

/** YoY consumption change for the same selection; null unless both years present. */
export function stateDelta(
  bundle: DataBundle,
  state: string,
  year: number,
  sector: UsSectorKey,
): number | null {
  const a = stateValue(bundle, state, year, sector);
  const b = stateValue(bundle, state, year - 1, sector);
  if (a == null || b == null) return null;
  return a - b;
}

/** Short-ton units: the EIA state data is reported in short tons. */
export const STATE_UNIT = "short tons";

/** The bundled 50-state + DC topology excludes Puerto Rico. */
export const MAPPED_STATES = Object.values(FIPS_TO_STATE).filter(code => code !== "PR");

/** The map and legend must use the same sector, geographic set and units. */
export function stateScaleStats(bundle: DataBundle, year: number, sector: UsSectorKey) {
  const values = MAPPED_STATES.map(st => stateValue(bundle, st, year, sector)).filter((v): v is number => v != null);
  const deltas = MAPPED_STATES.map(st => stateDelta(bundle, st, year, sector)).filter((v): v is number => v != null);
  return {
    domain: values.length ? [Math.min(...values), Math.max(...values)] as [number, number] : null,
    bound: deltas.length ? Math.max(...deltas.map(Math.abs)) : 0,
    reported: values.length,
  };
}
