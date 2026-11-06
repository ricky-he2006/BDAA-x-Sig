import { describe, expect, it } from "vitest";
import { COUNTRY_YEAR } from "../test/fixtures";
import { countryAnalysis, peerAnalysis } from "./countryAnalysis";
import type { CountryYear } from "../data/types";
const base = COUNTRY_YEAR.records.find(r => r.iso3 === "USA")!;
function row(year: number, ember: Partial<CountryYear["ember"]> = {}, ei: Partial<CountryYear["ei"]> = {}): CountryYear {
  return { ...base, year, ember: { ...base.ember, ...ember }, ei: { ...base.ei, ...ei } };
}
const records = (...rows: CountryYear[]) => new Map(rows.map(r => [r.year, r]));
describe("country chart analysis", () => {
  it("distinguishes rising share from falling output", () => {
    const data = records(row(2020, { clean_share: 40, clean: 100 }), row(2024, { clean_share: 50, clean: 90 }));
    expect(countryAnalysis(data, "Testland", "share")).toContain("A higher clean share here does not mean more clean electricity");
    expect(countryAnalysis(data, "Testland", "share")).toContain("10 percentage points");
  });
  it("uses common years rather than mismatched metric endpoints", () => {
    const data = records(row(2020, { clean: 10, fossil: 20, demand: 30 }), row(2024, { clean: 15, fossil: 25, demand: 40 }), row(2025, { clean: 20, fossil: null, demand: 45 }));
    const text = countryAnalysis(data, "Testland", "mix");
    expect(text).toContain("2020–2024");
    expect(text).toContain("Clean growth coexisted with fossil growth");
  });
  it("does not bridge missing annual demand observations", () => {
    expect(countryAnalysis(records(row(2020), row(2024)), "Testland", "additions")).toContain("not enough overlapping");
  });
  it("explains lower intensity alongside higher total emissions", () => {
    const data = records(row(2020, { ci: 400, emissions: 100 }), row(2024, { ci: 300, emissions: 110 }));
    expect(countryAnalysis(data, "Testland", "emissions")).toContain("cleaner per kWh, but total power emissions still increased");
  });
  it("identifies a switch from exports to imports and excludes zero demand", () => {
    const data = records(row(2020, { net_imports: -10, demand: 100 }), row(2024, { net_imports: 10, demand: 100 }), row(2025, { net_imports: 20, demand: 0 }));
    expect(countryAnalysis(data, "Testland", "trade")).toContain("shifted from net exports to net imports");
    expect(countryAnalysis(data, "Testland", "trade")).toContain("in 2024");
  });
  it("retains zero coal without inventing percentage growth", () => {
    const data = records(row(2020, {}, { coal_gen: 0 }), row(2024, {}, { coal_gen: 0 }));
    expect(countryAnalysis(data, "Testland", "coal")).toContain("was unchanged from 0 to 0 TWh");
  });
  it("limits a peer comparison to shared reported years", () => {
    const a = records(row(2020, { clean_share: 0 }), row(2024, { clean_share: 50 }));
    const b = records(row(2020, { clean_share: 20 }));
    const text = peerAnalysis(a, b, "A", "B");
    expect(text).toContain("In 2020");
    expect(text).toContain("Only one common year");
  });
});
