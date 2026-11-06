/**
 * Geo matching: world-atlas / us-atlas features -> dataset keys.
 *
 * The numeric ISO 3166-1 code -> alpha-3 table is generated from the Energy
 * Institute dataset (which carries ISO3166_numeric for every entity) by
 * `dashboard/scripts/export_dashboard_data.py`, plus a small verified extras
 * table for entities absent from EI. Natural-Earth feature *names* are a
 * fallback only; the primary key is the feature id.
 */

export interface GeoMapping {
  /** ISO 3166-1 numeric code (string, 3-digit) -> alpha-3. */
  numeric_to_alpha3: Record<string, string>;
  /** Normalized-alias feature name -> alpha-3 (fallback for features w/o id). */
  name_to_alpha3: Record<string, string>;
}

const normalize = (s: string): string =>
  s
    .toLowerCase()
    .replace(/\[.*?\]/g, " ") // "[Malvinas (Falkland) Is.]"
    .replace(/\(.*?\)/g, " ") // "(the)", "(Islamic Republic of)", "(brazzaville)"
    .replace(/[^a-z]+/g, " ")
    .trim()
    .replace(/\s+/g, " ");

export class GeoMatcher {
  private numeric: Record<string, string>;
  private name: Map<string, string>;

  constructor(private geo: GeoMapping) {
    this.numeric = geo.numeric_to_alpha3;
    this.name = new Map(Object.entries(geo.name_to_alpha3).map(([k, v]) => [normalize(k), v]));
  }

  /** Match a world-atlas feature; returns iso3 or null (feature stays uncolored). */
  matchFeature(
    id: string | number | null | undefined,
    name: string | null | undefined,
  ): string | null {
    if (id != null) {
      const s = String(id).padStart(3, "0");
      const byNum = this.numeric[s] ?? this.numeric[String(id)];
      if (byNum) return byNum;
    }
    if (name) {
      const byName = this.name.get(normalize(name));
      if (byName) return byName;
    }
    return null;
  }
}

/** FIPS state code (us-atlas feature id) -> EIA 2-letter state code. */
export const FIPS_TO_STATE: Record<string, string> = {
  "01": "AL",
  "02": "AK",
  "04": "AZ",
  "05": "AR",
  "06": "CA",
  "08": "CO",
  "09": "CT",
  "10": "DE",
  "11": "DC",
  "12": "FL",
  "13": "GA",
  "15": "HI",
  "16": "ID",
  "17": "IL",
  "18": "IN",
  "19": "IA",
  "20": "KS",
  "21": "KY",
  "22": "LA",
  "23": "ME",
  "24": "MD",
  "25": "MA",
  "26": "MI",
  "27": "MN",
  "28": "MS",
  "29": "MO",
  "30": "MT",
  "31": "NE",
  "32": "NV",
  "33": "NH",
  "34": "NJ",
  "35": "NM",
  "36": "NY",
  "37": "NC",
  "38": "ND",
  "39": "OH",
  "40": "OK",
  "41": "OR",
  "42": "PA",
  "44": "RI",
  "45": "SC",
  "46": "SD",
  "47": "TN",
  "48": "TX",
  "49": "UT",
  "50": "VT",
  "51": "VA",
  "53": "WA",
  "54": "WV",
  "55": "WI",
  "56": "WY",
  "72": "PR",
};
