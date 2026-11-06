"""Builds analysis-ready tables (data/processed/) from the cleaned datasets.

Tables:
* analysis_country_year.csv  - Ember base + Energy Institute joins (country, year)
* us_state_year_sector.csv   - EIA state-level, BASE sectors only (no double count)
* eia_us_aggregates.csv      - EIA US-total/region rows, aggregate sectors only
* coverage_calendar.csv      - per-source presence by entity x year (focus years)

Grain guarantees (enforced here and in tests):
* country table: at most one row per (geo_key, year, source variable block)
* state table:   at most one row per (state, year, base-sector)
* aggregate table: at most one row per (location, year, aggregate-sector)
"""
from __future__ import annotations

import pandas as pd

from . import config as C
from .audit_common import AuditLog, stable_sort
from .iso3166 import std_geo_key

EI_COUNTRY_VARS = {
    "elect_twh": "ei_elect_twh",
    "electbyfuel_total": "ei_electbyfuel_total_twh",
    "electbyfuel_coal": "ei_coal_generation_twh",
    "electbyfuel_gas": "ei_gas_generation_twh",
    "electbyfuel_nuclear": "ei_nuclear_generation_twh",
    "electbyfuel_ren_power": "ei_ren_power_generation_twh",
    "ren_power_twh": "ei_ren_power_twh",
    "wind_twh": "ei_wind_twh",
    "solar_twh": "ei_solar_twh",
    "hydro_twh": "ei_hydro_twh",
    "nuclear_twh": "ei_nuclear_twh",
    "coalprod_mt": "ei_coal_production_mt",
    "coalprod_ej": "ei_coal_production_ej",
    "coal_tes_ej": "ei_coal_tes_ej",
    "tes_ej": "ei_tes_ej",
    "co2_combust_mtco2": "ei_co2_combust_mtco2",
    "pop": "ei_population_millions",
}


def build_country_year(ember: pd.DataFrame, ei: pd.DataFrame,
                       log: AuditLog) -> pd.DataFrame:
    e = ei[~ei.is_aggregate].copy()
    e["geo_key"] = e.iso3.map(std_geo_key)
    piv = e.pivot_table(index=["geo_key", "Year"], columns="variable",
                        values="value", aggfunc="first")
    # EI_COUNTRY_VARS maps ORIGINAL EI variable name -> prefixed column name
    piv = piv.rename(columns={orig: prefixed for orig, prefixed
                             in EI_COUNTRY_VARS.items() if orig in piv.columns})
    piv = piv.reset_index()

    eb = ember[["iso3", "country", "continent", "year"] + C.EMBER_NUMERIC_COLS
               + ["has_previous_year", "growth_status",
                 "zero_generation_flag",
                 "carbon_intensity_precision_limited"]].copy()
    eb["geo_key"] = eb.iso3.map(std_geo_key)

    out = eb.merge(piv, left_on=["geo_key", "year"], right_on=["geo_key", "Year"],
                   how="left")
    out = out.drop(columns=["Year"])
    if "geo_key_right" in out.columns:
        out = out.drop(columns=["geo_key_right"])

    # derived, all nullable - never invented
    gen_ei = out.get("ei_elect_twh")
    coal = out.get("ei_coal_generation_twh")
    if gen_ei is not None and coal is not None:
        out["coal_share_of_generation_pct"] = (coal / gen_ei * 100
                                               ).where(gen_ei > 0)
    out["ei_variables_present"] = out[[c for c in out.columns if c.startswith("ei_")]] \
        .notna().any(axis=1)

    # grain check
    dups = out.duplicated(subset=["iso3", "year"]).sum()
    assert dups == 0, f"country-year grain violated ({dups} dups)"
    log.add("grain_country_year", "info", "verify", "processed", "iso3,year",
            f"{len(out)} rows, 1 row per (iso3, year); "
            f"{int(out.ei_variables_present.sum())} rows have at least one EI variable")
    return stable_sort(out, ["country", "year"])


