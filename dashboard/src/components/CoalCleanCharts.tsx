import type { EChartsOption } from "echarts";
import { axisStyle } from "./ChartCard";
import { CountryChart } from "./CountryChart";
import { entityColor } from "../viz/series";

export function CoalCleanChart({ title, years, clean, coal, dark, share = false, note }: {
  title: string; years: number[]; clean: (number | null)[]; coal: (number | null)[];
  dark: boolean; share?: boolean; note?: string;
}) {
  const option: EChartsOption = {
    tooltip: { trigger: "axis" }, legend: { show: true },
    xAxis: { type: "category", data: years, ...axisStyle(dark) },
    yAxis: { type: "value", min: 0, ...(share ? { max: 100 } : {}), name: share ? "%" : "TWh", ...axisStyle(dark) },
    series: ([['Clean energy', clean, 'clean'], ['Coal', coal, 'coal']] as const).map(([name, values, color]) => ({
      name, type: "line", data: [...values], connectNulls: false, symbolSize: 6,
      lineStyle: { width: 2.5, color: color === "coal" ? (dark ? "#e66767" : "#c53030") : entityColor(color, dark ? "dark" : "light") },
      itemStyle: { color: color === "coal" ? (dark ? "#e66767" : "#c53030") : entityColor(color, dark ? "dark" : "light") },
    })),
  };
  return <CountryChart title={title} option={option} note={note} />;
}

export function EnergyDefinition() {
  return <p className="note">Clean energy = renewables + nuclear. Coal and clean do not add up to 100% because other sources, including gas and oil, also generate electricity. Clean: Ember; coal: Energy Institute. Source totals can differ. Missing values stay blank.</p>;
}
