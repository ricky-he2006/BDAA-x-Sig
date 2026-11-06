# Energy Transition - Coal vs. Clean Energy

Investment research foundation for the **Advanced Track** thesis:
*Is clean electricity replacing coal worldwide, or is growing demand letting
both coexist?*

## Completed submission package

Start with [the editable slide deck](submission/energy_transition_pitch.pptx),
[PDF deck](submission/energy_transition_pitch.pdf),
[presentation script](submission/PRESENTATION_SCRIPT.md), and
[investment thesis](submission/INVESTMENT_THESIS.md).
The recommendation is **overweight clean energy / underweight coal**, with the
coal underweight focused on U.S. domestic thermal exposure and a three-year horizon.
It is an industry judgment; valuations and security-return forecasts are not estimated.

[Country review](submission/COUNTRY_REVIEW.md) covers all 213 geographies,
with six-panel figures for the 16 material coal/clean markets, including all
eight existing focus markets. [Project audit](submission/PROJECT_AUDIT.md)
documents corrections to historical research drafts. Numerical claims trace
to [evidence tables](submission/tables/claim_evidence.csv).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m src.pipeline
.venv/bin/python -m analysis.build_deliverables
.venv/bin/python -m analysis.build_presentation
.venv/bin/python -m pytest
```

Optional PDF export requires LibreOffice:

```bash
libreoffice --headless --convert-to pdf --outdir submission submission/energy_transition_pitch.pptx
```

Start with [the investment committee brief](submission/EXECUTIVE_SUMMARY.md)
or [the full investment thesis](submission/INVESTMENT_THESIS.md).

The deck contains eight main slides with a 6:15 speaking plan, plus seven evidence appendix slides. The full script and dashboard walkthrough are in submission/. Detailed
country research remains separate. The presenter guide and cue cards support rehearsal. [Submission checklist](submission/SUBMISSION_CHECKLIST.md)
lists the remaining team recording, YouTube upload, source-provenance and
repository-publication steps. The group video remains to be recorded and published.

## Repository layout

```
├── data/
│   ├── raw/          # byte-identical copies of the three source CSVs + MANIFEST.json (SHA-256)
│   ├── cleaned/      # per-source cleaned tables with validation flags
│   └── processed/    # analysis-ready tables for research & dashboard
├── src/              # reproducible cleaning / validation / processing pipeline
│   ├── config.py     # paths, sector/region definitions, unit registries
│   ├── iso3166.py    # geo code reference (243 ISO codes) + cross-source join keys
│   ├── audit_common.py
│   ├── clean_ember.py / clean_eia.py / clean_ei.py
│   ├── cross_validate.py
│   ├── process.py
│   ├── make_reports.py
│   └── pipeline.py   # entry point
├── tests/            # pytest validation suite (62 tests)
├── analysis/         # exploratory research scripts A–D -> analysis/output/
├── dashboard/        # Energy Atlas: React 18 + TypeScript + Vite app
│   ├── src/          # components, viz, data loading, state, tests (vitest, 92 tests)
│   ├── scripts/export_dashboard_data.py   # processed CSVs -> public/data/*.json
│   └── public/data/  # JSON data served to the app
└── reports/
    ├── data_quality_report.md   # full audit findings
    ├── cleaning_log.csv         # record-level audit trail
    ├── data_dictionary.md       # variable definitions & units
    ├── validation_summary.json  # machine-readable check results
    ├── research_findings.md     # ranked, tagged research findings (Phase 3)
    ├── investment_research_framework.md  # evidence matrix + decision rules (Phase 4)
    └── OVERNIGHT_PROGRESS.md    # handoff report
