import type { DataBundle } from "../data/loader";
import { MAPPED_STATES, stateValue } from "./stateValue";

export function annualChange(current: number | null | undefined, previous: number | null | undefined) {
  return current == null || previous == null || previous <= 0 ? null : (current / previous - 1) * 100;
}

/** Reported power-sector base rows only; never add national aggregate sector 98. */
export function coalDemandMarkets(data: DataBundle, year: number) {
  return MAPPED_STATES.flatMap(code => {
    const value = stateValue(data, code, year, "power");
    if (value == null) return [];
    const previous = stateValue(data, code, year - 1, "power");
    return [{ code, name: data.stateNames.get(code) ?? code, value, previous, growth: annualChange(value, previous) }];
  }).sort((a, b) => b.value - a.value || a.name.localeCompare(b.name));
}
