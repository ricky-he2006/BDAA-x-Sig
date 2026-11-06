import { describe, expect, it } from "vitest";
import { chartTakeaway } from "./chartTakeaway";

const describeValues = (data: (number | null)[]) => chartTakeaway({
  xAxis: { type: "category", data: [2020, 2021, 2022, 2023] },
  series: [{ name: "Coal generation", type: "line", data }],
});

describe("chart takeaways", () => {
  it("describes a decline and a recent reversal using actual observed years", () => {
    expect(describeValues([100, null, 60, 70])).toBe("Coal generation fell from 100 in 2020 to 70 in 2023 (30% lower). The latest reported interval moved in the opposite direction: up from 60 in 2022.");
  });
  it("preserves zeros without inventing percentage growth", () => {
    expect(describeValues([0, null, 10])).toBe("Coal generation rose from 0 in 2020 to 10 in 2022.");
  });
  it("does not infer trends from one observation or missing data", () => {
    expect(describeValues([null, 0])).toContain("one reported observation cannot establish a trend");
    expect(describeValues([null, null])).toBe("");
  });
  it("calls out an intermediate peak", () => {
    expect(describeValues([10, 30, 20, 15])).toContain("peaked at 30 in 2021");
  });
});
