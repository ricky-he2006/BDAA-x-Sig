# Sources, provenance and comparability

Analysis date: 6 November 2026. Numerical pitch claims use the local snapshots,
not newer online observations. See `input_manifest.json` and
`tables/claim_evidence.csv` for reproducible lineage.

The structured provenance record is in
[`data/provenance/energy_institute.json`](../data/provenance/energy_institute.json).
The official catalogue and summary identify the **2026, 75th edition**; access
was checked on **6 November 2026**. This verifies the publisher's current
catalogue edition, **not** the original edition/date of the local CSV.
No original download receipt or exact file URL was found; those fields remain
null. Direct catalogue requests returned HTTP 403. The catalogue access date
must not be presented as the original download date.

| Source | Local file / role | Status |
|---|---|---|
| Assignment Ember extract | `country_year_electricity_2020_2025.csv`; electricity demand, clean/fossil mix, trade, power emissions | Supplied data; 213 distinct geographies, uneven annual coverage. Original release date not recorded. |
| Assignment EIA extract | `eia_coal_consumption_quality_2020_2025.csv`; U.S. coal volume and delivered prices | Supplied data; sector 98 national series is used once, separately from state/base sectors. |
| Energy Institute narrow-format extract | `Statistical Review of World Energy Narrow format.csv`; coal output and coal/gas generation | Third dataset, already in repository. Locally hash-pinned; original edition/download date needs documentation. World totals use WLD alone. |

Official source pages checked on the analysis date:

- [Ember yearly electricity data](https://ember-energy.org/data/yearly-electricity-data/): source portal for electricity data. The assignment extract is retained as supplied; an exact current-download match is not asserted.
- [Energy Institute data downloads](https://www.energyinst.org/statistical-review/resources-and-data-downloads): lists a consolidated narrow-format dataset and the 2026 edition. The site notes that vintages can revise historical data. Exact local-file provenance remains unverified; preserve the original download receipt if available.
- [Energy Institute overview](https://www.energyinst.org/statistical-review): lists Ember as a partner. Cross-source agreement is not evidence of wholly independent measurement.
- [EIA Electric Power Annual, Table 1.1](https://www.eia.gov/electricity/annual/table.php?t=epa_01_01.html): current all-sector utility-scale coal consumption for electricity is 372.931 / 415.103 million short tons for 2024 / 2025. These are **not** the supplied national sector-98 observations. The page reports net coal generation of 652.156 / 734.928 TWh; those levels differ materially from the local EI series. Do not force equality without reconciling gross/net scope, sectors and vintage.
- [IEA Global Energy Review 2026, coal](https://www.iea.org/reports/global-energy-review-2026/coal): external context attributes the U.S. rebound to demand, gas prices and slower retirements; it describes divergent regional trends. Those causal explanations are external context, not results established by the two assignment datasets.

## Rules for the final presentation

1. The main historical comparison is a fixed 196-country panel for 2020–2024. A separate fixed 91-country panel is used for 2025 watch points. Country count alone is not electricity coverage: the latter represents 93.5% of **observed 2024 extract** generation, not 93.5% of the world.
2. Aggregate shares are ratios of aggregate generation, not averages of country percentages. Missing values are never zero-filled. Differences use adjacent calendar years only.
3. Coal (EI) and total fossil generation (Ember) are distinct. No cross-source residual is labelled as a fuel. Ember's clean + fossil + net imports = demand identity can be shown within-source.
4. Coal production (Mt), consumption (short tons), generation (TWh), and total energy supply (EJ) answer different questions. Normalize separately when indexing them; never subtract them.
5. U.S. delivered coal prices are nominal, delivered fuel costs, not producer realizations, margins or an investable coal price index. State coal consumption is not state mine production.
6. Heat-content units are unresolved for power-sector observations. No power-sector $/MMBtu investment claim is included. Receipts minus consumption is not verified stock change.
7. The third dataset adds coal-specific context unavailable in the supplied Ember aggregate-fossil columns. It does not provide valuations or independently establish export exposure.

## Rechecking outside sources

The online pages are supporting references and can change. For submission, save
the source edition/date or permitted download and record its hash; do not
silently overwrite the assignment snapshots. No paid data, market multiples,
equity returns, or company recommendations are represented as verified here.
