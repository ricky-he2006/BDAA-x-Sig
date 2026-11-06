import { useMemo, useState } from "react";
import { useApp } from "../state/AppState";
import { YEARS } from "../data/types";
import { downloadCountry, hasCountryData, reported, yearRanges, type CountryDataFilter } from "../viz/countryDirectory";

export function CountryDirectory() {
  const { data, selectCountry, setView, setYear } = useApp();
  const [query, setQuery] = useState("");
  const [source, setSource] = useState<CountryDataFilter>("any");
  const [year, setDirectoryYear] = useState("all");
  const rows = useMemo(() => {
    if (!data) return [];
    const q = query.trim().toLocaleLowerCase();
    return [...data.countryByIso.entries()].map(([iso, byYear]) => {
      const records = [...byYear.values()].sort((a, b) => a.year - b.year);
      const name = data.countryNames.get(iso) ?? iso;
      const considered = records.filter(r => year === "all" || r.year === Number(year));
      return { iso, name, records, considered,
        emberYears: yearRanges(records.filter(r => reported(r.ember.generation)).map(r => r.year)),
        eiYears: yearRanges(records.filter(r => r.ei_available).map(r => r.year)),
        coalYears: yearRanges(records.filter(r => reported(r.ei.coal_gen)).map(r => r.year)),
      };
    }).filter(r => (!q || `${r.name} ${r.iso}`.toLocaleLowerCase().includes(q))
      && r.considered.some(observation => hasCountryData(observation, source)))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [data, query, source, year]);
  if (!data) return null;
  return <div className="card">
    <div className="card-head"><h3>Country data directory</h3></div>
    <div className="card-body">
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 10 }}>
        <input aria-label="Find country data" placeholder="Country name or ISO code…" value={query} onChange={e => setQuery(e.target.value)} />
        <select aria-label="Country data type" value={source} onChange={e => setSource(e.target.value as CountryDataFilter)}>
          <option value="any">Any reported data</option><option value="electricity">Ember electricity</option>
          <option value="coal">Coal generation</option><option value="production">Coal production</option>
        </select>
        <select aria-label="Country data year" value={year} onChange={e => setDirectoryYear(e.target.value)}>
          <option value="all">All years</option>{YEARS.map(y => <option key={y} value={y}>{y}</option>)}
        </select>
      </div>
      <p className="note" role="status">Showing {rows.length} of {data.countryNames.size} geographies. Filters use reported observations, including zeros. Year ranges below show each source’s full available history.</p>
      <div style={{ maxHeight: 410, overflow: "auto" }}>
        <table className="tbl" aria-label="Country data directory"><thead><tr>
          <th>Country</th><th>ISO</th><th>Electricity years (Ember)</th><th>Energy years (EI)</th><th>Coal generation years (EI)</th><th>Explore / download</th>
        </tr></thead><tbody>{rows.map(r => <tr key={r.iso}>
          <td>{r.name}</td><td>{r.iso}</td><td>{r.emberYears}</td><td>{r.eiYears}</td><td>{r.coalYears}</td>
          <td><button className="iconbtn" aria-label={`Explore ${r.name}`} onClick={() => {
            setYear(year === "all" ? Math.max(...r.considered.map(v => v.year)) : Number(year));
            selectCountry(r.iso); setView("world");
          }}>Explore</button>{" "}<button className="iconbtn" aria-label={`Download ${r.name} data`} onClick={() => downloadCountry(r.records, r.iso)}>CSV</button></td>
        </tr>)}</tbody></table>
      </div>
      {rows.length === 0 && <p>No countries match these filters.</p>}
      <p className="note">Blank year ranges mean that source does not report the measure. Country CSV downloads contain the full available history, with separate source fields and availability flags. <a href="/evidence/country_directory.csv" download>Download the country coverage list</a>.</p>
    </div>
  </div>;
}
