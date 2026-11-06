import { readFileSync } from "node:fs";
import { beforeAll, afterAll, describe, expect, it, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { AppProvider } from "../state/AppState";
import { GrowthSection } from "./GrowthSection";
import { growthChanges, growthTotals, matchedGrowthCountries } from "../viz/growthComparison";
import type { CountryYear } from "../data/types";

const records: CountryYear[] = JSON.parse(readFileSync("public/data/country_year.json", "utf-8")).records;
const countryByIso = new Map<string, Map<number, CountryYear>>();
for (const r of records) {
  if (!countryByIso.has(r.iso3)) countryByIso.set(r.iso3, new Map());
  countryByIso.get(r.iso3)!.set(r.year, r);
}
const years = [2020, 2021, 2022, 2023, 2024, 2025];
beforeAll(() => vi.stubGlobal("fetch", async (input: RequestInfo | URL) => ({
  ok: true, json: async () => JSON.parse(readFileSync(`public${String(input)}`, "utf-8")),
})));
afterAll(() => vi.unstubAllGlobals());

describe("clean growth and demand", () => {
  it("checks the 2025 story against the shipped observations", () => {
    const matched = matchedGrowthCountries({countryByIso}, years);
    expect(matched).toHaveLength(27);
    const latest = growthChanges(growthTotals(matched, years)).at(-1)!;
    expect(latest.clean).toBeCloseTo(816.04, 2);
    expect(latest.demand).toBeCloseTo(725.14, 2);
    expect(latest.coal).toBeCloseTo(-45.94, 2);
    const us = growthChanges(growthTotals(matched.filter(([iso]) => iso === "USA"), years)).at(-1)!;
    expect(us.clean).toBeCloseTo(105.09, 2);
    expect(us.demand).toBeCloseTo(130.98, 2);
    expect(us.coalPct).toBeCloseTo(12.7974, 3);
  });
  it("excludes missing histories, preserves zero, and does not invent empty totals", () => {
    const template = records[0];
    const zero = new Map<number, CountryYear>(years.map(year => [year, {...template, year, ember: {...template.ember, clean: 0, demand: 0}, ei: {...template.ei, coal_gen: 0}}]));
    const missing = new Map(zero);
    missing.set(2025, {...missing.get(2025)!, ember: {...template.ember, clean: null}});
    const matches = matchedGrowthCountries({countryByIso: new Map([["ZERO", zero], ["MISSING", missing]])}, years);
    expect(matches.map(([iso]) => iso)).toEqual(["ZERO"]);
    expect(growthChanges(growthTotals(matches, years))[0].coveredPct).toBeNull();
    expect(growthTotals([], years)).toEqual([]);
    expect(growthChanges([{year: 2020, clean: 1, demand: 1, coal: 1}, {year: 2025, clean: 2, demand: 2, coal: 2}])).toEqual([]);
  });
  it("shows the sample-versus-U.S. comparison with scope and source links", async () => {
    render(<AppProvider><GrowthSection /></AppProvider>);
    const table = await screen.findByRole("table", {name: "2025 growth comparison"});
    const us = within(table).getByRole("row", {name: /United States/});
    expect(us).toHaveTextContent("+105.1");
    expect(us).toHaveTextContent("80.2%");
    expect(us).toHaveTextContent("+12.8%");
    expect(screen.getByText(/it was a major exception, not the only country/)).toBeInTheDocument();
    expect(screen.getByRole("link", {name: /Ember’s Global/})).toHaveAttribute("href", expect.stringContaining("global-electricity-review-2026"));
  });
});
