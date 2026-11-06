import type { EChartsOption } from "echarts";
import { useApp } from "../state/AppState";
import { YEARS } from "../data/types";
import { ChartCard, axisStyle } from "./ChartCard";
import { stateValue } from "../viz/stateValue";
import { annualChange, coalDemandMarkets } from "../viz/usTransition";
import { fmt, fmtSignedPct } from "../viz/format";
import { USMap } from "./USMap";
import { USLegend } from "./USLegend";

export function StatePanel() {
  const { data, year, dark, selectedState, selectState } = useApp();
  if (!data) return null;
  const markets = coalDemandMarkets(data, year);
  const leaders = markets.slice(0, 5);
  const growingLeaders = leaders.filter(m => m.growth != null && m.growth > 0);
  const national = YEARS.map(y => data.usAggregates.find(r => r.location === "US" && r.sector === 98 && r.year === y)?.consumption ?? null);
  const nationalGrowth = annualChange(national[YEARS.indexOf(year)], national[YEARS.indexOf(year - 1)]);
  const ax = axisStyle(dark);
  const chart = (values: (number | null)[], name: string): EChartsOption => ({
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: YEARS, ...ax },
    yAxis: { type: "value", min: 0, name: "Million short tons", ...ax },
    series: [{ name, type: "bar", data: values.map(v => v == null ? null : v / 1e6), itemStyle: { color: dark ? "#e66767" : "#c53030", borderRadius: [3, 3, 0, 0] } }],
  });
  const stateCurrent = selectedState ? stateValue(data, selectedState, year, "power") : null;
  const statePrior = selectedState ? stateValue(data, selectedState, year - 1, "power") : null;
  const stateGrowth = annualChange(stateCurrent, statePrior);
  const stateName = selectedState ? data.stateNames.get(selectedState) ?? selectedState : "";
  return <section className="us-state-markets" aria-label="State coal-demand markets">
    <h3>Priority coal-demand markets · {year}</h3>
    <p className="note">Ranked by reported electric-power coal consumption. Larger markets identify customer demand; growth adds context for a selective coal allocation.</p>
    {growingLeaders.length > 0 && <p className="us-market-takeaway"><strong>Large markets with rising demand:</strong> {growingLeaders.slice(0, 3).map(m => m.name).join(", ")}. Prioritize understanding suppliers serving these markets; check the full history before increasing exposure.</p>}
    {leaders.length > 0 ? <div className="us-market-table"><table className="tbl">
      <thead><tr><th>Demand market</th><th className="num">Million short tons</th><th className="num">Annual change</th><th>Demand signal</th></tr></thead>
      <tbody>{leaders.map((m, i) => <tr key={m.code}>
        <td><button className="us-market-link" onClick={() => selectState(m.code)} aria-pressed={selectedState === m.code}>{i+1}. {m.name}</button></td>
        <td className="num">{fmt(m.value / 1e6, 1)}</td>
        <td className="num">{fmtSignedPct(m.growth)}</td>
        <td>{m.growth == null ? "Change unavailable" : m.growth > 0 ? "Growing demand" : m.growth < 0 ? "Declining demand" : "Stable demand"}</td>
      </tr>)}</tbody>
    </table></div> : <p>No state power-sector consumption is reported for {year}.</p>}
    <p className="note">EIA base sectors 1+2+3 only. State clean-generation data is not in the supplied files. States locate coal users, not mines; market size alone does not establish supplier profitability.</p>
    <details className="us-state-map-details">
      <summary>Explore the state coal-demand map</summary>
      <div className="us-state-map-stage"><USMap /><USLegend /></div>
    </details>
    {selectedState && <section className="card us-state-detail" aria-label="Selected coal-demand market">
      <div className="card-head"><h3>{stateName} · power-sector coal</h3><button className="iconbtn" aria-label="Close state detail" onClick={() => selectState(null)}>✕</button></div>
      <div className="card-body">
        <dl className="kv"><dt className="k">Consumption · {year}</dt><dd className="v">{fmt(stateCurrent)} short tons</dd>
          <dt className="k">Change vs {year-1}</dt><dd className="v">{fmtSignedPct(stateGrowth)}</dd></dl>
        <p>{stateGrowth == null ? "Compare the available history; an annual growth rate cannot be calculated for this selection." : stateGrowth > 0
          ? "Rising power demand supports closer attention to suppliers serving this market. Test whether the increase persists."
          : stateGrowth < 0 ? "Consumption is declining. A large existing market still needs a clear persistence case before increasing coal exposure."
          : "Demand is unchanged. Assess the multi-year direction before increasing coal exposure."}</p>
        <ChartCard title={`${stateName} power-sector coal history`} tag="EIA · million short tons"
          option={chart(YEARS.map(y => stateValue(data, selectedState, y, "power")), "Power-sector coal")}
          note="Consumption sums reported sectors 1+2+3. Missing observations remain blank; no state clean-generation values are inferred." />
      </div>
    </section>}
    <details className="us-national-coal-check">
      <summary>Check the national coal-consumption evidence · EIA</summary>
      <p>U.S. power-sector coal consumption: {fmt(national[YEARS.indexOf(year)] == null ? null : national[YEARS.indexOf(year)]! / 1e6, 1)} million short tons in {year}; annual change {fmtSignedPct(nationalGrowth)}.</p>
      <ChartCard title="US electric power coal, 2020–2025" tag="EIA national sector 98" option={chart(national, "National coal consumption")}
        note="National sector 98 is kept separate from state base-sector sums. Consumption in short tons and electricity generation in TWh are different measures." />
    </details>
  </section>;
}
