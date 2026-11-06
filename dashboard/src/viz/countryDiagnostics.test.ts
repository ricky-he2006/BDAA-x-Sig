import { describe, expect, it } from "vitest";
import type { CountryYear } from "../data/types";
import { annualChanges, indexFrom2020 } from "./countryDiagnostics";

function record(year: number, clean: number | null): CountryYear {
  return { year, ember: { clean } } as CountryYear;
}
const pick = (r: CountryYear) => r.ember.clean;

describe("country diagnostics missing-data behavior", () => {
  it("does not bridge missing calendar years or metrics", () => {
    const rows = new Map([[2020, record(2020, 10)], [2022, record(2022, 30)],
      [2023, record(2023, null)], [2024, record(2024, 45)]]);
    expect(annualChanges(rows, [2020, 2021, 2022, 2023, 2024], pick)).toEqual([null, null, null, null, null]);
  });
  it("preserves true zero and negative year-on-year changes", () => {
    const rows = new Map([[2020, record(2020, 10)], [2021, record(2021, 10)], [2022, record(2022, 0)]]);
    expect(annualChanges(rows, [2020, 2021, 2022], pick)).toEqual([null, 0, -10]);
  });
  it("uses a fixed base and refuses a zero or absent base", () => {
    const rows = new Map([[2020, record(2020, 10)], [2022, record(2022, 15)]]);
    expect(indexFrom2020(rows, [2020, 2021, 2022], pick)).toEqual([100, null, 150]);
    expect(indexFrom2020(new Map([[2020, record(2020, 0)]]), [2020, 2021], pick)).toEqual([null, null]);
    expect(indexFrom2020(new Map(), [2020], pick)).toEqual([null]);
  });
});
