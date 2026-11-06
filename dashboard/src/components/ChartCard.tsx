import { useEffect, useId, useMemo, useRef, useState, type ReactNode } from "react";
import * as echarts from "echarts";
import { chartTakeaway } from "../viz/chartTakeaway";
import { INK } from "../viz/palette";
import { useApp } from "../state/AppState";

export interface ChartCardProps {
  title: string;
  analysis?: string;
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
  title, tag, option, height = 210, defaultCollapsed = false, note, analysis,
}: ChartCardProps) {
  const { dark } = useApp();
  const [collapsed, setCollapsed] = useState(defaultCollapsed);
  const [expanded, setExpanded] = useState(false);
  const dialogRef = useRef<HTMLDialogElement | null>(null);
  const largeBoxRef = useRef<HTMLDivElement | null>(null);
  const largeChartRef = useRef<echarts.ECharts | null>(null);
  const headingId = useId();
  const boxRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);

  const takeaway = useMemo(() => analysis ?? chartTakeaway(option), [analysis, option]);

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

  useEffect(() => {
    if (!expanded) return;
    const dialog = dialogRef.current;
    const el = largeBoxRef.current;
    if (!dialog || !el) return;
    dialog.showModal();
    const chart = echarts.init(el);
    largeChartRef.current = chart;
    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(el);
    return () => {
      observer.disconnect();
      chart.dispose();
      largeChartRef.current = null;
      if (dialog.open) dialog.close();
    };
  }, [expanded]);

  useEffect(() => {
    largeChartRef.current?.setOption(wrapped, true);
  }, [expanded, wrapped]);

  return (
    <div className={`card${collapsed ? " hidden-body" : ""}`}>
      <div className={`card-head${collapsed ? " collapsed" : ""}`}>
        <button className="chart-toggle" onClick={() => setCollapsed(c => !c)} aria-expanded={!collapsed}>
          <h3>{title}</h3>
          <span>{tag && <span className="tag">{tag}</span>} <span className="chev">▾</span></span>
        </button>
        <button className="chart-expand" aria-label={`Expand ${title}`} onClick={() => setExpanded(true)}>
          ⤢ <span>Expand</span>
        </button>
      </div>
      {/* Body stays mounted while collapsed (hidden by CSS): the echarts
          instance lives for the card's whole lifetime - unmounting it would
          leave cards that start collapsed with a blank chart when expanded. */}
      <div className="card-body">
        {takeaway && <p className="chart-takeaway">{takeaway}</p>}
        <div
          ref={boxRef}
          className="chart"
          style={{ height }}
          role="img"
          aria-label={title}
        />
        {note && <div className="note">{note}</div>}
      </div>
      {expanded && <dialog ref={dialogRef} className="chart-dialog" aria-labelledby={headingId}
        onClose={() => setExpanded(false)}
        onClick={event => {
          if (event.target === event.currentTarget) {
            const bounds = event.currentTarget.getBoundingClientRect();
            if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) {
              event.currentTarget.close();
            }
          }
        }}>
        <div className="chart-dialog-layout">
          <div className="chart-dialog-head">
            <div><h2 id={headingId}>{title}</h2>{tag && <div className="note">{tag}</div>}</div>
            <button className="chart-expand" autoFocus aria-label={`Close ${title}`}
              onClick={() => dialogRef.current?.close()}>✕ Close</button>
          </div>
          {takeaway && <p className="chart-takeaway">{takeaway}</p>}
          <div ref={largeBoxRef} className="chart-dialog-canvas" role="img" aria-label={`${title}, expanded`} />
          {note && <div className="note chart-dialog-note">{note}</div>}
        </div>
      </dialog>}
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
