"""Design the eight-slide investment pitch and its presentation materials.

Charts use the audited evidence CSVs; no country appendix is added to the deck.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission"
ASSETS = OUT / "pitch_figures"
NAVY, PAPER, WHITE = "122A40", "F7F9FC", "FFFFFF"
BLUE, ORANGE, MUTED, GRID = "2665B5", "B75C12", "53677A", "DDE5ED"
BRIGHT_BLUE, BRIGHT_ORANGE = "88BCFF", "FFBD87"


def text(slide, value, x, y, w, h, size=20, color=NAVY, bold=False):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.clear(); tf.word_wrap = True; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate(str(value).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = "Aptos"
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = RGBColor.from_string(color)
        p.space_before = p.space_after = Pt(0)
        p.line_spacing = 1.08
    return shape


def rect(slide, x, y, w, h, color, rounded=False):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
                               Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = RGBColor.from_string(color)
    s.line.fill.background()
    if rounded:
        s.adjustments[0] = .07
    return s


def label(slide, value, x, y, w, color=MUTED):
    return text(slide, value, x, y, w, .25, 11, color, True)


def chart_file(fig, name):
    fig.savefig(ASSETS / f"{name}.png", dpi=220, facecolor="white", bbox_inches="tight", pad_inches=.16)
    fig.savefig(ASSETS / f"{name}.svg", facecolor="white", bbox_inches="tight", pad_inches=.16)
    plt.close(fig)
    return ASSETS / f"{name}.png"


def charts():
    ASSETS.mkdir(exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 15,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.spines.left": False, "axes.spines.bottom": False,
                         "axes.labelcolor": "#" + MUTED, "text.color": "#" + NAVY,
                         "xtick.color": "#" + MUTED, "ytick.color": "#" + MUTED,
                         "grid.color": "#" + GRID, "axes.axisbelow": True})
    history = pd.read_csv(OUT / "tables/matched_2020_2024.csv").set_index("year")
    fig, ax = plt.subplots(figsize=(7.3, 3.0))
    for col, name, color in [("clean_generation_twh", "Clean", BLUE), ("fossil_generation_twh", "All fossil", ORANGE)]:
        v = history[col] / history.at[2020, col] * 100
        ax.plot(v.index, v, color="#" + color, lw=3.2, marker="o", ms=7)
        ax.text(2024.16, v.iloc[-1], f"{name}\n{v.iloc[-1]:.1f}", color="#" + color, fontsize=17, va="center", fontweight="bold")
    ax.set(xlim=(2019.85, 2025.0), ylim=(96, 134), xticks=history.index, yticks=[100, 110, 120, 130])
    ax.grid(axis="y"); ax.tick_params(length=0, pad=9)
    ax.text(0, 1.04, "GENERATION INDEX · 2020 = 100", transform=ax.transAxes, fontsize=12, color="#" + MUTED)
    hist = chart_file(fig, "generation_index")

    watch = pd.read_csv(OUT / "tables/2025_watch_evidence.csv")
    fig, ax = plt.subplots(figsize=(5.3, 2.7))
    d = watch[watch.source.eq("Ember")]
    ax.bar(["Demand", "Clean", "All fossil"], d.change_twh, color=["#8999A8", "#" + BLUE, "#" + ORANGE], width=.57)
    ax.axhline(0, color="#" + MUTED, lw=1)
    ax.set(ylim=(-230, 1120), yticks=[0, 400, 800])
    ax.grid(axis="y"); ax.tick_params(length=0, pad=8)
    for i, v in enumerate(d.change_twh):
        ax.text(i, v + (35 if v >= 0 else -35), f"{v:+,.0f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=18, fontweight="bold")
    clean_watch = chart_file(fig, "clean_additions_2025")

    fig, ax = plt.subplots(figsize=(5.3, 2.7))
    d = watch[watch.source.eq("EI")].set_index("geography").loc[["CHN", "IND", "USA"]]
    ax.bar(["China", "India", "U.S."], d.change_twh, color=["#" + BLUE, "#" + BLUE, "#" + ORANGE], width=.57)
    ax.axhline(0, color="#" + MUTED, lw=1)
    ax.set(ylim=(-130, 135), yticks=[-100, 0, 100])
    ax.grid(axis="y"); ax.tick_params(length=0, pad=8)
    for i, v in enumerate(d.change_twh):
        ax.text(i, v + (5 if v >= 0 else -5), f"{v:+,.0f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=18, fontweight="bold")
    coal_watch = chart_file(fig, "coal_changes_2025")

    nat = pd.read_csv(OUT / "tables/us_electric_power_coal.csv")
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.bar(nat.year, nat.consumption_million_short_tons, color=["#B5C2CE"] * 5 + ["#" + ORANGE], width=.65)
    ax.set(ylim=(0, 570), yticks=[0, 200, 400], xticks=nat.year)
    ax.grid(axis="y"); ax.tick_params(length=0, pad=9)
    for row in nat.itertuples():
        ax.text(row.year, row.consumption_million_short_tons + 12, f"{row.consumption_million_short_tons:.0f}", ha="center", fontsize=14, color="#" + (ORANGE if row.year == 2025 else MUTED), fontweight="bold")
    ax.text(0, 1.04, "U.S. POWER-SECTOR CONSUMPTION · MILLION SHORT TONS", transform=ax.transAxes, fontsize=12, color="#" + MUTED)
    us = chart_file(fig, "us_coal_consumption")
    return {"history": hist, "clean_watch": clean_watch, "coal_watch": coal_watch, "us": us}


def narrative(m):
    us = pd.read_csv(OUT / "tables/us_electric_power_coal.csv").set_index("year")
    remaining_gap = (us.at[2025, "consumption_million_short_tons"] / us.at[2020, "consumption_million_short_tons"] - 1) * 100
    return [
        dict(section="THE CALL", title="Invest in clean growth.\nStay selective on coal.", seconds=35,
             cue="State both calls and the U.S. thermal-coal scope before explaining the evidence.",
             takeaway="", source="Industry allocation judgment · November 2026–November 2029 · Evidence E01–E05",
             script="Our thesis is that clean electricity can grow without coal disappearing worldwide. Clean generation rose 25.4 percent through 2024, while fossil generation also increased. We therefore favor diversified low-carbon generation over three years. Our coal underweight focuses on U.S. domestic thermal producers: consumption declined through 2024, but the 2025 rebound lowers conviction. We will use the dashboard to test each claim and monitor whether that rebound persists. Security selection still requires valuation and financing evidence."),
        dict(section="THE EVIDENCE", title="Clean grew faster.\nFossil output still increased.", seconds=50,
             cue="Point to the two endpoints. Explain that the lines are generation indices, not investment returns.",
             takeaway="Clean and fossil generation expanded together.", source="Ember · fixed 196-country panel, 2020–2024 · E01–E02 · Clean = renewables + nuclear",
             script=f"Start with what the electricity system actually produced. Between 2020 and 2024, clean generation increased {m['clean_growth_2020_2024_pct']:.1f} percent across the same 196 countries. All-fossil generation also rose, by {m['fossil_growth_2020_2024_pct']:.1f} percent. Clean includes renewables and nuclear.\n\nThe blue line shows faster clean growth, while the orange line shows that fossil volumes remained resilient. A cleaner mix can therefore coexist with more fossil output. We hold country coverage constant so that missing observations cannot create a false decline. Ember supplies this system view; EIA and our third dataset, the Energy Institute, let us examine coal more closely. The aggregate, however, hides different country outcomes."),
        dict(section="WHY GEOGRAPHY MATTERS", title="The coal call needs a market context.", seconds=45,
             cue="Use the three examples as illustrations; do not read a list of countries.",
             takeaway="Similar changes in coal can have different investment implications.", source="2020–2024 · Ember clean generation; EI coal generation · E07–E09 · Three illustrations, not a representative sample",
             script="Three examples show why the geographic scope matters. China increased both clean and coal generation through 2024: that is coexistence. The United States combined rising clean output with falling coal generation over the same period.\n\nGermany gives us a useful caution. Coal generation fell there, but clean output and electricity demand also fell. That result alone cannot establish clean-energy substitution. These are observed outcomes, rather than explanations of what caused them. For investors, the implication is to specify the market and business model behind a coal position. The latest year makes that distinction even more important."),
        dict(section="THE LATEST SIGNAL", title="2025 strengthened clean growth.\nCoal moved differently by market.", seconds=55,
             cue="Explain the left panel, then the right. Keep the two sources and fuel definitions separate.",
             takeaway="The latest year supports clean growth and regional divergence.", source="2024–2025 changes, TWh · Left: Ember, 91 fixed countries · Right: EI coal generation · E06/E11",
             script=f"In 2025, clean-generation additions were about {m['matched_2025_clean_vs_demand_additions_pct']:.0f} percent of additional electricity demand in our 91-country Ember panel. All-fossil output fell in that sample. This is a consistent comparison, not a full-world estimate: the panel represents 93.5 percent of generation observed in the 2024 extract.\n\nThe right panel asks a separate question using EI coal generation. China and India declined, while the United States increased. That supports the case for clean expansion, while showing that coal can move against the broader pattern in individual markets. One annual decline does not establish a lasting global peak. The U.S. increase is the strongest counterargument to our coal underweight."),
        dict(section="THE COUNTERARGUMENT", title="U.S. coal recovered in 2025.\nOur underweight depends on persistence.", seconds=55,
             cue="Show the decline, rebound and remaining gap; distinguish EIA short tons from EI TWh. Point to the persistence rule and dashboard route.",
             takeaway="Historical decline supports caution; the rebound lowers conviction.",
             source="EIA national electric-power sector 98 · E04/E05; EI U.S. coal generation · E11 · Analyst monitoring rule",
             script=f"Our U.S. coal position is conditional. EIA power-sector coal consumption fell {abs(m['us_coal_2020_2024_pct']):.1f} percent from 2020 to 2024, then rebounded {m['us_coal_2025_yoy_pct']:.1f} percent in 2025. It remained {abs(remaining_gap):.1f} percent below 2020. The historical decline supports caution on domestic thermal exposure, but the rebound lowers our conviction.\n\nA second measure supports the direction: EI reports higher U.S. coal-fired generation in 2025. Consumption is measured in short tons; generation is in terawatt-hours. We compare their direction, without treating them as equivalent or identifying the cause.\n\nOur monitoring rule is to reconsider the underweight if consumption stays above its 2024 level for two further annual releases. In the dashboard, open United States and the national consumption history to inspect this risk."),
        dict(section="THE ALLOCATION", title="Match the country to the sector.\nThen test the investment economics.", seconds=55,
             cue="Distinguish the U.S. underweight from China and Germany research priorities. Link each sector to its observed country pathway.",
             takeaway="Favor clean growth; use country evidence to guide sector diligence.",
             source="2020–2024 country evidence · E04/E05/E08/E09 · Sector priorities are analyst interpretations, not security ratings",
             script="Our broad preference is diversified low-carbon generation. Country evidence then guides which sector exposures deserve closer attention. In the United States, the coal underweight focuses on domestic thermal producers serving power demand. Consumption declined through 2024, but the rebound makes that view conditional.\n\nIn China, clean generation rose 50.9 percent while coal rose 18.4 percent. Prioritize diligence on low-carbon generation owners without assuming coal demand immediately disappears. In Germany, clean generation, coal and demand all fell. For utilities and generation owners, investigate demand exposure, electricity trade and revenue contracts before making an allocation.\n\nChina and Germany are research priorities, not country buy ratings. Across all three, check valuation, cash flow, financing and the company’s actual revenue exposure before selecting securities."),
        dict(section="THE DECISION RULES", title="What would change our view?", seconds=45,
             cue="Explain the monitoring rules as judgment calls, not forecasts or estimated probabilities.",
             takeaway="Use observable reversal conditions, and keep the data limits explicit.", source="Analyst monitoring rules · SOURCES.md and PROJECT_AUDIT.md document source and coverage limitations",
             script="We would monitor three things. For coal, reconsider the U.S. underweight if consumption remains above its 2024 level for two further annual releases. For clean energy, reassess the overweight after two comparable years without clean-share gains, alongside rising fossil generation.\n\nFor the investments themselves, weak project returns or financing pressure would require another look at security selection. These are analyst decision rules, not fitted forecasts. We also retain the source limitations: incomplete country coverage, differences between data vintages, and an unverified original edition and download date for the local EI file. Those limits constrain the confidence and precision of the recommendation."),
        dict(section="THE DECISION", title="Own clean growth.\nKeep coal exposure selective.", seconds=35,
             cue="Finish with the allocation and horizon. Pause after the final sentence.",
             takeaway="", source="Industry outlook judgment · Supporting data, methods and country research remain in the repository and dashboard",
             script="Our conclusion is to overweight clean energy and underweight coal over three years, with the coal position focused on U.S. domestic thermal exposure. The evidence supports a growing clean-electricity industry and an uneven outlook for coal.\n\nWe would track generation additions, U.S. coal consumption and the economics of the investments available. The position should change when the evidence changes. For now, our recommendation is to participate in clean-power expansion and keep the coal underweight focused."),
    ]


def build_pitch(m, submission):
    images = charts()
    story = narrative(m)
    p = Presentation(); p.slide_width = Inches(13.333); p.slide_height = Inches(7.5)
    team = submission.get("team_name") or "Energy Transition Analyst Team"
    p.core_properties.title = "Invest in clean growth. Stay selective on coal."
    p.core_properties.author = team
    p.core_properties.subject = "Coal vs clean energy: eight-slide industry investment pitch"
    summaries = pd.read_csv(OUT / "tables/country_review_all.csv").set_index("iso3")
    speakers = ["A", "A", "B", "B", "C", "C", "D", "D"]
    elapsed = 0
    for i, d in enumerate(story, 1):
        dark = i in {1, 8}
        s = p.slides.add_slide(p.slide_layouts[6])
        s.background.fill.solid(); s.background.fill.fore_color.rgb = RGBColor.from_string(NAVY if dark else PAPER)
        label(s, d["section"], .6, .32, 10, BRIGHT_BLUE if dark else BLUE)
        text(s, f"{i:02d} / 08", 11.85, .32, .9, .24, 11, "B6C7D9" if dark else MUTED)
        text(s, d["title"], .6, .87 if dark else .82, 12.1, 1.5 if dark else 1.12, 40 if dark else 32, WHITE if dark else NAVY, True)
        if i == 1:
            text(s, "OUR THESIS: Clean expansion can coexist with fossil resilience.", .65, 2.48, 12, .45, 23, WHITE, True)
            text(s, "Clean +25.4% vs all fossil +10.3% · 196 fixed countries · 2020–2024", .65, 3.03, 12, .38, 18, "D8E5F2")
            for x, call, exposure, scope, rationale, color in [
                (.65, "OVERWEIGHT", "CLEAN ENERGY", "Diversified low-carbon generation", "Participate in growing clean output; assess valuation and financing before security selection.", BRIGHT_BLUE),
                (6.85, "UNDERWEIGHT", "COAL", "U.S. domestic thermal focus", "Consumption fell 14.4% through 2024; the 11.3% rebound in 2025 makes the call conditional.", BRIGHT_ORANGE),
            ]:
                rect(s, x, 3.65, 5.85, 2.22, "213C54", True)
                label(s, exposure, x + .25, 3.85, 5.3, "D8E5F2")
                text(s, call, x + .25, 4.2, 5.3, .42, 26, color, True)
                text(s, scope, x + .25, 4.75, 5.3, .35, 18, WHITE)
                text(s, rationale, x + .25, 5.22, 5.3, .55, 14, "D8E5F2")
            text(s, "3-YEAR HORIZON · NOV 2026–NOV 2029  |  DASHBOARD: VERIFY → COMPARE → MONITOR", .65, 6.12, 12, .32, 13, "D8E5F2", True)
            attribution = team + (" · " + ", ".join(submission["members"]) if submission.get("members") else "")
            text(s, attribution, .65, 6.61, 12, .24, 11, "B6C7D9")
        elif i == 2:
            text(s, "2020–2024 · the same 196 countries in every year", .62, 2.08, 11.7, .35, 17, MUTED)
            for y, value, caption, color in [(2.8, m["clean_growth_2020_2024_pct"], "Clean generation", BLUE), (4.3, m["fossil_growth_2020_2024_pct"], "All-fossil generation", ORANGE)]:
                text(s, f"+{value:.1f}%", .65, y, 3.5, .78, 44, color, True)
                text(s, caption, .7, y + .85, 3.5, .4, 19, MUTED)
            s.shapes.add_picture(str(images["history"]), Inches(4.05), Inches(2.5), width=Inches(8.6))
        elif i == 3:
            text(s, "Three examples · clean and coal generation changes, 2020–2024", .62, 1.65, 12, .4, 18, MUTED)
            examples = [("CHN", "China", "COEXISTENCE", "Clean and coal expanded together."),
                        ("USA", "United States", "TRANSITION", "Clean grew while coal generation fell."),
                        ("DEU", "Germany", "DEMAND MATTERS", "Demand also fell; coal decline alone does not establish substitution.")]
            for j, (iso, name, tag, note) in enumerate(examples):
                x = .6 + j * 4.13
                rect(s, x, 2.35, 3.88, 3.65, WHITE, True)
                text(s, name, x + .23, 2.62, 3.4, .5, 25, NAVY, True)
                label(s, tag, x + .23, 3.22, 3.4, MUTED)
                row = summaries.loc[iso]
                for y, prefix, val, color in [(3.77, "Clean", row.clean_generation_twh_pct, BLUE), (4.4, "Coal", row.ei_coal_generation_twh_pct, ORANGE)]:
                    text(s, prefix, x + .23, y + .06, 1.1, .4, 19, MUTED)
                    text(s, f"{val:+.1f}%", x + 1.45, y, 2.15, .5, 28, color, True)
                text(s, note, x + .23, 5.16, 3.4, .69, 16, MUTED)
        elif i == 4:
            rect(s, .6, 2.16, 6.0, 3.92, WHITE, True); rect(s, 6.85, 2.16, 5.88, 3.92, WHITE, True)
            label(s, "ELECTRICITY ADDITIONS · 91 COUNTRIES", .86, 2.37, 5.6, BLUE)
            label(s, "COAL GENERATION CHANGES · EI", 7.1, 2.37, 5.3, ORANGE)
            s.shapes.add_picture(str(images["clean_watch"]), Inches(.83), Inches(2.88), width=Inches(5.48))
            s.shapes.add_picture(str(images["coal_watch"]), Inches(7.05), Inches(2.88), width=Inches(5.35))
            text(s, "Changes in TWh. The Ember sample represents 93.5% of observed 2024 extract generation, not the entire world.", .65, 6.08, 12.0, .28, 11.5, MUTED)
        elif i == 5:
            us = pd.read_csv(OUT / "tables/us_electric_power_coal.csv").set_index("year")
            gap = (us.at[2025, "consumption_million_short_tons"] / us.at[2020, "consumption_million_short_tons"] - 1) * 100
            watch = pd.read_csv(OUT / "tables/2025_watch_evidence.csv")
            ei = watch[watch.source.eq("EI") & watch.geography.eq("USA")].iloc[0]
            s.shapes.add_picture(str(images["us"]), Inches(.64), Inches(2.3), width=Inches(6.8))
            rect(s, 8.15, 2.3, 4.58, 3.05, WHITE, True)
            for y, value, caption in [(2.52, m["us_coal_2020_2024_pct"], "2020–2024 decline"),
                                      (3.42, m["us_coal_2025_yoy_pct"], "2025 rebound"),
                                      (4.32, gap, "2025 vs 2020")]:
                text(s, f"{value:+.1f}%", 8.4, y, 1.85, .5, 29, ORANGE, True)
                text(s, caption, 10.28, y + .08, 2.2, .5, 16, MUTED)
            text(s, f"Second measure: EI U.S. coal generation +{ei.change_twh:.1f} TWh in 2025.", .75, 5.28, 11.8, .3, 15, NAVY, True)
            text(s, "Same upward direction; generation and consumption have different units.", .75, 5.64, 11.8, .24, 13, MUTED)
            text(s, "RECONSIDER if consumption stays above 2024 for two further annual releases.", .75, 5.98, 11.8, .28, 16, BLUE, True)
            text(s, "Dashboard: United States → US electric power coal, 2020–2025", .75, 6.31, 11.8, .15, 10, MUTED)
        elif i == 6:
            examples = [
                ("USA", "UNITED STATES", "Domestic thermal coal", "CONDITIONAL UNDERWEIGHT", "Power coal consumption −14.4% through 2024; +11.3% in 2025.", "Check exposure to domestic power demand; monitor rebound persistence.", ORANGE, "FCF0E5"),
                ("CHN", "CHINA", "Low-carbon generation", "RESEARCH PRIORITY", "Clean +50.9%; coal +18.4% through 2024: both expanded.", "Diligence on generation owners: contracts, cash flow and financing.", BLUE, "EAF2FB"),
                ("DEU", "GERMANY", "Utilities & generation", "RESEARCH PRIORITY", "Clean −7.9%; coal −21.4%; demand −4.6% through 2024.", "Check demand, electricity trade and revenue exposure before allocation.", BLUE, "EAF2FB"),
            ]
            for j, (iso, country, sector, action, evidence, diligence, color, fill) in enumerate(examples):
                x = .6 + j * 4.13
                rect(s, x, 2.24, 3.88, 3.72, fill, True)
                label(s, country, x + .23, 2.48, 3.42, color)
                text(s, sector, x + .23, 2.95, 3.42, .8, 23, NAVY, True)
                text(s, action, x + .23, 3.88, 3.42, .35, 12, color, True)
                text(s, evidence, x + .23, 4.34, 3.42, .65, 16, MUTED)
                text(s, diligence, x + .23, 5.17, 3.42, .65, 14, NAVY)
            text(s, "China / Germany: diligence priorities, not buy ratings. All exposures need valuation and financial checks.", .72, 6.13, 12, .27, 13, MUTED)
        elif i == 7:
            headers = [("MONITOR", .82, 2.6), ("RECONSIDER WHEN…", 3.55, 5.5), ("RESPONSE", 9.45, 3.0)]
            for value, x, w in headers: label(s, value, x, 1.92, w, BLUE)
            risks = [
                ("Coal recovery", "U.S. consumption stays above 2024\nfor two further annual releases.", "Reduce the coal\nunderweight."),
                ("Clean momentum", "Two comparable years without clean-share\ngains, alongside rising fossil output.", "Reassess the clean\noverweight."),
                ("Investment economics", "Weak project returns or financing pressure.\nAdditional financial data is required.", "Review security\nselection."),
            ]
            for j, (risk, condition, action) in enumerate(risks):
                y = 2.4 + j * 1.08
                rect(s, .6, y, 12.13, .94, WHITE, True)
                text(s, risk, .82, y + .18, 2.52, .63, 19, NAVY, True)
                text(s, condition, 3.55, y + .13, 5.6, .74, 18, MUTED)
                text(s, action, 9.45, y + .13, 3.0, .74, 18, BLUE, True)
            text(s, "Data limits: changing coverage · source vintages · local EI download provenance", .73, 5.91, 12, .3, 16, MUTED)
        else:
            for y, call, scope, color in [(3.0, "OVERWEIGHT CLEAN ENERGY", "Diversified low-carbon generation", BRIGHT_BLUE),
                                          (4.45, "UNDERWEIGHT COAL", "U.S. domestic thermal focus", BRIGHT_ORANGE)]:
                text(s, call, .68, y, 12, .65, 29, color, True)
                text(s, scope, .72, y + .7, 11.7, .4, 20, WHITE)
            text(s, "THREE-YEAR HORIZON  |  REVIEW THE POSITION AS THE EVIDENCE CHANGES", .7, 6.18, 12, .4, 14, "D8E5F2", True)

        if d["takeaway"]:
            rect(s, .6, 6.48, .05, .36, BLUE)
            text(s, d["takeaway"], .8, 6.47, 11.95, .38, 17, BLUE, True)
        rect(s, .6, 6.98, 12.13, .012, "385167" if dark else GRID)
        text(s, d["source"], .65, 7.11, 12.0, .23, 9.5, "B6C7D9" if dark else MUTED)
        end = elapsed + d["seconds"]
        d["time"] = f"{elapsed//60}:{elapsed%60:02d}–{end//60}:{end%60:02d}"
        d["speaker"] = speakers[i-1]
        s.notes_slide.notes_text_frame.text = f"Slide {i} | Speaker {d['speaker']} | {d['time']}\n\n{d['script']}\n\nDelivery cue (not spoken): {d['cue']}\n\nEvidence: {d['source']}"
        elapsed = end

    from analysis.pitch_appendix import add_appendix
    appendix_count = add_appendix(p, m)
    p.save(OUT / "energy_transition_pitch.pptx")
    words = sum(len(re.findall(r"\b[\w’'-]+\b", d["script"])) for d in story)
    manifest = {"main_slides": 8, "appendix_slides": appendix_count, "planned_seconds": elapsed,
                "spoken_words": words, "team_names_configured": bool(submission.get("members")),
                "design": f"eight-slide pitch with {appendix_count} judge-facing evidence appendix slides"}
    (OUT / "presentation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    script = ["# Presentation script", "", f"Eight main slides plus {appendix_count} evidence appendix slides · {words} main-pitch spoken words · planned main-pitch delivery 6:15. Appendix narration adds time and is excluded from that plan. Speaker labels A–D are suggestions; adjust for your group. Delivery cues are not spoken.", ""]
    for i, d in enumerate(story, 1):
        script += [f"## {i}. {d['title'].replace(chr(10), ' ')}", "", f"**Speaker {d['speaker']} · {d['time']} · {d['seconds']} seconds**", "",
                   d["script"], "", f"*Delivery cue: {d['cue']}*", ""]
    script += [f"# Evidence appendix narration — slides 9–{len(p.slides)}", "",
               f"Use these sections during questions or a separate evidence review. They are additional narration, outside the main pitch’s 6:15 plan. For a full {len(p.slides)}-slide presentation, rehearse and measure the combined runtime.", ""]
    for j, slide in enumerate(list(p.slides)[8:], 9):
        title = slide.shapes[2].text
        narration = slide.notes_slide.notes_text_frame.text
        script += [f"## {j}. {title.replace(chr(10), ' ')}", "",
                   f"**Appendix A{j - 8:02d} · additional narration · suggested speaker {['A', 'A', 'B', 'C', 'B', 'C', 'D'][(j - 9) % 7]}**", "",
                   narration, "", "*Delivery cue: point to each evidence card as you explain it. Keep source definitions and limitations visible.*", ""]
    script += ["## Transition to the live dashboard", "",
               "We’ve shown the recommendation and the methods behind it. Now we’ll use the dashboard to trace those claims to the observations, compare country pathways, and examine the U.S. rebound that challenges our coal view. The detailed demonstration is in DASHBOARD_WALKTHROUGH.md.", ""]
    (OUT / "PRESENTATION_SCRIPT.md").write_text("\n".join(script))
    cues = ["# Speaker cue cards", "", "Use these after rehearsing the full script. Explain the argument; do not read the slide text aloud.", ""]
    for i, d in enumerate(story, 1):
        cues += [f"## {i} · {d['time']} · Speaker {d['speaker']}", "", d["cue"], "", f"Close on: {d['takeaway'] or ('Overweight clean energy; underweight coal with a U.S. thermal focus.')}", ""]
    (OUT / "SPEAKER_CUE_CARDS.md").write_text("\n".join(cues))
    guide = f"""# Presenter guide and rehearsal

