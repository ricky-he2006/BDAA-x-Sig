import type { CountryYear } from "../data/types";

/** Never bridge an absent year or turn a missing metric into zero. */
export function annualChanges(
  records: Map<number, CountryYear>, years: number[],
  pick: (r: CountryYear) => number | null,
): (number | null)[] {
  return years.map((year) => {
    const now = records.get(year);
    const before = records.get(year - 1);
    if (!now || !before) return null;
    const a = pick(now), b = pick(before);
    return a == null || b == null ? null : a - b;
  });
}

/** A fixed 2020 base; an absent/zero base makes the whole index undefined. */
export function indexFrom2020(
  records: Map<number, CountryYear>, years: number[],
  pick: (r: CountryYear) => number | null,
): (number | null)[] {
  const baseRow = records.get(2020);
  const base = baseRow ? pick(baseRow) : null;
  return years.map((year) => {
    const row = records.get(year);
    const value = row ? pick(row) : null;
    return base == null || base <= 0 || value == null ? null : value / base * 100;
  });
}

export const COUNTRY_QUESTIONS: Record<string, string> = {
  USA: "Does the 2025 coal rebound persist? Compare coal with gas and the EIA state view; delivered prices do not measure producer margins.",
  CHN: "Does clean generation keep pace with demand? Compare absolute additions with coal output; a rising clean share can coexist with more coal.",
  IND: "Can clean additions meet additional demand? Compare TWh changes rather than percentage growth rates alone.",
  IDN: "How do coal production and domestic generation differ? Their divergence does not establish exports; missing 2025 electricity stays missing.",
  DEU: "Did coal fall alongside demand and clean output? Use the demand-change and electricity-trade charts before inferring clean substitution.",
  JPN: "Which fossil fuels declined as clean generation rose? Compare EI coal and gas; clean totals alone cannot identify the technology responsible.",
  AUS: "Does falling domestic coal generation coincide with falling production? Domestic electricity demand and export-producer exposure differ.",
  RUS: "Did additional demand come with fossil growth? Compare clean, coal and gas rather than applying a uniform global transition story.",
};
