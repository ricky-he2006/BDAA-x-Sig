import type { EChartsOption } from "echarts";

const number = (value: number) => value.toLocaleString("en-US", { maximumFractionDigits: 2 });

/** Describe only plotted observations; gaps and zero baselines never imply growth. */
export function chartTakeaway(option: EChartsOption): string {
  const axis = Array.isArray(option.xAxis) ? option.xAxis[0] : option.xAxis;
  const labels = axis && "data" in axis && Array.isArray(axis.data) ? axis.data : [];
  const series = Array.isArray(option.series) ? option.series : option.series ? [option.series] : [];
  return series.flatMap(item => {
    const raw = (item as { data?: unknown }).data;
    if (!Array.isArray(raw)) return [];
    const points = raw.flatMap((value, index) => typeof value === "number" && Number.isFinite(value)
      ? [{ value, year: String(labels[index] ?? index + 1) }] : []);
    if (!points.length) return [];
    const name = String(item.name ?? "Reported value").replace(/ Δ/g, " annual change");
    const first = points[0];
    const last = points[points.length - 1];
    if (points.length === 1) return [`${name}: ${number(last.value)} in ${last.year}; one reported observation cannot establish a trend.`];
    const change = last.value - first.value;
    const movement = change > 0 ? "rose" : change < 0 ? "fell" : "was unchanged";
    let sentence = `${name} ${movement} from ${number(first.value)} in ${first.year} to ${number(last.value)} in ${last.year}`;
    if (change !== 0 && first.value > 0 && last.value >= 0) {
      sentence += ` (${number(Math.abs(change / first.value * 100))}% ${change > 0 ? "higher" : "lower"})`;
    }
    sentence += ".";
    const previous = points[points.length - 2];
    const latestChange = last.value - previous.value;
    if (change * latestChange < 0) {
      sentence += ` The latest reported interval moved in the opposite direction: ${latestChange > 0 ? "up" : "down"} from ${number(previous.value)} in ${previous.year}.`;
    }
    {
      const peak = points.reduce((a, b) => b.value > a.value ? b : a);
      if (peak.value > first.value && peak.value > last.value) sentence += ` It peaked at ${number(peak.value)} in ${peak.year}.`;
    }
    return [sentence];
  }).join(" ");
}
