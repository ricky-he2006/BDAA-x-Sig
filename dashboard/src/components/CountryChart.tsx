import type { EChartsOption } from "echarts";
import { ChartCard, type ChartCardProps } from "./ChartCard";

export function isReportedNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

/** Country charts use numeric arrays. Omit empty series and whole empty cards,
 * while retaining reported zeros and gaps between reported years. */
export function CountryChart({ option, ...props }: ChartCardProps) {
  const candidates = Array.isArray(option.series) ? option.series : option.series ? [option.series] : [];
  const series = candidates.filter(s => {
    const values = (s as { data?: unknown }).data;
    return Array.isArray(values) && values.some(isReportedNumber);
  });
  if (series.length === 0) return null;
  return <ChartCard {...props} option={{ ...option, series } as EChartsOption} />;
}
