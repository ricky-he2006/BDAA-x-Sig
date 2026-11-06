# Data Quality Report - Energy Transition Datasets

Pipeline version `1.0.0`. Raw sources are preserved untouched in the project root and copied byte-for-byte into `data/raw/` (SHA-256 pinned in `data/raw/MANIFEST.json`):

| source file | SHA-256 | bytes |
|---|---|---|
| `country_year_electricity_2020_2025.csv` | `97a3bdb61fee446ef0965a3e1eb7c5db4654e542049d189c8e83c48abca55621` | 188,407 |
| `eia_coal_consumption_quality_2020_2025.csv` | `21dfb0489997be1e012c8b036c96ef32fb67441d9771d3c76c2fc38745c5fcca` | 403,894 |
| `Statistical Review of World Energy Narrow format.csv` | `0250f86d242cbf032a65ab119ef97db8c5eadc1adeacee35d706d9908146a25f` | 21,056,005 |

## 1. Original vs cleaned row counts

| dataset | raw rows | cleaned rows | dropped | reason |
|---|---|---|---|---|
| Ember Global Electricity | 1,138 | 1,138 | 0 | duplicate keys removed |
| EIA U.S. Coal | 1,750 | 1,750 | 0 | duplicate keys removed |
| Energy Institute Statistical Review | 299,320 | 299,320 | 0 | duplicate keys removed |
| analysis tables | - | - | - | `analysis_country_year.csv` 1,138 rows; `us_state_year_sector.csv` 831; `eia_us_aggregates.csv` 144 |

No records were dropped for missing values. Zero, missing, unavailable and not-applicable are kept distinct (see flags).

## 2. Missing-value analysis

### Ember (25 numeric-ish columns, 1,138 rows)

| column | missing | % of rows |
|---|---|---|
| `generation_twh` | 0 | 0.00% |
| `demand_twh` | 0 | 0.00% |
| `clean_generation_twh` | 0 | 0.00% |
| `fossil_generation_twh` | 0 | 0.00% |
| `renewable_generation_twh` | 0 | 0.00% |
| `wind_solar_generation_twh` | 0 | 0.00% |
| `clean_share_pct` | 0 | 0.00% |
| `wind_solar_share_pct` | 0 | 0.00% |
| `net_imports_twh` | 0 | 0.00% |
| `demand_per_capita_mwh` | 0 | 0.00% |
| `power_emissions_mtco2e` | 0 | 0.00% |
| `carbon_intensity_gco2e_kwh` | 6 | 0.53% |
| `clean_growth_surplus_twh` | 0 | 0.00% |
| `clean_growth_coverage_pct` | 473 | 41.56% |
| `net_import_share_pct` | 4 | 0.35% |

`clean_growth_coverage_pct` is missing for 473 rows - exactly the rows where demand did not grow (denominator <= 0), i.e. an **explained, structural** absence, not a defect. `carbon_intensity_gco2e_kwh` is missing for the 6 zero-generation rows (division undefined; emissions are 0.0 there).

### EIA (1,750 rows)

| column | missing | % of rows |
|---|---|---|
| `consumption` | 15 | 0.86% |
| `receipts` | 180 | 10.29% |
| `stocks` | 1215 | 69.43% |
| `price` | 1083 | 61.89% |
| `ash_pct` | 192 | 10.97% |
| `sulfur_pct` | 192 | 10.97% |
| `heat_content_raw` | 27 | 1.54% |

Missing price (~62%) and stocks (~70%) are **structural**: EIA does not publish delivered-price/stock data for most electric-power rows. Missing (year, state, sector) *rows* mean 'not reported' and are kept as absence - they are **not** zero consumption. Explicit `0.0` values are genuine zero-activity rows and are preserved.

### Energy Institute (299,320 rows, 1965-2025)

`Value` has no missing cells; absence of a (country, year, variable) cell is the missingness mechanism. Regional aggregates are flagged and excluded from country sums; numeric geography identifiers can be absent on these rows. `ISO3166_numeric` is null on (73,418 rows). 2025 coverage vs 2024: see section 6.

