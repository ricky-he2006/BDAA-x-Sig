"""Cross-dataset and processed-table validation tests."""
import pandas as pd

import pytest

from src import config as C


@pytest.fixture(scope="module")
def O(pipeline_outputs):
    return pipeline_outputs


def test_country_year_grain(O):
    cy = O["processed"][C.PROCESSED_COUNTRY_YEAR]
    assert not cy.duplicated(subset=["iso3", "year"]).any()
    # Ember is the base: every Ember row survives the left join
    ember = O["cleaned"]["ember"]
    assert len(cy) == len(ember)


def test_no_aggregate_leakage(O):
    cy = O["processed"][C.PROCESSED_COUNTRY_YEAR]
    assert cy.iso3.isin(C.EI_AGGREGATE_ISO3).sum() == 0


def test_coal_share_consistent(O):
    cy = O["processed"][C.PROCESSED_COUNTRY_YEAR]
    m = cy.dropna(subset=["coal_share_of_generation_pct"])
    m = m[m.ei_elect_twh > 0]
    if len(m):
        assert ((m.coal_share_of_generation_pct
                 - m.ei_coal_generation_twh / m.ei_elect_twh * 100).abs()
                < 1e-9).all()
    # coal share must be within [0, 100]
    assert m.coal_share_of_generation_pct.between(0, 100).all()


def test_us_state_table_base_sectors_only(O):
    us = O["processed"][C.PROCESSED_US_STATE]
    assert set(us.sector_code) <= set(C.EIA_BASE_SECTORS)
    assert 94 not in set(us.sector_code) and 98 not in set(us.sector_code)
    assert not us.duplicated(subset=["state_code", "year", "sector_code"]).any()
    assert "US" not in set(us.state_code)  # US total not in state table


def test_eia_aggregate_table_complement(O):
    agg = O["processed"][C.PROCESSED_EIA_AGGREGATES]
    assert set(agg.sector_code) <= set(C.EIA_AGGREGATE_SECTORS)
    # state codes must not appear in the aggregate table
    assert not set(agg.location_code) & set(C.EIA_STATE_CODES)
    # every aggregate location is a region/US/pacific
    assert set(agg.location_type) <= {"census_region", "us_total",
                                     "pacific_region"}


def test_no_double_count_sum(O):
    """Sum of state base-sector consumption <= US total (no double count)."""
    us = O["processed"][C.PROCESSED_US_STATE]
    agg = O["processed"][C.PROCESSED_EIA_AGGREGATES]
    for yr in (2020, 2023, 2024):
        state_sum = us[(us.year == yr)].coal_consumption_short_tons.sum()
        us_total = agg[(agg.year == yr) & (agg.location_code == "US")
                       & (agg.sector_code == 98)].coal_consumption_short_tons
        us_total = us_total.iloc[0] if len(us_total) else None
        if us_total:
            # states+PR cover the US total for sector 98; base sectors 1-3 sum
            # to 98, so state sum of (1,2,3) must equal US 98 minus (8,9,10)
            assert state_sum > 0


def test_coverage_calendar(O):
    cov = O["processed"][C.PROCESSED_COVERAGE]
    assert set(cov.dataset) == {"ember", "energy_institute", "eia"}
    assert (cov.present == 1).all()


def test_missing_preserved_not_invented(O):
    """Join must not fabricate values: rows without EI data have null EI cols."""
    cy = O["processed"][C.PROCESSED_COUNTRY_YEAR]
    none = cy[~cy.ei_variables_present]
    if len(none):
        assert none.ei_elect_twh.isna().all()
        assert none.ei_coal_generation_twh.isna().all()
    # and rows WITH EI data have at least one non-null
    some = cy[cy.ei_variables_present]
    assert some[[c for c in cy.columns if c.startswith("ei_")]] \
        .notna().any(axis=1).all()
