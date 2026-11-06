"""Research C - U.S. coal economics, 2020-2025.

Covers: national electric-power consumption, sector mix, state detail,
receipts vs consumption, stocks/inventory ratios, delivered prices,
quality (heat/sulfur/ash), the 2025 rebound, geographic concentration.

Data rules: state-level figures use BASE sectors only (1,2,3,8,9,10);
sector 98 (Electric Power) is used at the US-total/region level from the
aggregate table - never summed with state rows.
"""
import pandas as pd

from common import (load_eia_aggregates, load_us_state, md_table, save_csv,
                    write_md)

us_state = load_us_state()
agg = load_eia_aggregates()
YEARS = list(range(2020, 2026))
sections = []

# ---------------------------------------------------------------- national
us98 = agg[(agg.location_code == "US") & (agg.sector_code == 98)]
nat = us98[["year", "coal_consumption_short_tons", "coal_receipts_short_tons",
            "delivered_price_usd_per_short_ton"]].copy()
nat["consumption_mt"] = nat.coal_consumption_short_tons * 0.90718474 / 1_000_000
nat["yoy_pct"] = nat.coal_consumption_short_tons.pct_change() * 100
save_csv(nat, "c_us_national_sector98.csv")
sections.append(("US electric-power coal, sector 98 (EIA US-total rows)",
                 md_table(nat.round(2))))

# sector mix (base sectors, state-level sum = non-overlapping)
base = us_state[us_state.sector_code.isin([1, 2, 3, 8, 9, 10])]
mix = base.groupby("year")["coal_consumption_short_tons"].sum().to_frame() \
    .rename(columns={"coal_consumption_short_tons": "all_base"})
for s, nm in ((1, "electric_utility"), (2, "ipp_nonchp"), (3, "ipp_chp"),
              (8, "commercial"), (9, "coke"), (10, "other_industrial")):
    mix[nm] = base[base.sector_code == s].groupby("year")[
        "coal_consumption_short_tons"].sum()
save_csv(mix, "c_us_sector_mix.csv")
sections.append(("US sector mix, short tons (base sectors summed over states)",
                 md_table(mix.round(0))))

# ---------------------------------------------------------------- state level
# A state-year with no base-sector rows is "not reported", NOT zero -
# blanks stay blank in every table below.
piv = us_state.pivot_table(index="state_code", columns="year",
                           values="coal_consumption_short_tons",
                           aggfunc="sum")
piv["chg_20_24_pct"] = (piv[2024] / piv[2020] - 1).where(piv[2020] > 0)
piv["chg_24_25_pct"] = (piv[2025] / piv[2024] - 1).where(piv[2024] > 0)
save_csv(piv, "c_state_consumption_by_year.csv")
top = piv.nlargest(12, 2024)[[2020, 2021, 2022, 2023, 2024, 2025,
                              "chg_20_24_pct", "chg_24_25_pct"]]
sections.append(("Top states by base-sector coal consumption, short tons",
                 md_table(top.round(0))))

bigger = piv.nlargest(10, 2020)[[2020, 2024, 2025, "chg_20_24_pct"]]
sections.append(("States that were top-10 in 2020, where they stand now",
                 md_table(bigger.round(0))))

conc = (piv[2024].nlargest(5).sum() / piv[2024].sum() * 100)
sections.append(("Concentration 2024",
                 f"top-5 states = {conc:.1f}% of reported state-level base-sector "
                 "consumption (states with no 2024 rows are out of the denominator)"))

# 2025 rebound decomposition (states with a reported value in BOTH years;
# missing years are excluded, not treated as zero)
rb = piv[[2024, 2025]].copy()
rb["delta"] = rb[2025] - rb[2024]
rb = rb[rb.delta.notna() & (rb.delta != 0)].sort_values("delta", ascending=False)
total_delta = rb.delta.sum()
rb["share_of_change_pct"] = rb.delta / total_delta * 100
sections.append(("2024->2025 change by state, short tons (who drove the rebound; "
                 "share is of the measurable total change)",
                 md_table(rb.round(0))))

# sector decomposition of 2025 change at US level
us94 = agg[(agg.location_code == "US") & (agg.sector_code == 94)]
us94["yoy_pct"] = us94.coal_consumption_short_tons.pct_change() * 100
ind = base[base.sector_code.isin([8, 9, 10])].groupby("year")[
    "coal_consumption_short_tons"].sum()
ind = ind.to_frame("industrial_base")
ind["yoy_pct"] = ind.industrial_base.pct_change() * 100
sections.append(("2025 rebound - sector view (US level)",
                 "Sector 98 (electric power) vs sector 94 (IPP) vs industrial base:\n\n"
                 + md_table(us98[["year", "coal_consumption_short_tons"]].round(0))
                 + "\n\n" + md_table(us94[["year", "coal_consumption_short_tons"]].round(0))
                 + "\n\n" + md_table(ind.round(0))))

# ---------------------------------------------------------------- receipts/stocks/price
rcv = base.groupby("year")[["coal_consumption_short_tons",
                            "coal_receipts_short_tons"]].sum()
rcv["receipts_minus_consumption"] = rcv.coal_receipts_short_tons - rcv.coal_consumption_short_tons
sections.append(("US receipts vs consumption (base sectors, states)",
                 md_table(rcv.round(0))))

st = base[base.sector_code.isin([1, 2, 3])]
stk = st[st.coal_stocks_short_tons.notna()].groupby("year")[
    "coal_stocks_short_tons"].sum().to_frame("stocks_short_tons")
cons98 = us98.set_index("year").coal_consumption_short_tons
stk["inventory_to_annual_consumption"] = stk.stocks_short_tons / cons98
sections.append(("Electric-power stocks vs consumption (states with reported stocks)",
                 md_table(stk.join(cons98.to_frame("consumption_98"))
                          .round(0))))

# delivered price, US-level
us_price = agg[(agg.location_code == "US")].pivot(
    index="year", columns="sector_code",
    values="delivered_price_usd_per_short_ton")
sections.append(("US delivered coal price, $/short ton (by sector)",
                 md_table(us_price.round(2))))

# quality (state level, industrial sectors = Btu/lb native; power = assumed)
q = base[base.sector_code.isin([1, 8, 9, 10])]
q24 = q[q.year == 2024]
by_state_heat = q24.groupby("state_code").apply(
    lambda g: g.heat_content_btu_per_lb.dropna().median()).rename("med_heat_btu_lb")
by_state_sulf = q24[q24.sulfur_content_pct.notna()].groupby("state_code")[
    "sulfur_content_pct"].median().rename("med_sulfur_pct")
by_state_ash = q24[q24.ash_content_pct.notna()].groupby("state_code")[
    "ash_content_pct"].median().rename("med_ash_pct")
qual = pd.concat([by_state_heat, by_state_sulf, by_state_ash], axis=1).dropna()
big_states = set(q24[q24.coal_consumption_short_tons > 1e6].state_code)
qual = qual[qual.index.isin(big_states)]
sections.append(("State coal quality, 2024 (median of base-sector rows)",
                 md_table(qual.round(2))))

write_md("research_c_us_coal.md", sections)
print("research C complete")
