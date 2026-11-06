"""Validation tests for the ISO 3166-1 reference set (src/iso3166.py).

The official set was rebuilt after a defective first revision silently
omitted many real codes (ESP, ZAF, TCD, ...) and contained invalid
entries (CCA, CXA, FXY, MYT, MNR, VCU). These tests pin both the
integrity of the set and the previously-missing codes.
"""
import pandas as pd

from src import config as C
from src.iso3166 import (ISO3_NONISO_ACCEPTED, ISO3_OFFICIAL, is_known)


def test_official_set_integrity():
    assert len(ISO3_OFFICIAL) == 243          # no duplicates in the literal
    assert len(set(ISO3_OFFICIAL)) == 243
    assert all(len(c) == 3 for c in ISO3_OFFICIAL)
    # no code may be both official and "accepted non-ISO"
    assert not (set(ISO3_OFFICIAL) & set(ISO3_NONISO_ACCEPTED))


def test_previously_missing_codes_present():
    missing_before = ("ESP", "ZAF", "TCD", "LKA", "SSD", "DOM", "ASM",
                      "BMU", "GRD", "GLP", "GNB", "CHL", "URY", "ABW",
                      "GRL", "GUM", "CYM", "BTN", "TWN", "MNE", "PLW",
                      "MNP", "SLB", "TON", "SDN", "NAM", "JPN", "SGP",
                      "KWT", "KHM", "BHR", "ISR", "TUR", "MAC", "CIV",
                      "TZA", "COG", "BIH", "FLK", "HMD", "UMI", "ATF",
                      "AIA")
    for code in missing_before:
        assert is_known(code), f"{code} missing from ISO3_OFFICIAL"


def test_invalid_codes_absent():
    for code in ("CCA", "CXA", "FXY", "MYT", "MNR", "VCU", "ZIM", "SUN"):
        assert not is_known(code), f"{code} should not be official"
    # SUN/ANT/NRU are legitimate vendor codes, so they are accepted (not official)
    for code in ("SUN", "ANT", "NRU"):
        assert code in ISO3_NONISO_ACCEPTED


def test_every_source_code_is_adjudicated():
    """Any iso3 code present in the cleaned data must be either official,
    accepted non-ISO, or an EI regional aggregate - otherwise it would be
    an unexplained audit warning."""
    ok = set(ISO3_OFFICIAL) | set(ISO3_NONISO_ACCEPTED)
    for f, agg_codes in ((C.CLEANED_EMBER, ()), (C.CLEANED_EI, (
            C.EI_AGGREGATE_PREFIXES, C.EI_AGGREGATE_EXTRA)),
                        (C.CLEANED_EIA, ())):
        df = pd.read_csv(C.CLEANED / f, low_memory=False)
        if "iso3" not in df.columns:
            continue
        codes = set(df.iso3.dropna().astype(str).unique())
        unexplained = set()
        for c in codes:
            cu = c.upper()
            if cu in ok:
                continue
            if agg_codes and (cu.startswith(agg_codes[0])
                              or cu in agg_codes[1]):
                continue
            unexplained.add(cu)
        assert not unexplained, (
            f"{f}: codes with no reference entry: {sorted(unexplained)}")
