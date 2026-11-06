# Review of the existing project

The reproducible pipeline, missing-value handling, separation of overlapping EIA sectors and dashboard are strong foundations. The existing research was not submission-complete: it intentionally omitted ratings, had no deck/script, and contained several inconsistent conclusions. This package supplies a scoped investment judgment and preserves the source snapshots.

## Corrections and limits

| Issue in prior material | Resolution |
|---|---|
| Ember described as 213 countries in every year through 2024 | Actual counts: 213, 213, 213, 212, 196, 91. Main analysis uses 196 countries present with required metrics throughout 2020–2024; watch panel uses 91 throughout 2020–2025. |
| Fossil and coal declines described as a 2025 contradiction | They have the same sign and measure different fuels/panels. No contradiction is established. |
| A single annual decline called a durable global peak | Describe an observed sample decline only. A durable peak remains a hypothesis. |
| 'Coal share falling everywhere' | Removed. Country trajectories differ; the world share did not decline in every year either. |
| Brazil/Indonesia labelled exporters from production versus generation | Divergence is descriptive. Trade, stock changes, quality, and non-power use cannot be identified from these two series. |
| Grid called a proven bottleneck and 'regime-proof' | Removed from the recommendation: no grid-constraint or spending evidence supports that causal claim. |
| Nuclear availability inferred from aggregate clean data | No attribution without technology-level checks. Clean is renewables plus nuclear. |
| Coal-producing states inferred from EIA consuming states | State EIA table identifies consumption location, not mine exposure. |
| consumption_mt export divided by 1,000 | Fixed to divide short tons ×0.90718474 by 1,000,000 for million metric tonnes. |
| Quality report claimed ~1,128 intensity discrepancies | Current calculation flags 0; generator corrected and report regenerated. |
| Receipts minus consumption labelled inventory change | Treat as a partial flow balance only; compare the same reported rows and do not infer stock levels. |
| 2025 universally preliminary; earlier years universally final | Snapshot release metadata is not provided. Coverage and revision status are different. Current official releases can be newer; avoid blanket finality claims. |
| Listed-country sum called world | Use EI's WLD row alone for world totals; country sums are explicitly partial and never mixed with overlapping aggregates. |
| Two pathway taxonomies with different thresholds | Submission uses one definition: >20 TWh clean/coal in both endpoint years and >5% directional changes. |
| 2020 is a pandemic-affected base year | `baseline_sensitivity.csv` also compares 2021–2024 on the same fixed panel. Endpoint growth is descriptive, not a forecast of normal annual growth. |

## Remaining accuracy checks

The supplied files are the assignment basis, not byte-for-byte certified copies of today's official releases. The additional EI CSV is hash-pinned locally, but its original download date/edition is not recorded. The official site confirms a narrow-format dataset exists; the exact local vintage is not independently certified. Do not describe the three sources as fully independent: EI lists Ember as a partner.

External EIA Table 1.1 gives 2024/2025 all-sector utility-scale electricity coal consumption of 372.931/415.103 million short tons. These differ from supplied sector-98 values and definitions. Direction agrees, but they must not be silently substituted or called an exact match. Current official net coal generation also differs from the local EI series: scope/vintage reconciliation remains open. See SOURCES.md.

The recommendations are forward-looking industry judgments, not demonstrated equity excess returns. No historical multiples, valuation spreads, developer margins or security prices are in this package. The assignment permits a judgment; those limitations constrain confidence and selection of securities.
