import { describe, expect, it } from "vitest";
import { sectorsFor, stateConsumption, stateValue, stateDelta } from "./stateValue";
import type { DataBundle } from "../data/loader";
import type { UsStateYear } from "../data/types";

function rows(pairs: [number, number | null][]): UsStateYear[] {
  return pairs.map(([sector, consumption]) => ({
    state: "TX", state_name: "Texas", year: 2024, sector,
    sector_name: "x", consumption, receipts: null, stocks: null, price: null,
    heat_btu_lb: null, heat_unit: null, sulfur_pct: null, ash_pct: null,
  }));
}

describe("sectorsFor", () => {
  it("never includes the aggregate sectors 94/98 (double-count guard)", () => {
    expect(sectorsFor("all")).toEqual([1, 2, 3, 8, 9, 10]);
    expect(sectorsFor("power")).toEqual([1, 2, 3]);
    expect(sectorsFor(8)).toEqual([8]);
    for (const key of ["all", "power", 1, 2, 3, 8, 9, 10] as const) {
      expect(sectorsFor(key)).not.toContain(94);
      expect(sectorsFor(key)).not.toContain(98);
    }
  });
});

describe("stateConsumption", () => {
  it("sums only the selected sector(s)", () => {
    const r = rows([[1, 10], [2, 5], [8, 7], [10, 3]]);
    expect(stateConsumption(r, "all")).toBe(25);
    expect(stateConsumption(r, "power")).toBe(15);
    expect(stateConsumption(r, 8)).toBe(7);
  });

  it("returns null when the selected sector has no reported value", () => {
    const r = rows([[1, null], [8, 7]]);
    expect(stateConsumption(r, "power")).toBeNull();
    expect(stateConsumption(r, "all")).toBe(7);
  });
});

function fakeBundle(tx: [number, number | null][][]): DataBundle {
  const years = new Map<number, UsStateYear[]>();
  tx.forEach((pairs, i) => years.set(2020 + i, rows(pairs)));
  const stateByCode = new Map<string, Map<number, UsStateYear[]>>();
  stateByCode.set("TX", years);
  return {
    countryByIso: new Map(),
    countryNames: new Map(),
    geo: {} as DataBundle["geo"],
    stateByCode,
    stateNames: new Map([["TX", "Texas"]]),
    sectors: {},
    usAggregates: [], eiWorld: [], coverage: [], sources: [],
  };
}

describe("stateValue / stateDelta", () => {
  it("reads the right year and nulls missing years", () => {
    const b = fakeBundle([[[1, 100]], [[1, 130]]]);
    expect(stateValue(b, "TX", 2020, "all")).toBe(100);
    expect(stateValue(b, "TX", 2021, "all")).toBe(130);
    expect(stateValue(b, "TX", 2022, "all")).toBeNull();
  });

  it("computes YoY delta only when both years exist", () => {
    const b = fakeBundle([[[1, 100]], [[1, 130]]]);
    expect(stateDelta(b, "TX", 2021, "all")).toBe(30);
    expect(stateDelta(b, "TX", 2020, "all")).toBeNull(); // no 2019
    expect(stateDelta(b, "TX", 2022, "all")).toBeNull(); // missing 2022
  });
});
