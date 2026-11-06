import { useMemo } from "react";
import { useApp } from "../state/AppState";
import { YEARS } from "../data/types";
import { emberPanel, percentChange } from "../viz/researchMetrics";
import { fmt, fmtSignedPct } from "../viz/format";
import { CountryDirectory } from "./CountryDirectory";

const DOWNLOADS = [
  ["country_year.csv", "All plotted country/year observations"],
  ["us_state_year.csv", "U.S. state/base-sector data"],
  ["us_aggregates.csv", "Separate EIA national/regional aggregates"],
  ["ei_world.csv", "EI Total World observations"],
  ["matched_2020_2024.csv", "Main presentation: fixed 2020–2024 panel"],
  ["matched_2020_2025.csv", "2025 watch: fixed six-year panel"],
  ["country_pathways.csv", "Material-country pathway evidence"],
  ["claim_evidence.csv", "Claim-to-calculation references"],
  ["thesis.md", "Recommendation, horizon and risks"],
  ["sources.md", "Sources, definitions and limitations"],
  ["ei_provenance.json", "Energy Institute provenance record"],
  ["data_dictionary.md", "Field definitions and units"],
  ["data_quality.md", "Source quality report"],
] as const;

export function DataPanel() {
  const { data } = useApp();
  const panel = useMemo(() => data ? emberPanel(data, YEARS.slice(0, 5)) : [], [data]);
  if (!data) return null;
  const first = panel[0], last = panel[panel.length - 1];
  const world20 = data.eiWorld.find(r => r.year === 2020);
  const world24 = data.eiWorld.find(r => r.year === 2024);
  const power = (y: number) => data.usAggregates.find(r => r.location === "US" && r.year === y && r.sector === 98)?.consumption;
  const claims = [
    ["E01", "Clean generation, 2020–2024", percentChange(first?.clean, last?.clean), `Ember; ${first?.countries ?? 0} fixed countries`],
    ["E02", "All-fossil generation, 2020–2024", percentChange(first?.fossil, last?.fossil), "Same fixed Ember panel; all fossil is not coal"],
    ["E03", "World coal generation, 2020–2024", percentChange(world20?.coal_generation_twh, world24?.coal_generation_twh), "EI Total World row only"],
    ["E04", "U.S. power coal consumption, 2020–2024", percentChange(power(2020), power(2024)), "EIA national sector 98; short tons"],
    ["E05", "U.S. power coal consumption, 2024–2025", percentChange(power(2024), power(2025)), "Same national EIA scope"],
  ] as const;
  return <div>
    <div className="panel-title">Data coverage &amp; evidence</div>
    <p className="panel-sub">Values below are calculated from the data loaded by this dashboard. Missing observations stay missing; the three sources are available independently.</p>
    <div className="card">
      <div className="card-head"><h3>Coverage by source and year</h3></div>
      <div className="card-body">
        <table className="tbl"><thead><tr><th>Year</th><th>Ember countries</th><th>EI countries with plotted fields</th><th>EI coal generation</th></tr></thead>
          <tbody>{data.coverage.map(r => <tr key={r.year}><td>{r.year}</td><td>{r.ember_countries}</td><td>{r.ei_countries}</td><td>{r.ei_coal_countries}</td></tr>)}</tbody>
        </table>
        <p className="note">The country search includes {data.countryNames.size} geographies. Small islands and territories may have no polygon in the bundled world map; use search to open their records. An absent Ember year does not hide available EI data. Historical aggregate entities are excluded from the current-country map.</p>
      </div>
    </div>
    <div className="card">
      <div className="card-head"><h3>Numbers supporting the presentation</h3></div>
      <div className="card-body">
        <table className="tbl"><thead><tr><th>Claim</th><th>Measure</th><th>Change</th><th>Scope</th></tr></thead>
          <tbody>{claims.map(([id, label, value, scope]) => <tr key={id}><td>{id}</td><td>{label}</td><td>{fmtSignedPct(value)}</td><td>{scope}</td></tr>)}</tbody>
        </table>
        <p className="note">The main historical panel holds countries fixed through 2024. The Research tab’s six-year trend charts use their labelled matched samples instead. Ratios use generation-weighted totals. A single annual decline does not prove a durable world peak.</p>
        <p><strong>Industry judgment:</strong> overweight clean energy; underweight coal, focused on U.S. domestic thermal exposure, over November 2026–November 2029. Generation growth does not establish valuation, profitability or equity returns. See the downloadable thesis for risks and reversal conditions.</p>
      </div>
    </div>
    <CountryDirectory />
    <div className="card">
      <div className="card-head"><h3>Download the supporting data</h3></div>
      <div className="card-body"><ul>{DOWNLOADS.map(([file, label]) => <li key={file}><a href={`/evidence/${file}`} download>{label}</a></li>)}</ul>
        <p className="note">Country CSV includes separate Ember/EI blocks and availability flags. EIA base sectors exclude overlapping 94/98 totals. Exported values preserve source units; power-sector heat-content units remain unverified, so no quality-adjusted cost claim is made.</p>
      </div>
    </div>
    <div className="card">
      <div className="card-head"><h3>Source snapshots</h3></div>
      <div className="card-body">{data.sources.map(s => <details key={s.file} style={{ marginBottom: 10 }}><summary>{s.file}</summary>
        <p><a href={s.url} target="_blank" rel="noreferrer">Official source portal</a></p>
        <p className="note" style={{ overflowWrap: "anywhere" }}>Snapshot SHA-256: {s.sha256}</p>
      </details>)}
        <p className="note">Original download editions are not fully recorded. Current official releases can differ from these assignment snapshots. Partial geographic coverage and revision status are separate issues; outside source agreement is not assumed independent confirmation.</p>
        <p className="note">{fmt(data.countryByIso.size, 0)} searchable geographies; <a href="/evidence/manifest.json" download>download evidence file hashes</a>.</p>
      </div>
    </div>
  </div>;
}
