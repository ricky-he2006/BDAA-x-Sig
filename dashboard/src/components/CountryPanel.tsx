import { Fragment, useMemo, useState } from "react";
import type { EChartsOption } from "echarts";
import { useApp } from "../state/AppState";
import { YEARS } from "../data/types";
import { axisStyle } from "./ChartCard";
import { CountryChart, isReportedNumber } from "./CountryChart";
import type { CountryYear } from "../data/types";
import { entityColor } from "../viz/series";
import { fmt, fmtSigned, fmtPct } from "../viz/format";
import { annualChanges, indexFrom2020, COUNTRY_QUESTIONS } from "../viz/countryDiagnostics";

/** Year-indexed array of a numeric pick (nulls kept). */
function series(
  get: (iso: string, year: number) => number | null | undefined,
  iso: string,
): (number | null)[] {
  return YEARS.map((y) => {
    const v = get(iso, y);
    return v == null ? null : Number(v);
  });
}

/** a - b, null unless both present. */
function delta(a: number | null | undefined, b: number | null | undefined): number | null {
  if (a == null || b == null) return null;
  return a - b;
}

export function CountryPanel() {
  const { data, year, selectedIso, selectCountry, dark } = useApp();
  const [compareIso, setCompareIso] = useState<string | null>(null);
  const [showCompare, setShowCompare] = useState(false);

  const iso = selectedIso;
  const name = iso ? data?.countryNames.get(iso) : null;

  const cur = useMemo(() => {
    if (!data || !iso) return null;
    return data.countryByIso.get(iso)?.get(year) ?? null;
  }, [data, iso, year]);

  const prev = useMemo(() => {
    if (!data || !iso || year <= YEARS[0]) return null;
    return data.countryByIso.get(iso)?.get(year - 1) ?? null;
  }, [data, iso, year]);

  if (!data || !iso || !name) {
    return (
      <aside className="side">
        <div className="panel-title">Country explorer</div>
        <div className="panel-sub">Select a country on the globe or via search.</div>
        <div className="empty">
          Click any country to see its clean-vs-coal record,
          <br />
          2020–{YEARS[YEARS.length - 1]}.
        </div>
      </aside>
    );
  }

  const lastYear = YEARS[YEARS.length - 1];
  const mode: "light" | "dark" = dark ? "dark" : "light";
  const cs = (iso: string, y: number) => data.countryByIso.get(iso)?.get(y)?.ember.clean_share ?? null;
  const dem = (iso: string, y: number) => data.countryByIso.get(iso)?.get(y)?.ember.demand ?? null;
  const clean = (iso: string, y: number) => data.countryByIso.get(iso)?.get(y)?.ember.clean ?? null;
  const fossil = (iso: string, y: number) => data.countryByIso.get(iso)?.get(y)?.ember.fossil ?? null;
  const coalGen = (iso: string, y: number) => data.countryByIso.get(iso)?.get(y)?.ei.coal_gen ?? null;
  const ci = (iso: string, y: number) => data.countryByIso.get(iso)?.get(y)?.ember.ci ?? null;

  const x = YEARS;
  const ax = axisStyle(dark);

  const cleanShareOpt: EChartsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: x, ...ax, splitLine: { show: false } },
    yAxis: { type: "value", max: 100, ...ax },
    series: [
      {
        name: "Clean share",
        type: "line",
        data: series(cs, iso),
        smooth: false,
        symbolSize: 6,
        lineStyle: { width: 2.5, color: entityColor("clean", mode) },
        itemStyle: { color: entityColor("clean", mode) },
        areaStyle: { opacity: 0.12 },
      },
    ],
  };

  const mixOpt: EChartsOption = {
    tooltip: { trigger: "axis" },
    legend: { show: true, top: 0, right: 0 },
    xAxis: { type: "category", data: x, ...ax, splitLine: { show: false } },
    yAxis: { type: "value", ...ax },
    series: [
      { name: "Demand", type: "line", data: series(dem, iso), symbolSize: 5, lineStyle: { width: 2, type: "dashed", color: entityColor("demand", mode) }, itemStyle: { color: entityColor("demand", mode) } },
      { name: "Clean gen", type: "line", data: series(clean, iso), symbolSize: 5, lineStyle: { width: 2.5, color: entityColor("clean", mode) }, itemStyle: { color: entityColor("clean", mode) } },
      { name: "Fossil gen", type: "line", data: series(fossil, iso), symbolSize: 5, lineStyle: { width: 2.5, color: entityColor("fossil", mode) }, itemStyle: { color: entityColor("fossil", mode) } },
    ],
  };

  const coalOpt: EChartsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: x, ...ax, splitLine: { show: false } },
    yAxis: { type: "value", ...ax },
    series: [
      {
        name: "Coal-fired generation",
        type: "bar",
        data: series(coalGen, iso),
        barWidth: 18,
        itemStyle: { color: entityColor("coal", mode), borderRadius: [3, 3, 0, 0] },
      },
    ],
  };

  const ciOpt: EChartsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: x, ...ax, splitLine: { show: false } },
    yAxis: { type: "value", ...ax },
    series: [
      {
        name: "Carbon intensity",
        type: "line",
        data: series(ci, iso),
        smooth: false,
        symbolSize: 6,
        lineStyle: { width: 2.5, color: entityColor("clean", mode) },
        itemStyle: { color: entityColor("clean", mode) },
      },
    ],
  };

  // Comparison: clean share of this country vs a selected peer.
  const cmpOpt: EChartsOption = {
    tooltip: { trigger: "axis" },
    legend: { show: true, top: 0, right: 0, textStyle: { fontSize: 11 } },
    xAxis: { type: "category", data: x, ...ax, splitLine: { show: false } },
    yAxis: { type: "value", max: 100, ...ax },
    series: [
      { name, type: "line", data: series(cs, iso), smooth: false, symbolSize: 5, lineStyle: { width: 2.5, color: entityColor("clean", mode) }, itemStyle: { color: entityColor("clean", mode) } },
      ...(compareIso
        ? [{
            name: data.countryNames.get(compareIso) ?? compareIso,
            type: "line" as const,
            data: series(cs, compareIso),
            smooth: false,
            symbolSize: 5,
            lineStyle: { width: 2, color: entityColor("fossil", mode) },
            itemStyle: { color: entityColor("fossil", mode) },
          }]
        : []),
    ],
  };

  const cmpCountries = Array.from(data.countryNames.entries())
    .filter(([k]) => k !== iso && YEARS.some(y => isReportedNumber(cs(iso, y)) && isReportedNumber(cs(k, y))))
    .sort((a, b) => a[1].localeCompare(b[1]));

  const e = cur?.ember;
  const ei = cur?.ei;
  const records = data.countryByIso.get(iso) ?? new Map();
  const diagnosticAxes = {
    tooltip: { trigger: "axis" as const },
    legend: { show: true, top: 0, right: 0, textStyle: { fontSize: 10 } },
    xAxis: { type: "category" as const, data: x, ...ax },
    yAxis: { type: "value" as const, ...ax },
  };
  const additionsOpt: EChartsOption = {
    ...diagnosticAxes,
    series: [
      { name: "Clean Δ", type: "bar", data: annualChanges(records, x, r => r.ember.clean), itemStyle: { color: entityColor("clean", mode) } },
      { name: "Fossil Δ", type: "bar", data: annualChanges(records, x, r => r.ember.fossil), itemStyle: { color: entityColor("fossil", mode) } },
      { name: "Imports Δ", type: "bar", data: annualChanges(records, x, r => r.ember.net_imports), itemStyle: { color: entityColor("other", mode) } },
      { name: "Demand Δ", type: "line", data: annualChanges(records, x, r => r.ember.demand), lineStyle: { color: entityColor("demand", mode), type: "dashed" }, itemStyle: { color: entityColor("demand", mode) } },
    ],
  };
  const fuelOpt: EChartsOption = {
    ...diagnosticAxes,
    series: [
      { name: "Coal", type: "line", data: x.map(y => records.get(y)?.ei.coal_gen ?? null), itemStyle: { color: entityColor("coal", mode) } },
      { name: "Gas", type: "line", data: x.map(y => records.get(y)?.ei.gas_gen ?? null), itemStyle: { color: entityColor("gas", mode) } },
    ],
  };
  const emissionsOpt: EChartsOption = {
    ...diagnosticAxes,
    series: [
      { name: "Emissions", type: "line", data: indexFrom2020(records, x, r => r.ember.emissions), itemStyle: { color: entityColor("fossil", mode) } },
      { name: "Intensity", type: "line", data: indexFrom2020(records, x, r => r.ember.ci), itemStyle: { color: entityColor("clean", mode) } },
    ],
  };
  const productionOpt: EChartsOption = {
    ...diagnosticAxes,
    series: [
      { name: "Production", type: "line", data: indexFrom2020(records, x, r => r.ei.coal_prod_mt), itemStyle: { color: entityColor("demand", mode) } },
      { name: "Coal generation", type: "line", data: indexFrom2020(records, x, r => r.ei.coal_gen), itemStyle: { color: entityColor("coal", mode) } },
    ],
  };
  const importsOpt: EChartsOption = {
    ...diagnosticAxes,
    series: [{ name: "Net imports / demand", type: "bar", data: x.map(y => {
      const row = records.get(y)?.ember;
      return row?.net_imports == null || row.demand == null || row.demand <= 0 ? null : row.net_imports / row.demand * 100;
    }), itemStyle: { color: entityColor("other", mode) } }],
  };
  const snapshots = [
    { label: "Clean share", value: e?.clean_share, unit: "%", change: delta(e?.clean_share, prev?.ember.clean_share), changeUnit: "pp" },
    { label: "Electricity demand", value: e?.demand, unit: "TWh", change: delta(e?.demand, prev?.ember.demand), changeUnit: "TWh" },
    { label: "Clean generation", value: e?.clean, unit: "TWh", change: delta(e?.clean, prev?.ember.clean), changeUnit: "TWh" },
    { label: "Fossil generation", value: e?.fossil, unit: "TWh", change: delta(e?.fossil, prev?.ember.fossil), changeUnit: "TWh" },
    { label: "Carbon intensity", value: e?.ci, unit: "gCO₂e/kWh" },
    { label: "Coal-fired generation", value: ei?.coal_gen, unit: "TWh", detail: isReportedNumber(cur?.coal_share) ? `${fmtPct(cur.coal_share)} of gen` : undefined },
  ].filter(s => isReportedNumber(s.value));
  const history = [...records.values()];
  const hasEmber = history.some(r => isReportedNumber(r.ember.generation));
  const hasEi = history.some(r => r.ei_available);
  const hasCoal = history.some(r => isReportedNumber(r.ei.coal_gen));
  const hasGas = history.some(r => isReportedNumber(r.ei.gas_gen));
  const productionIndex = indexFrom2020(records, x, r => r.ei.coal_prod_mt);
  const coalIndex = indexFrom2020(records, x, r => r.ei.coal_gen);
  const canCompareProduction = productionIndex.some((v, i) => isReportedNumber(v) && isReportedNumber(coalIndex[i]));
  const productionOnlyOpt: EChartsOption = {
    ...diagnosticAxes,
    series: [{ name: "Coal production", type: "line", data: x.map(y => records.get(y)?.ei.coal_prod_mt ?? null), itemStyle: { color: entityColor("coal", mode) } }],
  };
  const intensityIndex = indexFrom2020(records, x, r => r.ember.ci);
  const canCompareEmissions = indexFrom2020(records, x, r => r.ember.emissions).some((v, i) =>
    isReportedNumber(v) && isReportedNumber(intensityIndex[i]));
  const peerIso = cmpCountries.some(([key]) => key === compareIso) ? compareIso : null;
  const peer = peerIso ? data.countryByIso.get(peerIso)?.get(year) : null;
  const columns: { title: string; pick: (r: CountryYear) => number | null }[] = [
    { title: "Demand TWh", pick: (r: CountryYear) => r.ember.demand },
    { title: "Clean TWh", pick: (r: CountryYear) => r.ember.clean },
    { title: "Fossil TWh", pick: (r: CountryYear) => r.ember.fossil },
    { title: "Coal TWh (EI)", pick: (r: CountryYear) => r.ei.coal_gen },
  ].filter(c => history.some(r => isReportedNumber(c.pick(r))));
  const tableRows = history.filter(r => columns.some(c => isReportedNumber(c.pick(r)))).sort((a, b) => a.year - b.year);
  const comparisonRows = [
    { label: "Clean share", a: e?.clean_share, b: peer?.ember.clean_share, unit: "%" },
    { label: "Demand", a: e?.demand, b: peer?.ember.demand, unit: "TWh" },
    { label: "Coal gen", a: ei?.coal_gen, b: peer?.ei.coal_gen, unit: "TWh" },
  ].filter(r => isReportedNumber(r.a) && isReportedNumber(r.b));
  const currentSources = [isReportedNumber(e?.generation) || isReportedNumber(e?.demand) ? "Ember" : null,
    cur?.ei_available ? "Energy Institute" : null].filter(Boolean);

  return (
    <aside className="side">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div className="panel-title">{name}</div>
          <div className="panel-sub">
            {cur?.continent ?? history[0]?.continent} · year {year}
            {year === lastYear && " (partial country coverage)"}
          </div>
        </div>
        <button className="iconbtn" onClick={() => selectCountry(null)} aria-label="Close">✕</button>
      </div>

      <div className="note" style={{ marginBottom: 12 }} aria-label="Country source availability">
        {currentSources.length > 0
          ? `${year} sources: ${currentSources.join(" · ")}.`
          : `No reported values for ${year}. Available historical observations are shown below.`}
      </div>
      {/* Headline stats */}
      {snapshots.length > 0 && <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-head"><h3>{year} snapshot</h3></div>
        <div className="card-body">
          <div className="kv">
            {snapshots.map(s => <Fragment key={s.label}>
              <span className="k">{s.label}</span>
              <span className="v">{s.unit === "%" ? fmtPct(s.value) : `${fmt(s.value)} ${s.unit}`}
                {isReportedNumber(s.change) && <small className="muted"> {fmtSigned(s.change)} {s.changeUnit}</small>}
                {s.detail && <small className="muted"> {s.detail}</small>}
              </span>
            </Fragment>)}
          </div>
        </div>
      </div>}

      <div className="note" style={{ marginBottom: 12 }}>
        {COUNTRY_QUESTIONS[iso] ?? "Compare clean and fossil additions with demand and trade. A change in generation share alone does not establish a change in fuel volumes."}
      </div>
      <CountryChart title="What met the change in demand?" tag="Ember · TWh" option={additionsOpt}
        note="Annual changes: clean + fossil + net imports ≈ demand. This is an accounting identity, not causal attribution. Missing years stay blank." />
      <CountryChart
        title="Clean electricity share"
        tag="Ember"
        option={cleanShareOpt}
        note={`Share of total generation from renewables + nuclear, ${YEARS[0]}–${lastYear}.`}
      />
      <CountryChart
        title="Demand vs clean & fossil generation"
        tag="Ember"
        option={mixOpt}
        note="Dashed line = demand; solid = clean and fossil generation (TWh)."
      />
      <CountryChart
        title="Coal-fired generation"
        tag="Energy Institute"
        option={coalOpt}
        note={isReportedNumber(cur?.coal_share) ? `Coal share of generation, ${year}: ${fmtPct(cur.coal_share)}.` : "Reported coal-fired generation, TWh."}
        defaultCollapsed
      />
      <CountryChart
        title="Carbon intensity of power"
        tag="Ember"
        option={ciOpt}
        note="gCO₂e per kWh of electricity. Lower is cleaner."
        defaultCollapsed
      />
      {hasGas && <CountryChart title={hasCoal ? "Coal versus gas generation" : "Gas-fired generation"} tag="EI · TWh" option={fuelOpt} defaultCollapsed
        note="Reported EI fuel generation. Coal is only part of all-fossil generation; EI and Ember totals can have different definitions." />}
      {canCompareEmissions && <CountryChart title="Emissions versus emissions intensity" tag="Ember · 2020 = 100" option={emissionsOpt} defaultCollapsed
        note="Cleaner electricity per kWh can coexist with rising total power emissions. Each series uses its own reported 2020 base." />}
      <CountryChart title={canCompareProduction ? "Coal production versus coal generation" : "Coal production"}
        tag={canCompareProduction ? "EI · 2020 = 100" : "EI · Mt"} option={canCompareProduction ? productionOpt : productionOnlyOpt} defaultCollapsed
        note={canCompareProduction ? "Different measures normalized to their own 2020 values. Divergence does not establish exports, stock changes or non-power demand." : "Reported coal production in million metric tonnes."} />
      <CountryChart title="Electricity trade exposure" tag="Ember · % of demand" option={importsOpt} defaultCollapsed
        note="Net imports divided by demand; negative values mean net exports. No value is shown for zero or missing demand." />

      {tableRows.length > 0 && <details className="card" style={{ marginBottom: 12 }}>
        <summary className="card-head">Underlying country observations</summary>
        <div className="card-body" style={{ overflowX: "auto" }}>
          <table className="tbl"><thead><tr><th>Year</th>{columns.map(c => <th key={c.title}>{c.title}</th>)}</tr></thead>
            <tbody>{tableRows.map(r => <tr key={r.year}><td>{r.year}</td>{columns.map(c => <td key={c.title}>{isReportedNumber(c.pick(r)) ? fmt(c.pick(r)) : ""}</td>)}</tr>)}</tbody>
          </table>
          <p className="note">Only reported fields and years are included; gaps stay blank. <a href="/evidence/country_year.csv" download>Download all country observations (CSV)</a>; use Data &amp; evidence for definitions and source snapshots.</p>
        </div>
      </details>}

      {cmpCountries.length > 0 && <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-head clickable" onClick={() => setShowCompare((s) => !s)} role="button" aria-expanded={showCompare}>
          <h3>Compare with another country</h3>
          <span className="chev" style={{ transform: showCompare ? "none" : "rotate(-90deg)" }}>▾</span>
        </div>
        {showCompare && (
          <div className="card-body">
            <select
              value={peerIso ?? ""}
              onChange={(ev) => setCompareIso(ev.target.value || null)}
              style={{ width: "100%", marginBottom: 8 }}
              aria-label="Comparison country"
            >
              <option value="">Select a country…</option>
              {cmpCountries.map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
            {peerIso && <CountryChart title={`Clean share: ${name} vs comparison`} tag="Ember" option={cmpOpt} height={200} />}
            {peerIso && comparisonRows.length > 0 && (
              <div className="kv" style={{ marginTop: 8 }}>
                {comparisonRows.map(r => <Fragment key={r.label}><span className="k">{r.label}</span>
                  <span className="v">{r.unit === "%" ? fmtPct(r.a) : fmt(r.a)} <span className="muted">vs</span> {r.unit === "%" ? fmtPct(r.b) : `${fmt(r.b)} ${r.unit}`}</span></Fragment>)}
              </div>
            )}
          </div>
        )}
      </div>}

      <div className="note">
        Sources: {[hasEmber ? "Ember (electricity)" : null, hasEi ? "Energy Institute (energy and coal)" : null].filter(Boolean).join("; ")}.
        {cur?.ci_precision_limited && " Carbon intensity may be rounded at source."}
        {cur?.zero_generation && " Zero generation reported — check coverage."}
        {" "}See Data &amp; evidence for coverage and source definitions.
      </div>
    </aside>
  );
}
