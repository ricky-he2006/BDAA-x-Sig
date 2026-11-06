import { Fragment } from "react";
import { useApp } from "../state/AppState";
import { YEARS } from "../data/types";
import { fmt, fmtPct } from "../viz/format";
import { isReportedNumber } from "./CountryChart";
import { CoalCleanChart, EnergyDefinition } from "./CoalCleanCharts";

export function CountryPanel() {
  const { data, year, selectedIso, selectCountry, dark } = useApp();
  const name = selectedIso ? data?.countryNames.get(selectedIso) : null;
  if (!data || !selectedIso || !name) return <aside className="side">
    <div className="panel-title">Coal &amp; clean energy</div>
    <p>Select a country on the globe or search to compare coal and clean electricity over time.</p>
    <EnergyDefinition />
  </aside>;
  const records = data.countryByIso.get(selectedIso);
  const current = records?.get(year);
  const clean = YEARS.map(y => records?.get(y)?.ember.clean ?? null);
  const coal = YEARS.map(y => records?.get(y)?.ei.coal_gen ?? null);
  const cleanShare = YEARS.map(y => records?.get(y)?.ember.clean_share ?? null);
  const coalShare = YEARS.map(y => records?.get(y)?.coal_share ?? null);
  const metrics = [
    { label: "Clean generation", value: current?.ember.clean, share: false },
    { label: "Coal-fired generation", value: current?.ei.coal_gen, share: false },
    { label: "Clean share", value: current?.ember.clean_share, share: true },
    { label: "Coal production", value: current?.ei.coal_prod_mt, share: false, unit: "Mt" },
    { label: "Coal energy use (supply)", value: current?.ei.coal_tes_ej, share: false, unit: "EJ" },
    { label: "Coal share", value: current?.coal_share, share: true },
  ].filter(m => isReportedNumber(m.value));
  const sources = [isReportedNumber(current?.ember.clean) ? "Ember" : null,
    isReportedNumber(current?.ei.coal_gen) ? "Energy Institute" : null].filter(Boolean);
  const columns = [
    { label: "Clean TWh", pick: (y: number) => records?.get(y)?.ember.clean },
    { label: "Coal TWh (EI)", pick: (y: number) => records?.get(y)?.ei.coal_gen },
    { label: "Coal production Mt", pick: (y: number) => records?.get(y)?.ei.coal_prod_mt },
    { label: "Coal energy use EJ", pick: (y: number) => records?.get(y)?.ei.coal_tes_ej },
    { label: "Clean %", pick: (y: number) => records?.get(y)?.ember.clean_share },
    { label: "Coal %", pick: (y: number) => records?.get(y)?.coal_share },
  ].filter(c => YEARS.some(y => isReportedNumber(c.pick(y))));
  return <aside className="side">
    <div style={{ display: "flex", justifyContent: "space-between" }}>
      <div><div className="panel-title">{name}</div><p className="panel-sub">Coal &amp; clean electricity · {year}</p></div>
      <button className="iconbtn" aria-label="Close" onClick={() => selectCountry(null)}>✕</button>
    </div>
    <EnergyDefinition />
    <p className="note"><strong>Investment themes:</strong> blue maps highlight clean electricity markets; red maps highlight coal generation, production or energy use. Use the trends below to explain whether activity is growing or shrinking.</p>
    <p className="note" aria-label="Country source availability">{sources.length
      ? `${year} sources: ${sources.join(" · ")}.`
      : `No reported values for ${year}. Available historical observations are shown below.`}</p>
    {metrics.length > 0 && <div className="card"><div className="card-head"><h3>{year} snapshot</h3></div>
      <div className="card-body kv">{metrics.map(m => <Fragment key={m.label}>
        <span className="k">{m.label}</span><span className="v">{m.share ? fmtPct(m.value) : `${fmt(m.value)} ${"unit" in m ? m.unit : "TWh"}`}</span>
      </Fragment>)}</div></div>}
    <CoalCleanChart title="Coal & clean electricity generation" years={YEARS} clean={clean} coal={coal} dark={dark}
      note="Compare output over time. TWh measures how much electricity was generated; growth in clean electricity alone does not prove coal fell." />
    <CoalCleanChart title="Coal & clean electricity share" years={YEARS} clean={cleanShare} coal={coalShare} dark={dark} share
      note="Share measures the percentage of electricity generation from each group." />
    {columns.length > 0 && <details><summary>View the numbers</summary><table className="tbl">
      <thead><tr><th>Year</th>{columns.map(c => <th key={c.label}>{c.label}</th>)}</tr></thead>
      <tbody>{YEARS.filter(y => columns.some(c => isReportedNumber(c.pick(y)))).map(y => <tr key={y}>
        <td>{y}</td>{columns.map(c => <td key={c.label}>{fmt(c.pick(y))}</td>)}</tr>)}</tbody>
    </table></details>}
  </aside>;
}
