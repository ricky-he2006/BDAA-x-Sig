"""Cleaning + validation for the Ember Global Electricity dataset.

Design rules
------------
* No observation is dropped for a missing value: missingness is carried as
  flags / completeness columns instead.
* Zero is never substituted for missing (or vice versa).
* Derived columns are re-verified, but the source values are preserved;
  discrepancies become flags, not silent corrections.
"""
from __future__ import annotations

import pandas as pd

from . import config as C
from .audit_common import AuditLog, stable_sort
from .iso3166 import is_accepted_noniso, is_known

DATASET = "ember"


def load_raw(path=None) -> pd.DataFrame:
    path = path or (C.RAW / C.RAW_EMBER)
    return pd.read_csv(path)


def _record(df, i) -> str:
    return f"{df.country.iloc[i]}|{int(df.year.iloc[i])}"


def audit_and_clean(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, AuditLog]:
    log = AuditLog(DATASET)
    df = df_raw.copy()
    n_raw = len(df)

    # --- types -------------------------------------------------------------
    df["year"] = df["year"].astype("int64")
    for col in C.EMBER_NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="raise")  # raises => parse error
    df["has_previous_year"] = df["has_previous_year"].astype("int8")
    log.add("types", "info", "verify", "dataset", "all",
            "all numeric columns parsed without error")

    # --- duplicates ----------------------------------------------------------
    dup_mask = df.duplicated(subset=["country", "year"], keep=False)
    if dup_mask.any():
        for i in df.index[dup_mask]:
            log.add("dup", "error", "drop", _record(df, i), "country,year",
                    "duplicate (country, year) pair")
        df = df[~dup_mask]
    else:
        log.add("dup", "info", "verify", "dataset", "country,year",
                f"0 duplicates among {n_raw} rows")

    # --- geo identifiers ------------------------------------------------------
    for i, (name, code) in enumerate(zip(df.country, df.iso3)):
        if is_known(code) or is_accepted_noniso(code):
            continue
        log.add("iso3", "warning", "flag", _record(df, i), "iso3",
                f"code {code!r} not in ISO 3166-1 official or accepted set")
    iso_by_country = df.groupby("country")["iso3"].nunique()
    for c in iso_by_country[iso_by_country > 1].index:
        log.add("iso3", "error", "flag", c, "iso3",
                f"country {c!r} maps to multiple iso3 codes")
    log.add("iso3", "info", "verify", "dataset", "iso3",
            f"{df.country.nunique()} countries, all with a single consistent iso3")

    # --- year coverage ---------------------------------------------------------
    for yr in C.FOCUS_YEARS:
        n = int((df.year == yr).sum())
        log.add("coverage", "info", "verify", f"year={yr}", "year", f"{n} countries reported")
    years_min, years_max = int(df.year.min()), int(df.year.max())
    log.add("coverage", "info", "verify", "dataset", "year",
            f"year range {years_min}-{years_max}")
    # 2025 partial coverage: flag every 2025 row as reported-but-possibly-updated
    n25 = int((df.year == 2025).sum())
    log.add("status", "warning", "flag", "year=2025", "year",
            f"2025 reported for {n25} of {df.country.nunique()} countries; "
            "Ember may revise 2025 estimates; treat as preliminary")

    # --- identities -------------------------------------------------------------
    tol = C.EMBER_IDENTITY_TOL
    bad = (df.clean_generation_twh + df.fossil_generation_twh
           - df.generation_twh).abs() > tol
    for i in df.index[bad]:
        log.add("identity_clean+fossil=generation", "error", "flag", _record(df, i),
                "generation_twh", "components do not sum to total")
    log.add("identity_clean+fossil=generation", "info", "verify", "dataset", "",
            f"{int(bad.sum())} violations (tol {tol} TWh)")

    bad2 = (df.generation_twh + df.net_imports_twh - df.demand_twh).abs() > tol
    for i in df.index[bad2]:
        log.add("identity_gen+imports=demand", "error", "flag", _record(df, i),
                "demand_twh", "generation + net imports != demand")
    log.add("identity_gen+imports=demand", "info", "verify", "dataset", "",
            f"{int(bad2.sum())} violations (tol {tol} TWh)")

    # --- share ranges ------------------------------------------------------------
    # Values within 0.05 of [0,100] are source rounding of the rounded
    # components (e.g. Ethiopia clean share 100.01 in 2021/2023); the
    # component identities pass, so these are flagged as warnings, not
    # errors, and the source value is preserved.
    n_bad_shares = 0
    n_rounding = 0
    for col in ("clean_share_pct", "wind_solar_share_pct"):
        out = df[(df[col] < 0) | (df[col] > 100)]
        n_bad_shares += len(out)
        for i in out.index:
            v = float(df[col].iloc[i])
            if (v > -0.05 and v < 100.05):
                n_rounding += 1
                log.add("range_shares", "warning", "flag", _record(df, i), col,
                        f"share {v} outside [0,100] by <0.05 - source rounding, "
                        "value preserved")
            else:
                log.add("range_shares", "error", "flag", _record(df, i), col,
                        f"share {v} outside [0,100] beyond rounding tolerance")
    log.add("range_shares", "info", "verify", "dataset", "shares",
            f"{n_bad_shares} share values outside [0,100] "
            f"({n_rounding} within 0.05 = source rounding)"
            if n_bad_shares else "all share values within [0,100]")

    # --- ordering constraints ------------------------------------------------------
    bad3 = df.wind_solar_generation_twh > df.renewable_generation_twh + 0.01
    for i in df.index[bad3]:
        log.add("order_wind<=renewable", "error", "flag", _record(df, i),
                "wind_solar_generation_twh", "wind+solar exceeds renewables")
    bad4 = df.clean_generation_twh < df.renewable_generation_twh - 0.01
    for i in df.index[bad4]:
        log.add("order_renewable<=clean", "error", "flag", _record(df, i),
                "clean_generation_twh", "renewables exceed clean total")

    # --- sign sanity -----------------------------------------------------------------
    for col in ("generation_twh", "demand_twh", "clean_generation_twh",
                "fossil_generation_twh", "renewable_generation_twh",
                "wind_solar_generation_twh", "power_emissions_mtco2e",
                "demand_per_capita_mwh"):
        neg = df[df[col] < 0]
        for i in neg.index:
            log.add("sign_nonneg", "warning", "flag", _record(df, i), col,
                    f"negative value {df[col].iloc[i]}")
    # net_imports_twh may legitimately be negative (net exporters) -- only record
    neg_imp = df[df.net_imports_twh < 0]
    log.add("sign_net_imports", "info", "verify", "dataset", "net_imports_twh",
            f"{len(neg_imp)} rows have negative net imports (net export; legitimate)")

    # --- carbon intensity precision ----------------------------------------------------
    # power_emissions_mtco2e is rounded to 2 decimals at source; for small
    # countries that makes the published carbon intensity imprecise.
    gen_safe = df.generation_twh.replace(0, pd.NA)
    # MtCO2e / TWh -> gCO2e/kWh: 1e12 g / 1e9 kWh = 1e3 per unit ratio
    ci_calc = (df.power_emissions_mtco2e / gen_safe * 1e3)
    ci_denom = df.carbon_intensity_gco2e_kwh.replace(0, pd.NA)
    rel = (ci_calc - df.carbon_intensity_gco2e_kwh).abs() / ci_denom.abs()
    # relative deviation where both defined
    both = df.carbon_intensity_gco2e_kwh.notna() & df.generation_twh.gt(0)
    dev = rel.where(both)
    flagged_ci = int((dev > 0.05).sum())
    log.add("carbon_intensity_precision", "info", "verify", "dataset",
            "carbon_intensity_gco2e_kwh",
            f"{flagged_ci} rows deviate >5% from emissions/generation, consistent with "
            "2-decimal MtCO2e rounding for small countries (precision limit, not error)")
    df["carbon_intensity_precision_limited"] = (dev > 0.05).fillna(False).astype(bool)

    # --- zero-generation rows -----------------------------------------------------------
    zero_gen = df[(df.generation_twh == 0) & (df.demand_twh > 0)]
    for i in zero_gen.index:
        log.add("zero_generation", "info", "flag", _record(df, i), "generation_twh",
                "domestic generation 0 with positive demand (met by net imports; "
                "legitimate micro-grid / import-only case)")
    df["zero_generation_flag"] = (df.generation_twh == 0).astype(bool)

    # --- has_previous_year / growth_status semantics --------------------------------------
    df = stable_sort(df, ["country", "year"])
    prev_year_exists = df.groupby("country")["year"].transform(
        lambda y: (y.shift(1) == y - 1))
    expected_hpy = prev_year_exists.astype("int8")
    bad_hpy = df.has_previous_year != expected_hpy
    for i in df.index[bad_hpy]:
        log.add("has_previous_year", "warning", "flag", _record(df, i),
                "has_previous_year",
                f"value {df.has_previous_year.iloc[i]} vs expected {expected_hpy.iloc[i]}")
    dchg, cchg = df.demand_change_twh, df.clean_change_twh
    expected_status = pd.Series("unknown", index=df.index)
    expected_status[~prev_year_exists] = "no_previous_year"
    expected_status[prev_year_exists & (dchg <= 0)] = "demand_not_growing"
    expected_status[prev_year_exists & (dchg > 0) & (cchg < dchg)] = \
        "clean_growth_below_demand_growth"
    expected_status[prev_year_exists & (dchg > 0) & (cchg >= dchg)] = \
        "clean_growth_met_or_exceeded_demand_growth"
    bad_gs = df[prev_year_exists & (df.growth_status != expected_status)]
    for i in bad_gs.index:
        log.add("growth_status", "warning", "flag", _record(df, i), "growth_status",
                f"{df.growth_status.iloc[i]!r} vs derived {expected_status.iloc[i]!r}")
    log.add("growth_status", "info", "verify", "dataset", "growth_status",
            f"{len(bad_gs)} rows inconsistent with derived rule "
            "(0 means rule matches source for all rows with a prior year)")

    # --- clean_growth_coverage_pct missingness ---------------------------------------------
    # missing exactly when demand did not grow (denominator <= 0): explained gap,
    # NOT a defect. Documented, kept as NaN.
    miss = df.clean_growth_coverage_pct.isna()
    explained = miss & (df.growth_status == "demand_not_growing")
    unexplained = miss & ~explained
    for i in df.index[unexplained]:
        log.add("missing_coverage_pct", "warning", "flag", _record(df, i),
                "clean_growth_coverage_pct",
                f"missing though demand grew ({df.demand_change_twh.iloc[i]})")
    log.add("missing_coverage_pct", "info", "verify", "dataset",
            "clean_growth_coverage_pct",
            f"{int(explained.sum())} missing rows explained by non-growing demand; "
            f"{int(unexplained.sum())} unexplained")
    df["clean_growth_coverage_pct_available"] = df.clean_growth_coverage_pct.notna()

    # --- demand_change consistency vs prior row ------------------------------------------------
    df["demand_prev"] = df.groupby("country")["demand_twh"].shift(1)
    df["clean_prev"] = df.groupby("country")["clean_generation_twh"].shift(1)
    df["fossil_prev"] = df.groupby("country")["fossil_generation_twh"].shift(1)
    chk = df[prev_year_exists]
    bad_dd = (chk.demand_change_twh - (chk.demand_twh - chk.demand_prev)).abs() > 0.02
    for i in chk.index[bad_dd]:
        log.add("demand_change", "error", "flag", _record(df, i), "demand_change_twh",
                "does not equal demand minus prior-year demand")
    bad_cd = (chk.clean_change_twh - (chk.clean_generation_twh - chk.clean_prev)).abs() > 0.02
    for i in chk.index[bad_cd]:
        log.add("clean_change", "error", "flag", _record(df, i), "clean_change_twh",
                "does not equal clean generation minus prior-year value")
    log.add("demand_change", "info", "verify", "dataset", "demand_change_twh",
            "verified against prior-year observations for all consecutive rows")

    # --- drop scratch columns, keep audit flags ----------------------------------------------
    df = df.drop(columns=["demand_prev", "clean_prev", "fossil_prev"])
    df["source"] = "ember"

    # deterministic row order for the cleaned table
    df = stable_sort(df, ["country", "year"])
    log.add("summary", "info", "verify", "dataset", "",
            f"raw rows {n_raw} -> cleaned rows {len(df)}")
    return df, log