```

## Data pipeline

```bash
python3 -m src.pipeline     # run the full pipeline (idempotent)
pytest                      # run the validation suite
```

The pipeline:
1. pins the raw sources (`data/raw/MANIFEST.json`, SHA-256) and never touches
   the originals in the project root;
2. cleans each source into `data/cleaned/` (types, identifiers, flags;
   **no silent corrections, no zero-imputation**);
3. cross-validates the three sources (join integrity, measure comparability);
4. builds the analysis tables in `data/processed/`;
5. writes the audit trail (`cleaning_log.csv`) and the report.

Running it repeatedly produces byte-identical outputs (verified by test).

## Key data rules (read before using the tables)

* **EIA sectors**: 94 = 2+3, 98 = 1+2+3 (exact). The state table
  (`us_state_year_sector.csv`) contains base sectors {1,2,3,8,9,10} only;
  aggregate sectors live in `eia_us_aggregates.csv`. Never combine the two.
* **Geography**: ALL EI regional aggregates — every `O-*` ("Other X") and
  `T-*` ("Total X") code plus `WLD` (Total World) and `ROW` — are flagged
  `is_aggregate` and never join with country rows. The country-level sum
  (109 listed countries) is a LOWER BOUND on world totals; the "Other X"
  residual is disclosed, never closed by adding aggregates back. EIA
  region/US rows are `is_geographic_aggregate`.
* **Missing vs zero**: both are real. Use `available_*` / `*_available`
  completeness flags. A missing row = not reported, never zero.
* **EIA heat-content**: two unit scales coexist (see report section 5.1);
  power-sector normalized Btu/lb values are flagged as assumed.
* **Coverage vs finality**: Ember counts are 213/213/213/212/196/91 in
  2020–2025. Source vintage metadata is incomplete; partial coverage does
  not itself establish preliminary status. The main pitch uses fixed
  196-country history through 2024 and a separate fixed 91-country watch panel.
* **Coal measures are distinct**: EIA consumption (short tons, electric
  power) ≠ EI production (Mt) ≠ EI coal TES (EJ) ≠ EI coal-fired generation
  (TWh).

## Dashboard (Energy Atlas)

React 18 + TypeScript (strict) + Vite. 3D globe (globe.gl) with 8
choropleth layers, year selector 2020–2025, country search, country
explorer panel, mandatory US 50-state drill-down (base sectors only —
aggregate EIA sectors 94/98 are kept separate, so double-counting is
structurally impossible), and a findings-driven industry research panel
(no hard-coded recommendations).

```bash
cd dashboard
npm install               # one-time
npm run dev               # -> http://localhost:5173
npm run typecheck         # tsc -b (strict)
npm test                  # vitest run (92 tests)
npm run build             # production build -> dist/
npm run preview           # serve the production build
```

The app reads JSON from `dashboard/public/data/`. After re-running the
Python pipeline, refresh it with:

```bash
python3 dashboard/scripts/export_dashboard_data.py
```

## Status

* **Data layer**: complete — 0 pipeline errors; see
  `reports/data_quality_report.md`.
* **Research and pitch**: current submission materials are in `submission/`;
  older `reports/research_findings.md` and `investment_research_framework.md`
  are marked historical and superseded for submission.
* **Dashboard**: country diagnostics expanded; research trends use fixed
  membership and explicit sample labels. Independent EI years are retained;
  Data & evidence provides coverage, claim calculations and downloads.
  Typecheck/build pass; 92 Vitest and 62 pytest tests pass.
  See `submission/DASHBOARD_AUDIT.md` for data and browser checks.

The Data & evidence tab includes a searchable country directory with source/year
filters and per-country CSV downloads. The final pitch remains eight main
slides; slide 4 covers global 2025 divergence and slide 6 contains the allocation
cards. Team names and submission URLs are configured in
`submission/submission.json`. See `submission/SUBMISSION_STATUS.md` for
remaining group/account actions. Build a code/deliverable ZIP with:

```bash
.venv/bin/python -m analysis.package_submission
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Vercel, Netlify and local builds.
The repository includes source data, processed tables and all static assets.
GitHub Actions runs validation and produces a static-site build artifact.
