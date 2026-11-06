import { useMemo } from "react";
import type { EChartsOption } from "echarts";
import { useApp } from "../state/AppState";
import { YEARS } from "../data/types";
import { ChartCard, axisStyle } from "./ChartCard";
import { entityColor } from "../viz/series";
import { stateValue } from "../viz/stateValue";
import { fmt, fmtSigned, fmtSignedPct, NA } from "../viz/format";
import { INK } from "../viz/palette";

const S_SHORT = "short tons";

/** National total from the EIA aggregate table (US rows, sectors 94/98). */
function usNational(data: NonNullable<ReturnType<typeof useApp>["data"]>, year: number, sector: number): number | null {
  let v: number | null = null;
  for (const r of data.usAggregates) {
    if (r.location === "US" && r.year === year && r.sector === sector && r.consumption != null) {
      v = (v ?? 0) + r.consumption;
    }
  }
  return v;
}

export function StatePanel() {
  const { data, selectedState } = useApp();
  if (!data) return null;
  // Separate components so the selected-state view's hooks are never
  // conditional on selection state (React hooks-order violation otherwise).
  return selectedState ? <StateDetail state={selectedState} /> : <USOverview />;
}

function StateDetail({ state }: { state: string }) {
  const { data, year, selectState, dark } = useApp();

  // Share of the national total (all base sectors vs US sector-98 is a different
  // scope; use state sum vs US *base-sector* sum for an apples-to-apples share).
  // The only hook - runs unconditionally; null-safe so the guard below can
  // follow it without a conditional-hook violation.
  const usBaseSeries = useMemo(() => {
    if (!data) return null;
    return YEARS.map((y) => {
      let s = 0;
      let any = false;
      for (const [code] of data.stateByCode) {
        const v = stateValue(data, code, y, "all");
        if (v != null) { s += v; any = true; }
      }
      return any ? s : null;
    });
  }, [data]);
  if (!data || usBaseSeries == null) return null;

  const name = data.stateNames.get(state) ?? state;
  const rowsFor = (y: number) => data.stateByCode.get(state)?.get(y);

  const sectors2 = [1, 2, 3];
  const allSeries = YEARS.map((y) => stateValue(data, state, y, "all"));
  const powerSeries = YEARS.map((y) => stateValue(data, state, y, "power"));
  const commercialSeries = YEARS.map((y) => stateValue(data, state, y, 8));
  const cokeSeries = YEARS.map((y) => stateValue(data, state, y, 9));
  const otherIndSeries = YEARS.map((y) => stateValue(data, state, y, 10));

  const shareSeries = YEARS.map((y, i) => {
    const a = allSeries[i];
    const b = usBaseSeries[i];
    if (a == null || b == null || b <= 0) return null;
    return (a / b) * 100;
  });

  const cur = rowsFor(year);
  const med = (rows: typeof cur, sector: number, field: "heat_btu_lb" | "sulfur_pct" | "ash_pct") => {
    if (!rows) return null;
    const vals = rows.filter((r) => r.sector === sector && r[field] != null).map((r) => r[field] as number);
    if (vals.length === 0) return null;
    vals.sort((a, b) => a - b);
    return vals[Math.floor(vals.length / 2)];
  };

  const ax = axisStyle(dark);
  const c = dark ? INK.dark : INK.light;

  const bySectorOpt: EChartsOption = {
    tooltip: { trigger: "axis" },
    legend: { show: true, top: 0, right: 0, textStyle: { fontSize: 10.5, color: c.secondary } },
    xAxis: { type: "category", data: YEARS, ...ax, splitLine: { show: false } },
    yAxis: { type: "value", ...ax, axisLabel: { ...ax.axisLabel, formatter: (v: number) => fmt(v / 1e6, 1) + "M" } },
    series: [
      { name: "Electric power (1+2+3)", type: "line", data: powerSeries, symbolSize: 4, lineStyle: { width: 2, color: entityColor("coal", dark ? "dark" : "light") }, itemStyle: { color: entityColor("coal", dark ? "dark" : "light") } },
      { name: "Commercial & inst. (8)", type: "line", data: commercialSeries, symbolSize: 4, lineStyle: { width: 2, color: entityColor("gas", dark ? "dark" : "light") }, itemStyle: { color: entityColor("gas", dark ? "dark" : "light") } },
      { name: "Coke plants (steelmaking)", type: "line", data: cokeSeries, symbolSize: 4, lineStyle: { width: 2, color: entityColor("nuclear", dark ? "dark" : "light") }, itemStyle: { color: entityColor("nuclear", dark ? "dark" : "light") } },
      { name: "Other industrial (10)", type: "line", data: otherIndSeries, symbolSize: 4, lineStyle: { width: 2, color: entityColor("renewable", dark ? "dark" : "light") }, itemStyle: { color: entityColor("renewable", dark ? "dark" : "light") } },
    ],
  };

  const allOpt: EChartsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: YEARS, ...ax, splitLine: { show: false } },
    yAxis: { type: "value", ...ax, axisLabel: { ...ax.axisLabel, formatter: (v: number) => fmt(v / 1e6, 1) + "M" } },
    series: [
      {
        name: "All base sectors",
        type: "bar",
        data: allSeries,
        barWidth: 22,
        itemStyle: { color: entityColor("coal", dark ? "dark" : "light"), borderRadius: [3, 3, 0, 0] },
      },
    ],
  };

  const shareOpt: EChartsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: YEARS, ...ax, splitLine: { show: false } },
    yAxis: { type: "value", min: 0, ...ax, axisLabel: { ...ax.axisLabel, formatter: (v: number) => v + "%" } },
    series: [
      {
        name: "Share of US (base sectors)",
        type: "line",
        data: shareSeries,
        smooth: false,
        symbolSize: 5,
        lineStyle: { width: 2.5, color: entityColor("clean", dark ? "dark" : "light") },
        itemStyle: { color: entityColor("clean", dark ? "dark" : "light") },
        areaStyle: { opacity: 0.12 },
      },
    ],
  };

  const consumptionAll = allSeries[YEARS.indexOf(year)];
  const consumptionAllPrev = allSeries[YEARS.indexOf(year - 1)];
  const receipts = (rows: typeof cur) => {
    if (!rows) return null;
    let v: number | null = null;
    for (const r of rows) if (r.receipts != null) v = (v ?? 0) + r.receipts;
    return v;
  };

  const heatUnit = cur?.find((r) => r.heat_btu_lb != null)?.heat_unit;

  return (
    <aside className="side">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div className="panel-title">{name}</div>
          <div className="panel-sub">
            US coal · year {year}
            {year === YEARS[YEARS.length - 1] && " (check source vintage)"}
          </div>
        </div>
        <button className="iconbtn" onClick={() => selectState(null)} aria-label="Close">✕</button>
      </div>

      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-head"><h3>{year} snapshot</h3></div>
        <div className="card-body">
          <div className="kv">
            <span className="k">Consumption (all base sectors)</span>
            <span className="v">{fmt(consumptionAll)} {S_SHORT}
              <small className="muted"> {fmtSigned(consumptionAll != null && consumptionAllPrev != null ? consumptionAll - consumptionAllPrev : null)} {S_SHORT}</small>
            </span>
            <span className="k">Consumption (electric power)</span>
            <span className="v">{fmt(powerSeries[YEARS.indexOf(year)])} {S_SHORT}</span>
            <span className="k">Receipts</span>
            <span className="v">{fmt(receipts(cur))} {S_SHORT}</span>
            <span className="k">Heat content (sector 1, assumed scale)</span>
            <span className="v">{med(cur, 1, "heat_btu_lb") != null ? `${fmt(med(cur, 1, "heat_btu_lb"))} Btu/lb` : NA}</span>
            <span className="k">Sulfur (sector 1)</span>
            <span className="v">{med(cur, 1, "sulfur_pct") != null ? fmt(med(cur, 1, "sulfur_pct"), 2) + "%" : NA}</span>
            <span className="k">Share of US (base sectors)</span>
            <span className="v">{shareSeries[YEARS.indexOf(year)] != null ? fmt(shareSeries[YEARS.indexOf(year)], 2) + "%" : NA}</span>
          </div>
          {year === YEARS[YEARS.length - 1] && (
            <div className="note">Supplied 2025 snapshot; release metadata is not recorded and revised official figures may differ.</div>
          )}
        </div>
      </div>

      <ChartCard
        title="Consumption by sector"
        tag="EIA"
        option={bySectorOpt}
        note="Electric power = sectors 1+2+3 (no double count with the 98 aggregate). Values in short tons; axis in millions."
      />
      <ChartCard
        title="All base sectors, 2020–2025"
        tag="EIA"
        option={allOpt}
        note="Nulls mean not reported, not zero."
        defaultCollapsed
      />
      <ChartCard
        title="Share of US consumption (base sectors)"
        tag="EIA"
        option={shareOpt}
        note="State sum ÷ sum of all 50 states + DC + PR for the same year/sectors."
        defaultCollapsed
      />

      <div className="note">
        Source: EIA state-level coal consumption (base sectors {sectors2.join(", ")} plus 8, 9, 10).
        Heat-content units for power sectors use the inferred scale
        {heatUnit ? ` (${heatUnit})` : ""}; the GJ/tonne-scale assumption for
        power-sector heat content is unverified against EIA API documentation.
      </div>
    </aside>
  );
}

