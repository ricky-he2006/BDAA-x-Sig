import { useMemo, useState } from "react";
import type { EChartsOption } from "echarts";
import { useApp } from "../state/AppState";
import { YEARS } from "../data/types";
import type { CountryYear } from "../data/types";
import { ChartCard, axisStyle } from "./ChartCard";
import { entityColor } from "../viz/series";
import { fmt, fmtSigned, fmtSignedPct, NA } from "../viz/format";

const FOCUS = ["USA", "CHN", "IND", "IDN", "DEU", "JPN", "AUS", "RUS"] as const;

type Tag = "verified" | "interpretation" | "hypothesis";

interface Evidence {
  label: string;
  value: string;
  source: string;
  tag: Tag;
  note?: string;
}

const TABS = [
  { key: "coal", label: "Coal" },
  { key: "clean", label: "Clean & renewables" },
  { key: "utility", label: "Utilities & retail" },
  { key: "gas", label: "Gas & grid" },
  { key: "cross", label: "Cross-country" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

type SampleSource = "ember" | "ei";
function isMatchedCountry(m: Map<number, CountryYear>, source: SampleSource): boolean {
  return YEARS.every(y => {
    const r = m.get(y);
    return r != null && (source === "ember"
      ? [r.ember.clean, r.ember.generation, r.ember.demand, r.ember.wind_solar].every(v => v != null)
      : [r.ei.coal_gen, r.ei.elect, r.ei.coal_prod_mt].every(v => v != null));
  });
}

/** Fixed six-year membership, with a common denominator within each source. */
function worldSum(
  data: NonNullable<ReturnType<typeof useApp>["data"]>,
  year: number,
  pick: (cy: CountryYear) => number | null,
  source: SampleSource = "ember",
): number | null {
  let s = 0;
  let any = false;
  for (const m of data.countryByIso.values()) {
    if (!isMatchedCountry(m, source)) continue;
    const cy = m.get(year);
    if (!cy) continue;
    const v = pick(cy);
    if (v != null) {
      s += v;
      any = true;
    }
  }
  return any ? s : null;
}

export function ResearchPanel() {
  const { data } = useApp();
  const [tab, setTab] = useState<TabKey>("coal");
  if (!data) return null;
  return (
    <div>
      <div className="panel-title">Industry research</div>
      <div className="panel-sub">
        Evidence is computed live from the cleaned datasets. Tags:
        <span className="badge" style={{ marginLeft: 6 }}>verified — directly from data</span>{" "}
        <span className="badge warn" style={{ marginLeft: 4 }}>interpretation — an inference</span>{" "}
        <span className="badge" style={{ marginLeft: 4, color: "var(--critical)" }}>hypothesis — untested</span>
      </div>
      <div className="pillrow">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={`pill${tab === t.key ? " active" : ""}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>
      {tab === "coal" && <CoalTab />}
      {tab === "clean" && <CleanTab />}
      {tab === "utility" && <UtilityTab />}
      {tab === "gas" && <GasTab />}
      {tab === "cross" && <CrossTab />}
      <div className="note" style={{ marginTop: 8 }}>
        Research charts use fixed 2020–2025 membership within each source, not full-world totals.
        The submitted industry recommendation and evidence are in
        <code> deliverables/INVESTMENT_THESIS.md</code>. Main pitch history uses a broader
        fixed 2020–2024 panel. Missing coverage and source revision status are separate limits.
      </div>
    </div>
  );
}

function Ev({ e }: { e: Evidence }) {
  return (
    <div style={{ display: "flex", gap: 10, padding: "6px 0", borderBottom: "1px solid var(--grid)" }}>
      <span
        className="badge"
        style={
          e.tag === "interpretation"
            ? { color: "var(--serious)" }
            : e.tag === "hypothesis"
              ? { color: "var(--critical)" }
              : undefined
        }
      >
        {e.tag}
      </span>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 600 }}>{e.label}</div>
        <div>{e.value}</div>
        <div className="muted" style={{ fontSize: 11 }}>{e.source}{e.note ? ` · ${e.note}` : ""}</div>
      </div>
    </div>
  );
}

/* ---------------- Coal ---------------- */

function CoalTab() {
  const { data, dark } = useApp();
  if (!data) return null;
  const d = data;
  const world24 = d.eiWorld.find(r => r.year === 2024);
  const world20 = d.eiWorld.find(r => r.year === 2020);

  const ev = useMemo<Evidence[]>(() => {
    const coal24 = worldSum(d, 2024, (cy) => cy.ei.coal_gen, "ei");
    const coal23 = worldSum(d, 2023, (cy) => cy.ei.coal_gen, "ei");
    const gen24 = worldSum(d, 2024, (cy) => cy.ei.elect, "ei");
    const prod24 = worldSum(d, 2024, (cy) => cy.ei.coal_prod_mt, "ei");
    const prod20 = worldSum(d, 2020, (cy) => cy.ei.coal_prod_mt, "ei");

    // Top producers 2024
    const prod = new Map<string, number>();
    for (const [iso, m] of d.countryByIso) {
      if (!isMatchedCountry(m, "ei")) continue;
      const v = m.get(2024)?.ei.coal_prod_mt;
      if (v != null) prod.set(iso, v);
    }
    const top5 = [...prod.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5);
    const top5sum = top5.reduce((s, [, v]) => s + v, 0);

    // US rebound
    const us = d.usAggregates.filter((r) => r.location === "US" && r.sector === 98);
    const c24 = us.find((r) => r.year === 2024)?.consumption ?? null;
    const c25 = us.find((r) => r.year === 2025)?.consumption ?? null;

    return [
      {
        label: "Matched-sample coal-fired generation",
        value: `${fmt(coal24)} TWh in 2024${coal23 != null ? ` (${fmtSignedPct(((coal24! - coal23) / coal23) * 100)} YoY)` : ""}; ≈${gen24 != null ? fmt((coal24! / gen24) * 100, 1) : NA}% of sample generation`,
        source: "EI; fixed countries with coal generation, production and total generation in all six joined years",
        tag: "verified",
      },
      {
        label: "Matched-sample coal production",
        value: `${fmt(prod24)} Mt in 2024 vs ${fmt(prod20)} Mt in 2020 (${prod20 != null ? fmtSignedPct(((prod24! - prod20) / prod20) * 100) : NA})`,
        source: "Energy Institute",
        tag: "verified",
      },
      {
        label: "Producer concentration",
        value: `Top-5 producers in sample = ${fmt(top5sum)} Mt in 2024 (${prod24 != null ? fmt((top5sum / prod24) * 100, 0) : NA}% of sample production): ${top5.map(([i, v]) => `${d.countryNames.get(i)} ${fmt(v)}`).join(", ")}`,
        source: "Energy Institute",
        tag: "verified",
      },
      {
        label: "US coal (electric power)",
        value:
          c24 != null && c25 != null
            ? `${fmt(c25)} short tons in 2025 vs ${fmt(c24)} in 2024 (${fmtSignedPct(((c25 - c24) / c24) * 100)})`
            : `2024: ${fmt(c24)} short tons`,
        source: "EIA aggregate, sector 98",
        tag: "verified",
        note: "Supplied snapshot; see U.S. view for consuming-state detail. Source vintages may differ.",
      },
      {
        label: "Production–generation divergence",
        value: "Production and domestic coal generation can diverge. Their different units and scopes do not identify exports, inventories or non-power use without additional data.",
        source: "Energy Institute (2020 vs 2024)",
        tag: "interpretation",
      },
    ];
  }, [d]);

  const coalSeries = YEARS.map((y) => worldSum(d, y, (cy) => cy.ei.coal_gen, "ei"));
  const coalSampleN = [...d.countryByIso.values()].filter(m => isMatchedCountry(m, "ei")).length;
  const opt: EChartsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: YEARS, ...axisStyle(dark), splitLine: { show: false } },
    yAxis: { type: "value", ...axisStyle(dark) },
    series: [
      {
        name: "Matched-sample coal generation (TWh)",
        type: "line",
        data: coalSeries,
        smooth: true,
        symbolSize: 5,
        lineStyle: { width: 2.5, color: entityColor("coal", dark ? "dark" : "light") },
        itemStyle: { color: entityColor("coal", dark ? "dark" : "light") },
      },
    ],
  };

  return (
    <>
      {world24 && <Ev e={{ label: "World coal generation (EI Total World)",
        value: `${fmt(world24.coal_generation_twh)} TWh in 2024; ${fmt(world24.coal_share_pct, 1)}% of EI fuel-level generation${world20 ? `; ${fmtSignedPct((world24.coal_generation_twh / world20.coal_generation_twh - 1) * 100)} since 2020` : ""}`,
        source: "EI WLD row only; no world/region/country summation", tag: "verified" }} />}
      {d.eiWorld.length > 0 && <ChartCard title="World coal generation (Total World row)" tag="EI · TWh"
        option={{ tooltip: { trigger: "axis" }, xAxis: { type: "category", data: YEARS, ...axisStyle(dark) },
          yAxis: { type: "value", ...axisStyle(dark) }, series: [{ name: "World coal generation", type: "line",
            data: YEARS.map(y => d.eiWorld.find(r => r.year === y)?.coal_generation_twh ?? null),
            itemStyle: { color: entityColor("coal", dark ? "dark" : "light") } }] }}
        note="Authoritative world row within the local EI snapshot; distinct from the matched-country series below. Source editions may revise observations." />}
      {ev.map((e) => (
        <Ev key={e.label} e={e} />
      ))}
      <ChartCard title="Matched-sample coal generation, 2020–2025" tag="Energy Institute" option={opt} note={`Fixed ${coalSampleN}-country sample with complete EI coal generation, production and total generation in all six years. Not a world total. Missing Ember observations do not remove available EI fields.`} />
    </>
  );
}

/* ---------------- Clean ---------------- */

function CleanTab() {
  const { data, dark } = useApp();
  if (!data) return null;
  const d = data;

  const ev = useMemo<Evidence[]>(() => {
    const clean24 = worldSum(d, 2024, (cy) => cy.ember.clean);
    const gen24 = worldSum(d, 2024, (cy) => cy.ember.generation);
    const clean20 = worldSum(d, 2020, (cy) => cy.ember.clean);
    const gen20 = worldSum(d, 2020, (cy) => cy.ember.generation);
    const ws20 = worldSum(d, 2020, (cy) => cy.ember.wind_solar);
    const ws24 = worldSum(d, 2024, (cy) => cy.ember.wind_solar);
    const dem20 = worldSum(d, 2020, (cy) => cy.ember.demand);
    const dem24 = worldSum(d, 2024, (cy) => cy.ember.demand);

    let met = 0;
    let below = 0;
    let notGrowing = 0;
    for (const [, m] of d.countryByIso) {
      const s = m.get(2024)?.ember.growth_status;
      if (s === "clean_growth_met_or_exceeded_demand_growth") met++;
      else if (s === "clean_growth_below_demand_growth") below++;
      else if (s === "demand_not_growing") notGrowing++;
    }

    return [
      {
        label: "Matched-sample clean share of generation",
        value: `${clean24 != null && gen24 ? fmt((clean24 / gen24) * 100, 1) : NA}% in 2024 vs ${clean20 != null && gen20 ? fmt((clean20 / gen20) * 100, 1) : NA}% in 2020`,
        source: "Ember; fixed 2020–2025 countries",
        tag: "verified",
      },
      {
        label: "Wind + solar generation",
        value: `${fmt(ws20)} → ${fmt(ws24)} TWh (2020→2024); CAGR ≈ ${ws20 != null && ws24 != null ? fmt((Math.pow(ws24 / ws20, 1 / 4) - 1) * 100, 1) : NA}%`,
        source: "Ember",
        tag: "verified",
      },
      {
        label: "Clean growth vs demand growth (2024 country statuses)",
        value: `${met} countries met/exceeded demand growth with clean; ${below} grew clean slower than demand; ${notGrowing} had no demand growth`,
        source: "Ember growth_status",
        tag: "verified",
      },
      {
        label: "Did clean absorb demand growth?",
        value:
          dem20 != null && dem24 != null && clean20 != null && clean24 != null && dem24 > dem20
            ? `Matched-sample clean added ${fmt(clean24 - clean20)} TWh vs demand growth of ${fmt(dem24 - dem20)} TWh — ${fmt(((clean24 - clean20) / (dem24 - dem20)) * 100, 0)}% ratio (descriptive)`
            : NA,
        source: "Ember (fixed 2020–2025 sample, 2020→2024 endpoint changes)",
        tag: "interpretation",
      },
    ];
  }, [d]);

  const shareSeries = YEARS.map((y) => {
    const c = worldSum(d, y, (cy) => cy.ember.clean);
    const g = worldSum(d, y, (cy) => cy.ember.generation);
    return c != null && g ? (c / g) * 100 : null;
  });
  const wsSeries = YEARS.map((y) => worldSum(d, y, (cy) => cy.ember.wind_solar));
  const opt: EChartsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: YEARS, ...axisStyle(dark), splitLine: { show: false } },
    yAxis: { type: "value", max: 100, ...axisStyle(dark), axisLabel: { ...axisStyle(dark).axisLabel, formatter: (v: number) => v + "%" } },
    series: [
      { name: "Clean share of generation", type: "line", data: shareSeries, smooth: true, symbolSize: 5, lineStyle: { width: 2.5, color: entityColor("clean", dark ? "dark" : "light") }, itemStyle: { color: entityColor("clean", dark ? "dark" : "light") } },
    ],
  };
  const wsOpt: EChartsOption = {
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: YEARS, ...axisStyle(dark), splitLine: { show: false } },
    yAxis: { type: "value", ...axisStyle(dark) },
    series: [
      { name: "Wind + solar (TWh)", type: "line", data: wsSeries, smooth: true, symbolSize: 5, lineStyle: { width: 2.5, color: entityColor("wind_solar", dark ? "dark" : "light") }, itemStyle: { color: entityColor("wind_solar", dark ? "dark" : "light") }, areaStyle: { opacity: 0.12 } },
    ],
  };

  return (
    <>
      {ev.map((e) => (
        <Ev key={e.label} e={e} />
      ))}
      <ChartCard title="Matched-sample clean share of generation" tag="Ember" option={opt} note="Fixed six-year country membership; ratio of generation sums, not average country shares." />
      <ChartCard title="Matched-sample wind + solar generation" tag="Ember" option={wsOpt} defaultCollapsed />
    </>
  );
}

/* ---------------- Utility ---------------- */

function UtilityTab() {
  const { data } = useApp();
  if (!data) return null;
  const d = data;

  const ev = useMemo<Evidence[]>(() => {
    const us = d.usAggregates.filter((r) => r.location === "US" && r.sector === 98);
    const p23 = us.find((r) => r.year === 2023)?.price ?? null;
    const p24 = us.find((r) => r.year === 2024)?.price ?? null;
    const cons24 = us.find((r) => r.year === 2024)?.consumption ?? null;
    // Stocks only exist in state rows; sum base-sector stocks for 2024.
    let stocks = 0;
    let anyStocks = false;
    for (const [code] of d.stateByCode) {
      const rows = d.stateByCode.get(code)?.get(2024);
      if (!rows) continue;
      for (const r of rows) {
        if (![1, 2, 3].includes(r.sector)) continue;
        if (r.stocks != null) {
          stocks += r.stocks;
          anyStocks = true;
        }
      }
    }

    return [
      {
        label: "US delivered coal price (electric power, national)",
        value:
          p24 != null && p23 != null
            ? `${fmt(p24, 2)} $/short ton in 2024 vs ${fmt(p23, 2)} in 2023 (${fmtSignedPct(((p24 - p23) / p23) * 100)})`
            : NA,
        source: "EIA aggregate, sector 98",
        tag: "verified",
      },
      {
        label: "US inventory buffer",
        value:
          anyStocks && cons24 != null && cons24 > 0
            ? `${fmt(stocks)} short tons on hand (2024) ≈ ${fmt((stocks / cons24) * 12, 1)} months of the 2024 electric-power burn rate (states' base sectors)`
            : NA,
        source: "EIA state rows (base sectors) vs national 98",
        tag: "interpretation",
        note: "Power-sector stocks only (sectors 1/2/3). Partial state reporting would make this incomplete; missing is not zero.",
      },
      {
        label: "Price sensitivity to sector mix",
        value: "State prices vary widely by sector and region; a coal-heavy state's delivered price tracks its own logistics, not the national average.",
        source: "EIA state rows",
        tag: "interpretation",
      },
      {
        label: "Retail rate pass-through",
        value: "Whether falling coal prices reach retail electricity rates depends on generation mix and fuel-hedge structures — not observable from this dataset.",
        source: "— (data gap)",
        tag: "hypothesis",
        note: "Needs utility financials / EIA electric-power data (not in scope tonight).",
      },
    ];
  }, [d]);

  return (
    <>
      {ev.map((e) => (
        <Ev key={e.label} e={e} />
      ))}
    </>
  );
}

/* ---------------- Gas & grid ---------------- */

function GasTab() {
  const { data, dark } = useApp();
  if (!data) return null;
  const d = data;

  const ev = useMemo<Evidence[]>(() => {
    const us = d.countryByIso.get("USA");
    const gas20 = us?.get(2020)?.ei.gas_gen ?? null;
    const gas24 = us?.get(2024)?.ei.gas_gen ?? null;
    const nuc20 = us?.get(2020)?.ei.nuclear_gen ?? null;
    const nuc24 = us?.get(2024)?.ei.nuclear_gen ?? null;
    const dem20 = us?.get(2020)?.ember.demand ?? null;
    const dem24 = us?.get(2024)?.ember.demand ?? null;
    const clean20 = us?.get(2020)?.ember.clean ?? null;
    const clean24 = us?.get(2024)?.ember.clean ?? null;

    return [
      {
        label: "US gas-fired generation",
        value: `${fmt(gas20)} → ${fmt(gas24)} TWh (2020→2024)${gas20 != null && gas24 != null ? ` (${fmtSignedPct(((gas24 - gas20) / gas20) * 100)})` : ""}`,
        source: "Energy Institute",
        tag: "verified",
      },
      {
        label: "US nuclear generation",
        value: `${fmt(nuc20)} → ${fmt(nuc24)} TWh (2020→2024)`,
        source: "Energy Institute",
        tag: "verified",
      },
      {
        label: "US demand vs clean growth",
        value:
          dem20 != null && dem24 != null && clean20 != null && clean24 != null
            ? `Demand ${fmt(dem20)} → ${fmt(dem24)} TWh; clean ${fmt(clean20)} → ${fmt(clean24)} TWh (Δ ${fmt(clean24 - clean20)})`
            : NA,
        source: "Ember",
        tag: "verified",
      },
      {
        label: "Substitution vs addition",
        value: "Clean generation grew alongside demand and gas in the U.S. over 2020–2024. These output changes do not identify causal fuel displacement or installed capacity.",
        source: "Energy Institute + Ember (US)",
        tag: "interpretation",
      },
    ];
  }, [d]);

  const gasSeries = YEARS.map((y) => d.countryByIso.get("USA")?.get(y)?.ei.gas_gen ?? null);
  const cleanSeries = YEARS.map((y) => d.countryByIso.get("USA")?.get(y)?.ember.clean ?? null);
  const opt: EChartsOption = {
    tooltip: { trigger: "axis" },
    legend: { show: true, top: 0, right: 0, textStyle: { fontSize: 10.5 } },
    xAxis: { type: "category", data: YEARS, ...axisStyle(dark), splitLine: { show: false } },
    yAxis: { type: "value", ...axisStyle(dark) },
    series: [
      { name: "US gas gen (EI)", type: "line", data: gasSeries, symbolSize: 4, lineStyle: { width: 2, color: entityColor("gas", dark ? "dark" : "light") }, itemStyle: { color: entityColor("gas", dark ? "dark" : "light") } },
      { name: "US clean gen (Ember)", type: "line", data: cleanSeries, symbolSize: 4, lineStyle: { width: 2.5, color: entityColor("clean", dark ? "dark" : "light") }, itemStyle: { color: entityColor("clean", dark ? "dark" : "light") } },
    ],
  };

  return (
    <>
      {ev.map((e) => (
        <Ev key={e.label} e={e} />
      ))}
      <ChartCard title="US gas vs clean generation" tag="EI + Ember" option={opt} note="Different sources; levels may not reconcile exactly. Both series shown on one TWh axis." />
    </>
  );
}

/* ---------------- Cross-country ---------------- */

function CrossTab() {
  const { data } = useApp();
  if (!data) return null;
  const d = data;

  const rows = useMemo(() => {
    return FOCUS.map((iso) => {
      const c24 = d.countryByIso.get(iso)?.get(2024);
      const c20 = d.countryByIso.get(iso)?.get(2020);
      return {
        iso,
        name: d.countryNames.get(iso) ?? iso,
        cshare24: c24?.ember.clean_share ?? null,
        coal24: c24?.ei.coal_gen ?? null,
        coal20: c20?.ei.coal_gen ?? null,
        dem24: c24?.ember.demand ?? null,
      };
    });
  }, [d]);

  // Pathway counts across material countries (2020 and 2024 coal gen both > 20 TWh).
  const pathways = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const [, m] of d.countryByIso) {
      const c20 = m.get(2020);
      const c24 = m.get(2024);
      if (!c20 || !c24) continue;
      if (c20.ei.coal_gen == null || c24.ei.coal_gen == null) continue;
      if (c20.ei.coal_gen <= 20 || c24.ei.coal_gen <= 20) continue;
      const clean20 = c20.ember.clean, clean24 = c24.ember.clean;
      if (clean20 == null || clean24 == null || clean20 <= 20 || clean24 <= 20) continue;
      const dc = (c24.ei.coal_gen - c20.ei.coal_gen) / c20.ei.coal_gen;
      let label = "mixed";
      const cleanChange = clean24 / clean20 - 1;
      if (dc < -0.05 && cleanChange > .05) label = "transition";
      else if (dc > 0.05 && cleanChange > .05) label = "coexistence";
      else if (dc < -0.05) label = "coal_decline";
      else if (dc > 0.05) label = "coal_growth";
      counts[label] = (counts[label] ?? 0) + 1;
    }
    return counts;
  }, [d]);

  return (
    <>
      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-head"><h3>Focus markets, 2024</h3></div>
        <div className="card-body">
          <table className="tbl">
            <thead>
              <tr>
                <th>Country</th>
                <th className="num">Clean share 2024</th>
                <th className="num">Coal gen 2024 (TWh)</th>
                <th className="num">Δ coal 2020→24</th>
                <th className="num">Demand 2024 (TWh)</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.iso}>
                  <td>{r.name}</td>
                  <td className="num">{r.cshare24 != null ? fmt(r.cshare24, 1) + "%" : NA}</td>
                  <td className="num">{fmt(r.coal24)}</td>
                  <td className="num">{r.coal20 != null && r.coal24 != null ? fmtSigned(r.coal24 - r.coal20) : NA}</td>
                  <td className="num">{fmt(r.dem24)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="note">Coal gen: Energy Institute. Clean share/demand: Ember. Null = not reported.</div>
        </div>
      </div>
      <div className="card" style={{ marginBottom: 12 }}>
        <div className="card-head"><h3>Pathway mix, material countries (&gt;20 TWh coal and clean, 2020 &amp; 2024)</h3></div>
        <div className="card-body">
          <div className="kv">
            {Object.entries(pathways).map(([k, v]) => (
              <span key={k} style={{ display: "contents" }}>
                <span className="k">{k.replace(/_/g, " ")}</span>
                <span className="v">{v}</span>
              </span>
            ))}
          </div>
          <div className="note">
            Thresholds: coal and clean generation changes ±5%; both fuel groups must
            exceed 20 TWh in both endpoint years. Descriptive categories do not establish causality.
          </div>
        </div>
      </div>
    </>
  );
}
