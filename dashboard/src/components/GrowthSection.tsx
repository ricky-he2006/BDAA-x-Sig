import type { EChartsOption } from "echarts";
import { useApp } from "../state/AppState";
import { YEARS } from "../data/types";
import { fmtPct, fmtSigned, fmtSignedPct } from "../viz/format";
import { growthChanges, growthTotals, matchedGrowthCountries } from "../viz/growthComparison";
import { ChartCard, axisStyle } from "./ChartCard";

export function GrowthSection() {
  const { data, dark } = useApp();
  if (!data) return null;
  const countries = matchedGrowthCountries(data, YEARS);
  const changes = growthChanges(growthTotals(countries, YEARS));
  const latest = changes.find(r => r.year === 2025);
  const us = countries.filter(([iso]) => iso === "USA");
  const usLatest = growthChanges(growthTotals(us, YEARS)).find(r => r.year === 2025);
  const scopes = [
    { label: `Matched sample (${countries.length} countries)`, countries },
    { label: "Sample excluding U.S.", countries: countries.filter(([iso]) => iso !== "USA") },
    { label: "United States", countries: us },
    { label: "China", countries: countries.filter(([iso]) => iso === "CHN") },
    { label: "India", countries: countries.filter(([iso]) => iso === "IND") },
  ].map(scope => ({ label: scope.label, change: growthChanges(growthTotals(scope.countries, YEARS)).find(r => r.year === 2025) }));
  const option: EChartsOption = {
    tooltip: { trigger: "axis" }, legend: { show: true },
    xAxis: { type: "category", data: changes.map(r => r.year), ...axisStyle(dark) },
    yAxis: { type: "value", name: "Δ TWh", ...axisStyle(dark) },
    series: [
      { name: "Clean growth", type: "bar", data: changes.map(r => r.clean), itemStyle: { color: dark ? "#3987e5" : "#2a78d6" } },
      { name: "Demand growth", type: "bar", data: changes.map(r => r.demand), itemStyle: { color: dark ? "#c3c2b7" : "#52514e" } },
      { name: "Coal change", type: "line", data: changes.map(r => r.coal), itemStyle: { color: dark ? "#e66767" : "#c53030" }, lineStyle: { width: 2.5 } },
    ],
  };
  return <section aria-label="Clean growth and electricity demand">
    <div className="card"><div className="card-head"><h3>Is clean electricity catching up with demand?</h3></div>
      <div className="card-body">
        <p>Compare the extra clean electricity generated each year with the extra electricity people use. When clean growth exceeds demand growth, there is less room for fossil generation in the electricity mix.</p>
        {latest ? <p><strong>2025: {latest.demand > 0 && latest.clean >= latest.demand ? "clean growth exceeded demand growth" : "compare clean and demand growth"}.</strong>{" "}
          In this sample, clean generation changed by {fmtSigned(latest.clean)} TWh versus {fmtSigned(latest.demand)} TWh of demand change.
          {latest.coveredPct != null && ` Clean additions were ${fmtPct(latest.coveredPct)} of demand growth.`}{" "}
          Coal generation changed by {fmtSigned(latest.coal)} TWh ({fmtSignedPct(latest.coalPct)}).
        </p> : <p>No complete country sample is available for this comparison.</p>}
        <p className="note">Fixed {countries.length}-country sample with clean, demand and coal observations in every year from 2020–2025; not a world total. Clean and demand: Ember. Coal generation: Energy Institute. TWh compares absolute additions; percentages of growth are descriptive, not causal attribution.</p>
      </div></div>
    {changes.length > 0 && <ChartCard title="Annual clean growth vs electricity demand growth" tag="2021–2025 · Δ TWh" option={option}
      analysis="Compare the blue and gray bars each year; the red line shows whether coal generation rose or fell."
      note="Each point compares that year with the previous year. Clean is part of electricity supply; catching up means meeting additional demand, not supplying all electricity. Imports, gas and other sources also affect the balance." />}
    <div className="card"><div className="card-head"><h3>2025: does the U.S. follow a different path?</h3></div>
      <div className="card-body">
        {usLatest ? <p>U.S. clean generation changed by {fmtSigned(usLatest.clean)} TWh versus {fmtSigned(usLatest.demand)} TWh of demand change
          {usLatest.coveredPct != null && ` (${fmtPct(usLatest.coveredPct)} coverage of demand growth)`}.
          {" "}Coal generation changed by {fmtSignedPct(usLatest.coalPct)}.
          {latest && latest.coal < 0 && usLatest.coal > 0 ? " The U.S. coal rebound ran against the sample’s overall decline; it was a major exception, not the only country where coal rose." : " Compare this with the sample and other large markets below."}
        </p> : <p>The U.S. does not have a complete series for this comparison.</p>}
        <div style={{ overflowX: "auto" }}><table className="tbl" aria-label="2025 growth comparison">
          <thead><tr><th>Market</th><th>Clean change (TWh)</th><th>Demand change (TWh)</th><th>Clean / demand growth</th><th>Coal change (TWh)</th><th>Coal change (%)</th></tr></thead>
          <tbody>{scopes.filter(s => s.change).map(({ label, change: c }) => <tr key={label}><td>{label}</td>
            <td>{fmtSigned(c!.clean)}</td><td>{fmtSigned(c!.demand)}</td><td>{fmtPct(c!.coveredPct)}</td><td>{fmtSigned(c!.coal)}</td><td>{fmtSignedPct(c!.coalPct)}</td></tr>)}</tbody>
        </table></div>
        <p className="note">Ratios are blank when demand did not grow. China and India are included only if they meet the same six-year coverage requirement. Coal here means electricity generation, not all coal consumption.</p>
        <details><summary>Global context and the U.S. exception</summary>
          <p className="note"><a href="https://ember-energy.org/latest-insights/global-electricity-review-2026/2025-in-review/" target="_blank" rel="noreferrer">Ember’s Global Electricity Review 2026</a> reports that global clean additions exceeded demand growth in 2025 and coal generation declined. Its world estimates use broader coverage than this dashboard’s matched sample.</p>
          <p className="note"><a href="https://www.iea.org/reports/global-energy-review-2026/coal" target="_blank" rel="noreferrer">IEA’s Global Energy Review 2026</a> attributes the U.S. coal rebound to electricity demand, higher gas prices and policies slowing coal retirements. Its coal consumption measure differs from the generation series above. A single year does not establish a lasting coal decline or rebound.</p>
        </details>
      </div></div>
  </section>;
}
