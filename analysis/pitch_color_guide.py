"""Explain the dashboard's implemented map encodings and screening workflow."""
from pptx.dml.color import RGBColor


def add_color_guide(p):
    from analysis.pitch_design import text, rect, label, NAVY, PAPER, WHITE, BLUE, MUTED, GRID
    specs = [
        ("WORLD · BLUE FILTERS", "Blue fill means a higher selected value.", [
            ("Clean electricity share · %", "Darker blue = higher clean share", "Open clean/fossil output and demand; check growth and economics."),
            ("Renewable generation · TWh", "Darker blue = more renewable output", "Check output growth and scale, then project valuation."),
            ("Electricity demand · TWh", "Darker blue = more electricity demand", "Compare demand additions with clean and fossil additions."),
            ("Carbon intensity · gCO2e/kWh", "Darker blue = higher emissions per kWh", "Inspect mix and emissions. Darker here = more carbon-intensive.")],
         "Dark blue + red outline can mean a high clean share AND rising coal generation. Inspect both histories.",
         "The blue color is a magnitude scale, not an investment rating. Under clean share, darker blue means a higher percentage of clean electricity. Under renewable generation or demand, it means more TWh, which also reflects market size. Under carbon intensity, darker blue instead means higher emissions per kilowatt-hour. Start by reading the selected filter and units. To investigate clean-generation exposure, open the country’s clean, fossil and demand histories, then examine relevant company or project economics. A dark-blue clean-share fill together with a red outline can occur because a high clean share and rising annual coal generation can coexist. Neither color establishes a buy recommendation."),
        ("WORLD · ORANGE FILTERS", "Orange fill shows coal scale or dependence.", [
            ("Coal-fired generation · TWh", "Darker orange = more coal electricity", "Open coal and demand histories; distinguish size from growth."),
            ("Coal share of generation · %", "Darker orange = greater coal dependence", "Compare coal TWh and clean share; dependence differs from scale."),
            ("Coal production · Mt", "Darker orange = more coal produced", "Check producer exposure; exports require trade evidence."),
            ("Coal energy supply (TES) · EJ", "Darker orange = more coal energy supply", "Inspect energy-system exposure, including non-power uses.")],
         "Red outline = coal generation rose vs prior year; blue = fell. Direction prompts research, not a long/short trade.",
         "All four orange filters show levels in the selected year. Generation measures coal electricity in TWh; share measures coal dependence as a percentage; production measures coal mined in million metric tonnes; total energy supply measures energy in exajoules. The world outline remains annual coal-generation change in TWh under every filter. A red outline does not mean coal producers are profitable or undervalued, and a blue outline does not establish an attractive short. Check the size and persistence of the change, the company’s domestic versus export exposure, realized prices, costs, contracts and valuation. Production-versus-generation divergence alone does not measure exports. Neutral outlines can indicate little or no change; missing comparisons must be checked in the tooltip."),
        ("UNITED STATES · COAL & CLEAN", "U.S. coal & clean: national first, then states.", [
            ("Generation · TWh", "Blue = clean; red = coal", "Compare national output histories from Ember and EI."),
            ("Share · %", "Each source’s reported generation share", "Distinguish electricity mix from absolute output."),
            ("Priority coal-demand markets", "EIA state power consumption, sectors 1+2+3", "Rank market size and annual growth; open a state history."),
            ("Optional state map & Map key", "Orange fill; red/blue consumption change", "Inspect coal customers. No state clean data is inferred.")],
         "2025: Texas, Missouri and Indiana lead reported power coal demand and all grew. Prioritize supplier exposure research.",
         "The United States now starts with the same national coal-versus-clean comparison as the globe. Choose generation in TWh or generation share in percent. Clean electricity is blue and comes from Ember; coal electricity is red and comes from EI. Next, the state table ranks reported power-sector coal consumption and shows annual change. In the supplied 2025 data, Texas, Missouri and Indiana are the largest markets and all three grew. Within a selective coal allocation, prioritize understanding suppliers serving those markets, while checking persistence of the demand trend. The optional map uses orange fill for consumption levels and red or blue outlines for annual consumption increases or decreases. Expand Map key for scales and missingness. State data covers power coal consumption only; no state clean-generation values are invented. States identify coal customers, not mines, supplier contracts or investment returns. The separate national EIA consumption check uses sector 98 and remains available in an optional disclosure."),
    ]
    for k, (section, title, rows, interpretation, narration) in enumerate(specs):
        s = p.slides.add_slide(p.slide_layouts[6])
        s.background.fill.solid(); s.background.fill.fore_color.rgb = RGBColor.from_string(PAPER)
        label(s, "DASHBOARD READING GUIDE · " + section, .6, .32, 11, BLUE)
        label(s, f"A{len(p.slides)-8:02d}", 12, .32, .7)
        text(s, title, .6, .9, 12.1, .85, 31, NAVY, True)
        ramp = ["CDE2FB", "5598E7", "0D366B"] if k == 0 else ["FDEEE2", "C76A18", "832E07"]
        for j, color in enumerate(ramp): rect(s, .65 + .36*j, 1.91, .3, .2, color)
        text(s, "State map: low → high power coal consumption" if k == 2 else "Low → high selected value · read the filter and units first", 1.9, 1.86, 10.6, .28, 15, MUTED)
        cols = [("FILTER", .82, 3.1), ("WHAT THE COLOR / SCOPE MEANS", 4.05, 4.0), ("WHAT TO INSPECT NEXT", 8.25, 4.15)]
        for heading, x, w in cols: label(s, heading, x, 2.32, w, BLUE)
        row_h = .83 if len(rows) <= 4 else .47
        for j, row in enumerate(rows):
            y = 2.74 + j*row_h
            rect(s, .6, y, 12.13, row_h-.06, WHITE, True)
            for i, (content, (_,x,w)) in enumerate(zip(row, cols)):
                text(s, content, x, y+.08, w, row_h-.12, 15.5 if len(rows) <= 4 else 13.5, NAVY if i==0 else MUTED, i==0)
        text(s, interpretation, .7, 6.17, 12, .4, 15, BLUE, True)
        text(s, "Missing fill means unreported, not zero. Compare tooltip values: scales change with year and filter.", .7, 6.67, 12, .23, 11, MUTED)
        rect(s,.6,6.98,12.13,.012,GRID)
        text(s, "Source: dashboard/src/data/types.ts; components/Legend.tsx; components/USMap.tsx; viz/layerValue.ts", .65,7.11,12,.23,9,MUTED)
        s.notes_slide.notes_text_frame.text = narration
    return len(specs)
