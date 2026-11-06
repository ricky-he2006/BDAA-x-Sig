"""Check final artifacts, evidence lineage, hashes and presentation timing."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission"


def verify():
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)

    metrics = json.loads((OUT / "metrics.json").read_text())
    manifest = json.loads((OUT / "input_manifest.json").read_text())
    for name, digest in manifest.items():
        check(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, f"Input changed after build: {name}")
    countries = pd.read_csv(OUT / "tables/country_review_all.csv")
    material = pd.read_csv(OUT / "tables/material_country_pathways.csv")
    check(countries.iso3.nunique() == 213, "Country coverage mismatch")
    check(len(material) == 16, "Material-country population mismatch")
    for iso in countries.iso3:
        check((OUT / f"countries/{iso}.md").exists(), f"Missing review: {iso}")
    for iso in material.iso3:
        for ext in ["png", "svg"]:
            check((OUT / f"figures/country_{iso}.{ext}").exists(), f"Missing country figure: {iso}.{ext}")
    check(countries.demand_identity_residual_twh.dropna().abs().max() < .1, "Demand identity does not reconcile")
    claims = pd.read_csv(OUT / "tables/claim_evidence.csv")
    check(not claims.claim_id.duplicated().any(), "Duplicate claim IDs")
    for name in claims.table:
        check((OUT / "tables" / name).exists(), f"Missing evidence table {name}")
    for suffix, expected_n, expected_years in [("2020_2024", 196, 5), ("2020_2025", 91, 6)]:
        panel = pd.read_csv(OUT / f"tables/matched_{suffix}_membership.csv")
        check(panel.groupby("iso3").year.nunique().eq(expected_years).all(), "Incomplete matched panel")
        check(panel.groupby("year").iso3.nunique().eq(expected_n).all(), "Variable matched membership")
    p = Presentation(OUT / "energy_transition_pitch.pptx")
    pm = json.loads((OUT / "presentation_manifest.json").read_text())
    check(len(p.slides) == pm["main_slides"] + pm["appendix_slides"], "Slide count mismatch")
    check(300 <= pm["planned_seconds"] < 420, "Speaking plan outside brief")
    check(650 <= pm["spoken_words"] <= 900, "Script likely outside intended speaking duration")
    for i, slide in enumerate(p.slides):
        check(bool(slide.notes_slide.notes_text_frame.text.strip()), f"Missing notes on slide {i+1}")
        for shape in slide.shapes:
            check(shape.top >= 0 and shape.left >= 0 and shape.left + shape.width <= p.slide_width + 10000
                  and shape.top + shape.height <= p.slide_height + 10000, f"Shape outside slide {i+1}")
    check((OUT / "energy_transition_pitch.pdf").exists(), "PDF not exported (requires LibreOffice)")
    browser_path = OUT / "previews/browser_check.json"
    browser = json.loads(browser_path.read_text()) if browser_path.exists() else None
    if browser:
        check(not browser["page_errors"], "Browser runtime errors")
        check(browser.get("completed", True), "Browser acceptance checks incomplete")
        check(not browser.get("http_errors", []), "Browser HTTP failures")
        check(not browser.get("external_asset_requests", []), "Dashboard depends on external assets")
    data_audit_path = OUT / "dashboard_data_audit.json"
    if data_audit_path.exists():
        check(not json.loads(data_audit_path.read_text())["errors"], "Dashboard source field mismatch")
    result = {"errors": errors, "country_reviews": len(countries), "detailed_country_figures": len(material),
              "figure_pairs_png_svg": len(list((OUT / "figures").glob("*.png"))),
              "slides": len(p.slides), "main_slides": pm["main_slides"], "planned_seconds": pm["planned_seconds"],
              "spoken_words": pm["spoken_words"], "browser_checked": bool(browser),
              "clean_growth_2020_2024_pct": metrics["clean_growth_2020_2024_pct"]}
    (OUT / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    verify()
