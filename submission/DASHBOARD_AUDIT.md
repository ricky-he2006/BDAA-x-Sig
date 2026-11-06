# Dashboard and data audit

Checked 6 November 2026. Machine results: `dashboard_data_audit.json` and
`previews/browser_check.json`. The checks validate this repository snapshot,
not the completeness of external publishers' latest releases.

## What was fixed

- Independent source coverage: restored 14 EI-only country/year records
  previously hidden by an Ember-left join. Indonesia 2025 coal is visible;
  its missing Ember electricity observations remain null.
- Added EI's six Total World observations separately. World, region and
  country rows are never added together.
- Added Data & evidence: live pitch calculations, coverage by source/year,
  source hashes, definitions, limitations and downloadable evidence tables.
- Added a directory for all 213 geographies: name/code search, data-type and
  year filters, source-specific histories, opening a country in the globe,
  and full-history CSV downloads. Missing values remain blank and zeros remain
  reported data. EI provenance is available as a separate download.
- U.S. legend now uses the same state/sector scale and short-ton units as
  the map. It no longer displays a global clean-energy legend.
- Fixed relative growth labels that incorrectly used `pp`; relative growth
  uses `%`, while share changes use percentage points.
- Removed a fixed 10% state-share axis ceiling; missing national totals no
  longer produce a fabricated zero metric-tonne equivalent.
- Added national delivered-price history, clearly distinguished from mine
  realizations or producer margins. Missing 2021 price remains blank.
- Added state/territory selection, including Puerto Rico, which has data
  but no polygon in the bundled 50-state/DC topology.
- Bundled globe textures locally. Optional rotation, reset and country focus
  controls are available. Theme changes preserve the globe/camera instance.
- Retained the fixes for missing polygon geometry and conflicting Three.js
  versions. A WebGL-unavailable message preserves access to the underlying
  country and U.S. data instead of crashing the page.
- Restarted the default port-5173 server, which was still serving an old
  dependency bundle despite correct production output. Development startup
  now forces dependency optimization and deduplicates Three.js.
- Fixed narrow-screen sizing and scroll access to the research/evidence
  views. Analytical charts show current values without animated interpolation.
- Country sidebars omit unavailable snapshot rows, empty chart cards and
  all-null series. Reported zeros remain visible. Historical observations
  stay accessible when the selected year is missing; table columns and peer
  comparisons require reported data. Zero-base production is shown in raw Mt
  rather than as an undefined index.

## Data reconciliation

**33,569 field comparisons passed**, with no mismatches within source CSV
precision. Checks compare every plotted Ember field, selected EI fields,
EIA state/aggregate fields and world totals to the cleaned/processed sources.
They also verify export freshness, independent availability flags and hashes
of downloadable evidence files.

| Data block | Dashboard coverage |
|---|---|
| Searchable current geographies | 213 |
| Country/year records | 1,152: 1,138 Ember records + 14 restored EI-only years |
| Ember geography counts, 2020–2025 | 213 / 213 / 213 / 212 / 196 / 91 |
| Current geographies with selected EI energy fields | 82 per year |
| Geographies with EI coal generation reported | 31 per year; missing is not presumed zero |
| EI Total World rows | 6, kept separate |
| State/base-sector records | 831, excluding overlapping sectors 94/98 |
| National/regional aggregate records | 144, kept separate from states |

The EI source contains more variables and historical/regional entities than
are relevant to the plotted energy measures. These remain in the raw and
cleaned files; the dashboard does not pretend that all 109 listed entities
have every plotted metric. Historical USSR is not mapped as a modern country.
The 110m world geometry omits some small geographies; country search and tables
provide access to those observations.

The Data & evidence view reproduces the submitted 196-country historical
panel: clean generation +25.4%, all fossil +10.3%, 2020–2024. EI's world coal
change is +11.2%. U.S. national sector-98 coal consumption changes are −14.4%
through 2024 and +11.3% in 2025. These are computed from loaded records, not
typed into the interface as independent numerical claims.

## Browser acceptance checks

Production build tested in Chromium, with external asset requests blocked:

- All eight original focus-country explorers and new chart cards.
- All 48 globe layer/year combinations (eight layers, six years).
- Actual rendered U.S. polygon click opens the state drill-down.
- All 48 U.S. sector/year combinations, checking all 51 state/DC no-data
  styles against source observations: 2,448 state/selection checks.
- State clicking and Puerto Rico access through the selector.
- All five research tabs; world totals and matched samples stay labelled.
- Fifteen evidence download paths, with byte comparisons, plus an actual
  browser CSV download verified by hash.
- Rotation/reset/focus, theme switching without globe recreation, narrow
  layout, and simulated WebGL failure with working country data.
- No page runtime errors, failed HTTP responses or external asset requests.

Unit/component validation: **92 Vitest tests** and **62 pytest tests** pass;
TypeScript and the production build pass. Browser screenshots are in `previews/`.

## What the data can support

The provided snapshots support the displayed generation, demand, fuel-use,
trade, price and emissions comparisons, and the explicitly labelled industry
outlook judgment. They do **not** establish equity valuations, project margins,
future returns, reliability, causal displacement, coal export flows or grid
bottlenecks. Missing inventories/prices and unresolved power-sector heat units
are disclosed, not filled in. The original EI download edition remains
unrecorded; reconciliation with current official vintages is still open.

## Rebuild and check

```bash
.venv/bin/python -m src.pipeline
.venv/bin/python -m analysis.build_deliverables
.venv/bin/python -m analysis.build_presentation
.venv/bin/python dashboard/scripts/export_dashboard_data.py
.venv/bin/python -m analysis.verify_dashboard_data
.venv/bin/python -m pytest
cd dashboard
npm run typecheck
npm test
npm run build
npm run preview -- --host 127.0.0.1 --port 5176
```

With the preview running, from the repository root (Playwright/Chromium required):

```bash
.venv/bin/python dashboard/scripts/check_browser.py http://127.0.0.1:5176
```
