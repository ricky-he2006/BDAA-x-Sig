"""Audit deck images, narrative numbers, PDF parity and supporting graph files."""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import fitz
import pandas as pd
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission"


def verify():
    errors = []

    def check(value, message):
        if not value:
            errors.append(message)

    m = json.loads((OUT / "metrics.json").read_text())
    history = pd.read_csv(OUT / "tables/matched_2020_2024.csv").set_index("year")
    for col, key in [("clean_generation_twh", "clean_growth_2020_2024_pct"),
                     ("fossil_generation_twh", "fossil_growth_2020_2024_pct")]:
        actual = (history.at[2024, col] / history.at[2020, col] - 1) * 100
        check(math.isclose(actual, m[key], abs_tol=1e-8), f"Historical metric mismatch: {key}")
    us = pd.read_csv(OUT / "tables/us_electric_power_coal.csv").set_index("year")
    check(us.sector_code.eq(98).all() and us.location_code.eq("US").all(), "U.S. chart includes overlapping sectors or locations")
    for start, end, key in [(2020, 2024, "us_coal_2020_2024_pct"), (2024, 2025, "us_coal_2025_yoy_pct")]:
        actual = (us.at[end, "consumption_million_short_tons"] / us.at[start, "consumption_million_short_tons"] - 1) * 100
        check(math.isclose(actual, m[key], abs_tol=1e-8), f"U.S. chart mismatch: {key}")
    watch = pd.read_csv(OUT / "tables/2025_watch_evidence.csv")
    check((watch.change_twh - (watch.value_2025 - watch.value_2024)).abs().max() < 1e-8, "2025 changes do not reconcile")
    ember = watch[watch.source.eq("Ember")].set_index("measure")
    check(list(ember.index) == ["Demand", "Clean", "All fossil"], "2025 chart row order differs from labels")
    check(math.isclose(ember.at["Clean", "change_twh"] / ember.at["Demand", "change_twh"] * 100,
                       m["matched_2025_clean_vs_demand_additions_pct"], abs_tol=1e-8), "2025 addition ratio mismatch")
    deck = Presentation(OUT / "energy_transition_pitch.pptx")
    pdf = fitz.open(OUT / "energy_transition_pitch.pdf")
    manifest = json.loads((OUT / "presentation_manifest.json").read_text())
    expected = manifest["main_slides"] + manifest["appendix_slides"]
    check(len(deck.slides) == len(pdf) == expected, "PPTX/PDF slide counts must match the presentation manifest")
    images = {2: ["generation_index"], 4: ["clean_additions_2025", "coal_changes_2025"], 5: ["us_coal_consumption"]}
    image_count = 0
    for i, slide in enumerate(deck.slides, 1):
        embedded = [hashlib.sha256(s.image.blob).hexdigest() for s in slide.shapes if hasattr(s, "image")]
        image_count += len(embedded)
        for name in images.get(i, []):
            for ext in ["png", "svg"]:
                check((OUT / f"pitch_figures/{name}.{ext}").is_file(), f"Missing pitch asset {name}.{ext}")
            digest = hashlib.sha256((OUT / f"pitch_figures/{name}.png").read_bytes()).hexdigest()
            check(digest in embedded, f"Slide {i} embeds a stale or different chart: {name}")
        # PDF export must retain all native slide text, not merely page count.
        normalize = lambda s: re.sub(r"\s+", "", s).replace("\u00ad", "")
        pdf_text = normalize(pdf[i-1].get_text())
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text.strip():
                check(normalize(shape.text) in pdf_text, f"Native slide text missing from PDF page {i}: {shape.text[:55]}")
    for folder in ["figures", "pitch_figures"]:
        for png in (OUT / folder).glob("*.png"):
            check(png.with_suffix(".svg").exists(), f"Missing vector version: {png.name}")
    for name in ["INVESTMENT_THESIS.md", "EXECUTIVE_SUMMARY.md"]:
        for link in re.findall(r"\]\(([^)]+)\)", (OUT / name).read_text()):
            if not link.startswith(("https://", "http://", "#")):
                check((OUT / link.split("#")[0]).exists(), f"Broken {name} evidence link: {link}")
    result = {"errors": errors, "pitch_charts": image_count, "supporting_graphs": len(list((OUT / "figures").glob("*.png"))),
              "pdf_pages": len(pdf), "chart_hashes_verified": True if not errors else False}
    (OUT / "pitch_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    verify()