## 3. Invalid and duplicate records

- **Ember**: 0 duplicate (country, year) keys; 0 invalid values. All share columns within [0,100]; all generation/demand values >= 0; net imports may be negative (net exporters - legitimate).
- **EIA**: 0 duplicate (year, location, sector) keys; 0 unparseable numbers; all values within physical ranges (see `cleaning_log.csv` for the exact rule outcomes).
- **Energy Institute**: 0 duplicate (country, year, variable) cells among 299,320 rows; negative values present - see log

## 4. Corrections and exclusions

No source values were corrected or overwritten. The pipeline only adds flags and derived columns. Exclusions are confined to exact duplicate keys (none found in any dataset). Every flag and its reason is in `reports/cleaning_log.csv` (306 entries).

## 5. Suspicious observations requiring further investigation

1. **EIA `heat-content` dual scale (WARNING).** Power-sector rows (1, 2, 3, 94, 98) carry values 0-27 while industrial rows (8, 9, 10) carry ~7,200-15,000. The industrial scale is Btu/lb; the power scale is dimensionally a GJ/tonne-scale energy-per-mass value whose exact unit is not stated in the file - and the `heat-content-units` column is corrupted (it contains the *sulfur* unit string for every row). `heat_content_btu_lb` for power sectors is an **assumed** conversion (x429.9228, 1 GJ/t = 1 Btu/lb-equivalent factor) and is flagged `heat_content_normalized_is_assumed`. Verify against the primary EIA API before using in analysis.
2. **Ember carbon intensity precision (INFO).** 0 rows deviate >5% from emissions/generation recomputation. Deviations, if any, are flagged `carbon_intensity_precision_limited`; a flag alone does not establish its cause.
3. **Coverage and revision status (WARNING).** Ember 2025 covers 91/213 geographies. Release metadata for these supplied snapshots is not recorded, so uniform final/preliminary status cannot be certified for any year. Partial geographic coverage is distinct from preliminary status. Preserve the snapshot and disclose external-vintage differences.
4. **US 2025 coal rebound (INFO).** EIA US electric-power coal consumption rose +11.3% YoY (373.3M -> 415.4M short tons). Large moves can be legitimate; recorded for research, not treated as error.
5. **Geography code variants (INFO).** A few geographies use non-ISO vendor codes (e.g. Kosovo, Taiwan variants). Accepted, flagged, and normalized via `std_geo_key` for joins only - source codes preserved.

## 6. Geographic and temporal coverage limitations

- **Ember**: 213 countries; 2020-2022 full coverage; 2023 = 212 (Ukraine absent); 2024 = 196 (small territories absent); 2025 = 91 countries only. 17 countries do not span the full 2020-2024 window (mostly micro-territories).
- **EIA**: 51 states + DC + PR, 10 census/pacific regions, US total; 2020-2025. (state, sector) presence varies by year - small industrial cells disappear when not reported (absence, not zero).
- **Energy Institute**: 135 countries + 7 aggregates, 1965-2025 (full history preserved). Latest-year (2025) figures are estimates.
- **Joins**: Ember x EI match on 107 of 213 Ember geographies (Ember-only: ['abw', 'afg', 'arm', 'asm', 'atg', 'bdi', 'ben', 'bfa', 'bhs', 'bih', 'blz', 'bmu', 'brb', 'btn', 'bwa', 'caf', 'civ', 'cmr', 'cok', 'com', 'cpv', 'cri', 'cym', 'dji', 'dma', 'dom', 'eri', 'eth', 'fji', 'flk', 'fro', 'geo', 'gha', 'gib', 'gin', 'glp', 'gmb', 'gnb', 'grd', 'grl', 'gtm', 'guf', 'gum', 'hnd', 'hti', 'jam', 'jor', 'ken', 'kgz', 'khm', 'kir', 'kna', 'kosovo', 'lao', 'lbn', 'lbr', 'lca', 'lso', 'mac', 'mda', 'mdv', 'mli', 'mlt', 'mne', 'mrt', 'msr', 'mtq', 'mus', 'mwi', 'nam', 'ner', 'nic', 'niu', 'npl', 'nru', 'pan', 'pri', 'prk', 'pry', 'pse', 'pyf', 'reu', 'rwa', 'sen', 'shn', 'slb', 'sle', 'slv', 'som', 'spm', 'stp', 'sur', 'swz', 'syc', 'tca', 'tgo', 'tjk', 'tls', 'ton', 'uga', 'ury', 'vct', 'vgb', 'vir', 'vut', 'wsm']). EI aggregates are never joined to country rows.

