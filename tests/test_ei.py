"""Validation tests for the cleaned Energy Institute dataset."""
import pandas as pd

import pytest

from src import config as C


@pytest.fixture(scope="module")
def ei(pipeline_outputs):
    return pipeline_outputs["cleaned"]["ei"]


def test_row_count(ei):
    assert len(ei) == 299320


def test_unique_cell(ei):
    assert not ei.duplicated(subset=["country", "Year", "variable"]).any()


def test_aggregates_separated(ei):
    # The flag must mark EXACTLY the EI regional-aggregate codes:
    # O-* / T-* prefixed codes plus WLD (Total World) and ROW.
    # (Some of these carry vendor-assigned numeric ISO codes, so iso_num
    # is NOT a discriminator - the code prefix is.)
    expected = {c for c in ei.iso3.unique()
                if c.startswith(C.EI_AGGREGATE_PREFIXES)
                or c in C.EI_AGGREGATE_EXTRA}
    assert set(ei.iso3[ei.is_aggregate]) == expected
    assert "WLD" in expected and "ROW" in expected
    assert len(expected) >= 32
    assert not ei.is_aggregate[ei.iso3 == "USA"].any()
    assert not ei.is_aggregate[ei.iso3 == "CHN"].any()


def test_country_sum_excludes_all_aggregates(ei):
    """The 2024 country-level sum of coal production must be close to the
    EI 'Total World' row (within the 'Other X' residual, ~2%), not 3x it."""
    cty = ei[(ei.iso3 == "USA") | (ei.iso3 == "CHN")]
    assert cty.is_aggregate.sum() == 0
    wld = ei[(ei.iso3 == "WLD") & (ei.Year == 2024)
             & (ei.variable == "coalprod_mt")].value
    assert len(wld) == 1
    countries = ei[(~ei.is_aggregate) & (ei.Year == 2024)
                   & (ei.variable == "coalprod_mt")]
    country_sum = countries.value.sum()
    assert 0.85 * float(wld.iloc[0]) < country_sum < float(wld.iloc[0])


def test_variable_registry(ei):
    assert set(ei.variable.unique()) <= set(C.EI_VAR_UNITS)
    assert ei.variable_unit.notna().all()


def test_no_missing_values(ei):
    assert not ei.value.isna().any()


def test_focus_year_coverage(ei):
    us = ei[ei.iso3 == "USA"]
    for var in ("coalprod_mt", "coal_tes_ej", "electbyfuel_coal", "elect_twh"):
        assert {2020, 2021, 2022, 2023, 2024, 2025} <= set(
            us[us.variable == var].Year), var


def test_2025_present_but_flagged(ei, pipeline_outputs):
    assert (ei.Year == 2025).any()
    log = pipeline_outputs["summary"]
    assert log["audit_energy_institute"]["warnings"] >= 1  # 2025 finality warning


def test_magnitude_units(ei):
    """Spot-check unit plausibility (catches scale errors like kWh vs MWh)."""
    us = ei[ei.iso3 == "USA"]
    elect = us[(us.variable == "elect_twh") & (us.Year == 2024)].value.iloc[0]
    assert 3000 < elect < 5000, f"US elect_twh 2024 = {elect}"
    coal = us[(us.variable == "coalprod_mt") & (us.Year == 2024)].value.iloc[0]
    assert 400 < coal < 1000, f"US coalprod_mt 2024 = {coal}"
    pop = us[(us.variable == "pop") & (us.Year == 2024)].value.iloc[0]
    assert 250 < pop < 400, f"US pop 2024 = {pop} (should be millions)"
