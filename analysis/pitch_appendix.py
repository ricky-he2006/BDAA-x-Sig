"""Judge-facing evidence appendix; uses the pitch's existing visual system."""
from pptx.dml.color import RGBColor
from pptx.util import Inches


def add_appendix(p, m):
    from analysis.pitch_design import text, rect, label, NAVY, PAPER, WHITE, BLUE, MUTED, GRID
    slides = [
        ("DATA & INTEGRATION", "Three sources, three distinct measurement roles", [
            ("CORE 1 · EMBER", "1,138 country-year rows · 2020–2025\nDemand, clean and all-fossil electricity in TWh.\nClean includes renewables and nuclear."),
            ("CORE 2 · EIA", "1,750 year/location/sector rows · 2020–2025\nU.S. coal consumption in short tons. National sector 98 is kept separate from state base sectors."),
            ("OPTIONAL THIRD · ENERGY INSTITUTE", "299,320 country/year/variable rows · 1965–2025\nAdds coal-specific generation (TWh). Match country/year to Ember; compare U.S. direction with EIA, without equating tons to TWh.")],
         "Source: reports/data_quality_report.md; PROJECT_AUDIT.md; data/provenance/energy_institute.json",
         "Both core sources matter: Ember tests system growth; EIA tests the U.S. thermal-coal call. EI isolates coal within fossil generation. Normalize geography keys before country/year matching; exclude regional aggregates. The broader Ember/EI geography intersection is 107, not the fixed historical panel. EI's original local edition/download date remains unverified; its publisher catalogue is documented. EI lists Ember as a partner, so this is triangulation rather than three fully independent sources."),
        ("CLEANING & VALIDATION", "Preserve missingness. Prevent false comparisons.", [
            ("PRESERVE SOURCE VALUES", "Raw files are SHA-256 pinned. No source values overwritten; no duplicate keys found. Missing observations stay missing; explicit zeros remain zeros."),
            ("CONTROL COVERAGE & OVERLAP", "196 fixed countries for 2020–2024; 91 for 2020–2025. Never sum overlapping EIA national, regional and state aggregates. EI world totals use WLD alone."),
            ("CHECK DEFINITIONS BEFORE CALCULATING", "Validate keys, share ranges and accounting identities. EIA heat-content units are ambiguous: exclude those conversions from the thesis. Delivered price is a fuel cost, not a producer margin.")],
         "Source: reports/data_quality_report.md; tests/test_deliverables.py; analysis/verify_pitch.py",
         "Ember coverage shrinks from 213 geographies in 2020 to 196 in 2024 and 91 in 2025. A naive annual sum could confuse missing countries with decline. Fixed membership prevents that error but does not remove selection bias. Missing prices cannot be imputed as zero. The pipeline retains flags and source values; its checks cover grain uniqueness, missing versus zero, sector separation and accounting. Show the actual audit outputs if asked; do not claim every reported cross-source number matches."),
        ("ROBUSTNESS", "Faster clean growth survives a different baseline", [
            ("2020 → 2024 · 196 FIXED COUNTRIES", f"Clean generation +{m['clean_growth_2020_2024_pct']:.1f}%\nAll-fossil generation +{m['fossil_growth_2020_2024_pct']:.1f}%\nGrowth = (endpoint / baseline − 1) × 100."),
            ("2021 → 2024 · THE SAME 196 COUNTRIES", f"Clean generation +{m['clean_growth_2021_2024_pct']:.1f}%\nAll-fossil generation +{m['fossil_growth_2021_2024_pct']:.1f}%\nDirection persists after moving beyond the 2020 baseline."),
            ("WHAT THE CHECK DOES AND DOES NOT SHOW", "The clean-growth lead is robust to this baseline choice. These are unequal-length cumulative windows, not annualized forecasts. The 91-country 2025 panel is a separate comparison.")],
         "Source: tables/baseline_sensitivity.csv · E01/E02/E10; tables/2025_watch_evidence.csv · E06",
         "We use descriptive accounting because the question asks whether generation expanded together, not to estimate a causal policy effect. Aggregate share is summed clean TWh divided by summed total TWh, not an unweighted country mean. Clean additions divided by demand additions is only meaningful with positive demand growth; it does not prove causal substitution. No confidence interval is fitted to these supplied snapshot totals. Uncertainty comes from revisions, definitions, coverage and the forward-looking allocation judgment."),
        ("ORIGINALITY & DECISION VALUE", "Classify pathways, then make the coal call specific", [
            ("A TRANSPARENT COUNTRY SCREEN", "Require clean and coal generation above 20 TWh at both endpoints. Apply directional changes beyond ±5% for 2020–2024. Sixteen material markets qualify; thresholds are analyst choices."),
            ("THE FINDING THAT CHANGES THE DECISION", "China: clean +50.9%, coal +18.4%.\nU.S.: clean +14.1%, coal −15.6%.\nGermany: clean −7.9%, coal −21.4%; demand also fell."),
            ("TURN THE FINDING INTO AN ACTION", "Favor diversified low-carbon generation exposure. Focus the coal underweight on U.S. domestic thermal producers. Review persistence of the U.S. rebound before extending the call.")],
         "Source: tables/material_country_pathways.csv; tables/country_review_all.csv · E07–E09",
         "The contribution is a decision framework that separates clean expansion from coal displacement, uses both core sources, and treats the strongest counterexample as a monitoring rule. The sixteen markets are a selected material population, not worldwide frequencies. Threshold sensitivity has not been established; do not call the labels universal. Generation and consumption support an industry outlook, while valuation and project economics are still needed before choosing securities."),
        ("DASHBOARD EVIDENCE TOUR", "Trace the recommendation back to the observations", [
            ("1 · VERIFY THE HEADLINE", "Data & evidence → Numbers supporting the presentation. Match E01/E02/E04/E05 to slides 2 and 5. Check source, units and fixed-panel scope before comparing."),
            ("2 · TEST THE INTERPRETATION", "World → China, then Germany → expand demand/mix and coal charts. Compare 2020 and 2024. Research → Coal shows EI's world total separately from matched samples."),
            ("3 · CHALLENGE AND REPRODUCE THE CALL", "United States → national consumption and delivered price. Show the 2025 rebound. Return to Data & evidence for coverage, claim references and downloadable observations.")],
         "Companion: submission/DASHBOARD_WALKTHROUGH.md · detailed route, narration and claim-to-view mapping",
         "Use the dashboard during questions or as a separate demonstration so the timed main pitch stays focused. The year slider changes map/snapshot values; charts retain their historical series. Research's six-year matched sample differs from the main 196-country historical panel. State maps describe consumption locations, not mines. Downloads make observations inspectable; they do not settle causality or prove stock outperformance. The detailed walkthrough explains how each view supports, qualifies or challenges the recommendation."),
    ]
    for j, (section, title, cards, source, notes) in enumerate(slides, 1):
        s = p.slides.add_slide(p.slide_layouts[6])
        s.background.fill.solid(); s.background.fill.fore_color.rgb = RGBColor.from_string(PAPER)
        label(s, 'EVIDENCE APPENDIX · ' + section, .6, .32, 11, BLUE)
        label(s, f'A{j:02d}', 12, .32, .7)
        text(s, title, .6, .9, 12.1, 1.05, 31, NAVY, True)
        for k, (heading, body) in enumerate(cards):
            x = .6 + k * 4.13
            rect(s, x, 2.25, 3.88, 4.25, WHITE, True)
            text(s, heading, x + .23, 2.5, 3.42, .7, 16, BLUE, True)
            text(s, body, x + .23, 3.3, 3.42, 2.95, 19, MUTED)
        rect(s, .6, 6.98, 12.13, .012, GRID)
        text(s, source, .65, 7.11, 12, .23, 9, MUTED)
        s.notes_slide.notes_text_frame.text = notes
    return len(slides)
