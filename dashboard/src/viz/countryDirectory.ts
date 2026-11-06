import type { CountryYear } from "../data/types";

export type CountryDataFilter = "any" | "electricity" | "coal" | "production";
export function reported(v: unknown): v is number { return typeof v === "number" && Number.isFinite(v); }

export function hasCountryData(r: CountryYear, source: CountryDataFilter): boolean {
  if (source === "electricity") return reported(r.ember.generation);
  if (source === "coal") return reported(r.ei.coal_gen);
  if (source === "production") return reported(r.ei.coal_prod_mt);
  return reported(r.ember.generation) || r.ei_available;
}

/** Compress consecutive years only; never conceal a gap. */
export function yearRanges(years: number[]): string {
  const sorted = [...new Set(years)].sort((a, b) => a - b);
  const ranges: string[] = [];
  for (let i = 0; i < sorted.length; i++) {
    const start = sorted[i];
    while (i + 1 < sorted.length && sorted[i + 1] === sorted[i] + 1) i++;
    ranges.push(start === sorted[i] ? String(start) : `${start}–${sorted[i]}`);
  }
  return ranges.join(", ");
}

function csvCell(v: unknown): string {
  if (v == null) return "";
  const s = String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

/** Export loaded observations exactly, retaining zeros and blank missing cells. */
export function countryCsv(records: CountryYear[]): string {
  const rows = [...records].sort((a, b) => a.year - b.year).map(r => ({
    iso3: r.iso3, country: r.name, year: r.year,
    ember_available: r.ember_available ?? reported(r.ember.generation), ei_available: r.ei_available,
    ...Object.fromEntries(Object.entries(r.ember).map(([k, v]) => [`ember.${k}`, v])),
    ...Object.fromEntries(Object.entries(r.ei).map(([k, v]) => [`ei.${k}`, v])),
    coal_share_pct: r.coal_share,
  }));
  if (!rows.length) return "";
  const headers = Object.keys(rows[0]);
  return [headers.join(","), ...rows.map(r => headers.map(h => csvCell((r as Record<string, unknown>)[h])).join(","))].join("\n") + "\n";
}

export function downloadCountry(records: CountryYear[], iso: string) {
  const url = URL.createObjectURL(new Blob([countryCsv(records)], { type: "text/csv;charset=utf-8" }));
  const a = document.createElement("a");
  a.href = url; a.download = `${iso}_country_data.csv`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
