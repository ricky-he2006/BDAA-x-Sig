import { describe, expect, it } from "vitest";
import { fmt, fmtPct, fmtSigned, fmtSignedPct, NA } from "./format";

describe("format: missing values render as unavailable, never as zero", () => {
  it("null and undefined render as the em-dash", () => {
    expect(fmt(null)).toBe(NA);
    expect(fmt(undefined)).toBe(NA);
    expect(fmtPct(null)).toBe(NA);
    expect(fmtSigned(null)).toBe(NA);
    expect(fmtSignedPct(undefined)).toBe(NA);
  });

  it("NaN renders as the em-dash (defense in depth)", () => {
    expect(fmt(Number.NaN)).toBe(NA);
    expect(fmtPct(Number.NaN)).toBe(NA);
  });

  it("a real zero renders as zero, not as unavailable", () => {
    expect(fmt(0)).toBe("0");
    expect(fmtPct(0)).toBe("0%");
    expect(fmtSigned(0)).toBe("0");
  });

  it("labels relative growth as percent, distinct from percentage-point share changes", () => {
    expect(fmtSignedPct(11.289)).toBe("+11.3%");
    expect(fmtSignedPct(-14.356)).toBe("−14.4%");
    expect(fmtSignedPct(0)).toBe("0%");
    expect(fmtSignedPct(Infinity)).toBe(NA);
    expect(fmt(-Infinity)).toBe(NA);
  });
});
