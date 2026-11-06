import { useState } from "react";
import { useApp } from "../state/AppState";
import { YEARS } from "../data/types";
import { CoalCleanChart, EnergyDefinition } from "./CoalCleanCharts";
import { fmt, fmtPct, fmtSignedPct } from "../viz/format";
import { annualChange } from "../viz/usTransition";
import { StatePanel } from "./StatePanel";

export function USView() {
  const { data, year, dark } = useApp();
  const [measure, setMeasure] = useState<"generation" | "share">("generation");
  if (!data) return null;
  const records = data.countryByIso.get("USA");
  const current = records?.get(year), previous = records?.get(year - 1);
  const share = measure === "share";
  const clean = YEARS.map(y => share ? records?.get(y)?.ember.clean_share ?? null : records?.get(y)?.ember.clean ?? null);
  const coal = YEARS.map(y => share ? records?.get(y)?.coal_share ?? null : records?.get(y)?.ei.coal_gen ?? null);
  const cleanGrowth = annualChange(current?.ember.clean, previous?.ember.clean);
  const coalGrowth = annualChange(current?.ei.coal_gen, previous?.ei.coal_gen);
  const snapshot = [
    { name: "Clean electricity", value: share ? current?.ember.clean_share : current?.ember.clean, growth: cleanGrowth, css: "clean", source: "Ember" },
    { name: "Coal electricity", value: share ? current?.coal_share : current?.ei.coal_gen, growth: coalGrowth, css: "coal", source: "Energy Institute" },
  ];
  return <div className="us-transition">
    <header className="us-transition-head">
      <p className="us-eyebrow">UNITED STATES · {year}</p>
      <h2>Coal &amp; clean electricity</h2>
      <p>Compare the national transition, then see where demand supports the remaining coal market.</p>
    </header>
    <div className="pillrow" role="group" aria-label="U.S. electricity measure">
      <button className={`pill${!share ? " active" : ""}`} aria-pressed={!share} onClick={() => setMeasure("generation")}>Generation · TWh</button>
      <button className={`pill${share ? " active" : ""}`} aria-pressed={share} onClick={() => setMeasure("share")}>Share · %</button>
    </div>
    <div className="us-energy-snapshot">
      {snapshot.map(s => <section key={s.name} className={`card us-energy-stat ${s.css}`} aria-label={`${s.name} snapshot`}>
        <h3>{s.name}</h3>
        <div className="us-energy-value">{share ? fmtPct(s.value) : `${fmt(s.value, 1)} TWh`}</div>
        <p className="note">{s.growth == null ? "Annual generation change unavailable" : `${fmtSignedPct(s.growth)} generation vs ${year - 1}`}</p>
        <span className="note">{s.source}</span>
      </section>)}
    </div>
    <EnergyDefinition />
    <CoalCleanChart title={share ? "U.S. coal & clean electricity share" : "U.S. coal & clean electricity generation"}
      years={YEARS} clean={clean} coal={coal} dark={dark} share={share}
      note="Blue = clean; red = coal. Compare annual output and the longer trend. Generation growth does not establish investment returns." />
    <section className="us-investment-bridge">
      <h3>From the national thesis to state coal markets</h3>
      <p>Favor clean-growth exposure nationally. Within a selective coal allocation, focus research on suppliers serving large power-demand markets with sustained consumption. The state data below identifies those markets.</p>
    </section>
    <StatePanel />
  </div>;
}
