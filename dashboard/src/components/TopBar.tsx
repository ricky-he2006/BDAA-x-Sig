import { useMemo } from "react";
import { useApp } from "../state/AppState";
import { LAYERS, PRESENTATION_LAYERS, YEARS, type LayerKey, type ViewKey } from "../data/types";

const VIEW_LABELS: Record<ViewKey, string> = {
  world: "World",
  us: "United States",
  research: "Coal & clean",
  data: "Data & evidence",
};

export function TopBar() {
  const {
    view, setView, year, setYear, layer, setLayer, search, setSearch, dark, toggleDark,
    data, selectCountry,
  } = useApp();

  const pickFromSearch = () => {
    if (!data) return;
    const q = search.trim().toLowerCase();
    if (!q) return;
    const codeMatch = Array.from(data.countryNames.entries()).find(([iso]) => iso.toLowerCase() === q);
    const exact = Array.from(data.countryNames.entries()).find(
      ([, name]) => name.toLowerCase() === q,
    );
    const partial = Array.from(data.countryNames.entries()).find(
      ([, name]) => name.toLowerCase().includes(q),
    );
    const hit = codeMatch ?? exact ?? partial;
    if (hit) selectCountry(hit[0]);
  };

  const lastYear = YEARS[YEARS.length - 1];
  const searchIndex = useMemo(() => {
    if (!data) return [];
    const names = Array.from(data.countryNames.entries()); // [iso3, name]
    return names
      .map(([iso, name]) => ({ iso, name }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [data]);

  return (
    <header className="topbar">
      <div className="brand">
        <h1>Energy Atlas</h1>
        <span className="sub">Coal & clean investment themes · 2020–{lastYear}</span>
      </div>

      <nav className="viewtabs" role="tablist" aria-label="View">
        {(Object.keys(VIEW_LABELS) as ViewKey[]).map((k) => (
          <button
            key={k}
            role="tab"
            aria-selected={view === k}
            className={view === k ? "active" : ""}
            onClick={() => setView(k)}
          >
            {VIEW_LABELS[k]}
          </button>
        ))}
      </nav>

      <div className="controls">
        {(view === "world" || view === "us") && <label className="yearctl">
          <span className="k muted">Year</span>
          <input
            type="range"
            min={YEARS[0]}
            max={lastYear}
            step={1}
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            aria-label="Year"
          />
          <span className="yr">{year}</span>
          {year === lastYear && <span className="yrnote">coverage varies</span>}
        </label>}

        {view === "world" && <label className="yearctl">
          <span className="k muted">Explore</span>
          <select
            value={layer}
            onChange={(e) => setLayer(e.target.value as LayerKey)}
            aria-label="Map layer"
          >
            {[{ label: "Blue · clean energy", keys: PRESENTATION_LAYERS.filter(k => k.startsWith("clean")) },
              { label: "Red · coal", keys: PRESENTATION_LAYERS.filter(k => k.startsWith("coal")) }].map(group => (
              <optgroup key={group.label} label={group.label}>{group.keys.map(k => (
                <option key={k} value={k}>{LAYERS[k].label}</option>
              ))}</optgroup>
            ))}
          </select>
        </label>}

        {view === "world" && (
          <input
            type="text"
            list="country-list"
            placeholder="Search country…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") pickFromSearch();
            }}
            aria-label="Search country"
          />
        )}
        <datalist id="country-list">
          {searchIndex.map((c) => (
            <option key={c.iso} value={c.name} />
          ))}
        </datalist>

        <button className="iconbtn" onClick={toggleDark} aria-label="Toggle theme">
          {dark ? "Light" : "Dark"}
        </button>
      </div>
    </header>
  );
}
