"""Economic comparability and accounting checks for the final analysis."""
import numpy as np
import pandas as pd
import pytest

from analysis.build_deliverables import matched_panel, country_summary, pathway, change


def test_matched_panel_excludes_missing_year_and_missing_metric():
    rows = pd.DataFrame([
        {"iso3": "AAA", "year": 2020, "value": 0},
        {"iso3": "AAA", "year": 2021, "value": 2},
        {"iso3": "BBB", "year": 2020, "value": 20},
        {"iso3": "CCC", "year": 2020, "value": 30},
        {"iso3": "CCC", "year": 2021, "value": np.nan},
    ])
    actual = matched_panel(rows, [2020, 2021], ["value"])
    assert set(actual.iso3) == {"AAA"}  # true zero is retained
    with pytest.raises(ValueError, match="Duplicate"):
        matched_panel(pd.concat([rows, rows.iloc[:1]]), [2020, 2021], ["value"])


def test_country_accounting_and_declining_demand(pipeline_outputs):
    cy = pipeline_outputs["processed"]["analysis_country_year.csv"]
    s = country_summary(cy).set_index("iso3")
    assert s.demand_identity_residual_twh.dropna().abs().max() < .1
    germany = s.loc["DEU"]
    assert germany.demand_twh_delta < 0
    assert germany.clean_generation_twh_delta < 0
    assert germany.pathway == "coal_decline"
    assert pd.isna(germany.clean_additions_vs_demand_additions_pct)
    assert not s.loc["IDN", "has_2025"]  # never invent Indonesia 2025 Ember


def test_pathways_require_material_bases_and_use_output_not_share():
    assert pathway(40, 10, 30, 30, 42, 33) == "coexistence"
    assert pathway(-10, -20, 100, 100, 90, 80) == "coal_decline"
    assert pathway(500, -30, 1, 100, 6, 70) == "below_materiality_threshold"
    assert pd.isna(change(0, 10))  # zero-to-positive is not a finite growth rate


def test_final_panels_have_fixed_membership_and_distinct_windows(pipeline_outputs):
    cy = pipeline_outputs["processed"]["analysis_country_year.csv"]
    fields = ["demand_twh", "generation_twh", "clean_generation_twh", "fossil_generation_twh"]
    p24 = matched_panel(cy, list(range(2020, 2025)), fields)
    p25 = matched_panel(cy, list(range(2020, 2026)), fields)
    assert p24.groupby("year").iso3.nunique().tolist() == [196] * 5
    assert p25.groupby("year").iso3.nunique().tolist() == [91] * 6
    assert set(p25.iso3).issubset(set(p24.iso3))
    summary = country_summary(cy)
    assert summary.iso3.nunique() == 213
    assert len(summary[~summary.pathway.isin(["below_materiality_threshold", "insufficient_data"])]) == 16


def test_quality_report_uses_current_intensity_flags(pipeline_outputs):
    from src import config as C
    ember = pipeline_outputs["cleaned"]["ember"]
    n = int(ember.carbon_intensity_precision_limited.sum())
    report = (C.REPORTS / "data_quality_report.md").read_text()
    assert f"{n:,} rows deviate >5%" in report
    assert "{rc[" not in report
