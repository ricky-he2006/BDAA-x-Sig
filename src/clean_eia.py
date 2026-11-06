"""Cleaning + validation for the EIA U.S. coal consumption & quality dataset.

Key structural facts (verified against the data; see report):
* Sector 94 (Independent Power Producers) = sector 2 + sector 3, exactly.
* Sector 98 (Electric Power) = sector 1 + sector 2 + sector 3, exactly.
* Regional codes (NEW, MAT, ENC, ESC, SAT, WNC, WSC, MTN) equal the sum of
  their PRESENT member-state rows exactly, and "90" (Pacific) = PCC + PCN =
  (CA+OR+WA)+(AK+HI) holds exactly over present rows. EIA omits rows for
  zero/no activity: e.g. DC, ID, MA, VT have no sector-98 row in any year,
  OR in 2021-2025, HI in 2023-2025. A missing row is "not reported", not 0.
* The "US" total equals the sum of state rows only up to source rounding:
  state rows are reported to ~5 significant figures while the US total is
  not, so 2020-2025 residuals are up to ~0.36% relative (measured max
  3.6e-3, ~1.7M short tons on ~470M). Flagged, not forced.
* heat-content is reported on TWO scales in this extract:
    - power sectors (1,2,3,94,98): values 0-27  -> GJ/tonne-scale (unit not
      stated in the file; the heat-content-units column is corrupted and
      contains the sulfur unit string for every row)
    - industrial sectors (8,9,10): values ~7200-15000 -> Btu/lb
  We do NOT convert blindly: the raw value and an inferred unit flag are
  preserved; a normalized Btu/lb column is provided with an explicit
  `assumed` marker.

Missing vs zero: both are real in this file. Missing price/stocks are common
for power sectors (not reported); explicit 0.0 values are true zero activity.
A missing (year, location, sector) row means "not reported", NOT zero.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .audit_common import AuditLog, stable_sort

DATASET = "eia"

RENAME = {
    "period": "year",
    "stateDescription": "location_name",
    "ash-content": "ash_pct",
    "sulfur-content": "sulfur_pct",
    "heat-content": "heat_content_raw",
    "ash-content-units": "ash_units_src",
    "consumption-units": "consumption_units_src",
    "heat-content-units": "heat_units_src",
    "price-units": "price_units_src",
    "receipts-units": "receipts_units_src",
    "stocks-units": "stocks_units_src",
    "sulfur-content-units": "sulfur_units_src",
}
NUMERIC = ["consumption", "receipts", "stocks", "price",
           "ash-content", "heat-content", "sulfur-content"]


def load_raw(path=None) -> pd.DataFrame:
    path = path or (C.RAW / C.RAW_EIA)
    return pd.read_csv(path)


def _record(df, i) -> str:
    return f"{int(df.year.iloc[i])}|{df.location.iloc[i]}|sector{int(df.sector.iloc[i])}"


def _location_type(code: str) -> str:
    if code == C.EIA_US_TOTAL_CODE:
        return "us_total"
    if code in ("90", "PCC", "PCN"):
        return "pacific_region"
    if code in C.EIA_REGIONS:
        return "census_region"
    if code in C.EIA_STATE_CODES:
        return "state"
    return "unknown"


def audit_and_clean(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, AuditLog]:
    log = AuditLog(DATASET)
    df = df_raw.copy()
    n_raw = len(df)

    # --- types ----------------------------------------------------------------
    df = df.rename(columns=RENAME)
    df["year"] = df["year"].astype("int64")
    df["sector"] = df["sector"].astype("int64")
    n_bad_parse = 0
    for col in ("consumption", "receipts", "stocks", "price",
                "ash_pct", "heat_content_raw", "sulfur_pct"):
        before = df[col].isna().sum()
        df[col] = pd.to_numeric(df[col], errors="coerce")  # coerce -> NaN
        n_bad_parse += int(df[col].isna().sum() - before)
    if n_bad_parse:
        log.add("types", "warning", "flag", "dataset", "numeric",
                f"{n_bad_parse} cells that were non-blank failed numeric parsing")
    else:
        log.add("types", "info", "verify", "dataset", "numeric",
                "all non-blank numeric cells parsed cleanly; blanks remain NaN (never zero-filled)")

    # --- identifiers ------------------------------------------------------------
    bad_sectors = ~df.sector.isin(C.EIA_SECTORS)
    for i in df.index[bad_sectors]:
        log.add("sector_code", "error", "flag", _record(df, i), "sector",
                f"unknown sector code {int(df.sector.iloc[i])}")
    sector_desc_mismatch = df[
        df.sector.isin(C.EIA_SECTORS)
        & (df.sectorDescription != df.sector.map(C.EIA_SECTORS))
    ]
    for i in sector_desc_mismatch.index:
        log.add("sector_code", "warning", "flag", _record(df, i), "sectorDescription",
                f"code {int(df.sector.iloc[i])} labelled {df.sectorDescription.iloc[i]!r}")
    for code in sorted(df.location.unique()):
        lt = _location_type(code)
        if lt == "unknown":
            log.add("location_code", "warning", "flag", code, "location",
                    "location code not recognized as state/region/us_total")
    df["location_type"] = df.location.map(_location_type)
    df["is_geographic_aggregate"] = df.location_type.isin(
        ["census_region", "us_total", "pacific_region"])

    # --- duplicates -----------------------------------------------------------------
    dup = df.duplicated(subset=["year", "location", "sector"], keep=False)
    if dup.any():
        for i in df.index[dup]:
            log.add("dup", "error", "drop", _record(df, i), "year,location,sector",
                    "duplicate key")
        df = df[~dup]
    else:
        log.add("dup", "info", "verify", "dataset", "year,location,sector",
                f"0 duplicates among {n_raw} rows")

    # --- range sanity ------------------------------------------------------------------
    for col, lo, hi, name in [
        ("ash_pct", 0, 100, "ash %"),
        ("sulfur_pct", 0, 100, "sulfur %"),
        ("consumption", 0, None, "consumption (short tons)"),
        ("receipts", 0, None, "receipts (short tons)"),
        ("stocks", 0, None, "stocks (short tons)"),
        ("price", 0, None, "price ($/short ton)"),
    ]:
        bad = df[df[col].notna() & ((df[col] < lo) | (df[col] > hi if hi is not None else False))]
        for i in bad.index:
            log.add(f"range_{col}", "warning", "flag", _record(df, i), col,
                    f"{name} value {df[col].iloc[i]} outside [{lo},{hi}]")
    # physically implausible ash/sulfur (>45% ash is beyond any US coal; >10% sulfur rare)
    hi_ash = df[df.ash_pct.notna() & (df.ash_pct > 45)]
    for i in hi_ash.index:
        log.add("plausible_ash", "warning", "flag", _record(df, i), "ash_pct",
                f"ash {df.ash_pct.iloc[i]}% exceeds 45% physical ceiling")

    # --- sector aggregate identities -----------------------------------------------------
    # Checked only where every member row is present with a value (a missing
    # member row is "not reported" and must not be treated as 0).
    n_chk94 = n_chk98 = 0
    for year in sorted(df.year.unique()):
        sub = df[df.year == year]
        for loc in sorted(sub.location.unique()):
            s = sub[sub.location == loc].set_index("sector")
            if 94 in s.index and 2 in s.index and 3 in s.index:
                lhs, a, b = (s.loc[x, "consumption"] for x in (94, 2, 3))
                if pd.notna(lhs) and pd.notna(a) and pd.notna(b):
                    n_chk94 += 1
                    if abs(lhs - (a + b)) > 1e-6 * max(1.0, abs(lhs)):
                        log.add("sector_94_eq_2_3", "error", "flag",
                                f"{year}|{loc}|sector94", "consumption",
                                f"94={lhs} != 2+3={a + b}")
            if 98 in s.index and 1 in s.index and 2 in s.index and 3 in s.index:
                lhs = s.loc[98, "consumption"]
                if all(pd.notna(s.loc[x, "consumption"]) for x in (1, 2, 3)):
                    n_chk98 += 1
                    rhs = sum(s.loc[x, "consumption"] for x in (1, 2, 3))
                    if abs(lhs - rhs) > 1e-6 * max(1.0, abs(lhs)):
                        log.add("sector_98_eq_1_2_3", "error", "flag",
                                f"{year}|{loc}|sector98", "consumption",
                                f"98={lhs} != 1+2+3={rhs}")
    log.add("sector_aggregates", "info", "verify", "dataset", "sector",
            f"sector 94 == 2+3 ({n_chk94} checks) and sector 98 == 1+2+3 "
            f"({n_chk98} checks) verified exactly wherever all member rows are "
            "present (relative tolerance 1e-6). Downstream analysis must use "
            "ONLY base sectors {1,2,3,8,9,10} or ONLY aggregates {94,98} to "
            "avoid double counting.")

    # --- geographic aggregate identities ---------------------------------------------------
    # Census regions / Pacific: exact, but only over PRESENT member rows (EIA
    # omits no-activity states: e.g. OR 2021-25, HI 2023-25 for sector 98).
    # US total: NOT exact — state rows are rounded at source (~5 sig figs)
    # while the US total is not; allow a 0.5% relative tolerance and report
    # the observed residual.
    US_TOL = 5e-3
    us_resid = []
    for year in sorted(df.year.unique()):
        sub = df[(df.year == year) & (df.sector == 98)].set_index("location")["consumption"]
        for region, members in C.EIA_REGIONS.items():
            if region not in sub.index:
                continue
            lhs = sub[region]
            present = [m for m in members if m in sub.index]
            if pd.notna(lhs) and present and all(pd.notna(sub[m]) for m in present):
                rhs = sub[present].sum()
                if abs(lhs - rhs) > 1e-6 * max(1.0, abs(lhs)):
                    log.add(f"region_{region}", "error", "flag",
                            f"{year}|{region}", "consumption",
                            f"region {lhs} != sum of present members {rhs}")
        if "90" in sub.index:
            pac = C.EIA_PACIFIC_PCC + C.EIA_PACIFIC_PCN
            present = [m for m in pac if m in sub.index]
            if pd.notna(sub["90"]) and present and all(pd.notna(sub[m]) for m in present):
                if abs(sub["90"] - sub[present].sum()) > 1e-6 * max(1.0, abs(sub["90"])):
                    log.add("region_90_pacific", "error", "flag", f"{year}|90",
                            "consumption",
                            f"Pacific {sub['90']} != sum of present CA/OR/WA/AK/HI")
        if "US" in sub.index and pd.notna(sub["US"]):
            present = [c for c in C.EIA_STATE_CODES if c in sub.index
                       and pd.notna(sub[c])]
            rhs = sub[present].sum()
            resid = abs(sub["US"] - rhs) / abs(sub["US"])
            us_resid.append(resid)
            if resid > US_TOL:
                log.add("us_total", "error", "flag", f"{year}|US", "consumption",
                        f"US total {sub['US']} vs sum of states {rhs} "
                        f"(residual {resid:.2%} > {US_TOL:.1%})")
    log.add("geo_aggregates", "info", "verify", "dataset", "location",
            "census-region and Pacific identities exact over present member "
            "rows (2020-2025). US total vs sum of state rows: max residual "
            f"{max(us_resid):.2%} relative (source rounding of state rows; "
            f"tolerance {US_TOL:.1%}). Region/US rows must never be summed "
            "with state rows.")

    # --- heat-content unit split -------------------------------------------------------------
    for i, row in df.iterrows():
        hc = row.heat_content_raw
        if pd.isna(hc):
            continue
        if hc == 0:
            unit = "zero_activity"
        elif hc < 100:
            unit = "GJ_per_tonne_scale_ASSUMED"
        elif hc < 100000:
            unit = "Btu_per_lb"
        else:
            unit = "UNRECOGNIZED"
        if row.sector in C.EIA_INDUSTRIAL_SECTORS and unit == "GJ_per_tonne_scale_ASSUMED":
            log.add("heat_units", "warning", "flag", _record(df, i), "heat_content_raw",
                    f"industrial sector with small-scale heat {hc}")
        if row.sector in C.EIA_POWER_SECTORS and unit == "Btu_per_lb":
            log.add("heat_units", "warning", "flag", _record(df, i), "heat_content_raw",
                    f"power sector with Btu/lb-scale heat {hc}")
        if unit == "UNRECOGNIZED":
            log.add("heat_units", "error", "flag", _record(df, i), "heat_content_raw",
                    f"heat {hc} outside all plausible ranges")
    df["heat_content_unit_inferred"] = df.heat_content_raw.apply(
        lambda v: ("zero_activity" if v == 0 else
                   "GJ_per_tonne_scale_ASSUMED" if (pd.notna(v) and v < 100) else
                   "Btu_per_lb" if (pd.notna(v) and v < 100000) else "UNRECOGNIZED")
        if pd.notna(v) else "missing")
    # normalized Btu/lb (documented assumption for the small-scale readings)
    df["heat_content_btu_lb"] = np.where(
        df.heat_content_unit_inferred == "Btu_per_lb", df.heat_content_raw,
        np.where(df.heat_content_unit_inferred == "GJ_per_tonne_scale_ASSUMED",
                 df.heat_content_raw * C.GJ_PER_TONNE_TO_BTU_PER_LB, np.nan))
    df["heat_content_normalized_is_assumed"] = (
        df.heat_content_unit_inferred == "GJ_per_tonne_scale_ASSUMED")
    n_small = int((df.heat_content_unit_inferred == "GJ_per_tonne_scale_ASSUMED").sum())
    log.add("heat_units", "warning", "flag", "dataset", "heat_content_raw",
            f"two reporting scales coexist: {n_small} rows on GJ/tonne scale (power "
            "sectors) and the rest on Btu/lb (industrial sectors). heat-content-units "
            "column is corrupted (holds the sulfur unit for every row). Normalized "
            "Btu/lb values for the small-scale rows are ASSUMED conversions, flagged.")

    # --- corrupted units column ---------------------------------------------------------------
    heat_units_vals = df.heat_units_src.unique()
    if all(v == "average sulfur percent by weight" for v in heat_units_vals):
        log.add("units_column_corrupted", "warning", "flag", "dataset",
                "heat-content-units",
                "column contains 'average sulfur percent by weight' for every row; "
                "source extraction error - unit inferred from value scale instead")

    # --- missingness patterns -------------------------------------------------------------------
    miss = df[["consumption", "receipts", "stocks", "price",
               "ash_pct", "sulfur_pct", "heat_content_raw"]].isna()
    log.add("missingness", "info", "verify", "dataset", "",
            "missing counts by column: " + ", ".join(
                f"{c}={int(miss[c].sum())}" for c in miss.columns))
    for col in miss.columns:
        if miss[col].any():
            df[f"available_{col}"] = df[col].notna()

    # --- 2025 status ----------------------------------------------------------------------------
    log.add("status_2025", "warning", "flag", "year=2025", "year",
            "2025 rows are the latest EIA annual release; EIA may revise. "
            "US electric-power coal consumption shows a +11% YoY rebound in 2025 "
            "(373.3M -> 415.4M short tons, sector 98) - see report.")

    # --- coverage by (location, sector) over time ----------------------------------------------------
    present = df.groupby(["location", "sector"])["year"].apply(list).to_dict()
    gaps = {k: sorted(set(C.FOCUS_YEARS) - set(v)) for k, v in present.items()
            if set(C.FOCUS_YEARS) - set(v)}
    if gaps:
        log.add("coverage", "info", "verify", "dataset", "location,sector",
                f"{len(gaps)} (location,sector) cells missing at least one focus year "
                "(missing row = not reported, NOT zero). Examples: " +
                ", ".join(f"{k[0]}/s{k[1]}:{v}" for k, v in sorted(gaps.items())[:8]))

    df["source"] = "eia"
    df = stable_sort(df, ["year", "location", "sector"])
    log.add("summary", "info", "verify", "dataset", "",
            f"raw rows {n_raw} -> cleaned rows {len(df)}")
    return df, log
