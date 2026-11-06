"""Shared configuration: paths, dataset constants, and reference vocabularies.

Everything here is deterministic (no timestamps, no randomness) so that the
pipeline produces byte-identical outputs on every run.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
CLEANED = DATA / "cleaned"
PROCESSED = DATA / "processed"
REPORTS = ROOT / "reports"

RAW_EMBER = "country_year_electricity_2020_2025.csv"
RAW_EIA = "eia_coal_consumption_quality_2020_2025.csv"
RAW_EI = "Statistical Review of World Energy Narrow format.csv"

CLEANED_EMBER = "ember_country_year.csv"
CLEANED_EIA = "eia_us_coal.csv"
CLEANED_EI = "energy_institute_global_energy.csv"

PROCESSED_COUNTRY_YEAR = "analysis_country_year.csv"
PROCESSED_US_STATE = "us_state_year_sector.csv"
PROCESSED_EIA_AGGREGATES = "eia_us_aggregates.csv"
PROCESSED_COVERAGE = "coverage_calendar.csv"

PIPELINE_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Ember Global Electricity (country_year_electricity_2020_2025.csv)
# ---------------------------------------------------------------------------
EMBER_NUMERIC_COLS = [
    "generation_twh", "demand_twh", "clean_generation_twh", "fossil_generation_twh",
    "renewable_generation_twh", "wind_solar_generation_twh", "clean_share_pct",
    "wind_solar_share_pct", "net_imports_twh", "demand_per_capita_mwh",
    "power_emissions_mtco2e", "carbon_intensity_gco2e_kwh", "demand_change_twh",
    "clean_change_twh", "fossil_change_twh", "clean_share_change_pp",
    "clean_growth_surplus_twh", "clean_growth_coverage_pct", "net_import_share_pct",
]
EMBER_SHARE_COLS = ["clean_share_pct", "wind_solar_share_pct", "clean_share_change_pp",
                    "clean_growth_coverage_pct"]
# Tolerance for identity checks, in TWh (source rounds to 2 decimals).
EMBER_IDENTITY_TOL = 0.05

# ---------------------------------------------------------------------------
# EIA U.S. Coal Consumption & Quality (eia_coal_consumption_quality_2020_2025.csv)
# ---------------------------------------------------------------------------
# Sector codes as used by the EIA coal consumption/quality tables.
# Base sectors are mutually exclusive; 94 and 98 are aggregations (overlapping).
EIA_SECTORS = {
    1: "Electric Utility",
    2: "IPP Non-CHP",
    3: "IPP CHP",
    8: "Commercial and Institutional",
    9: "Coke Plants",
    10: "Other Industrial",
    94: "Independent Power Producers",   # = 2 + 3
    98: "Electric Power",               # = 1 + 2 + 3
}
EIA_BASE_SECTORS = [1, 2, 3, 8, 9, 10]
EIA_AGGREGATE_SECTORS = {94: [2, 3], 98: [1, 2, 3]}
EIA_POWER_SECTORS = [1, 2, 3, 94, 98]    # sectors whose heat-content is on the
                                         # small (GJ/tonne-scale) reading
EIA_INDUSTRIAL_SECTORS = [8, 9, 10]      # sectors whose heat-content is in Btu/lb

# 50 states + DC + PR. (DE was missing from an earlier draft of this list -
# Delaware rows existed in the data and were mislabelled "unknown".)
EIA_STATE_CODES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
    "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
    "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
    "WV", "WI", "WY", "PR",
]
# Census regions / EIA sub-regions and their member state codes.
EIA_REGIONS = {
    "NEW": ["CT", "MA", "ME", "NH", "RI", "VT"],              # New England
    "MAT": ["NJ", "NY", "PA"],                                # Middle Atlantic
    "ENC": ["IL", "IN", "MI", "OH", "WI"],                    # East North Central
    "ESC": ["AL", "KY", "MS", "TN"],                          # East South Central
    "SAT": ["DE", "DC", "FL", "GA", "MD", "NC", "SC", "VA", "WV"],  # South Atlantic
    "WNC": ["IA", "KS", "MN", "MO", "NE", "ND", "SD"],        # West North Central
    "WSC": ["AR", "LA", "OK", "TX"],                          # West South Central
    "MTN": ["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY"],  # Mountain
}
# Pacific region (location code "90"); PCC/PCN are its contiguous/noncontiguous parts.
EIA_PACIFIC_PCC = ["CA", "OR", "WA"]
EIA_PACIFIC_PCN = ["AK", "HI"]
EIA_US_TOTAL_CODE = "US"

# 1 GJ/tonne expressed in Btu/lb (used to normalize the small-scale readings;
# see the unit split documented in reports/data_quality_report.md).
GJ_PER_TONNE_TO_BTU_PER_LB = 429.922766795  # 947817.12 Btu / 2204.62262 lb

# ---------------------------------------------------------------------------
# Energy Institute Statistical Review (long format)
# ---------------------------------------------------------------------------
# The EI file also carries pre-computed regional aggregates with vendor
# prefixes: "O-*" (Other region), "T-*" (Total region), plus WLD (Total
# World) and ROW (Rest of World). ALL of these must never be summed with
# individual-country rows; the cleaned data's `is_aggregate` flag marks the
# full set (the 7 codes below are the ones that also carry OPEC/OECD
# membership flags, i.e. are referenced by other checks).
EI_AGGREGATE_ISO3 = {
    "O-EAFR": "Other Eastern Africa",
    "O-MAFR": "Other Middle Africa",
    "O-NAM": "Other North America",
    "O-WAFR": "Other Western Africa",
    "ROW": "Rest of World",
    "T-NOPEC": "Total Non-OPEC",
    "T-OPEC": "Total OPEC",
}
EI_AGGREGATE_PREFIXES = ("O-", "T-")
EI_AGGREGATE_EXTRA = {"WLD", "ROW"}
# Units for the 90 variables in this extract, per the Statistical Review of
# World Energy methodology (see reports/data_dictionary.md).
EI_VAR_UNITS = {
    "biodiesel_cons_kboed": "thousand barrels of oil equivalent/day (kboed)",
    "biodiesel_prod_kboed": "kboed",
    "biodiesel_prod_pj": "petajoules (PJ)",
    "biodiesel_tes_pj": "PJ",
    "biofuels_cons_kbd": "thousand barrels/day (kbd)",
    "biofuels_cons_kboed": "kboed",
    "biofuels_prod_kbd": "kbd",
    "biofuels_prod_kboed": "kboed",
    "biofuels_prod_pj": "PJ",
    "biofuels_tes_ej": "exajoules (EJ)",
    "biofuels_tes_pj": "PJ",
    "biogeo_tes_ej": "EJ",
    "biogeo_twh": "terawatt-hours (TWh)",
    "biogeo_twh_net": "TWh",
    "co2_combust_mtco2": "megatonnes CO2 (MtCO2)",
    "co2_combust_pc": "tonnes CO2/capita",
    "co2_combust_per_tes_ej": "MtCO2/EJ",
    "co2_mtco2": "MtCO2",
    "coal_tes_ej": "EJ",
    "coalprod_ej": "EJ",
    "coalprod_mt": "million tonnes (Mt)",
    "cobalt_kt": "thousand tonnes (kt)",
    "cobaltres_kt": "kt",
    "diesel_gasoil_cons_kbd": "kbd",
    "elect_twh": "TWh",
    "electbyfuel_coal": "TWh",
    "electbyfuel_gas": "TWh",
    "electbyfuel_hydro": "TWh",
    "electbyfuel_nuclear": "TWh",
    "electbyfuel_oil": "TWh",
    "electbyfuel_other": "TWh",
    "electbyfuel_ren_power": "TWh",
    "electbyfuel_total": "TWh",
    "ethanol_cons_kboed": "kboed",
    "ethanol_prod_kboed": "kboed",
    "ethanol_prod_pj": "PJ",
    "ethanol_tes_pj": "PJ",
    "fuel_oil_cons_kbd": "kbd",
    "gas_tes_ej": "EJ",
    "gascons_bcfd": "billion cubic feet/day",
    "gascons_bcm": "billion cubic metres",
    "gasflared_bcm": "bcm",
    "gasflared_mtco2": "MtCO2",
    "gasoline_cons_kbd": "kbd",
    "gasprod_bcfd": "bcfd",
    "gasprod_bcm": "bcm",
    "gasprod_ej": "EJ",
    "graphite_kt": "kt",
    "graphiteres_kt": "kt",
    "hydro_tes_ej": "EJ",
    "hydro_twh": "TWh",
    "hydro_twh_net": "TWh",
    "kerosene_cons_kbd": "kbd",
    "light_dist_cons_kbd": "kbd",
    "liqcons_kbd": "kbd",
    "lithium_kt": "kt",
    "lithiumres_kt": "kt",
    "lpg_cons_kbd": "kbd",
    "methane_process_mtco2": "MtCO2",
    "middle_dist_cons_kbd": "kbd",
    "naphtha_cons_kbd": "kbd",
    "nuclear_tes_ej": "EJ",
    "nuclear_twh": "TWh",
    "nuclear_twh_net": "TWh",
    "oil_tes_ej": "EJ",
    "oilcons_kbd": "kbd",
    "oilcons_mt": "million tonnes",
    "oilprod_crudecond_kbd": "kbd",
    "oilprod_kbd": "kbd",
    "oilprod_mt": "million tonnes",
    "oilprod_ngl_kbd": "kbd",
    "other_oil_cons_kbd": "kbd",
    "pop": "millions",
    "rareearths_kt": "kt",
    "rareearthsres_kt": "kt",
    "refcap_kbd": "kbd",
    "refcaputil_pct": "percent",
    "refthru_kbd": "kbd",
    "ren_power_tes_ej": "EJ",
    "ren_power_twh": "TWh",
    "ren_power_twh_net": "TWh",
    "renewables_tes_ej": "EJ",
    "solar_tes_ej": "EJ",
    "solar_twh": "TWh",
    "solar_twh_net": "TWh",
    "tes_ej": "EJ",
    "tes_gj_pc": "GJ/capita",
    "wind_tes_ej": "EJ",
    "wind_twh": "TWh",
    "wind_twh_net": "TWh",
}

# Years of interest for the investment thesis.
FOCUS_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
