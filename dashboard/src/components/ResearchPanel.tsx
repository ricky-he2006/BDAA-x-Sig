import { GrowthSection } from "./GrowthSection";
import { useApp } from "../state/AppState";
import { YEARS } from "../data/types";
import { fmt, fmtSignedPct } from "../viz/format";
import { percentChange } from "../viz/researchMetrics";
import { CoalCleanChart, EnergyDefinition } from "./CoalCleanCharts";

export function ResearchPanel() {
  const { data, dark, selectCountry, setView } = useApp();
  if (!data) return null;
  const years = YEARS.filter(y => y <= 2024);
  // Use the same countries and years for both series. Never turn missing data into zero.
  const countries = [...data.countryByIso.entries()].filter(([, records]) => years.every(y => {
    const r = records.get(y);
    return r != null && r.ember.clean != null && r.ei.coal_gen != null;
  }));
  const clean = years.map(y => countries.length ? countries.reduce((sum, [, records]) => sum + records.get(y)!.ember.clean!, 0) : null);
  const coal = years.map(y => countries.length ? countries.reduce((sum, [, records]) => sum + records.get(y)!.ei.coal_gen!, 0) : null);
  const first = years[0], last = years[years.length - 1];
  return <div>
    <div className="panel-title">Coal &amp; clean energy</div>
    <p className="panel-sub">Where are the clean-energy and coal investment opportunities?</p>
    <EnergyDefinition />
    <div className="card"><div className="card-head"><h3 style={{ color: dark ? "#3987e5" : "#2a78d6" }}>Blue: explore clean-energy investment</h3></div>
      <div className="card-body">Start with countries generating a lot of clean electricity or with a high clean share. Check whether clean output is growing to support the investment story.</div></div>
    <div className="card"><div className="card-head"><h3 style={{ color: dark ? "#e66767" : "#c53030" }}>Red: explore coal investment</h3></div>
      <div className="card-body">Look for countries producing and using a lot of coal. Compare production, coal energy use and coal-fired electricity to identify large coal markets. Check whether activity is growing before making the investment case.</div></div>
    <p className="note">Colors show industry activity. They identify markets to investigate; they do not measure company returns or valuation. A country can be strong in both themes.</p>
    <GrowthSection />
    <p className="note">Fixed {countries.length}-country sample, {first}–{last}; not full-world totals. Both series use the same countries with reported generation in every year. The 2025 growth section above uses its own fixed six-year sample.</p>
    <div className="card"><div className="card-head"><h3>What changed from {first} to {last}?</h3></div>
      <div className="card-body"><table className="tbl"><thead><tr><th>Electricity source</th><th>{first} (TWh)</th><th>{last} (TWh)</th><th>Change</th></tr></thead>
        <tbody>{[["Clean energy", clean], ["Coal", coal]].map(([label, values]) => {
          const series = values as (number | null)[];
          return <tr key={label as string}><td>{label as string}</td><td>{fmt(series[0])}</td><td>{fmt(series[series.length - 1])}</td><td>{fmtSignedPct(percentChange(series[0], series[series.length - 1]))}</td></tr>;
        })}</tbody></table>
        <p className="note">TWh measures electricity generated. Both sources can grow at the same time; clean growth alone does not show that coal was replaced.</p>
      </div></div>
    <CoalCleanChart title="Coal & clean electricity over time" years={years} clean={clean} coal={coal} dark={dark}
      note="Compare direction and size of change within this fixed country sample." />
    <div className="card"><div className="card-head"><h3>Compare countries, {last}</h3></div><div className="card-body">
      <table className="tbl"><thead><tr><th>Country</th><th>Clean (TWh)</th><th>Coal (TWh)</th><th>Clean share</th><th>Coal share</th><th>Coal production (Mt)</th><th>Coal energy use (EJ)</th></tr></thead>
        <tbody>{["USA", "CHN", "IND", "DEU", "GBR"].map(iso => {
          const r = data.countryByIso.get(iso)?.get(last);
          if (!r) return null;
          return <tr key={iso}><td><button className="iconbtn" onClick={() => { selectCountry(iso); setView("world"); }}>{r.name}</button></td>
            <td>{fmt(r.ember.clean)}</td><td>{fmt(r.ei.coal_gen)}</td><td>{fmt(r.ember.clean_share)}%</td><td>{fmt(r.coal_share)}%</td><td>{fmt(r.ei.coal_prod_mt)}</td><td>{fmt(r.ei.coal_tes_ej)}</td></tr>;
        })}</tbody></table>
      <p className="note">Coal energy use is total energy supply (TES), including uses beyond electricity. Mt = million tonnes; EJ = exajoules. This table includes available countries outside the fixed trend sample.</p>
    </div></div>
  </div>;
}
