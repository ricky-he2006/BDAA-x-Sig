"""Research B - Global coal-market evolution, 2020-2025.

Covers: coal-fired generation, coal production, coal TES, major producers,
major generators, geographic concentration, production vs generation
divergence, and coexistence patterns (clean up + coal up / coal down).

Data notes:
* Coal measures are distinct (generation TWh vs production Mt vs TES EJ) and
  are reported side by side, never equated.
* EI latest-year (2025) figures are estimates.
* 'World proxy' = sum of all country-level entities (excludes ALL EI
  regional aggregates - O-*/T-*/WLD/ROW - to avoid double counting). It is
  a LOWER BOUND on world totals: the 'Other X' aggregates contain countries
  the Statistical Review does not list individually. The EI 'Total World'
  row is reported alongside as ground truth.
"""
import pandas as pd

from common import (load_country_year, load_eia_aggregates, md_table, save_csv,
                    write_md)
from src import config as C

# ---- EI country-level wide table --------------------------------------------
ei = pd.read_csv(C.CLEANED / C.CLEANED_EI)
cty = ei[~ei.is_aggregate]
wide = cty.pivot_table(index=["country", "iso3", "Year"], columns="variable",
                       values="value", aggfunc="first").reset_index()
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

sections = []

# ------------------------------------------------------------------ world proxy
w = wide[wide.Year.isin(YEARS)]
world = w.groupby("Year")[["electbyfuel_coal", "coalprod_mt", "coal_tes_ej"]].sum()
world["n_countries"] = w.groupby("Year")["iso3"].nunique()
world["coal_gen_share_pct"] = (
    world["electbyfuel_coal"] / w.groupby("Year")["electbyfuel_total"].sum() * 100)
save_csv(world.reset_index(), "b_world_coal_series.csv")
n24 = int(world.loc[2024, "n_countries"])
n25 = int(world.loc[2025, "n_countries"])
note = f"\n\nn_countries: 2024={n24}, 2025={n25}"
if n25 < n24:
    note += (f" - the 2025 panel covers only {n25} entities (2024: {n24}), "
             "so the 2025 total is NOT comparable to 2020-2024 totals.")
note += " 2025 figures are EI estimates."
sections.append(
    ("World-proxy coal series (sum of country-level entities; excludes ALL "
     "EI regional aggregates O-*/T-*/WLD/ROW to avoid double counting)",
     md_table(world.round(2)) + note))

# ground-truth check: EI's own 'Total World' row vs our country sum
truth = ei[(ei.iso3 == "WLD") & (ei.Year.isin(YEARS))] \
    .pivot_table(index="Year", columns="variable", values="value")
gt_rows = []
for var in ("coalprod_mt", "electbyfuel_coal", "coal_tes_ej"):
    if var not in truth.columns:
        continue
    for yr in YEARS:
        t = truth.loc[yr, var]
        s = world.loc[yr, var] if yr in world.index else float("nan")
        if pd.isna(t):
            continue
        gt_rows.append({"variable": var, "year": yr,
                        "ei_total_world": round(float(t), 1),
                        "sum_of_listed_countries": round(float(s), 1),
                        "gap_pct_of_truth": round((t - s) / t * 100, 2)})
gt = pd.DataFrame(gt_rows)
sections.append(("Ground-truth check: EI 'Total World' row vs sum of listed "
                 "countries (world proxy is a lower bound)",
                 md_table(gt) +
                 "\n\nThe gap is the 'Other X' residual: countries the "
                 "Statistical Review folds into regional 'Other' aggregates "
                 "rather than listing individually. It must not be closed by "
                 "adding those aggregates back (that would double-count the "
                 "countries they contain)."))

# ------------------------------------------------------------------ top producers
for yr in (2024, 2025):
    top = w[w.Year == yr].nlargest(12, "coalprod_mt")[
        ["country", "coalprod_mt", "coal_tes_ej"]].copy()
    tot = w[w.Year == yr].coalprod_mt.sum()
    top["share_pct"] = top.coalprod_mt / tot * 100
    sections.append((f"Top coal producers, {yr} (Mt; share of world proxy)",
                     md_table(top.round(1))))
    save_csv(top.reset_index(drop=True), f"b_top_producers_{yr}.csv")

topg = w[w.Year == 2024].nlargest(12, "electbyfuel_coal")[
    ["country", "electbyfuel_coal"]].copy()
topg["share_pct"] = topg.electbyfuel_coal / w[w.Year == 2024].electbyfuel_coal.sum() * 100
sections.append(("Top coal-fired generators, 2024 (TWh)", md_table(topg.round(1))))
save_csv(topg.reset_index(drop=True), "b_top_generators_2024.csv")

