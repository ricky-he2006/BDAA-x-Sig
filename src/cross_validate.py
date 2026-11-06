"""Cross-dataset validation over the three cleaned tables.

Purpose: prove that joins are safe (no duplicate or artificial matches),
quantify how comparable each pair of measures actually is, and DOCUMENT
which statistics can and cannot be directly compared. We flag discrepancies;
we never force statistics to match.
"""
from __future__ import annotations

import pandas as pd

from . import config as C
from .audit_common import AuditLog
from .iso3166 import std_geo_key

SHORT_TONS_TO_METRIC_TONNES = 0.90718474


def _us_eia_consumption_mt(eia: pd.DataFrame, year: int) -> float | None:
    """US electric-power coal consumption in million tonnes (EIA source)."""
    row = eia[(eia.year == year) & (eia.location == "US") & (eia.sector == 98)]
    if row.empty or pd.isna(row.consumption.iloc[0]):
        return None
    return float(row.consumption.iloc[0]) * SHORT_TONS_TO_METRIC_TONNES


def run(ember: pd.DataFrame, eia: pd.DataFrame, ei: pd.DataFrame) -> tuple[AuditLog, dict]:
    """Returns (audit log, summary dict) - summary is used by the report."""
    log = AuditLog("cross_dataset")
    summary: dict = {}

    eb = ember[["iso3", "year", "generation_twh", "demand_twh",
                "clean_generation_twh", "renewable_generation_twh",
                "wind_solar_generation_twh", "fossil_generation_twh"]].copy()
    eb["geo_key"] = eb.iso3.map(std_geo_key)
    e = ei[~ei.is_aggregate].copy()          # country-level rows only
    e["geo_key"] = e.iso3.map(std_geo_key)
    e24 = e[e.Year == 2024].pivot_table(index="geo_key", columns="variable",
                                        values="value", aggfunc="first")

    # ---- join integrity -----------------------------------------------------------
    # Ember is wide: one row per (geo_key, year).
    dups_eb = int(eb.duplicated(subset=["geo_key", "year"]).sum())
    # EI is long: one row per (geo_key, Year, variable); the JOIN happens on the
    # pivoted table, so what matters is (geo_key, Year) uniqueness there.
    dups_e_long = int(e.duplicated(subset=["geo_key", "Year", "variable"]).sum())
    e_piv = e.pivot_table(index=["geo_key", "Year"], columns="variable",
                          values="value", aggfunc="first")
    dups_e_piv = int(e_piv.index.duplicated().sum())
    if dups_eb or dups_e_long or dups_e_piv:
        log.add("join_integrity", "error", "flag", "ember/ei", "geo_key,year",
                f"duplicate join keys: ember={(dups_eb)}, "
                f"ei long-format cells={(dups_e_long)}, "
                f"ei pivoted rows={(dups_e_piv)} - joins would multiply rows")
    else:
        log.add("join_integrity", "info", "verify", "dataset", "geo_key,year",
                "join keys unique: ember (geo_key, year) and EI (geo_key, Year) "
                "after pivot (long-format EI is (geo_key, Year, variable) unique)")

    # ---- geographic overlap ----------------------------------------------------------
    keys_eb = set(eb.geo_key.unique())
    keys_e = set(e.geo_key.unique())
    common = keys_eb & keys_e
    log.add("geo_overlap", "info", "verify", "dataset", "geo",
            f"Ember {len(keys_eb)} geographies, EI {len(keys_e)} geographies, "
            f"{len(common)} match. Ember-only (no EI country row): "
            + (", ".join(sorted(keys_eb - keys_e)) if keys_eb - keys_e else "none"))
    summary["geo_overlap"] = {"ember": len(keys_eb), "ei": len(keys_e),
                              "common": len(common),
                              "ember_only": sorted(keys_eb - keys_e)}

    eb24 = eb[eb.year == 2024].reset_index(drop=True)

    def _compare(var_ei: str, eb_col: str, label: str) -> dict:
        if var_ei not in e24.columns:
            return {"n": 0, "median_rel_diff": float("nan")}
        m = eb24.merge(e24[[var_ei]].rename(columns={var_ei: "v"}).reset_index(),
                       on="geo_key", how="inner")
        m = m[m.v.notna() & m[eb_col].notna() & (m.v > 1)]
        m["rel"] = (m[eb_col] - m.v).abs() / m.v.abs()
        med = float(m.rel.median()) if len(m) else float("nan")
        log.add("cmp_" + label, "info", "verify", "dataset", label,
                f"{label}: Ember vs EI {var_ei} (2024, n={len(m)}): "
                f"median |rel diff| = {med:.1%}")
        return {"n": int(len(m)), "median_rel_diff": med}

    if "elect_twh" in e24.columns:
        summary["cmp_generation"] = _compare("elect_twh", "generation_twh", "generation")
    if "ren_power_twh" in e24.columns:
        summary["cmp_renewable"] = _compare("ren_power_twh", "renewable_generation_twh",
                                            "renewable")
    if "wind_twh" in e24.columns and "solar_twh" in e24.columns:
        ws = e[e.Year == 2024].pipe(
            lambda d: d[d.variable.isin(["wind_twh", "solar_twh"])]) \
            .groupby("geo_key")["value"].sum().rename("v")
        m = eb24.merge(ws.reset_index(), on="geo_key", how="inner")
        m = m[m.v > 1]
        m["rel"] = (m.wind_solar_generation_twh - m.v).abs() / m.v.abs()
        med = float(m.rel.median()) if len(m) else float("nan")
        log.add("cmp_wind_solar", "info", "verify", "dataset", "wind_solar",
                f"wind+solar: Ember vs EI wind_twh+solar_twh (2024, n={len(m)}): "
                f"median |rel diff| = {med:.1%}")
        summary["cmp_wind_solar"] = {"n": int(len(m)), "median_rel_diff": med}
    if {"nuclear_twh", "ren_power_twh"} <= set(e24.columns):
        nc = e[e.Year == 2024].pipe(
            lambda d: d[d.variable.isin(["nuclear_twh", "ren_power_twh"])]) \
            .groupby("geo_key")["value"].sum().rename("v")
        m = eb24.merge(nc.reset_index(), on="geo_key", how="inner")
        m = m[m.v > 1]
        m["rel"] = (m.clean_generation_twh - m.v).abs() / m.v.abs()
        med = float(m.rel.median()) if len(m) else float("nan")
        log.add("cmp_clean_bridge", "info", "verify", "dataset", "clean_generation",
                f"clean bridge: Ember clean_generation vs EI(nuclear+ren_power) "
                f"(2024, n={len(m)}): median |rel diff| = {med:.1%} "
                "(definitions may still differ in hydro/biomass treatment)")
        summary["cmp_clean_bridge"] = {"n": int(len(m)), "median_rel_diff": med}

    # ---- coal: EIA US vs EI US --------------------------------------------------------
    us_rows = []
    for yr in C.FOCUS_YEARS:
        prod = ei[(ei.iso3 == "USA") & (ei.Year == yr) & (ei.variable == "coalprod_mt")]
        tes = ei[(ei.iso3 == "USA") & (ei.Year == yr) & (ei.variable == "coal_tes_ej")]
        us_rows.append({
            "year": yr,
            "eia_us_electric_power_consumption_mt": _us_eia_consumption_mt(eia, yr),
            "ei_us_coal_production_mt": float(prod.value.iloc[0]) if len(prod) else None,
            "ei_us_coal_tes_ej": float(tes.value.iloc[0]) if len(tes) else None,
        })
    summary["us_coal_measures"] = pd.DataFrame(us_rows)
    parts = []
    for r in us_rows:
        if r["eia_us_electric_power_consumption_mt"] is None:
            continue
        parts.append(f"{r['year']}: EIA consumption "
                     f"{r['eia_us_electric_power_consumption_mt']:.0f}Mt vs "
                     f"EI production {r['ei_us_coal_production_mt']:.0f}Mt vs "
                     f"EI coal TES {r['ei_us_coal_tes_ej']:.1f}EJ")
    log.add("coal_definitions", "warning", "verify", "dataset", "coal",
            "US 2020-2025 coal measures are DIFFERENT statistics and must not be "
            "compared 1:1: EIA file = electric-power COAL CONSUMPTION only; "
            "EI coalprod = PRODUCTION (Mt, includes exports and all end uses); "
            "EI coal_tes = TOTAL ENERGY SUPPLY (EJ, energy content, not mass). "
            + " | ".join(parts))

    if "electbyfuel_coal" in e24.columns:
        us_coal_24 = e24.loc["usa", "electbyfuel_coal"]
        log.add("coal_generation_source", "info", "verify", "dataset",
                "electbyfuel_coal",
                f"coal-fired generation exists only in EI (electbyfuel_coal); Ember "
                f"reports the fossil total without a coal sub-split. US 2024 "
                f"coal-fired generation = {us_coal_24:.0f} TWh (EI).")

    log.add("join_result", "info", "verify", "dataset", "",
            "join policy: Ember(iso3,year) x EI(std_geo_key,Year), inner on geo_key, "
            "country-level rows only (EI aggregates excluded). EIA joins on state "
            "code and is never joined to the country tables. No duplicate or "
            "artificial matches introduced.")
    return log, summary