The deck has **eight main slides and {appendix_count} evidence appendix slides**. Use the appendix for judging questions or a separate evidence review. Detailed country
research remains in the dashboard and COUNTRY_REVIEW.md. Present the investment
argument; use the repository for follow-up questions.

## Timing and handoffs

The eight-slide main script has **{words} spoken words** and a **6:15** plan. Appendix narration for slides 9–{len(p.slides)} is included separately in PRESENTATION_SCRIPT.md and adds time. The main pitch runs at about {words / 6.25:.0f}
words per minute. Reserve 10–15 seconds for speaker handoffs. Rehearse aloud and
measure the actual recording; keep it below the seven-minute cap.

| Speaker | Slides | Content |
|---|---|---|
| A | 1–2 | Recommendation and aggregate evidence |
| B | 3–4 | Market context and the 2025 signal |
| C | 5–6 | Counterargument and allocation |
| D | 7–8 | Reversal conditions and closing decision |

Adjust the split for your group. The script's final sentence on each topic
prepares the next; keep handoffs to a brief name or a pause. Do not add a new
introduction every time the speaker changes.

## Delivery

- Start with the call. Say “overweight clean energy” and “underweight coal” clearly.
- Explain each chart's meaning before listing numbers. Point to the line or bar.
- On slide 3, use three examples to establish geographic scope; avoid a country tour.
- On slide 4, distinguish the Ember electricity panel from EI coal generation.
- On slide 5, give the coal rebound a fair hearing. It limits conviction in the call.
- On slide 6, explain the investment judgment; avoid suggesting the data proves stock returns.
- On slide 7, name what would change your view. The thresholds are analyst rules.
- On slide 8, repeat both positions and the three-year horizon, then stop.

