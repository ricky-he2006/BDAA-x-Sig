"""Research A - Global electricity transition, 2020-2025.

Covers: demand growth, clean vs fossil growth, renewable/wind-solar expansion,
clean growth vs demand growth, carbon intensity, country/region differences.

Coverage handled explicitly (never forced to match):
* Ember reports full panels for 2020-2024 and a PARTIAL panel for 2025
  (only a subset of countries updated). Full-panel totals therefore cover a
  different set of countries in 2025; that row is labelled partial and
  carries its own country count.
* For trend comparisons a matched sample (countries present in EVERY year
  2020-2025) is computed so every row is on an identical country set.
"""
import pandas as pd

from common import load_country_year, md_table, save_csv, write_md

CY = load_country_year()
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

# matched sample: present in all six years -> every row below is comparable
counts = CY.groupby("iso3")["year"].nunique()
matched_iso = set(counts[counts == len(YEARS)].index)
cy_m = CY[CY.iso3.isin(matched_iso)]

sections = []

# ---------------------------------------------------------------- full panel
def totals(d: pd.DataFrame) -> pd.DataFrame:
    g = d.groupby("year").agg(
        n_countries=("iso3", "nunique"),
        demand_twh=("demand_twh", "sum"),
        generation_twh=("generation_twh", "sum"),
        clean_generation_twh=("clean_generation_twh", "sum"),
        fossil_generation_twh=("fossil_generation_twh", "sum"),
        renewable_generation_twh=("renewable_generation_twh", "sum"),
        wind_solar_generation_twh=("wind_solar_generation_twh", "sum"),
        power_emissions_mtco2e=("power_emissions_mtco2e", "sum"))
    g["clean_share_pct"] = g.clean_generation_twh / g.generation_twh * 100
    # MtCO2e / TWh -> gCO2e/kWh: 1e12 g / 1e9 kWh = 1e3 per unit ratio
    g["carbon_intensity_gco2e_kwh"] = g.power_emissions_mtco2e / g.generation_twh * 1e3
    return g

full = totals(CY)
save_csv(full.reset_index(), "a_global_series_full_panel.csv")
sections.append(
    ("Global series - full panel (each year sums the countries reported that year)",
     md_table(full.reset_index().round(2)) +
     "\n\n2025 row = PARTIAL panel: Ember 2025 covers only "
     f"{int(full.loc[2025, 'n_countries'])} countries, so it is NOT comparable "
     "to the 2020-2024 totals above. Use the matched sample below for trends."))

# ---------------------------------------------------------------- matched sample
gm = totals(cy_m)
save_csv(gm.reset_index(), "a_global_series_matched.csv")
sections.append(("Global series - matched sample (present in all years 2020-2025)",
                 md_table(gm.round(2)) +
                 f"\n\nMatched sample = {len(matched_iso)} countries; every row "
                 "covers the identical country set, so changes are apples-to-apples."))

# growth rates on matched sample
gm_yoy = gm[["demand_twh", "generation_twh", "clean_generation_twh",
             "fossil_generation_twh", "renewable_generation_twh",
             "wind_solar_generation_twh"]].pct_change() * 100
gm_yoy.index.name = "year"
save_csv(gm_yoy, "a_global_yoy_matched.csv")
sections.append(("Year-over-year % (matched sample)", md_table(gm_yoy.round(2))))

# clean growth coverage of demand growth (only years with positive demand growth)
dd = gm["demand_twh"].diff()
gm["clean_demand_coverage_pct"] = gm["clean_generation_twh"].diff() / dd.where(dd > 0) * 100
gm_r = gm.reset_index()
sections.append(("Clean growth as % of demand growth (matched; blank = demand fell)",
                 md_table(gm_r[["year", "clean_demand_coverage_pct"]].round(1))))

# ---------------------------------------------------------------- by continent
cc = cy_m[cy_m.year.isin(YEARS)].groupby(["continent", "year"]).agg(
    demand=("demand_twh", "sum"), clean=("clean_generation_twh", "sum"),
    fossil=("fossil_generation_twh", "sum"),
    ws=("wind_solar_generation_twh", "sum"),
    emissions=("power_emissions_mtco2e", "sum"),
    generation=("generation_twh", "sum")).reset_index()
cc["clean_share_pct"] = cc.clean / cc.generation * 100
save_csv(cc, "a_continent_series.csv")
piv = cc.pivot(index="year", columns="continent", values="clean_share_pct")
sections.append(("Clean share by continent, % (matched sample)",
                 md_table(piv.round(1))))

# top movers
top = cy_m[cy_m.year == 2024].nlargest(15, "clean_generation_twh")[
    ["country", "clean_generation_twh", "demand_twh", "clean_share_pct"]]
sections.append(("Largest clean generators, 2024 (matched sample)", md_table(top.round(1))))
ws24 = cy_m[cy_m.year == 2024].nlargest(15, "wind_solar_generation_twh")[
    ["country", "wind_solar_generation_twh"]]
sections.append(("Largest wind+solar generators, 2024", md_table(ws24.round(1))))

# fossil decline? (matched: present in both 2020 and 2024)
name_by_iso = cy_m.drop_duplicates("iso3").set_index("iso3")["country"]
fossil_delta = (cy_m[cy_m.year == 2024].set_index("iso3")["fossil_generation_twh"]
                - cy_m[cy_m.year == 2020].set_index("iso3")["fossil_generation_twh"])
fossil_delta = fossil_delta[fossil_delta.notna()]

def _labeled(s: pd.Series) -> pd.DataFrame:
    out = s.rename("delta_twh").reset_index()
    out["country"] = out.iso3.map(name_by_iso)
    return out[["country", "iso3", "delta_twh"]]

decliners = _labeled(fossil_delta.nsmallest(15))
growers = _labeled(fossil_delta.nlargest(15))
save_csv(decliners, "a_fossil_delta_2020_2024_decliners.csv")
save_csv(growers, "a_fossil_delta_2020_2024_growers.csv")
sections.append(("Fossil generation change 2020->2024, TWh: biggest declines",
                 md_table(decliners.round(1))))
sections.append(("Fossil generation change 2020->2024, TWh: biggest increases",
                 md_table(growers.round(1))))

# carbon intensity
sections.append(("Global carbon intensity (matched sample)",
                 md_table(gm_r[["year", "carbon_intensity_gco2e_kwh"]].round(1))))

write_md("research_a_global_electricity.md", sections)
print("research A complete")
