"""Research D - Cross-country comparison of major markets, 2020-2025.

US, China, India, Indonesia, Germany (+ Japan, Australia, Russia as context)
across demand, clean share, renewables, coal generation/production/TES and
carbon intensity. Contrasting transition pathways are classified from the
2020->2024 changes on a consistent basis.
"""
import pandas as pd

from common import load_country_year, md_table, save_csv, write_md

cy = load_country_year()
MARKETS = {
    "USA": "United States", "CHN": "China", "IND": "India",
    "IDN": "Indonesia", "DEU": "Germany", "JPN": "Japan",
    "AUS": "Australia", "RUS": "Russia",
}
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
sections = []

rows = []
for iso, name in MARKETS.items():
    d = cy[(cy.iso3 == iso) & cy.year.isin(YEARS)]
    for _, r in d.iterrows():
        rows.append({
            "market": name, "iso3": iso, "year": int(r.year),
            "demand_twh": r.demand_twh,
            "clean_share_pct": r.clean_share_pct,
            "renewable_twh": r.renewable_generation_twh,
            "wind_solar_twh": r.wind_solar_generation_twh,
            "coal_generation_twh": r.ei_coal_generation_twh,
            "coal_share_pct": r.coal_share_of_generation_pct,
            "coal_production_mt": r.ei_coal_production_mt,
            "coal_tes_ej": r.ei_coal_tes_ej,
            "carbon_intensity_gco2e_kwh": r.carbon_intensity_gco2e_kwh,
            "co2_combust_mtco2": r.ei_co2_combust_mtco2,
            "emission": "2025 preliminary" if r.year == 2025 else "",
        })
mkt = pd.DataFrame(rows)
save_csv(mkt, "d_market_panel.csv")

for name in MARKETS.values():
    sub = mkt[mkt.market == name]
    if sub.empty:
        sections.append((f"{name}: NO DATA", "market not present in joined table"))
        continue
    sub = sub.sort_values("year")
    sections.append((name, md_table(sub.round(1))))

# pathway classification 2020 -> 2024 (consistent window; 2025 is preliminary)
piv = mkt[mkt.year.isin([2020, 2024])].pivot_table(
    index="market", columns="year",
    values=["clean_share_pct", "coal_generation_twh", "demand_twh"],
    aggfunc="first").reset_index()
# pivot column order is lexicographic: (value, year)
piv.columns = ["market", "cshare_20", "cshare_24", "coal_20", "coal_24",
               "dem_20", "dem_24"]
piv["coal_chg_pct"] = (piv.coal_24 / piv.coal_20 - 1).where(piv.coal_20 > 0)
piv["demand_chg_pct"] = (piv.dem_24 / piv.dem_20 - 1).where(piv.dem_20 > 0)
piv["clean_share_chg_pp"] = piv.cshare_24 - piv.cshare_20

def pathway(r):
    # material coal base in 2020 and a complete change measure, else the
    # classification is not defensible
    if pd.isna(r.coal_chg_pct) or pd.isna(r.clean_share_chg_pp) \
            or r.coal_20 <= 20:
        return "insufficient_data"
    if r.coal_chg_pct < -0.10 and r.clean_share_chg_pp > 5:
        return "coal_falling_clean_rising"
    if r.coal_chg_pct > 0.05 and r.clean_share_chg_pp > 5:
        return "coexistence_both_growing"
    if r.coal_chg_pct < -0.10:
        return "coal_falling"
    if r.coal_chg_pct > 0.05:
        return "coal_growing"
    return "mixed"

piv["pathway"] = piv.apply(pathway, axis=1)
save_csv(piv, "d_pathways_2020_2024.csv")
sections.append(("Transition pathways, 2020->2024", md_table(piv.round(2))))

# global context: how many countries in each pathway (all joined countries)
# column order from pivot_table: value-name-lexicographic, then year
allp = cy[cy.year.isin([2020, 2024])].pivot_table(
    index="iso3", columns="year",
    values=["clean_generation_twh", "ei_coal_generation_twh", "demand_twh"],
    aggfunc="first").reset_index()
allp.columns = ["iso3", "clean_20", "clean_24", "dem_20", "dem_24",
                "coal_20", "coal_24"]
n_complete = len(allp)
allp = allp.dropna()
n_both_years = len(allp)
# defensible classification needs a material coal AND clean base in BOTH years
mat = allp[(allp.coal_20 > 20) & (allp.coal_24 > 20)
           & (allp.clean_20 > 20) & (allp.clean_24 > 20)]
allp = mat.copy()
allp["coal_chg"] = allp.coal_24 / allp.coal_20 - 1
allp["clean_chg"] = allp.clean_24 / allp.clean_20 - 1
allp["pathway"] = allp.apply(lambda r: (
    "coexistence" if (r.coal_chg > 0.05 and r.clean_chg > 0.05) else
    "transition" if (r.clean_chg > 0.05 and r.coal_chg < -0.05) else
    "coal_decline" if r.coal_chg < -0.05 else
    "coal_growth" if r.coal_chg > 0.05 else "mixed"), axis=1)
save_csv(allp, "d_allcountry_pathway_2020_2024.csv")
pc = allp.pathway.value_counts().to_frame("n_countries")
pc.index.name = "pathway"
tot = pc.n_countries.sum()
pc["share_pct"] = pc.n_countries / tot * 100
sections.append(("All-country pathway mix, 2020->2024 (material countries only)",
                 md_table(pc.round(1)) +
                 f"\n\nclassification thresholds: >5% change = material. "
                 f"Population: {n_complete} iso3s have any 2020/2024 rows, "
                 f"{n_both_years} have all six values; "
                 f"{len(allp)} retain a material coal AND clean base in both "
                 "years (others excluded from the mix, not silently dropped - "
                 "see d_allcountry_pathway_2020_2024.csv for the included set)."))

write_md("research_d_cross_country.md", sections)
print("research D complete")
