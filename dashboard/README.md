# Energy Atlas — dashboard

Interactive 3D atlas of the clean-vs-coal electricity transition, 2020–2025.
Built from the cleaned datasets produced by the pipeline at the repository root.

**Central question** the interface is built around: *Is clean electricity
replacing coal worldwide, or is growing demand letting both coexist — and what
does that imply for allocating capital between the two industries?* The
dashboard reports evidence and links a scoped industry allocation judgment;
it does not estimate security valuations or investment returns.

## Views

| Tab | What it shows |
|---|---|
| **World** | 3D globe (globe.gl / three.js). Country fill = the selected layer (2020–2025 year selector); country outline = year-over-year change in coal-fired generation (diverging blue↓/red↑). Click a country → right-hand explorer panel with snapshot stats, clean-share / mix / coal / carbon-intensity charts, and a country-vs-country comparison. Click the US → drill into the US view. |
| **United States** | National coal-versus-clean electricity comparison with Generation (TWh) and Share (%) filters, using the existing Ember and EI U.S. observations. State markets rank electric-power coal consumption (EIA base sectors 1+2+3), show annual growth, and open state histories. An optional zoomable state map uses one orange scale for power-sector coal consumption, with a short collapsible key; changes are shown in tooltips and state histories. The separate national EIA sector-98 consumption check is optional. No state clean-generation data is inferred. |
| **Research** | Five industry tabs, tagged observations/interpretations/hypotheses. World coal uses EI's WLD row separately from labelled matched samples. Final scope and limitations: `submission/INVESTMENT_THESIS.md`. |
| **Data & evidence** | Source/year coverage, live calculations backing the main pitch, downloadable plotted observations and claim tables, source portals and snapshot hashes. |

## Data flow

```
data/raw/  (originals, pinned by SHA-256 in data/raw/MANIFEST.json)
   └─ python3 -m src.pipeline          → data/cleaned/, data/processed/
   └─ python3 dashboard/scripts/export_dashboard_data.py
        → public/data/country_year.json
        → public/data/us_state_year.json
        → public/data/us_aggregates.json
        → public/data/geo.json         (feature id → dataset iso3; complete ISO 3166-1
                                       numeric table cross-checked against EI + name fallback
                                       for the no-id Kosovo feature)
```

The `geo.json` numeric table is a **complete** ISO 3166-1 reference (all 174
features that carry a numeric id in the bundled `world-atlas/countries-110m`
topology), **not** derived from the Energy Institute file. Sourcing it from EI
(as an earlier version did) left ~70 major countries unmapped because EI carries
`iso_num` for only ~110 entities, so those countries rendered uncolored on the
globe. The export cross-checks the table against EI's own `iso_num` as a
data-integrity guard. A small set of microstates/territories (e.g. Singapore,
Aruba, the Caribbean island states) have no feature at 110m resolution; they are
still reachable via the search box. Regression tests:
`src/data/globeCoverage.test.ts`.

Country sidebars show only reported current-year metrics and chart series.
Empty cards/columns are omitted, genuine zeros remain visible, and historical
charts stay available when the selected year has no data. Peer comparisons
require overlapping reported observations.

Data & evidence includes the Country data directory: search all 213 geographies,
filter reported observations by data type/year, inspect source histories, open
the country explorer and download its full available history as CSV. The filters
do not discard reported zeros. Coverage ranges preserve gaps.

Nothing in this dashboard is hard-coded data. All values come from the four
JSON files in `public/data/`. **Never** edit those by hand — regenerate them.

The country export contains **1,152 records**: 1,138 Ember observations plus
14 EI-only country/year observations previously hidden by the Ember-left join.
Source blocks have independent availability flags: Indonesia 2025 coal is
shown, while its absent Ember observations stay null. Selected EI fields cover
82 current geographies, with coal generation reported for 31; these are not
claimed as complete world coverage. Historical USSR and regional aggregates
are excluded from the current-country map. EI's separate world series has six WLD rows.

The exporter also writes `public/evidence/` with CSVs, source notes, claim
references and hashes. It requires the final analysis package to exist; see the
root README for the build order. Original source files remain unchanged.

Earth textures are bundled locally in `public/textures/`; globe rendering does
not require a CDN. Rotation is optional, focus/reset controls are available,
and theme changes preserve the globe instance. Without WebGL, a visible message
explains the limitation while search, country tables and U.S. data remain usable.

**JSON contract:** the four files are strict RFC 8259 JSON. Missing values
are `null` — never `NaN` (Python's default `json.dumps` emits a bare `NaN`
token that browser `JSON.parse` rejects) and never `0` (zero is data, not
missingness). The export script enforces this with `allow_nan=False` plus a
standards-compliant re-parse of every file before it reports success
(regression tests: `tests/test_dashboard_export.py` and
`src/data/realData.test.ts`).

## Commands

```bash
npm install            # once
npm run dev            # vite dev server on :5173
npm test               # vitest run (jsdom; echarts stubbed in src/test/setup.ts)
npm run typecheck      # tsc -b
npm run build          # tsc -b && vite build → dist/
node scripts/check_palette.mjs   # regenerate the orange ramp + validate all ramps
                               # against the dataviz validator (light + dark)
```

From the repository root:

```bash
.venv/bin/python dashboard/scripts/export_dashboard_data.py
.venv/bin/python -m analysis.verify_dashboard_data
# Optional browser check, after starting the app (requires Playwright/Chromium):
.venv/bin/python dashboard/scripts/check_browser.py http://127.0.0.1:5173
```

The field audit compares more than 33,000 values and verifies export freshness,
independent source coverage and downloadable evidence hashes. Browser checks
exercise all layer/year and U.S. sector/year combinations. Results are written
to `submission/dashboard_data_audit.json` and `submission/previews/browser_check.json`.

## Color system

- **Categorical slots** (both themes) follow the dataviz validated palette;
  hue order is fixed and never cycled.
- **Sequential (one hue, light→dark):** blue for magnitude layers
  (clean share, renewable, demand, carbon intensity); orange — computed by
  OKLab interpolation from `#fdeee2` to `#832e07`, 13 steps — for coal layers
  (coal gen, coal share, coal production, coal TES).
- **Diverging (two hues + neutral midpoint):** blue pole = coal falling,
  red pole = coal rising, gray midpoint; used for country/state outlines.
- **Entity colors** are stable across every chart: demand = neutral dashed
  (secondary ink), clean = blue slot, fossil/coal = orange slot, etc.
  (`src/viz/series.ts`). One axis per chart — no dual axes.
- No data is never rendered as 0: countries/states without a reported value get
  a receded fill, and numeric cells show an em-dash.
- Dark mode is its own validated palette, not an automatic flip.

## Files

- `src/state/AppState.tsx` — app state (view, year, layer, US sector, selections, theme)
- `src/data/` — JSON types, loader, geo mapping (FIPS→state, feature→iso3)
- `src/viz/` — palette (OKLab ramps, scales), layer values, state values, formatting, entity colors
- `src/components/` — TopBar, Globe, Legend, CountryPanel, USMap, StatePanel, ResearchPanel, ChartCard
- `src/test/` — setup (echarts stub), fixtures, and component/unit tests