# concentration
for col, label in (("coalprod_mt", "production"),
                   ("electbyfuel_coal", "generation")):
    s24 = w[w.Year == 2024].nlargest(5, col)[col].sum()
    tot24 = w[w.Year == 2024][col].sum()
    sections.append((f"Concentration: top-5 {label} share 2024",
                     f"top-5 = {100 * s24 / tot24:.1f}% of world-proxy {label}"))

# ------------------------------------------------------------------ divergence
d = w[w.Year.isin([2020, 2024])].pivot(index="country", columns="Year",
                                       values=["coalprod_mt", "electbyfuel_coal"])
d.columns = [f"{a}_{b}" for a, b in d.columns]
piv = d.dropna(subset=["coalprod_mt_2020", "coalprod_mt_2024",
                       "electbyfuel_coal_2020", "electbyfuel_coal_2024"]).copy()
piv["prod_chg_pct"] = piv.coalprod_mt_2024 / piv.coalprod_mt_2020 - 1
piv["gen_chg_pct"] = piv.electbyfuel_coal_2024 / piv.electbyfuel_coal_2020 - 1
save_csv(piv.reset_index(), "b_prod_vs_gen_change_2020_2024.csv")
prod_up_gen_down = piv[(piv.prod_chg_pct > 0.05) & (piv.gen_chg_pct < -0.05)] \
    .reset_index()[["country", "coalprod_mt_2020", "coalprod_mt_2024",
                    "prod_chg_pct", "electbyfuel_coal_2020",
                    "electbyfuel_coal_2024", "gen_chg_pct"]]
prod_up_gen_down = prod_up_gen_down.sort_values("prod_chg_pct", ascending=False)
sections.append(("Production up while domestic coal generation down, 2020->2024 "
                 "(exporters / non-power demand)", md_table(prod_up_gen_down.round(2))))
gen_up_prod_down = piv[(piv.gen_chg_pct > 0.05) & (piv.prod_chg_pct < -0.05)] \
    .reset_index()[["country", "prod_chg_pct", "gen_chg_pct",
                    "coalprod_mt_2020", "coalprod_mt_2024"]]
sections.append(("Generation up while production down, 2020->2024 (importers)",
                 md_table(gen_up_prod_down.sort_values("gen_chg_pct",
                                                       ascending=False).round(2))))

# ------------------------------------------------------------------ coexistence
cy = load_country_year()
cm = cy[cy.year.isin([2020, 2024])].pivot_table(
    index="iso3", columns="year",
    values=["clean_generation_twh", "ei_coal_generation_twh"],
    aggfunc="first").reset_index()
# pivot column order is lexicographic by value name, then year
cm.columns = ["iso3", "clean_2020", "clean_2024", "coal_2020", "coal_2024"]
cm = cm.merge(cy.dropna(subset=["country"]).drop_duplicates("iso3")
              [["iso3", "country"]], on="iso3")
both = cm.dropna(subset=["clean_2020", "coal_2020", "clean_2024", "coal_2024"]) \
    .copy()
both = both[(both.coal_2020 > 50) | (both.clean_2020 > 50)]  # material size
# change defined only on a non-zero base; zero->x is not a % change
both["clean_chg_pct"] = (both.clean_2024 / both.clean_2020 - 1) \
    .where(both.clean_2020 > 0)
both["coal_chg_pct"] = (both.coal_2024 / both.coal_2020 - 1) \
    .where(both.coal_2020 > 0)
both_up = both[(both.clean_chg_pct > 0.05) & (both.coal_chg_pct > 0.05)]
both_down_clean_up = both[(both.clean_chg_pct > 0.05) & (both.coal_chg_pct < -0.05)]
save_csv(both.sort_values("coal_2024", ascending=False),
         "b_coexistence_2020_2024.csv")
n_zero20 = int(((both.coal_2020 == 0) & (both.coal_2024 > 0)).sum())
sections.append(("Countries where BOTH clean and coal-fired generation grew, "
                 "2020->2024 (TWh; >5% change on a non-zero base, "
                 "material sizes only)",
                 md_table(both_up[["country", "iso3", "clean_2020", "clean_2024",
                                   "coal_2020", "coal_2024",
                                   "clean_chg_pct", "coal_chg_pct"]]
                          .sort_values("coal_2024", ascending=False)
                          .round(2))))
sections.append(("Countries where clean grew but coal-fired generation fell "
                 "2020->2024",
                 md_table(both_down_clean_up[["country", "iso3", "clean_chg_pct",
                                              "coal_2020", "coal_2024",
                                              "coal_chg_pct"]]
                          .sort_values("coal_2020", ascending=False)
                          .round(2))))
if n_zero20:
    sections.append(("Countries with no coal generation in 2020 that report some "
                     "in 2024 (change rate undefined, listed separately)",
                     md_table(both[(both.coal_2020 == 0) & (both.coal_2024 > 0)]
                              [["country", "iso3", "coal_2024", "clean_2024"]]
                              .sort_values("coal_2024", ascending=False).round(1))))

write_md("research_b_coal_market.md", sections)
print("research B complete")
