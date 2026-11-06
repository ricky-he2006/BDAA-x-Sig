import { describe, expect, it } from "vitest";
import { GeoMatcher, FIPS_TO_STATE } from "./geo";

const GEO = {
  numeric_to_alpha3: {
    "840": "USA",
    "156": "CHN",
    "356": "IND",
    "276": "DEU",
    "532": "XKS",
  },
  name_to_alpha3: {
    "United States of America": "USA",
    "Czechia": "CZE",
    "Dem. Rep. of the Congo": "COD",
    "Congo (brazzaville)": "COG",
    "Iran (Islamic Republic of)": "IRN",
  },
};

describe("GeoMatcher", () => {
  const m = new GeoMatcher(GEO);

  it("matches numeric ids (with and without padding)", () => {
    expect(m.matchFeature("840", "United States of America")).toBe("USA");
    expect(m.matchFeature("840", "United States of America")).toBe("USA");
    expect(m.matchFeature("048", "Bermuda")).toBeNull();
    expect(m.matchFeature("156", "China")).toBe("CHN");
  });

  it("falls back to normalized names when the id is unknown", () => {
    expect(m.matchFeature("999", "Czechia")).toBe("CZE");
    expect(m.matchFeature(null, "Dem. Rep. of the Congo")).toBe("COD");
    // Natural-Earth disambiguation suffixes are stripped before matching.
    expect(m.matchFeature(null, "Congo (brazzaville)")).toBe("COG");
    expect(m.matchFeature(null, "Iran (Islamic Republic of)")).toBe("IRN");
  });

  it("returns null for unknown features (they stay uncolored, not faked)", () => {
    expect(m.matchFeature("999", "Nowhere")).toBeNull();
    expect(m.matchFeature(null, null)).toBeNull();
  });
});

describe("FIPS_TO_STATE", () => {
  it("covers all 50 states + DC + PR", () => {
    const expected = new Set([
      "AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA","KS",
      "KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC",
      "ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","PR",
    ]);
    expect(new Set(Object.values(FIPS_TO_STATE))).toEqual(expected);
    expect(Object.keys(FIPS_TO_STATE)).toHaveLength(52);
  });

  it("maps well-known FIPS codes", () => {
    expect(FIPS_TO_STATE["48"]).toBe("TX");
    expect(FIPS_TO_STATE["06"]).toBe("CA");
    expect(FIPS_TO_STATE["39"]).toBe("OH");
    expect(FIPS_TO_STATE["11"]).toBe("DC");
    expect(FIPS_TO_STATE["72"]).toBe("PR");
    expect(FIPS_TO_STATE["02"]).toBe("AK");
    expect(FIPS_TO_STATE["15"]).toBe("HI");
  });
});
