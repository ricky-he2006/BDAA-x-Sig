"""Regression tests for the dashboard JSON export (dashboard/scripts/
export_dashboard_data.py).

Guards the 2026-11-05 fix for the browser load failure
("Unexpected token 'N', ..."price": NaN"... is not valid JSON"):
Python's json module serializes float('nan') as the bare token `NaN`
(allow_nan=True default), which RFC 8259 does not allow and browser
JSON.parse rejects. The contract under test:

* every non-finite value (NaN / +Inf / -Inf, Python or NumPy) serializes
  as JSON `null` - including inside nested dicts and lists;
* missing stays missing: never 0 (missing coal prices and state
  inventories must export as null, not zero);
* real zeros stay 0 (zero consumption is data, not missing);
* serialization uses allow_nan=False (a non-finite value fails the run
  instead of writing an unparseable file);
* every generated file parses with a standards-compliant decoder.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "dashboard" / "scripts"))

import export_dashboard_data as E  # noqa: E402

DATA = ROOT / "dashboard" / "public" / "data"
FILES = ("country_year.json", "us_state_year.json",
         "us_aggregates.json", "geo.json")


def _walk(v):
    """Yield every scalar leaf of a nested structure."""
    if isinstance(v, dict):
        for x in v.values():
            yield from _walk(x)
    elif isinstance(v, list):
        for x in v:
            yield from _walk(x)
    else:
        yield v


def _reject(const: str):
    raise ValueError(f"non-strict JSON token {const!r}")


def test_sanitize_non_finite_becomes_null():
    assert E._sanitize(float("nan")) is None
    assert E._sanitize(float("inf")) is None
    assert E._sanitize(float("-inf")) is None
    assert E._sanitize(np.float64("nan")) is None
    assert E._sanitize(np.float64(np.inf)) is None
    assert E._sanitize(np.float64(-np.inf)) is None
    assert E._sanitize(pd.NA) is None
    assert E._sanitize(pd.NaT) is None


def test_sanitize_preserves_real_zero_and_values():
    """Missing is never turned into 0, and real 0 is never turned into null."""
    assert E._sanitize(0) == 0
    assert E._sanitize(0.0) == 0.0
    assert E._sanitize(np.float64(0.0)) == 0.0
    assert E._sanitize(12.5) == 12.5
    assert E._sanitize(-3.25) == -3.25
    out = E._sanitize(np.int64(42))
    assert out == 42 and type(out) is int
    assert E._sanitize(np.bool_(True)) is True
    assert E._sanitize("NA") == "NA"          # string "NA" is not missing
    assert E._sanitize(None) is None


def test_sanitize_recurses_into_nested_dicts_and_lists():
    src = {
        "a": float("nan"),
        "b": [1.0, np.float64("inf"), {"c": pd.NA, "d": 0.0}],
        "e": {"f": float("-inf"), "g": "ok", "h": [None, 2, [float("nan")]]},
    }
    out = E._sanitize(src)
    assert out == {
        "a": None,
        "b": [1.0, None, {"c": None, "d": 0.0}],
        "e": {"f": None, "g": "ok", "h": [None, 2, [None]]},
    }


def test_allow_nan_guard_rejects_non_finite():
    with pytest.raises(ValueError):
        json.dumps({"x": float("nan")}, allow_nan=False)


def _assert_no_non_finite(payload, name):
    for v in _walk(payload):
        if isinstance(v, float):
            assert math.isfinite(v), f"{name}: non-finite float leaked into payload"


def _records(payload):
    return payload["records"]


def test_us_state_missing_price_and_stocks_are_null_not_zero():
    payload = E.export_us_state()
    _assert_no_non_finite(payload, "us_state_year")
    recs = {(r["state"], r["year"], r["sector"]): r for r in _records(payload)}

    # Missing coal prices: AK 2020 sectors 3/8/10 are unreported in the
    # source; AK 2020 sector 1 is reported. Both must survive, distinct.
    assert recs[("AK", 2020, 3)]["price"] is None
    assert recs[("AK", 2020, 1)]["price"] == pytest.approx(49.26)
    # ...and missingness is never filled with zero:
    assert recs[("AK", 2020, 3)]["consumption"] == pytest.approx(220848.0)

    # Missing inventories: electric-power stocks are structurally
    # unreported for most rows (AK 2020 sectors 1/3/10).
    assert recs[("AK", 2020, 1)]["stocks"] is None
    assert recs[("AK", 2020, 3)]["stocks"] is None

    # Real zeros stay zeros: CA 2020 sector 3 has zero consumption AND a
    # missing price - the two must not be conflated.
    ca = recs[("CA", 2020, 3)]
    assert ca["consumption"] == 0.0
    assert ca["price"] is None


def test_us_aggregates_missing_price_is_null():
    payload = E.export_us_aggregates()
    _assert_no_non_finite(payload, "us_aggregates")
    recs = {(r["location"], r["year"], r["sector"]): r for r in _records(payload)}
    # US sector 98 delivered prices: 2020 reported, 2021 unreported.
    assert recs[("US", 2020, 98)]["price"] == pytest.approx(36.13)
    assert recs[("US", 2021, 98)]["price"] is None
    assert recs[("US", 2022, 98)]["price"] == pytest.approx(44.50)
    # At least one reported price must survive (not wiped to null).
    assert any(r["price"] is not None for r in _records(payload))


def test_country_year_nested_clean_and_flags_real():
    payload = E.export_country_year()
    _assert_no_non_finite(payload, "country_year")
    by_key = {(r["iso3"], r["year"]): r for r in _records(payload)}

    # Top-level coal_share is null exactly when EI variables are absent.
    no_ei = [r for r in _records(payload) if not r["ei_available"]]
    assert no_ei, "expected Ember-only countries"
    for r in no_ei:
        assert r["coal_share"] is None
        assert all(v is None for v in r["ei"].values())

    # Flags are carried through from the cleaned Ember table - not the
    # always-False values the old phantom r.get() produced.
    zero_gen = {r["iso3"] for r in _records(payload) if r["zero_generation"]}
    assert zero_gen == {"LSO", "NIU"}, zero_gen   # Lesotho 2023-24, Niue 2020-23
    assert all(isinstance(r["zero_generation"], bool) for r in _records(payload))
    assert all(isinstance(r["ci_precision_limited"], bool) for r in _records(payload))


def test_export_is_deterministic():
    a = json.dumps(E.export_us_state(), sort_keys=True, allow_nan=False)
    b = json.dumps(E.export_us_state(), sort_keys=True, allow_nan=False)
    assert a == b


def test_generated_files_parse_with_strict_json():
    """Requirement: every generated file must parse with a
    standards-compliant JSON parser (RFC 8259: no NaN/Infinity tokens)."""
    for name in FILES:
        text = (DATA / name).read_text(encoding="utf-8")
        try:
            obj = json.loads(text, parse_constant=_reject)
        except ValueError as e:
            pytest.fail(f"{name}: {e}")
        assert isinstance(obj, dict), name


def test_independent_ei_years_and_world_totals_are_preserved():
    payload = E.export_country_year()
    by_key = {(r["iso3"], r["year"]): r for r in payload["records"]}
    idn = by_key[("IDN", 2025)]
    assert idn["ember_available"] is False
    assert idn["ember"]["generation"] is None
    assert idn["ember"]["demand"] is None
    assert idn["ei"]["coal_gen"] > 0
    assert ("SUN", 2025) not in by_key  # historical USSR is not a current country
    assert len(payload["ei_world"]) == 6
    world24 = next(r for r in payload["ei_world"] if r["year"] == 2024)
    assert world24["coal_generation_twh"] == pytest.approx(10569.71153)
    coverage25 = next(r for r in payload["coverage"] if r["year"] == 2025)
    assert coverage25["ember_countries"] == 91
    assert coverage25["ei_countries"] == 82


def test_every_plotted_source_field_and_evidence_file_is_current(pipeline_outputs):
    from analysis.verify_dashboard_data import audit
    result = audit()
    assert result["errors"] == []
    assert result["source_field_comparisons"] > 30_000
    assert result["ei_only_records_restored"] == 14
