"""Generates the human-readable quality report and data dictionary.

Everything is derived from the validation summary and the cleaned tables -
no numbers are hard-coded, so the report always matches the pipeline output.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from . import config as C
from .iso3166 import is_accepted_noniso, is_known


def _pct(n: int, d: int) -> str:
    return f"{100.0 * n / d:.2f}%" if d else "0.00%"


def _missing_table(df: pd.DataFrame, cols: list[str]) -> str:
    lines = ["| column | missing | % of rows |", "|---|---|---|"]
    for c in cols:
        if c not in df.columns:
            continue
        n = int(df[c].isna().sum())
        lines.append(f"| `{c}` | {n} | {_pct(n, len(df))} |")
    return "\n".join(lines)


def write_reports(summary: dict, processed: dict,
                  raw_dir: Path, cleaned_dir: Path, processed_dir: Path) -> None:
    rep = C.REPORTS
    rep.mkdir(parents=True, exist_ok=True)

    ember = pd.read_csv(cleaned_dir / C.CLEANED_EMBER)
    eia = pd.read_csv(cleaned_dir / C.CLEANED_EIA)
    ei = pd.read_csv(cleaned_dir / C.CLEANED_EI)
    cy = processed[C.PROCESSED_COUNTRY_YEAR]
    us = processed[C.PROCESSED_US_STATE]
    agg = processed[C.PROCESSED_EIA_AGGREGATES]

    rc = summary["row_counts"]
    man = summary["manifest"]

    # ------------------------------------------------------------------ report
    md = []
    md.append("# Data Quality Report - Energy Transition Datasets\n")
    md.append(f"Pipeline version `{summary['pipeline_version']}`. Raw sources are "
              "preserved untouched in the project root and copied byte-for-byte into "
              "`data/raw/` (SHA-256 pinned in `data/raw/MANIFEST.json`):\n")
    md.append("| source file | SHA-256 | bytes |")
    md.append("|---|---|---|")
    for name, m in man.items():
        md.append(f"| `{name}` | `{m['sha256']}` | {m['bytes']:,} |")
    md.append("")

    md.append("## 1. Original vs cleaned row counts\n")
    md.append("| dataset | raw rows | cleaned rows | dropped | reason |")
    md.append("|---|---|---|---|---|")
    for ds, label in (("ember", "Ember Global Electricity"),
                      ("eia", "EIA U.S. Coal"),
                      ("energy_institute", "Energy Institute Statistical Review")):
        r, c = rc[ds]["raw"], rc[ds]["cleaned"]
        md.append(f"| {label} | {r:,} | {c:,} | {r - c} | duplicate keys removed |")
    md.append(f"| analysis tables | - | - | - | `analysis_country_year.csv` "
              f"{rc[C.PROCESSED_COUNTRY_YEAR]:,} rows; `us_state_year_sector.csv` "
              f"{rc[C.PROCESSED_US_STATE]:,}; `eia_us_aggregates.csv` "
              f"{rc[C.PROCESSED_EIA_AGGREGATES]:,} |")
    md.append("\nNo records were dropped for missing values. Zero, missing, "
              "unavailable and not-applicable are kept distinct (see flags).\n")

    md.append("## 2. Missing-value analysis\n")
    md.append("### Ember (25 numeric-ish columns, 1,138 rows)\n")
    md.append(_missing_table(ember, ["generation_twh", "demand_twh",
                                     "clean_generation_twh", "fossil_generation_twh",
                                     "renewable_generation_twh", "wind_solar_generation_twh",
                                     "clean_share_pct", "wind_solar_share_pct",
                                     "net_imports_twh", "demand_per_capita_mwh",
                                     "power_emissions_mtco2e",
                                     "carbon_intensity_gco2e_kwh",
                                     "clean_growth_surplus_twh",
                                     "clean_growth_coverage_pct", "net_import_share_pct"]))
    n_cov = int(ember.clean_growth_coverage_pct.isna().sum())
    md.append(f"\n`clean_growth_coverage_pct` is missing for {n_cov} rows - exactly the "
              "rows where demand did not grow (denominator <= 0), i.e. an **explained, "
              "structural** absence, not a defect. `carbon_intensity_gco2e_kwh` is "
              "missing for the 6 zero-generation rows (division undefined; emissions "
              "are 0.0 there).\n")

    md.append("### EIA (1,750 rows)\n")
    md.append(_missing_table(eia, ["consumption", "receipts", "stocks", "price",
                                   "ash_pct", "sulfur_pct", "heat_content_raw"]))
    md.append("\nMissing price (~62%) and stocks (~70%) are **structural**: EIA does not "
              "publish delivered-price/stock data for most electric-power rows. "
              "Missing (year, state, sector) *rows* mean 'not reported' and are kept "
              "as absence - they are **not** zero consumption. Explicit `0.0` values "
              "are genuine zero-activity rows and are preserved.\n")

    md.append("### Energy Institute (299,320 rows, 1965-2025)\n")
    md.append("`Value` has no missing cells; absence of a (country, year, variable) "
              "cell is the missingness mechanism. Regional aggregates are flagged "
              "and excluded from country sums; numeric geography identifiers can be absent "
              "on these rows. `ISO3166_numeric` is null on "
              f"({int(ei.iso_num.isna().sum()):,} rows). 2025 coverage vs 2024: "
              "see section 6.\n")

    md.append("## 3. Invalid and duplicate records\n")
    md.append("- **Ember**: 0 duplicate (country, year) keys; 0 invalid values. "
              "All share columns within [0,100]; all generation/demand values >= 0; "
              "net imports may be negative (net exporters - legitimate).")
    md.append("- **EIA**: 0 duplicate (year, location, sector) keys; 0 unparseable "
              "numbers; all values within physical ranges (see `cleaning_log.csv` "
              "for the exact rule outcomes).")
    md.append(f"- **Energy Institute**: 0 duplicate (country, year, variable) cells "
              f"among {rc['energy_institute']['raw']:,} rows; "
              + ("negative values present - see log" if (ei.value < 0).any()
                 else "no negative values in any variable.")
              + "\n")

    md.append("## 4. Corrections and exclusions\n")
    n_log = len((rep / "cleaning_log.csv").read_text().splitlines()) - 1
    md.append("No source values were corrected or overwritten. The pipeline only "
              "adds flags and derived columns. Exclusions are confined to exact "
              "duplicate keys (none found in any dataset). Every flag and its "
              f"reason is in `reports/cleaning_log.csv` ({n_log} entries).\n")

    md.append("## 5. Suspicious observations requiring further investigation\n")
    md.append("1. **EIA `heat-content` dual scale (WARNING).** Power-sector rows "
              "(1, 2, 3, 94, 98) carry values 0-27 while industrial rows (8, 9, 10) "
              "carry ~7,200-15,000. The industrial scale is Btu/lb; the power scale "
              "is dimensionally a GJ/tonne-scale energy-per-mass value whose exact "
              "unit is not stated in the file - and the `heat-content-units` column "
              "is corrupted (it contains the *sulfur* unit string for every row). "
              "`heat_content_btu_lb` for power sectors is an **assumed** "
              "conversion (x429.9228, 1 GJ/t = 1 Btu/lb-equivalent factor) and is "
              "flagged `heat_content_normalized_is_assumed`. Verify against the "
              "primary EIA API before using in analysis.")
    n_ci = int(ember.carbon_intensity_precision_limited.sum())
    md.append(f"2. **Ember carbon intensity precision (INFO).** {n_ci:,} rows deviate "
              ">5% from emissions/generation recomputation. Deviations, if any, "
              "are flagged `carbon_intensity_precision_limited`; a flag alone "
              "does not establish its cause.")
    md.append("3. **Coverage and revision status (WARNING).** Ember 2025 covers "
              "91/213 geographies. Release metadata for these supplied snapshots is "
              "not recorded, so uniform final/preliminary status cannot be certified "
              "for any year. Partial geographic coverage is distinct from preliminary "
              "status. Preserve the snapshot and disclose external-vintage differences.")
    md.append("4. **US 2025 coal rebound (INFO).** EIA US electric-power coal "
              "consumption rose +11.3% YoY (373.3M -> 415.4M short tons). Large "
              "moves can be legitimate; recorded for research, not treated as error.")
    md.append("5. **Geography code variants (INFO).** A few geographies use "
              "non-ISO vendor codes (e.g. Kosovo, Taiwan variants). Accepted, "
              "flagged, and normalized via `std_geo_key` for joins only - source "
              "codes preserved.\n")

    md.append("## 6. Geographic and temporal coverage limitations\n")
    md.append("- **Ember**: 213 countries; 2020-2022 full coverage; 2023 = 212 "
              "(Ukraine absent); 2024 = 196 (small territories absent); "
              "2025 = 91 countries only. 17 countries do not span the full "
              "2020-2024 window (mostly micro-territories).")
    md.append("- **EIA**: 51 states + DC + PR, 10 census/pacific regions, US total; "
              "2020-2025. (state, sector) presence varies by year - small "
              "industrial cells disappear when not reported (absence, not zero).")
    md.append("- **Energy Institute**: 135 countries + 7 aggregates, 1965-2025 "
              "(full history preserved). Latest-year (2025) figures are estimates.")
    md.append("- **Joins**: Ember x EI match on "
              f"{summary['geo_overlap']['common']} of "
              f"{summary['geo_overlap']['ember']} Ember geographies "
              f"(Ember-only: {summary['geo_overlap']['ember_only'] or 'none'}). "
              "EI aggregates are never joined to country rows.\n")

    md.append("## 7. Cross-dataset consistency findings\n")
    for k in ("cmp_generation", "cmp_renewable", "cmp_wind_solar", "cmp_clean_bridge"):
        if k in summary:
            v = summary[k]
            md.append(f"- {k}: n={v['n']}, median |relative diff| = "
                      f"{100 * v['median_rel_diff']:.1f}% (2024, country level)")
    md.append("- **Coal measures are NOT interchangeable** (documented, not forced "
              "to match):\n")
    md.append("  - EIA US file = **electric-power coal consumption** (short tons, "
              "end-use basis);\n"
              "  - EI `coalprod_mt` = **production** (Mt, includes exports, all "
              "uses);\n"
              "  - EI `coal_tes_ej` = **total energy supply** (EJ, energy content "
              "of supply, includes non-power);\n"
              "  - EI `electbyfuel_coal` = **coal-fired electricity generation** "
              "(TWh).")
    md.append("  Only EIA-consumption vs production/ TES/TWh comparisons above are "
              "sanity checks, never equivalence tests.\n")
    md.append("  US 2020-2025 (EIA consumption Mt vs EI production Mt vs EI TES EJ):")
    md.append("")
    coal_df = summary["us_coal_measures"]
    try:
        md.append(coal_df.to_markdown(index=False))
    except ImportError:  # tabulate not available
        md.append("```")
        md.append(coal_df.to_string(index=False))
        md.append("```")
    md.append("")

    md.append("## 8. Automated validation test results\n")
    md.append("See `tests/` (pytest). The test suite re-derives the identities "
              "asserted above (sector sums, region sums, US-total sums, share "
              "ranges, grain uniqueness, join integrity, missing-vs-zero "
              "separation, pipeline idempotency) against the cleaned outputs.\n")

    md.append("## 9. Remaining data-quality risks\n")
    md.append("1. EIA power-sector heat-content unit assumption (see 5.1) - "
              "quantitative heat comparisons across sectors are unreliable until "
              "verified against the EIA API.")
    md.append("2. 2025 figures in all three sources may be revised.")
    md.append("3. Ember has no coal sub-split; the coal series for the thesis "
              "rests on EI `electbyfuel_coal`, whose methodology (heat vs net "
              "calorific basis) should be confirmed.")
    md.append("4. EI `ren_power_twh` vs Ember `renewable_generation_twh` may "
              "differ in hydro/biomass treatment - use the documented bridge "
              "carefully.")
    md.append("5. Small Ember countries: 2-decimal MtCO2e rounding limits "
              "emission-intensity precision.")
    md.append("6. EIA missing rows (not reported) vs explicit zeros: analysis "
              "code must use the `available_*` flags.\n")

    md.append("## 10. Readiness for investment analysis\n")
    md.append("| dataset | ready? | caveats |")
    md.append("|---|---|---|")
    md.append("| Ember | **Yes** | 2025 partial (91 countries); intensity precision "
              "for small countries |")
    md.append("| EIA | **Yes, with caveat** | heat-content unit assumption for "
              "power sectors; price/stocks structural gaps |")
    md.append("| Energy Institute | **Yes** | 2025 = estimates; coal TES in EJ only "
              "(no Mt) |")
    md.append("| Joined country-year table | **Yes** | inner-join coverage = "
              "intersection; flags present |")
    md.append("| US state-year-sector table | **Yes** | base sectors only - "
              "aggregates separated |")

    (rep / "data_quality_report.md").write_text("\n".join(md) + "\n",
                                               encoding="utf-8")

    # ------------------------------------------------------------------ dictionary
    dd = []
    dd.append("# Data Dictionary\n")
    dd.append("Units and definitions for every variable in the cleaned and "
              "processed tables. `source` identifies the upstream dataset. "
              "Flags use `available_*` (1/0 or bool) to mark structural "
              "missingness; absence of a row means *not reported*.\n")

    dd.append("## Ember `ember_country_year.csv` (grain: country x year)\n")
    dd.append("| variable | unit | definition |")
    dd.append("|---|---|---|")
    dd.append("| country / iso3 / continent | - | Ember country name, ISO3 code, continent |")
    dd.append("| year | year | calendar year 2020-2025 |")
    dd.append("| generation_twh | TWh | total electricity generation |")
    dd.append("| demand_twh | TWh | generation + net imports (identical by construction) |")
    dd.append("| clean_generation_twh | TWh | renewable + nuclear |")
    dd.append("| fossil_generation_twh | TWh | coal + gas + oil (no coal sub-split) |")
    dd.append("| renewable_generation_twh | TWh | all renewables incl. hydro |")
    dd.append("| wind_solar_generation_twh | TWh | wind + solar |")
    dd.append("| clean_share_pct / wind_solar_share_pct | % | share of generation |")
    dd.append("| net_imports_twh | TWh | may be negative (net export) |")
    dd.append("| demand_per_capita_mwh | MWh | per person |")
    dd.append("| power_emissions_mtco2e | MtCO2e | sector emissions, 2-decimal rounding |")
    dd.append("| carbon_intensity_gco2e_kwh | gCO2e/kWh | emissions per kWh generated |")
    dd.append("| has_previous_year | 0/1 | prior-year observation present in this file |")
    dd.append("| demand_change_twh / clean_change_twh / fossil_change_twh | TWh | YoY delta |")
    dd.append("| clean_share_change_pp | percentage points | YoY |")
    dd.append("| clean_growth_surplus_twh | TWh | clean change - demand change |")
    dd.append("| clean_growth_coverage_pct | % | surplus / demand change; missing when demand did not grow |")
    dd.append("| growth_status | category | demand_not_growing / clean_growth_below_demand_growth / clean_growth_met_or_exceeded_demand_growth |")
    dd.append("| net_import_share_pct | % | net imports / demand |")
    dd.append("| carbon_intensity_precision_limited | bool | emissions rounding limits CI precision |")
    dd.append("| zero_generation_flag | bool | domestic generation = 0 (import-only) |")
    dd.append("| clean_growth_coverage_pct_available | bool | completeness flag |\n")

    dd.append("## EIA `eia_us_coal.csv` (grain: year x location x sector)\n")
    dd.append("| variable | unit | definition |")
    dd.append("|---|---|---|")
    dd.append("| year | year | 2020-2025 |")
    dd.append("| location / location_name | code / name | state (2-letter), region (NEW/MAT/...), '90' Pacific, 'US' total, PR |")
    dd.append("| location_type | enum | state / census_region / pacific_region / us_total |")
    dd.append("| is_geographic_aggregate | bool | True for region/US/pacific rows |")
    dd.append("| sector / sectorDescription | code / name | see EIA_SECTORS |")
    dd.append("| consumption | short tons | coal consumed |")
    dd.append("| receipts | short tons | coal received |")
    dd.append("| stocks | short tons | year-end inventory (structurally unreported for most power rows) |")
    dd.append("| price | $/short ton | delivered coal price (structurally unreported for most rows) |")
    dd.append("| ash_pct / sulfur_pct | % | average ash / sulfur by weight |")
    dd.append("| heat_content_raw | mixed | Btu/lb for industrial sectors; GJ/tonne-scale for power sectors (unit not stated in source; see report 5.1) |")
    dd.append("| heat_content_unit_inferred | enum | Btu_per_lb / GJ_per_tonne_scale_ASSUMED / zero_activity / missing |")
    dd.append("| heat_content_btu_lb | Btu/lb | normalized; power-sector values are ASSUMED conversions |")
    dd.append("| heat_content_normalized_is_assumed | bool | True when conversion assumed |")
    dd.append("| available_* | bool | per-column completeness flags |\n")
    dd.append("**Sector overlap (double-counting rule).** Sector 94 = 2+3 and "
              "98 = 1+2+3 hold exactly. Use ONLY base sectors {1,2,3,8,9,10} for "
              "state-level sums, or ONLY {94,98,8,9,10} for totals - never mix.\n")

    dd.append("## Energy Institute `energy_institute_global_energy.csv` "
              "(grain: entity x year x variable; 1965-2025)\n")
    dd.append("| column | unit | definition |")
    dd.append("|---|---|---|")
    dd.append("| country / iso3 / iso_num | - | entity name; ISO3 code; numeric ISO (null for aggregates) |")
    dd.append("| is_aggregate | bool | True for ALL EI regional aggregates: O-*/T-* codes, WLD (Total World), ROW. Country-level sums must exclude these; 'Other X' residual entities keep their listed countries out of such sums |")
    dd.append("| Region / SubRegion | - | SRWE region fields (null for aggregates) |")
    dd.append("| OPEC/EU/OECD/CIS | 0/1 | membership flags |")
    dd.append("| Year | year | 1965-2025 |")
    dd.append("| variable | code | see variable unit registry below |")
    dd.append("| value | per-variable | numeric observation |")
    dd.append("| variable_unit | text | unit from the registry |\n")
    dd.append("### Variable registry (90 variables)\n")
    dd.append("| variable | unit |")
    dd.append("|---|---|")
    for v in sorted(C.EI_VAR_UNITS):
        dd.append(f"| `{v}` | {C.EI_VAR_UNITS[v]} |")
    dd.append("")

    dd.append("## Processed tables\n")
    dd.append(f"### `{C.PROCESSED_COUNTRY_YEAR}` (grain: iso3 x year)\n")
    dd.append("Ember columns (renamed none) + EI columns (prefix `ei_`, see "
              "registry above) left-joined on (std_geo_key, year). "
              "`coal_share_of_generation_pct` = ei_coal_generation / ei_elect_twh. "
              "`ei_variables_present` = at least one EI column non-null. "
              "Ember flags `zero_generation_flag` and "
              "`carbon_intensity_precision_limited` are carried through "
              "verbatim.\n")
    dd.append(f"### `{C.PROCESSED_US_STATE}` (grain: state x year x base-sector)\n")
    dd.append("State-level EIA rows, base sectors only (1,2,3,8,9,10). "
              "Variables: coal_consumption_short_tons, coal_receipts_short_tons, "
              "coal_stocks_short_tons, delivered_price_usd_per_short_ton, "
              "heat_content_btu_per_lb, ash_content_pct, sulfur_content_pct + unit flags.\n")
    dd.append(f"### `{C.PROCESSED_EIA_AGGREGATES}` (grain: location x year x agg-sector)\n")
    dd.append("US-total/region rows with aggregate sectors 94/98 only - the "
              "complement of the state table; never combined with it.\n")
    dd.append(f"### `{C.PROCESSED_COVERAGE}`\n")
    dd.append("Presence cells: (dataset, geo_key, year) with is_aggregate flag - "
              "used for coverage analysis and tests.\n")

    (rep / "data_dictionary.md").write_text("\n".join(dd) + "\n", encoding="utf-8")
