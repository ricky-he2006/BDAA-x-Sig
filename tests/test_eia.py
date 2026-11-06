"""Validation tests for the cleaned EIA dataset."""
import numpy as np
import pandas as pd

import pytest

from src import config as C


@pytest.fixture(scope="module")
def eia(pipeline_outputs):
    return pipeline_outputs["cleaned"]["eia"]


def test_row_count(eia):
    assert len(eia) == 1750


def test_unique_key(eia):
    assert not eia.duplicated(subset=["year", "location", "sector"]).any()


def test_sector_aggregate_identities(eia):
    """94 == 2+3 and 98 == 1+2+3 exactly (double-counting guard)."""
    for (yr, loc), grp in eia.groupby(["year", "location"]):
        s = grp.set_index("sector")["consumption"]
        if 94 in s.index and 2 in s.index and 3 in s.index:
            assert s[94] == pytest.approx(s[2] + s[3], abs=1e-6)
        if 98 in s.index and all(x in s.index for x in (1, 2, 3)):
            assert s[98] == pytest.approx(s[1] + s[2] + s[3], abs=1e-6)


def test_region_identities(eia):
    """Census regions and Pacific: EXACT over present member rows (EIA omits
    no-activity states, e.g. OR 2021-25, HI 2023-25 for sector 98).
    US total: only within source rounding - state rows are reported to ~5
    significant figures while the US total is not (measured max residual
    ~0.36%); assert the bound rather than exactness."""
    e98 = eia[eia.sector == 98]
    for yr in sorted(e98.year.unique()):
        sub = e98[e98.year == yr].set_index("location")["consumption"]
        for region, members in C.EIA_REGIONS.items():
            if region not in sub.index:
                continue
            present = [m for m in members if m in sub.index]
            if present and pd.notna(sub[region]) and \
                    all(pd.notna(sub[m]) for m in present):
                assert sub[region] == pytest.approx(sub[present].sum(), abs=1e-6), \
                    f"{region} {yr}"
        if "90" in sub.index and pd.notna(sub["90"]):
            present = [m for m in C.EIA_PACIFIC_PCC + C.EIA_PACIFIC_PCN
                       if m in sub.index and pd.notna(sub[m])]
            if present:
                assert sub["90"] == pytest.approx(sub[present].sum(), abs=1e-6), \
                    f"90 {yr}"
        if "US" in sub.index and pd.notna(sub["US"]):
            codes = [c for c in C.EIA_STATE_CODES if c in sub.index]
            resid = abs(sub["US"] - sub[codes].sum()) / abs(sub["US"])
            assert resid < 5e-3, f"US residual {yr}: {resid:.2%}"


def test_location_types(eia):
    assert set(eia.location_type) <= {"state", "census_region",
                                     "pacific_region", "us_total"}
    assert eia.loc[eia.location == "US", "location_type"].iloc[0] == "us_total"
    assert eia.is_geographic_aggregate[eia.location_type == "state"].sum() == 0


def test_heat_content_unit_split(eia):
    ind = eia[eia.sector.isin(C.EIA_INDUSTRIAL_SECTORS)]
    pow_ = eia[eia.sector.isin(C.EIA_POWER_SECTORS)]
    # industrial sectors report on the Btu/lb scale (>= 100)
    assert (ind.heat_content_raw.dropna() >= 100).all()
    # power sectors report on the small scale (0-27); 0 = zero activity
    assert (pow_.heat_content_raw.dropna() < 100).all()
    f = C.GJ_PER_TONNE_TO_BTU_PER_LB
    # normalized value only for NON-ZERO readings (zero -> not a unit case)
    pow_pos = pow_[pow_.heat_content_raw > 0]
    assumed = pow_pos[pow_pos.heat_content_unit_inferred
                      == "GJ_per_tonne_scale_ASSUMED"]
    assert np.allclose(assumed.heat_content_btu_lb,
                       assumed.heat_content_raw * f, rtol=1e-9)
    btu = pow_pos[pow_pos.heat_content_unit_inferred == "Btu_per_lb"]
    assert np.allclose(btu.heat_content_btu_lb, btu.heat_content_raw, rtol=1e-9)
    # every positive power reading is flagged assumed-GJ-scale in this extract
    assert pow_.heat_content_normalized_is_assumed[pow_.heat_content_raw > 0].all()
    # zero-activity rows stay un-normalized, never 0-invented-as-real
    assert pow_.loc[pow_.heat_content_raw == 0, "heat_content_btu_lb"].isna().all()


def test_missing_vs_zero(eia):
    # explicit zeros exist AND missing exists; they are distinct
    assert (eia.consumption == 0).any()
    assert eia.consumption.isna().any()
    assert eia.consumption.isna().sum() == 15
    assert (eia.consumption == 0).sum() > 0
    # completeness flags present and consistent
    assert (eia.available_consumption == eia.consumption.notna()).all()


def test_no_negative_values(eia):
    for col in ("consumption", "receipts", "stocks", "price", "ash_pct",
                "sulfur_pct"):
        assert (eia[col].dropna() >= 0).all(), col


def test_us_total_rebound_preserved(eia):
    us = eia[(eia.location == "US") & (eia.sector == 98)]
    c24 = us[us.year == 2024].consumption.iloc[0]
    c25 = us[us.year == 2025].consumption.iloc[0]
    # 2025 rebound is a real observation - it must be preserved, not removed
    assert c25 > c24
    assert c25 / c24 - 1 > 0.10