## 7. Cross-dataset consistency findings

- cmp_generation: n=78, median |relative diff| = 1.5% (2024, country level)
- cmp_renewable: n=68, median |relative diff| = 56.0% (2024, country level)
- cmp_wind_solar: n=64, median |relative diff| = 1.6% (2024, country level)
- cmp_clean_bridge: n=69, median |relative diff| = 35.0% (2024, country level)
- **Coal measures are NOT interchangeable** (documented, not forced to match):

  - EIA US file = **electric-power coal consumption** (short tons, end-use basis);
  - EI `coalprod_mt` = **production** (Mt, includes exports, all uses);
  - EI `coal_tes_ej` = **total energy supply** (EJ, energy content of supply, includes non-power);
  - EI `electbyfuel_coal` = **coal-fired electricity generation** (TWh).
  Only EIA-consumption vs production/ TES/TWh comparisons above are sanity checks, never equivalence tests.

  US 2020-2025 (EIA consumption Mt vs EI production Mt vs EI TES EJ):

|   year |   eia_us_electric_power_consumption_mt |   ei_us_coal_production_mt |   ei_us_coal_tes_ej |
|-------:|---------------------------------------:|---------------------------:|--------------------:|
|   2020 |                            3.95375e+08 |                    485.738 |             9.20225 |
|   2021 |                            4.54894e+08 |                    523.837 |            10.5728  |
|   2022 |                            4.28948e+08 |                    539.009 |             9.91071 |
|   2023 |                            3.51267e+08 |                    524.311 |             8.18961 |
|   2024 |                            3.38614e+08 |                    464.969 |             7.93044 |
|   2025 |                            3.7684e+08  |                    483.563 |             8.73009 |

## 8. Automated validation test results

See `tests/` (pytest). The test suite re-derives the identities asserted above (sector sums, region sums, US-total sums, share ranges, grain uniqueness, join integrity, missing-vs-zero separation, pipeline idempotency) against the cleaned outputs.

## 9. Remaining data-quality risks

1. EIA power-sector heat-content unit assumption (see 5.1) - quantitative heat comparisons across sectors are unreliable until verified against the EIA API.
2. 2025 figures in all three sources may be revised.
3. Ember has no coal sub-split; the coal series for the thesis rests on EI `electbyfuel_coal`, whose methodology (heat vs net calorific basis) should be confirmed.
4. EI `ren_power_twh` vs Ember `renewable_generation_twh` may differ in hydro/biomass treatment - use the documented bridge carefully.
5. Small Ember countries: 2-decimal MtCO2e rounding limits emission-intensity precision.
6. EIA missing rows (not reported) vs explicit zeros: analysis code must use the `available_*` flags.

## 10. Readiness for investment analysis

| dataset | ready? | caveats |
|---|---|---|
| Ember | **Yes** | 2025 partial (91 countries); intensity precision for small countries |
| EIA | **Yes, with caveat** | heat-content unit assumption for power sectors; price/stocks structural gaps |
| Energy Institute | **Yes** | 2025 = estimates; coal TES in EJ only (no Mt) |
| Joined country-year table | **Yes** | inner-join coverage = intersection; flags present |
| US state-year-sector table | **Yes** | base sectors only - aggregates separated |
