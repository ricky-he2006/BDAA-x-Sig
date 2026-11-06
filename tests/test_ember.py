"""Validation tests for the cleaned Ember dataset."""
import pandas as pd

import pytest


@pytest.fixture(scope="module")
def ember(pipeline_outputs):
    return pipeline_outputs["cleaned"]["ember"]


def test_row_count(ember):
    assert len(ember) == 1138


def test_unique_country_year(ember):
    assert not ember.duplicated(subset=["country", "year"]).any()


def test_year_coverage(ember):
    counts = ember.year.value_counts()
    assert counts[2020] == counts[2021] == counts[2022] == 213
    assert counts[2023] == 212
    assert counts[2024] == 196
    assert counts[2025] == 91


def test_component_identities(ember):
    assert ((ember.clean_generation_twh + ember.fossil_generation_twh
             - ember.generation_twh).abs() <= 0.05).all()
    assert ((ember.generation_twh + ember.net_imports_twh
             - ember.demand_twh).abs() <= 0.05).all()


def test_share_ranges(ember, pipeline_outputs):
    """Shares are within [0,100] up to source rounding (components are
    2-decimal rounded): out-of-range values may exceed by <0.05, and every
    such row MUST appear in the audit log (Ethiopia clean share 100.01 in
    2021/2023 is the known instance)."""
    from src import config as C
    import pandas as pd

    out = ember[((ember.clean_share_pct < 0) | (ember.clean_share_pct > 100)) |
                ((ember.wind_solar_share_pct < 0) | (ember.wind_solar_share_pct > 100))]
    for col in ("clean_share_pct", "wind_solar_share_pct"):
        assert ember[col].between(-0.05, 100.05).all(), col
    log = pd.read_csv(C.REPORTS / "cleaning_log.csv")
    # one log entry per (row, column) - at least every affected row is logged
    logged_rows = set(log[log.check_id == "range_shares"].record)
    assert set(out.country + "|" + out.year.astype(int).astype(str)) <= logged_rows


def test_ordering_constraints(ember):
    assert (ember.wind_solar_generation_twh
            <= ember.renewable_generation_twh + 0.01).all()
    assert (ember.clean_generation_twh
            >= ember.renewable_generation_twh - 0.01).all()


def test_nonnegative_core(ember):
    for col in ("generation_twh", "demand_twh", "clean_generation_twh",
                "fossil_generation_twh", "power_emissions_mtco2e"):
        assert (ember[col] >= 0).all(), col


def test_missing_is_not_zero(ember):
    # carbon intensity missing exactly where generation is zero
    ci_missing = ember.carbon_intensity_gco2e_kwh.isna()
    assert (ci_missing == (ember.generation_twh == 0)).all()
    # zero generation rows kept (not dropped)
    assert (ember.generation_twh == 0).any()


def test_coverage_flag_explained(ember):
    # clean_growth_coverage_pct missing <=> demand did not grow
    miss = ember.clean_growth_coverage_pct.isna()
    assert (miss == (ember.growth_status == "demand_not_growing")).all()


def test_demand_change_consistent(ember):
    e = ember.sort_values(["country", "year"])
    prev = e.groupby("country")["demand_twh"].shift(1)
    prev_year = e.groupby("country")["year"].shift(1)
    ok = e.year == prev_year + 1
    assert ((e.demand_change_twh - (e.demand_twh - prev))[ok].abs() <= 0.02).all()
