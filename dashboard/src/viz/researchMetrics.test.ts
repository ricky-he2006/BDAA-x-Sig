import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { buildBundle } from "../data/loader";
import { emberPanel, percentChange } from "./researchMetrics";

const load = (name: string) => JSON.parse(readFileSync(`public/data/${name}`, "utf-8"));
const bundle = buildBundle(load("country_year.json"), load("us_state_year.json"), load("us_aggregates.json"), load("geo.json"));

describe("dashboard evidence agrees with submitted analysis", () => {
  it("reproduces every main historical panel total from the shipped evidence CSV", () => {
    const csv = readFileSync("public/evidence/matched_2020_2024.csv", "utf-8").trim().split("\n");
    const headers = csv[0].split(",");
    const expected = csv.slice(1).map(line => Object.fromEntries(line.split(",").map((v, i) => [headers[i], Number(v)])));
    const actual = emberPanel(bundle, [2020, 2021, 2022, 2023, 2024]);
    for (let i = 0; i < actual.length; i++) {
      expect(actual[i].countries).toBe(expected[i].n_countries);
      expect(actual[i].clean).toBeCloseTo(expected[i].clean_generation_twh, 6);
      expect(actual[i].fossil).toBeCloseTo(expected[i].fossil_generation_twh, 6);
      expect(actual[i].demand).toBeCloseTo(expected[i].demand_twh, 6);
      expect(actual[i].generation).toBeCloseTo(expected[i].generation_twh, 6);
    }
    expect(percentChange(actual[0].clean, actual[4].clean)).toBeCloseTo(25.3875493476, 7);
  });
  it("keeps EI-only years out of the six-year Ember panel", () => {
    const idn = bundle.countryByIso.get("IDN")!.get(2025)!;
    expect(idn.ember_available).toBe(false);
    expect(idn.ember.demand).toBeNull();
    expect(idn.ei.coal_gen).toBeGreaterThan(0);
    expect(emberPanel(bundle, [2020, 2021, 2022, 2023, 2024, 2025]).map(r => r.countries)).toEqual([91, 91, 91, 91, 91, 91]);
  });
  it("does not treat zero or missing bases as percentage growth", () => {
    expect(percentChange(0, 10)).toBeNull();
    expect(percentChange(null, 10)).toBeNull();
    expect(percentChange(10, 0)).toBe(-100);
  });
});