If you run long, remove supporting adjectives and secondary numbers. Keep the
recommendation, main evidence, 2025 coverage caveat, strongest counterargument
and reversal conditions. The full script is rehearsal material; cue cards are
for delivery. Neither establishes a measured recording duration.

## Likely questions and concise answers

**Why underweight coal after a rebound?** U.S. power coal consumption fell 14.4%
through 2024 and rose 11.3% in 2025. The rebound lowers conviction. Our call is
focused on domestic thermal exposure, with an explicit persistence trigger.

**Does clean growth prove attractive stock returns?** No. The industry preference
is a forward-looking judgment. Security selection still requires valuations,
project returns, contract economics and financing data.

**Are the 2025 numbers global?** The Ember panel contains 91 fixed countries and
93.5% of generation observed in the 2024 extract, not 93.5% of the world. EI's
world coal number uses its WLD row alone; country changes are shown separately.

**Why use a pandemic-affected 2020 baseline?** The same panel's 2021–2024 clean
growth was {m['clean_growth_2021_2024_pct']:.1f}% versus {m['fossil_growth_2021_2024_pct']:.1f}% for all fossil. The faster clean growth persists under that baseline;
these endpoint growth rates are not annual forecasts.

**Does the data identify why coal changed?** No. Generation changes and accounting
identities do not establish policy, weather, fuel-price or grid causality.