def build_us_state(eia: pd.DataFrame, log: AuditLog) -> pd.DataFrame:
    st = eia[eia.location_type == "state"].copy()
    st = st[st.sector.isin(C.EIA_BASE_SECTORS)].copy()  # base sectors only
    cols = ["year", "location", "location_name", "sector", "sectorDescription",
            "consumption", "receipts", "stocks", "price",
            "ash_pct", "heat_content_raw", "heat_content_btu_lb",
            "heat_content_unit_inferred", "sulfur_pct"]
    out = st[cols].rename(columns={
        "location": "state_code", "location_name": "state_name",
        "sector": "sector_code", "sectorDescription": "sector_name",
        "consumption": "coal_consumption_short_tons",
        "receipts": "coal_receipts_short_tons",
        "stocks": "coal_stocks_short_tons",
        "price": "delivered_price_usd_per_short_ton",
        "ash_pct": "ash_content_pct",
        "heat_content_btu_lb": "heat_content_btu_per_lb",
        "sulfur_pct": "sulfur_content_pct",
        "heat_content_raw": "heat_content_raw",
        "heat_content_unit_inferred": "heat_content_unit_inferred",
    })
    out["units"] = ("consumption/receipts/stocks: short tons; price: $/short ton; "
                    "heat: Btu/lb (industrial) or GJ/tonne scale ASSUMED->Btu/lb "
                    "(power sectors, see flag); ash/sulfur: %")
    dups = out.duplicated(subset=["state_code", "year", "sector_code"]).sum()
    assert dups == 0, f"state-year-sector grain violated ({dups} dups)"
    log.add("grain_us_state", "info", "verify", "processed",
            "state,year,sector",
            f"{len(out)} rows; base sectors only ({C.EIA_BASE_SECTORS}) - aggregates "
            "94/98 excluded to prevent double counting")
    return stable_sort(out, ["year", "state_code", "sector_code"])


def build_eia_aggregates(eia: pd.DataFrame, log: AuditLog) -> pd.DataFrame:
    agg = eia[eia.is_geographic_aggregate].copy()
    agg = agg[agg.sector.isin(C.EIA_AGGREGATE_SECTORS)].copy()  # aggregate sectors only
    out = agg[["year", "location", "location_name", "location_type", "sector",
               "sectorDescription", "consumption", "receipts", "price",
               "heat_content_btu_lb", "ash_pct", "sulfur_pct"]].rename(columns={
        "location": "location_code", "location_name": "location_name",
        "sector": "sector_code", "sectorDescription": "sector_name",
        "consumption": "coal_consumption_short_tons",
        "receipts": "coal_receipts_short_tons",
        "price": "delivered_price_usd_per_short_ton",
        "ash_pct": "ash_content_pct", "sulfur_pct": "sulfur_content_pct",
    })
    dups = out.duplicated(subset=["location_code", "year", "sector_code"]).sum()
    assert dups == 0, f"aggregate grain violated ({dups} dups)"
    log.add("grain_eia_aggregates", "info", "verify", "processed",
            "location,year,sector",
            f"{len(out)} rows; geographic aggregates with aggregate sectors only "
            "(94/98) - never combine with the state table")
    return stable_sort(out, ["year", "location_code", "sector_code"])


def build_coverage(ember: pd.DataFrame, eia: pd.DataFrame, ei: pd.DataFrame,
                   log: AuditLog) -> pd.DataFrame:
    rows = []
    # Ember: (geo, year) presence
    for (geo, yr), g in ember.groupby(["iso3", "year"]):
        rows.append({"dataset": "ember", "geo_key": std_geo_key(geo),
                     "iso3": geo, "year": int(yr), "present": 1})
    # EI: focus years only, country-level (aggregates listed separately)
    e = ei[ei.Year.isin(C.FOCUS_YEARS)]
    for (iso, yr), g in e.groupby(["iso3", "Year"]):
        agg = (iso in C.EI_AGGREGATE_EXTRA
               or iso.startswith(C.EI_AGGREGATE_PREFIXES))
        rows.append({"dataset": "energy_institute",
                     "geo_key": iso.lower() if agg else std_geo_key(iso),
                     "iso3": iso, "year": int(yr),
                     "present": 1,
                     "is_aggregate": int(agg)})
    # EIA: focus years, states + US total
    ee = eia[eia.year.isin(C.FOCUS_YEARS)]
    for (loc, yr), g in ee[ee.location.isin(C.EIA_STATE_CODES + [C.EIA_US_TOTAL_CODE])] \
            .groupby(["location", "year"]):
        rows.append({"dataset": "eia", "geo_key": str(loc).lower(),
                     "iso3": str(loc), "year": int(yr), "present": 1,
                     "is_aggregate": int(loc == C.EIA_US_TOTAL_CODE)})
    df = pd.DataFrame(rows)
    df["is_aggregate"] = df.get("is_aggregate", 0).fillna(0).astype(int)
    log.add("coverage", "info", "verify", "processed", "coverage_calendar",
            f"{len(df)} presence cells across 3 datasets (focus years for EI/EIA)")
    return stable_sort(df, ["dataset", "geo_key", "year"])


def process(ember: pd.DataFrame, eia: pd.DataFrame, ei: pd.DataFrame,
            log: AuditLog) -> dict[str, pd.DataFrame]:
    return {
        C.PROCESSED_COUNTRY_YEAR: build_country_year(ember, ei, log),
        C.PROCESSED_US_STATE: build_us_state(eia, log),
        C.PROCESSED_EIA_AGGREGATES: build_eia_aggregates(eia, log),
        C.PROCESSED_COVERAGE: build_coverage(ember, eia, ei, log),
    }
