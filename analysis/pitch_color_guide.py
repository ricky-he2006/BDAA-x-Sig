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
        ("UNITED STATES · SECTOR FILTERS", "Select the coal user, then inspect its history.", [
            ("All sectors", "Reported base sectors 1+2+3+8+9+10", "Overview of reported consumption."),
            ("Electric power", "Base sectors 1+2+3", "Start here for the thermal-power thesis."),
            ("Electric utility", "Sector 1", "Inspect utility consumption."),
            ("IPP non-CHP / IPP CHP", "Sectors 2 / 3, separately", "Compare independent power producers."),
            ("Commercial & inst.", "Sector 8", "Inspect commercial/institutional use."),
            ("Coke plants (steelmaking)", "Sector 9", "Separate steelmaking from power."),
            ("Other industrial", "Sector 10", "Inspect other industrial demand.")],
         "Orange fill = consumption level. Red/blue outline = annual consumption rise/fall in the selected sector scope.",
         "In the U.S. map the sector filter changes which coal users are included. Darker orange means more coal consumed in short tons. Red outlines mean consumption rose from the prior year; blue outlines mean it fell, for the selected scope. This differs from the world map, whose outlines measure coal generation in TWh. Start with Electric power for the domestic thermal thesis, then inspect states and their sector histories. Electric power includes utilities and two independent-power-producer categories. Coke plants are a steelmaking exposure that our thermal-power underweight does not automatically cover. The national chart separately uses EIA sector 98; do not add it to the base sectors. States identify consumption locations, not mines or producer revenue exposure. The large U.S. legend is hidden; read the scope note and hover values. Zoom in for smaller states, then reset the map."),
    ]
    for k, (section, title, rows, interpretation, narration) in enumerate(specs):
        s = p.slides.add_slide(p.slide_layouts[6])
        s.background.fill.solid(); s.background.fill.fore_color.rgb = RGBColor.from_string(PAPER)
        label(s, "DASHBOARD READING GUIDE · " + section, .6, .32, 11, BLUE)
        label(s, f"A{len(p.slides)-8:02d}", 12, .32, .7)
        text(s, title, .6, .9, 12.1, .85, 31, NAVY, True)
        ramp = ["CDE2FB", "5598E7", "0D366B"] if k == 0 else ["FDEEE2", "C76A18", "832E07"]
        for j, color in enumerate(ramp): rect(s, .65 + .36*j, 1.91, .3, .2, color)
        text(s, "Low → high selected value · read the filter and units first", 1.9, 1.86, 10.6, .28, 15, MUTED)
        cols = [("FILTER", .82, 3.1), ("WHAT THE COLOR / SCOPE MEANS", 4.05, 4.0), ("WHAT TO INSPECT NEXT", 8.25, 4.15)]
        for heading, x, w in cols: label(s, heading, x, 2.32, w, BLUE)
        row_h = .83 if k < 2 else .47
        for j, row in enumerate(rows):
            y = 2.74 + j*row_h
            rect(s, .6, y, 12.13, row_h-.06, WHITE, True)
            for i, (content, (_,x,w)) in enumerate(zip(row, cols)):
                text(s, content, x, y+.08, w, row_h-.12, 15.5 if k < 2 else 13.5, NAVY if i==0 else MUTED, i==0)
        text(s, interpretation, .7, 6.17, 12, .4, 15, BLUE, True)
        text(s, "Missing fill means unreported, not zero. Compare tooltip values: scales change with year and filter.", .7, 6.67, 12, .23, 11, MUTED)
        rect(s,.6,6.98,12.13,.012,GRID)
        text(s, "Source: dashboard/src/data/types.ts; components/Legend.tsx; components/USMap.tsx; viz/layerValue.ts", .65,7.11,12,.23,9,MUTED)
        s.notes_slide.notes_text_frame.text = narration
    return len(specs)
