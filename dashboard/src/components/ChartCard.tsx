import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import * as echarts from "echarts";
import { INK } from "../viz/palette";
import { useApp } from "../state/AppState";

export interface ChartCardProps {
  title: string;
  tag?: string;
  option: echarts.EChartsOption;
  height?: number;
  defaultCollapsed?: boolean;
  note?: ReactNode;
}

/**
 * Collapsible card hosting one echarts instance. The chart's ink colors are
 * re-applied on theme change; the instance is created/destroyed with the DOM
 * node and re-sized via ResizeObserver.
 */
export function ChartCard({
  title, tag, option, height = 210, defaultCollapsed = false, note,
}: ChartCardProps) {
  const { dark } = useApp();
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const boxRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);

  const textColor = dark ? INK.dark.secondary : INK.light.secondary;

  // Apply default fonts/legend position; caller fields win on conflict.
  const wrapped = useMemo<echarts.EChartsOption>(() => {
    return {
      // Rapid country/year changes should show the current observation
      // immediately, rather than an interpolated value between snapshots.
      animation: false,
      textStyle: { color: textColor, fontSize: 11 },
      grid: { top: 30, right: 14, bottom: 24, left: 46 },
      toolbox: { right: 0, bottom: 0, feature: { saveAsImage: { title: "Download chart", name: title.replace(/[^a-z0-9]+/gi, "_") } } },
      legend: { textStyle: { color: textColor, fontSize: 11 }, top: 0, right: 0 },
      ...option,
    };
  }, [option, textColor, title]);

  useEffect(() => {
    const el = boxRef.current;
    if (!el) return;
    const chart = echarts.init(el);
    chartRef.current = chart;
    const ro = new ResizeObserver(() => chart.resize());
    ro.observe(el);
    return () => {
      ro.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    chartRef.current?.setOption(wrapped, true);
  }, [wrapped]);

  useEffect(() => {
    if (!collapsed) requestAnimationFrame(() => chartRef.current?.resize());
  }, [collapsed]);

  return (
    <div className={`card${collapsed ? " hidden-body" : ""}`}>
      <div
        className={`card-head${collapsed ? " collapsed" : ""} clickable`}
        onClick={() => setCollapsed((c) => !c)}
        role="button"
        aria-expanded={!collapsed}
      >
        <h3>{title}</h3>
        <span>
          {tag && <span className="tag">{tag}</span>}{" "}
          <span className="chev">▾</span>
        </span>
      </div>
      {/* Body stays mounted while collapsed (hidden by CSS): the echarts
          instance lives for the card's whole lifetime - unmounting it would
          leave cards that start collapsed with a blank chart when expanded. */}
      <div className="card-body">
        <div
          ref={boxRef}
          className="chart"
          style={{ height }}
          role="img"
          aria-label={title}
        />
        {note && <div className="note">{note}</div>}
      </div>
    </div>
  );
}

/** Shared axis style for echarts options (recessive grid, ink labels). */
export function axisStyle(dark: boolean) {
  const ink = dark ? INK.dark : INK.light;
  return {
    axisLine: { lineStyle: { color: ink.grid } },
    axisTick: { show: false },
    axisLabel: { color: ink.secondary, fontSize: 10.5 },
    splitLine: { lineStyle: { color: ink.grid } },
  };
}
