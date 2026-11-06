import { describe, expect, it } from "vitest";
import { countryCsv, hasCountryData, yearRanges } from "./countryDirectory";
import { COUNTRY_YEAR } from "../test/fixtures";

describe("country directory coverage and downloads", () => {
  it("compresses consecutive years without concealing missing years", () => {
    expect(yearRanges([2025, 2020, 2021, 2023, 2025])).toBe("2020–2021, 2023, 2025");
    expect(yearRanges([])).toBe("");
  });
  it("includes reported zero output but excludes missing measures from filters", () => {
    const r = { ...COUNTRY_YEAR.records[0], ei: { ...COUNTRY_YEAR.records[0].ei, coal_gen: 0, coal_prod_mt: null } };
    expect(hasCountryData(r, "coal")).toBe(true);
    expect(hasCountryData(r, "production")).toBe(false);
  });
  it("exports sorted, correctly quoted observations with zero distinct from missing", () => {
    const r = COUNTRY_YEAR.records[0];
    const csv = countryCsv([{ ...r, name: 'Country, "quoted"', ei: { ...r.ei, coal_gen: 0, coal_prod_mt: null } }]);
    expect(csv).toContain('"Country, ""quoted"""');
    const header = csv.split("\n")[0].split(",");
    expect(header).toContain("ei.coal_gen");
    expect(header).toContain("ember_available");
    const ordinary = countryCsv([{ ...r, ei: { ...r.ei, coal_gen: 0, coal_prod_mt: null } }]).trim().split("\n");
    const h = ordinary[0].split(","), row = ordinary[1].split(",");
    expect(row[h.indexOf("ei.coal_gen")]).toBe("0");
    expect(row[h.indexOf("ei.coal_prod_mt")]).toBe("");
    expect(countryCsv([])).toBe("");
  });
});