function USOverview() {
  const { data, year, dark, selectState, usSector } = useApp();

  // Top states this year (all base sectors), clickable. The only hook -
  // unconditional and null-safe; the data guard follows it.
  const top = useMemo(() => {
    if (!data) return [];
    const rows: { code: string; name: string; v: number }[] = [];
    for (const [code, name] of data.stateNames) {
      const v = stateValue(data, code, year, "all");
      if (v != null) rows.push({ code, name, v });
    }
    rows.sort((a, b) => b.v - a.v);
    return rows.slice(0, 15);
  }, [data, year]);
  if (!data) return null;

  const national98 = usNational(data, year, 98);
  const national98Prev = usNational(data, year - 1, 98);
  const delta98 = national98 != null && national98Prev != null ? national98 - national98Prev : null;

  const ax = axisStyle(dark);

  const natOpt: EChartsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: YEARS, ...ax, splitLine: { show: false } },
    yAxis: { type: "value", ...ax, axisLabel: { ...ax.axisLabel, formatter: (v: number) => fmt(v / 1e6, 0) + "M" } },
    series: [
      {
        name: "US electric power (sector 98)",
        type: "bar",
        data: YEARS.map((y) => usNational(data, y, 98)),
        barWidth: 22,
        itemStyle: { color: entityColor("coal", dark ? "dark" : "light"), borderRadius: [3, 3, 0, 0] },
      },
    ],
  };
  const priceOpt: EChartsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: YEARS, ...ax },
    yAxis: { type: "value", ...ax },
    series: [{ name: "Delivered coal price ($/short ton)", type: "line",
      data: YEARS.map(y => data.usAggregates.find(r => r.location === "US" && r.year === y && r.sector === 98)?.price ?? null),
      itemStyle: { color: entityColor("demand", dark ? "dark" : "light") } }],
  };

  return (
    <aside className="side">
      <div className="panel-title">United States</div>
      <div className="panel-sub">
        Coal consumption · year {year}
        {year === YEARS[YEARS.length - 1] && " (check source vintage)"}
      </div>

      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-head"><h3>National (electric power, sector 98)</h3></div>
        <div className="card-body">
          <div className="kv">
            <span className="k">Consumption {year}</span>
            <span className="v">{fmt(national98)} {S_SHORT} (≈{fmt(national98 == null ? null : national98 * 0.90718474 / 1e6, 1)} Mt)</span>
            <span className="k">Δ vs {year - 1}</span>
            <span className="v down">
              {fmtSigned(delta98)} {S_SHORT}
              {delta98 != null && national98Prev != null ? ` (${fmtSignedPct((delta98 / national98Prev) * 100)})` : ""}
            </span>
          </div>
          {year === 2025 && national98 != null && national98Prev != null && national98 > national98Prev && (
            <div className="note" style={{ color: "var(--serious)" }}>
              2025 shows a rebound vs 2024 — driven largely by a few states; see the state
              breakdown on the map. The supplied snapshot may differ from revised official figures.
            </div>
          )}
        </div>
      </div>

      <ChartCard
        title="US electric power coal, 2020–2025"
        tag="EIA aggregate 98"
        option={natOpt}
        note="Sector 98 = Electric power (1+2+3) from the EIA national aggregate rows — the only US total used here."
      />
      <ChartCard title="U.S. delivered coal price" tag="EIA · USD/short ton" option={priceOpt}
        note="National sector 98, nominal delivered price. Missing 2021 remains blank. This is a fuel cost, not a producer margin or mine realization." />

      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-head"><h3>Top states, {year} (all base sectors)</h3></div>
        <div className="card-body" style={{ maxHeight: 320, overflowY: "auto" }}>
          <table className="tbl">
            <thead>
              <tr>
                <th>State</th>
                <th className="num">Consumption (st)</th>
                <th className="num">Share</th>
              </tr>
            </thead>
            <tbody>
              {top.map((r) => {
                const tot = top.reduce((s, x) => s + x.v, 0);
                return (
                  <tr key={r.code} className="clickable" onClick={() => selectState(r.code)}>
                    <td>{r.name}</td>
                    <td className="num">{fmt(r.v)}</td>
                    <td className="num">{tot > 0 ? fmt((r.v / tot) * 100, 1) + "%" : NA}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <div className="note">
            Sector shown: all base sectors ({usSector === "all" ? "map uses the same scope" : "map sector differs — see pills"}).
            Share is of the top-15 total, not the national total.
          </div>
        </div>
      </div>

      <div className="note">
        National figures use the EIA aggregate rows (location = US) to avoid
        summing states by hand; state figures use base sectors only, so the map
        never double-counts the 94/98 aggregate rows.
      </div>
    </aside>
  );
}
