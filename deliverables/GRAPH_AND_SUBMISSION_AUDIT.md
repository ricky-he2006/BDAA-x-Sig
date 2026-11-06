# Graph and submission review

Checked 6 November 2026 against the assignment, thesis and current eight-slide deck.

## Assessment

The current thesis has the graphs it needs. Keep the deck at eight slides. Four embedded charts, three geographic comparison cards, allocation cards and explicit decision rules cover the investment argument. The repository also contains 26 supporting PNG/SVG figure pairs. More countries or chart volume would not resolve the remaining financial and provenance limitations.

## Coverage of the argument

| Question | Main presentation | Supporting evidence | Assessment |
|---|---|---|---|
| Does clean output grow faster than fossil? | Slide 2 indexed generation chart | figures/01_global_volumes; matched_2020_2024.csv | Covered. Index measures output growth, not investment returns. |
| Does a global coal-decline thesis follow? | Slide 3 geographic cards | figures/02_country_pathways, 05_counterexamples; ei_world_totals.csv | Covered with limits. Coal and clean can grow together; U.S. experience is not a global proxy. |
| What changed in 2025? | Slide 4 clean/demand/fossil bars and China/India/U.S. coal bars | figures/06_2025_watch, 10_2025_global_divergence; 2025_watch_evidence.csv | Covered. Different sources and fuel definitions remain labelled. |
| What challenges the coal underweight? | Slide 5 six-year U.S. consumption bars | figures/04_us_coal_volume_price; us_electric_power_coal.csv | Covered. The 2025 rebound is explicit, and delivered prices are not producer margins. |
| What should the investor do? | Slides 1, 6 and 8 industry positions | INVESTMENT_THESIS.md and EXECUTIVE_SUMMARY.md | Covered as an industry judgment, not a measured excess-return forecast. |
| What changes the view? | Slide 7 monitoring rules | Thesis risk table and presenter Q&A | Covered. Thresholds are analyst rules, not fitted forecasts. |
| How complete is coverage? | Slide 2 fixed panel and slide 4 sample caveat | figures/07_coverage; panel membership CSVs | Covered. The 93.5% statistic refers to observed 2024 extract generation, not world electricity. |
| Is the 2020 baseline driving the conclusion? | Presenter Q&A | tables/baseline_sensitivity.csv; thesis baseline paragraph | Covered numerically. Another main-deck chart is unnecessary. |
| Do state and quality patterns matter? | Retained outside the timed pitch | figures/08_us_state_changes, 09_us_coal_quality | Available for follow-up. State consumption is not mine production; unresolved heat units limit quality-adjusted cost claims. |
| Can individual countries be reviewed? | Three illustrations only | 213 country reviews, 16 detailed figures and searchable dashboard directory | Covered outside the deck, consistent with the requested presentation scope. |

All paths above are relative to deliverables; CSV files are in tables/. Pitch-specific chart exports are in pitch_figures/.

## Current checks

- Python analysis/data tests: 62 passed.
- Dashboard tests: 92 passed; TypeScript and production build passed.
- Source-field audit: 33,569 comparisons, no mismatches.
- Dedicated pitch audit: four embedded chart PNG hashes match their generated exports; all chart SVG counterparts exist; historical growth, national-sector scope and 2025 changes reconcile.
- PDF and PPTX each have eight slides; native slide text is retained in the PDF. Every slide has notes. The script has 782 words with a 6:15 plan; actual recording time remains unmeasured.
- Thesis and executive-summary local evidence links resolve.
- Browser acceptance results are recorded separately in previews/browser_check.json. Check its completed field and error arrays for the latest run; machine checks do not establish subjective visual quality.

Reproduce the presentation-specific check with `python -m analysis.verify_pitch`. Other checks and browser commands are in VERIFICATION.md. Raw evidence checks use the supplied snapshots; they do not independently certify those snapshots against the original publishers.

## What remains unfinished

1. **EI provenance:** exact original local edition, file download URL and download date are not recorded. The current catalogue access date cannot fill that gap. The third dataset is useful and hash-pinned, but exact-vintage verification remains incomplete.
2. **Team metadata:** names and actual speaker assignments must be entered in submission.json and the deck rebuilt.
3. **Published repository:** the ZIP is prepared locally; a published repository URL is not configured.
4. **Actual group video:** record the presentation, confirm its runtime is at most seven minutes, upload as Unlisted and verify the URL while signed out. A script and a planned runtime do not complete this deliverable.
5. **Investment economics:** no valuation or cash-flow dataset establishes attractive returns. This is a limitation of the investment conclusion, not a missing mandatory chart. A future valuation/project-return comparison is useful only after acquiring and validating appropriate data.

No additional country graphs, forecasting models or dashboard features are needed before these submission items are completed.