**What about exporters or metallurgical coal?** The U.S. thermal-power call cannot
be extended automatically to other business models. Production-versus-generation
divergence does not establish export flows.

**How certain is the third dataset's provenance?** The local file is hash-pinned.
The official EI catalogue and its current edition were checked, but the exact
original local download edition/date remain unverified. State that limitation;
do not substitute the catalogue access date for the original download date.

## Claims to avoid

- A durable global fossil peak has been proven.
- The matched Ember panel represents 93.5% of world electricity.
- Clean generation growth guarantees equity outperformance.
- Delivered fuel prices establish coal-producer profitability.
- Grid constraints or coal exports were measured by these datasets.

## Sources and tools

The two assignment extracts supply Ember electricity and EIA coal observations;
the local Energy Institute file supplies coal-specific country/world context.
Full lineage: tables/claim_evidence.csv, SOURCES.md and PROJECT_AUDIT.md.
Python/pandas generated the evidence; matplotlib generated charts; python-pptx
generated the editable deck; React/TypeScript/ECharts power the dashboard.

## Before recording

Enter actual names in submission.json, rebuild, and check the PDF. Record the
real group with readable slides and clear audio. Verify the actual runtime,
upload as Unlisted, and check signed-out playback. No recording or account upload
is performed by the deck generator.
"""
    (OUT / "PRESENTER_GUIDE.md").write_text(guide)
    (OUT / "REHEARSAL.md").write_text(guide)
    (OUT / "PITCH_SLIDE_MAP.md").write_text("# Slide evidence map\n\n" + "\n".join(
        f"- **Slide {i}: {d['title'].replace(chr(10), ' ')}** — {d['source']}" for i, d in enumerate(story, 1)) + "\n")
    with (OUT / "PITCH_SLIDE_MAP.md").open("a") as evidence_map:
        evidence_map.write("\n## Evidence appendix\n\n")
        for j, slide in enumerate(list(p.slides)[8:], 9):
            evidence_map.write(f"- **Slide {j} / A{j - 8:02d}: {slide.shapes[2].text}** — see slide source footer and PRESENTATION_SCRIPT.md.\n")
    print(f"Designed {len(p.slides)} slides; {words} spoken words; {elapsed}s main-pitch plan; {appendix_count} appendix slides")
    return manifest
