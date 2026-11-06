import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_provenance_does_not_invent_a_local_download_date():
    p = json.loads((ROOT / "data/provenance/energy_institute.json").read_text())
    assert p["local_sha256"] == hashlib.sha256((ROOT / p["local_file"]).read_bytes()).hexdigest()
    assert "original_download_date" in p and "local_edition_verified" in p
    if p["local_edition_verified"] is None:
        assert "not independently certified" in p["verification_status"]
    if p["original_download_date"] is not None:
        assert p.get("local_verification_evidence"), "A confirmed original download date needs its own receipt/evidence"
    assert p["official_catalogue_url"].startswith("https://www.energyinst.org/")


def test_latest_country_comparison_uses_coal_not_all_fossil(pipeline_outputs):
    cy = pipeline_outputs["processed"]["analysis_country_year.csv"].set_index(["iso3", "year"])
    table = pd.read_csv(ROOT / "submission/tables/2025_watch_evidence.csv")
    for iso in ["CHN", "IND", "USA"]:
        row = table[(table.source == "EI") & (table.geography == iso)].iloc[0]
        expected = cy.loc[(iso, 2025), "ei_coal_generation_twh"] - cy.loc[(iso, 2024), "ei_coal_generation_twh"]
        assert abs(row.change_twh - expected) < 1e-8
        assert (row.change_twh > 0) == (iso == "USA")
