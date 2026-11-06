"""Cleaning + validation for the Energy Institute Statistical Review
(long/narrow format, 1965-2025, ~299k observations, 90 variables).

Rules:
* Full history is preserved (this file is the project's long-term reference).
* Aggregates (O-*, T-*, ROW) are separated from individual countries via
  `is_aggregate` - they must never be summed with country rows.
* 2025 observations are treated as reported-by-source, finality unverified
  (the Statistical Review publishes estimates for the latest years).
* Missingness: a (country, year, variable) cell absent from the file is
  "not reported", which is distinct from an explicit 0.0 value.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .audit_common import AuditLog, stable_sort
from .iso3166 import is_accepted_noniso, is_known

DATASET = "energy_institute"


def load_raw(path=None) -> pd.DataFrame:
    path = path or (C.RAW / C.RAW_EI)
    return pd.read_csv(path, low_memory=False)


def audit_and_clean(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, AuditLog]:
    log = AuditLog(DATASET)
    df = df_raw.copy()
    n_raw = len(df)

    # --- types ------------------------------------------------------------------
    df["Year"] = df["Year"].astype("int64")
    df["ISO3166_numeric"] = pd.to_numeric(df["ISO3166_numeric"], errors="coerce").astype("Int64")
    for col in ("OPEC", "EU", "OECD", "CIS"):
        df[col] = df[col].fillna(0).astype("int8")  # aggregates carry no flags
    df = df.rename(columns={"Country": "country", "ISO3166_alpha3": "iso3",
                            "ISO3166_numeric": "iso_num", "Var": "variable",
                            "Value": "value"})
    log.add("types", "info", "verify", "dataset", "all",
            "Year/Value/flags parsed; iso_num nullable (absent for aggregates)")

    # --- geo identifiers -----------------------------------------------------------
    def _is_ei_aggregate(c) -> bool:
        return (str(c).startswith(C.EI_AGGREGATE_PREFIXES)
                or c in C.EI_AGGREGATE_EXTRA)
    unknown = df[~df.iso3.map(lambda c: is_known(c) or is_accepted_noniso(c)
                              or c in C.EI_AGGREGATE_ISO3 or _is_ei_aggregate(c))]
    for code in sorted(unknown.iso3.unique()):
        n = int((unknown.iso3 == code).sum())
        log.add("iso3", "warning", "flag", code, "iso3",
                f"code not in official/accepted/aggregate set ({n} rows)")
    multi = df.groupby("country")["iso3"].nunique()
    for c in multi[multi > 1].index:
        log.add("iso3", "error", "flag", c, "iso3", "same country, multiple iso3 codes")
    df["is_aggregate"] = (df.iso3.astype(str).str.startswith(C.EI_AGGREGATE_PREFIXES)
                          | df.iso3.isin(C.EI_AGGREGATE_EXTRA)
                          | df.iso3.isin(C.EI_AGGREGATE_ISO3)).astype(bool)
    n_agg = int(df.is_aggregate.sum())
    n_agg_entities = int(df.iso3[df.is_aggregate].nunique())
    log.add("aggregates", "info", "verify", "dataset", "iso3",
            f"{df.country.nunique()} entities: "
            f"{df.country.nunique() - n_agg_entities} countries + "
            f"{n_agg_entities} EI regional aggregates ({n_agg} aggregate rows; "
            "all O-*/T-*/WLD/ROW codes). Country-level sums must use "
            "is_aggregate == False; the 'Other X' residuals (countries not "
            "listed individually) remain excluded from such sums.")

    # --- variable registry -------------------------------------------------------------
    unregistered = sorted(set(df.variable.unique()) - set(C.EI_VAR_UNITS))
    if unregistered:
        for v in unregistered:
            log.add("var_registry", "warning", "flag", v, "variable", "unit not in registry")
    else:
        log.add("var_registry", "info", "verify", "dataset", "variable",
                f"all {df.variable.nunique()} variables present in unit registry")
    df["variable_unit"] = df.variable.map(C.EI_VAR_UNITS)

    # --- duplicates -----------------------------------------------------------------------
    dup = df.duplicated(subset=["country", "Year", "variable"], keep=False)
    if dup.any():
        for i in df.index[dup]:
            log.add("dup", "error", "drop",
                    f"{df.country.iloc[i]}|{int(df.Year.iloc[i])}|{df.variable.iloc[i]}",
                    "country,year,variable", "duplicate cell")
        df = df[~dup]
    else:
        log.add("dup", "info", "verify", "dataset", "country,year,variable",
                f"0 duplicate cells among {n_raw} rows")

    # --- sign and range sanity ---------------------------------------------------------------
    neg = df[df.value < 0]
    for var in sorted(neg.variable.unique()):
        sub = neg[neg.variable == var]
        for _, r in sub.head(10).iterrows():  # cap per-variable noise
            log.add("sign_negative", "warning", "flag",
                    f"{r.country}|{int(r.Year)}|{var}",
                    "value", f"negative value {r.value} for {var}")
    if len(neg):
        log.add("sign_negative", "warning", "flag", "dataset", "value",
                f"{len(neg)} negative values across "
                f"{sorted(neg.variable.unique())} - investigate before use")
    else:
        log.add("sign_negative", "info", "verify", "dataset", "value",
                "no negative values in any variable")

    pct = df[df.variable.isin(["refcaputil_pct"])]
    bad_pct = pct[(pct.value < 0) | (pct.value > 100)]
    log.add("range_percent", "info", "verify", "dataset", "refcaputil_pct",
            f"{len(bad_pct)} percent values outside [0,100]" if len(bad_pct)
            else "refcaputil_pct within [0,100]")

    # --- temporal coverage ------------------------------------------------------------------
    years = sorted(df.Year.unique())
    log.add("coverage_years", "info", "verify", "dataset", "Year",
            f"year range {years[0]}-{years[-1]}, {len(years)} distinct years")
    ent = df.groupby("country")["Year"].agg(["min", "max", "nunique"])
    short = ent[ent["nunique"] < 10]
    log.add("coverage_entities", "info", "verify", "dataset", "country",
            f"{len(short)} entities have <10 years of data (mostly recent entrants/"
            "aggregates): " + ", ".join(
                f"{c}({int(r['min'])}-{int(r['max'])})" for c, r in short.iterrows()))
    # 2025 finality
    n25 = int((df.Year == 2025).sum())
    log.add("status_2025", "warning", "flag", "year=2025", "Year",
            f"{n25} observations for 2025; Statistical Review latest-year figures are "
            "estimates subject to revision - do not treat as final")
    # 2025 vs 2024 entity coverage
    e24 = set(df[df.Year == 2024].country)
    e25 = set(df[df.Year == 2025].country)
    log.add("coverage_2025", "info", "verify", "dataset", "Year",
            f"2024 has {len(e24)} entities, 2025 has {len(e25)}; "
            f"missing in 2025: {sorted(e24 - e25) if e24 - e25 else 'none'}")

    # --- per-variable 2020-2025 completeness for the thesis-relevant set -------------------------
    thesis_vars = ["coalprod_mt", "coalprod_ej", "coal_tes_ej", "electbyfuel_coal",
                   "elect_twh", "electbyfuel_total", "ren_power_twh", "wind_twh",
                   "solar_twh", "co2_combust_mtco2", "tes_ej", "pop"]
    sub = df[df.variable.isin(thesis_vars) & df.Year.isin(C.FOCUS_YEARS)]
    cov = sub.pivot_table(index="country", columns=["variable", "Year"],
                          values="value", aggfunc="count")
    # report only countries (exclude aggregates)
    agg_countries = set(df.country[df.is_aggregate].unique())
    cov = cov.loc[[c for c in cov.index if c not in agg_countries]]
    missing_cells = 0
    holes = {}
    for var in thesis_vars:
        cols = [c for c in cov.columns if c[0] == var]
        if not cols:
            continue
        m = cov[cols].isna().sum(axis=1)
        missing_cells += int(m.sum())
        for c in m[m > 0].index:
            holes.setdefault(var, []).append((c, int(m[c])))
    log.add("thesis_var_completeness", "info", "verify", "dataset",
            "thesis variables",
            f"2020-2025 country-level completeness for {len(thesis_vars)} thesis "
            f"variables: {missing_cells} missing (country, variable-year) cells. "
            "Worst: " + "; ".join(
                f"{v}: {worst[0]}={worst[1]}yrs" for v, lst in holes.items()
                for worst in sorted(lst, key=lambda t: -t[1])[:2])
            if holes else "complete for all countries")

    # --- spot magnitude checks (unit verification) -----------------------------------------------
    us_name = df.loc[df.iso3 == "USA", "country"].unique()
    us_name = us_name[0] if len(us_name) else "United States"
    us = df[df.country == us_name]
    checks = [
        ("elect_twh", 3000, 5000, "US total electricity TWh"),
        ("coalprod_mt", 400, 1000, "US coal production Mt"),
        ("coal_tes_ej", 5, 15, "US coal TES EJ (~8 EJ in the 2020s)"),
        ("pop", 250, 400, "US population millions"),
        ("tes_ej", 80, 130, "US total energy supply EJ"),
        ("electbyfuel_coal", 500, 1000, "US coal-fired electricity TWh (~700)"),
        ("co2_combust_mtco2", 4000, 6000, "US combustion CO2 Mt"),
    ]
    for var, lo, hi, label in checks:
        v24 = us[us.variable == var]
        v24 = v24[v24.Year == 2024]
        if len(v24):
            val = float(v24.value.iloc[0])
            ok = lo <= val <= hi
            log.add("magnitude_check", "info" if ok else "error", "verify",
                    f"US|2024|{var}", "value",
                    f"{label}: 2024 value {val} "
                    f"{'within' if ok else 'OUTSIDE'} plausible range [{lo},{hi}]")
        else:
            log.add("magnitude_check", "warning", "flag", f"US|2024|{var}", "value",
                    f"{label}: no 2024 observation")

    # consistency: electbyfuel_total vs elect_twh
    p = df.pivot_table(index=["country", "Year"], columns="variable",
                       values="value", aggfunc="first")
    if "elect_twh" in p and "electbyfuel_total" in p:
        d = (p["elect_twh"] - p["electbyfuel_total"]).abs()
        bad = d[(d > 5) & p["elect_twh"].notna() & p["electbyfuel_total"].notna()]
        log.add("identity_electricity", "info", "verify", "dataset",
                "elect_twh vs electbyfuel_total",
                f"{len(bad)} cells differ by >5 TWh (rounding/methodology) "
                "in " + ", ".join(f"{c}|{y}" for (c, y) in bad.index[:5])
                if len(bad) else "match within 5 TWh everywhere")

    df["source"] = "energy_institute"
    df = stable_sort(df, ["country", "Year", "variable"])
    log.add("summary", "info", "verify", "dataset", "",
            f"raw rows {n_raw} -> cleaned rows {len(df)}")
    return df, log
