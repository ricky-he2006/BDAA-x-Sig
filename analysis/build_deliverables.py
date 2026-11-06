"""Build audited evidence, country reviews, figures and the submission brief.

Run from the repository root: python -m analysis.build_deliverables
No network calls. Input snapshots stay unchanged. PPTX generation is separate.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
FIG = OUT / "figures"
TABLES = OUT / "tables"
COUNTRIES = OUT / "countries"
YEARS = list(range(2020, 2026))
CORE = ["USA", "CHN", "IND", "IDN", "DEU", "JPN", "AUS", "RUS"]
BLUE, ORANGE, AQUA, INK = "#2864B4", "#C76A18", "#168779", "#172C43"
SPECIAL = {
    "USA": ("Coal declined through 2024, rebounded in 2025; all-fossil generation rose over 2020–2024.",
            "Separate the coal and gas trajectories; pair the EIA national volume and price panels. Do not infer mine margins from delivered prices."),
    "CHN": ("Clean and coal generation both expanded through 2024; 2025 is a separate watch point.",
            "Show absolute TWh additions alongside shares. A clean-share gain does not establish falling coal volumes."),
    "IND": ("Demand growth accompanied increases in both clean and coal generation through 2024.",
            "Compare demand and clean additions in TWh; monitor whether the latest coal decline persists. Do not label percentage-growth comparisons as absolute additions."),
    "IDN": ("Coal and clean generation grew together through 2024.",
            "Index coal production and coal generation separately. Their divergence does not identify export flows. Ember has no 2025 row here; do not backfill it."),
    "DEU": ("Coal, clean generation and demand all declined over 2020–2024.",
            "Prioritize the demand identity and net-import panel. Clean-share improvement alone cannot establish rising clean output or domestic coal replacement."),
    "JPN": ("Clean generation grew while coal and total fossil generation declined through 2024.",
            "Compare coal and gas on an EI-only basis; show clean-generation growth against nearly flat demand. Technology attribution requires a separate fuel-level check."),
    "AUS": ("Clean generation grew and coal generation fell through 2024.",
            "Contrast domestic generation with production indices. Domestic coal decline cannot establish export-producer decline."),
    "RUS": ("Coal generation grew while clean generation was nearly flat through 2024.",
            "Show demand additions and EI coal/gas changes; do not treat a global clean-energy trajectory as uniform across markets."),
    "KOR": ("Clean generation rose while coal generation fell through 2024.",
            "Compare EI coal and gas changes and Ember clean additions; determine whether the clean increase exceeds additional demand before claiming substitution."),
    "MYS": ("Clean generation rose while coal generation was roughly flat through 2024.",
            "Show absolute coal output beside its share and demand growth. A flat coal series is materially different from a large decline."),
    "POL": ("Clean generation grew rapidly from a smaller base while coal generation fell through 2024.",
            "Pair percentage growth with TWh additions to avoid exaggerating a low-base effect; show remaining coal generation alongside the cleaner mix."),
    "THA": ("Clean generation increased while coal generation declined through 2024.",
            "Prioritize coal versus gas and electricity trade; coal decline alone does not establish falling total fossil dependence."),
    "TUR": ("Clean generation and coal generation both increased through 2024.",
            "Compare demand additions, clean additions and coal additions separately. Add production indices only as a different measure, not an export balance."),
    "TWN": ("Both clean and coal generation declined through 2024.",
            "Show gas and demand alongside the clean decline; do not label this pathway as clean-output-led coal replacement."),
    "VNM": ("Clean and coal generation both expanded through 2024.",
            "Use TWh additions and 2020 indices together. Percentage clean growth does not establish absolute coal displacement in a growing electricity market."),
    "ZAF": ("Clean generation rose from a smaller base and coal generation fell through 2024.",
            "Show absolute generation and demand, then net imports. Output changes alone do not diagnose reliability, outages or supply adequacy."),
}


def matched_panel(df: pd.DataFrame, years: list[int], required: list[str]) -> pd.DataFrame:
    """Keep a geography only if every requested year and metric is present."""
    d = df[df.year.isin(years)].copy()
    if d.duplicated(["iso3", "year"]).any():
        raise ValueError("Duplicate country/year input")
    valid = d[required].notna().all(axis=1)
    eligible = d.loc[valid].groupby("iso3").year.nunique()
    ids = eligible[eligible.eq(len(years))].index
    return d[d.iso3.isin(ids)].sort_values(["iso3", "year"])


def change(a: float, b: float) -> float:
    return (b / a - 1) * 100 if pd.notna(a) and pd.notna(b) and a > 0 else np.nan


def pathway(clean_pct: float, coal_pct: float, clean0: float, coal0: float,
            clean1: float, coal1: float) -> str:
    if any(pd.isna(x) for x in [clean_pct, coal_pct, clean0, coal0, clean1, coal1]):
        return "insufficient_data"
    if min(clean0, coal0, clean1, coal1) <= 20:
        return "below_materiality_threshold"
    if clean_pct > 5 and coal_pct < -5:
        return "transition"
    if clean_pct > 5 and coal_pct > 5:
        return "coexistence"
    if coal_pct < -5:
        return "coal_decline"
    if coal_pct > 5:
        return "coal_growth"
    return "mixed"


def fmt(v: float, signed: bool = False) -> str:
    if pd.isna(v):
        return "not reported"
    return f"{v:+,.1f}" if signed else f"{v:,.1f}"


def fmt_rate(v: float) -> str:
    return "not reported" if pd.isna(v) else fmt(v, True) + "%"


def md(df: pd.DataFrame) -> str:
    return df.to_markdown(index=False, floatfmt=".2f", missingval="—")


def save_table(df: pd.DataFrame, name: str) -> None:
    df.to_csv(TABLES / name, index=False, lineterminator="\n")


def save(fig: plt.Figure, name: str, footer: str) -> None:
    fig.text(.015, .012, footer, fontsize=8, color="#536477")
    fig.tight_layout(rect=(0, .045, 1, .96))
    for ext in ["png", "svg"]:
        fig.savefig(FIG / f"{name}.{ext}", dpi=170, facecolor="white")
    plt.close(fig)


def style() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.labelcolor": INK, "text.color": INK,
                         "axes.titleweight": "bold", "axes.grid": True,
                         "grid.alpha": .15, "axes.axisbelow": True})


def country_summary(cy: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for iso, d in cy.groupby("iso3", sort=True):
        d = d.set_index("year").sort_index()
        r = {"iso3": iso, "country": d.country.iloc[0], "continent": d.continent.iloc[0],
             "ember_years": ",".join(map(str, d.index)), "has_2025": 2025 in d.index,
             "core_market": iso in CORE}
        for col in ["demand_twh", "generation_twh", "clean_generation_twh", "fossil_generation_twh",
                    "wind_solar_generation_twh", "ei_coal_generation_twh", "ei_coal_production_mt",
                    "net_imports_twh", "power_emissions_mtco2e", "carbon_intensity_gco2e_kwh"]:
            a = d.at[2020, col] if 2020 in d.index else np.nan
            b = d.at[2024, col] if 2024 in d.index else np.nan
            r[col + "_2020"] = a
            r[col + "_2024"] = b
            r[col + "_delta"] = b - a
            r[col + "_pct"] = change(a, b)
        r["clean_share_change_pp"] = (d.at[2024, "clean_share_pct"] - d.at[2020, "clean_share_pct"]
                                        if {2020, 2024}.issubset(d.index) else np.nan)
        r["pathway"] = pathway(r["clean_generation_twh_pct"], r["ei_coal_generation_twh_pct"],
                               r["clean_generation_twh_2020"], r["ei_coal_generation_twh_2020"],
                               r["clean_generation_twh_2024"], r["ei_coal_generation_twh_2024"])
        # A descriptive ratio, not a causal attribution; undefined for declining demand.
        dd = r["demand_twh_delta"]
        r["clean_additions_vs_demand_additions_pct"] = r["clean_generation_twh_delta"] / dd * 100 if dd > 0 else np.nan
        r["demand_identity_residual_twh"] = dd - r["clean_generation_twh_delta"] - r["fossil_generation_twh_delta"] - r["net_imports_twh_delta"]
        rows.append(r)
    return pd.DataFrame(rows)


def country_figure(iso: str, d: pd.DataFrame) -> None:
    d = d.set_index("year").reindex(YEARS)
    fig, axes = plt.subplots(3, 2, figsize=(13.3, 10.2))
    fig.suptitle(f"{iso} | {d.country.dropna().iloc[0]}: electricity and coal", fontsize=19, x=.04, ha="left")
    ax = axes[0, 0]
    for col, label, color in [("demand_twh", "Demand", INK), ("clean_generation_twh", "Clean", BLUE),
                              ("fossil_generation_twh", "All fossil", ORANGE)]:
        ax.plot(YEARS, d[col], "o-", label=label, color=color)
    ax.set(title="Absolute generation and demand", ylabel="TWh")
    ax.legend(fontsize=9)
    ax = axes[0, 1]
    for col, label, color in [("clean_generation_twh", "Clean", BLUE), ("fossil_generation_twh", "All fossil", ORANGE),
                              ("net_imports_twh", "Net imports", "#8B6BAE")]:
        vals = d[col].diff()  # reindex makes missing years break changes
        offset = {"Clean": -.25, "All fossil": 0, "Net imports": .25}[label]
        ax.bar(np.array(YEARS) + offset, vals, width=.24, label=label, color=color)
    ax.plot(YEARS, d.demand_twh.diff(), "ko--", label="Demand change", markersize=4)
    ax.axhline(0, color=INK, lw=.7)
    ax.set(title="Yearly demand identity (not causal attribution)", ylabel="Change, TWh")
    ax.legend(fontsize=8, ncol=2)
    ax = axes[1, 0]
    for col, label, color in [("ei_coal_generation_twh", "Coal", ORANGE), ("ei_gas_generation_twh", "Gas", "#8B6BAE")]:
        ax.plot(YEARS, d[col], "o-", label=label, color=color)
    ax.set(title="Coal versus gas: EI only", ylabel="TWh")
    ax.legend(fontsize=9)
    ax = axes[1, 1]
    for col, label, color in [("ei_coal_production_mt", "Coal production", INK),
                              ("ei_coal_generation_twh", "Coal generation", ORANGE),
                              ("clean_generation_twh", "Clean generation (Ember)", BLUE)]:
        if pd.notna(d.at[2020, col]) and d.at[2020, col] > 0:
            ax.plot(YEARS, d[col] / d.at[2020, col] * 100, "o-", label=label, color=color)
    ax.axhline(100, color="#999999", lw=.7)
    ax.set(title="Different measures, same index base", ylabel="2020 = 100; not export flows")
    ax.legend(fontsize=8)
    ax = axes[2, 0]
    for col, label, color in [("power_emissions_mtco2e", "Power emissions", ORANGE),
                              ("carbon_intensity_gco2e_kwh", "Power intensity", BLUE)]:
        if pd.notna(d.at[2020, col]) and d.at[2020, col] > 0:
            ax.plot(YEARS, d[col] / d.at[2020, col] * 100, "o-", label=label, color=color)
    ax.set(title="Cleaner per kWh versus lower total emissions", ylabel="2020 = 100")
    ax.legend(fontsize=9)
    ax = axes[2, 1]
    ax.bar(YEARS, d.net_imports_twh, color="#8B6BAE")
    ax.axhline(0, color=INK, lw=.7)
    ax.set(title="Electricity trade", ylabel="Net imports, TWh (negative = exports)")
    for ax in axes.flat:
        ax.set_xticks(YEARS)
        ax.tick_params(labelsize=9)
        ax.axvspan(2024.5, 2025.5, color="#AAAAAA", alpha=.09)
    save(fig, f"country_{iso}", "Sources: supplied Ember extract; local EI snapshot. Gaps stay missing. Shading = 2025 watch year; definitions differ across sources.")


def build() -> dict:
    for p in [OUT, FIG, TABLES, COUNTRIES]:
        p.mkdir(parents=True, exist_ok=True)
    style()
    cy = pd.read_csv(ROOT / "data/processed/analysis_country_year.csv")
    ei = pd.read_csv(ROOT / "data/cleaned/energy_institute_global_energy.csv")
    agg = pd.read_csv(ROOT / "data/processed/eia_us_aggregates.csv")
    required = ["generation_twh", "demand_twh", "clean_generation_twh", "fossil_generation_twh",
                "wind_solar_generation_twh", "power_emissions_mtco2e", "net_imports_twh"]
    panel24 = matched_panel(cy, list(range(2020, 2025)), required)
    panel25 = matched_panel(cy, YEARS, required)
    sums = {}
    for name, panel in [("matched_2020_2024", panel24), ("matched_2020_2025", panel25)]:
        g = panel.groupby("year")[required].sum(min_count=1)
        g["n_countries"] = panel.groupby("year").iso3.nunique()
        g["clean_share_pct"] = 100 * g.clean_generation_twh / g.generation_twh
        g["intensity_gco2e_kwh"] = 1000 * g.power_emissions_mtco2e / g.generation_twh
        sums[name] = g
        save_table(g.reset_index(), name + ".csv")
        save_table(panel[["iso3", "country", "year"]], name + "_membership.csv")
    coverage = cy.groupby("year").agg(n_countries=("iso3", "nunique"), generation_twh=("generation_twh", "sum"))
    # Coverage of the 91-country panel measured against observed 2024 extract, not the world.
    observed24 = coverage.at[2024, "generation_twh"]
    observed_share = sums["matched_2020_2025"].at[2024, "generation_twh"] / observed24 * 100
    save_table(coverage.reset_index(), "ember_coverage.csv")
    summary = country_summary(cy)
    save_table(summary, "country_review_all.csv")
    material = summary[~summary.pathway.isin(["insufficient_data", "below_materiality_threshold"])]
    save_table(material, "material_country_pathways.csv")
    world = ei[ei.iso3.eq("WLD") & ei.Year.isin(YEARS)].pivot(index="Year", columns="variable", values="value")
    world["coal_share_pct"] = world.electbyfuel_coal / world.electbyfuel_total * 100
    save_table(world[["electbyfuel_coal", "electbyfuel_total", "coalprod_mt", "coal_tes_ej", "coal_share_pct"]].reset_index(), "ei_world_totals.csv")
    nat = agg[agg.location_code.eq("US") & agg.sector_code.eq(98)].sort_values("year").copy()
    nat["consumption_million_short_tons"] = nat.coal_consumption_short_tons / 1e6
    nat["consumption_million_metric_tonnes"] = nat.coal_consumption_short_tons * .90718474 / 1e6
    save_table(nat, "us_electric_power_coal.csv")

    g24, g25 = sums["matched_2020_2024"], sums["matched_2020_2025"]
    sensitivity = []
    for start in [2020, 2021]:
        for col in required:
            sensitivity.append({"start_year": start, "end_year": 2024,
                                "metric": col, "start_value": g24.at[start, col],
                                "end_value": g24.at[2024, col],
                                "change_pct": change(g24.at[start, col], g24.at[2024, col]),
                                "n_fixed_countries": int(g24.n_countries.iloc[0])})
    save_table(pd.DataFrame(sensitivity), "baseline_sensitivity.csv")
    metrics = {
        "countries_reviewed": len(summary), "core_markets": CORE,
        "material_countries": len(material), "panel24_n": int(g24.n_countries.iloc[0]),
        "panel25_n": int(g25.n_countries.iloc[0]), "panel25_share_observed_2024_generation_pct": observed_share,
        "clean_growth_2020_2024_pct": change(g24.at[2020, "clean_generation_twh"], g24.at[2024, "clean_generation_twh"]),
        "fossil_growth_2020_2024_pct": change(g24.at[2020, "fossil_generation_twh"], g24.at[2024, "fossil_generation_twh"]),
        "clean_share_2020_pct": g24.at[2020, "clean_share_pct"],
        "clean_share_2024_pct": g24.at[2024, "clean_share_pct"],
        "ws_growth_2020_2024_pct": change(g24.at[2020, "wind_solar_generation_twh"], g24.at[2024, "wind_solar_generation_twh"]),
        "ei_world_coal_growth_2020_2024_pct": change(world.at[2020, "electbyfuel_coal"], world.at[2024, "electbyfuel_coal"]),
        "ei_world_coal_2025_yoy_pct": change(world.at[2024, "electbyfuel_coal"], world.at[2025, "electbyfuel_coal"]),
        "us_coal_2020_2024_pct": change(nat.iloc[0].coal_consumption_short_tons, nat[nat.year.eq(2024)].iloc[0].coal_consumption_short_tons),
        "us_coal_2025_yoy_pct": change(nat[nat.year.eq(2024)].iloc[0].coal_consumption_short_tons, nat[nat.year.eq(2025)].iloc[0].coal_consumption_short_tons),
        "matched_2025_clean_vs_demand_additions_pct": ((g25.at[2025, "clean_generation_twh"] - g25.at[2024, "clean_generation_twh"]) /
                                                       (g25.at[2025, "demand_twh"] - g25.at[2024, "demand_twh"]) * 100),
        "matched_2025_fossil_yoy_pct": change(g25.at[2024, "fossil_generation_twh"], g25.at[2025, "fossil_generation_twh"]),
        "ci_flags": int(cy.carbon_intensity_precision_limited.sum()),
        "clean_growth_2021_2024_pct": change(g24.at[2021, "clean_generation_twh"], g24.at[2024, "clean_generation_twh"]),
        "fossil_growth_2021_2024_pct": change(g24.at[2021, "fossil_generation_twh"], g24.at[2024, "fossil_generation_twh"]),
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")

    # Slide figures: all endpoint comparisons state the panel and source.
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7))
    for col, label, color in [("clean_generation_twh", "Clean", BLUE), ("fossil_generation_twh", "All fossil", ORANGE),
                              ("wind_solar_generation_twh", "Wind + solar", AQUA)]:
        axes[0].plot(g24.index, g24[col] / g24.at[2020, col] * 100, "o-", color=color, label=label)
    axes[0].set(title="Clean grew faster; fossil volumes also rose", ylabel="2020 = 100")
    axes[0].set_xticks(g24.index)
    axes[0].legend(fontsize=9)
    axes[1].plot(world.index, world.electbyfuel_coal, "o-", color=ORANGE)
    axes[1].set(title="World coal generation: volumes remain large", ylabel="TWh (EI Total World)")
    axes[1].axvspan(2024.5, 2025.2, color="#AAAAAA", alpha=.12)
    save(fig, "01_global_volumes", f"Sources: Ember, fixed {len(panel24.iso3.unique())}-country panel (2020–2024); EI Total World row (2020–2025). Different measures and coverage.")

    fig, ax = plt.subplots(figsize=(12, 5))
    colors = {"transition": BLUE, "coexistence": ORANGE, "coal_decline": "#8B6BAE", "coal_growth": "#A33C34", "mixed": "#888888"}
    for category, d in material.groupby("pathway"):
        ax.scatter(d.clean_generation_twh_pct, d.ei_coal_generation_twh_pct,
                   s=70 + 250 * d.ei_coal_generation_twh_2024 / material.ei_coal_generation_twh_2024.max(),
                   color=colors[category], label=category.replace("_", " "), alpha=.85)
        for r in d.itertuples():
            ax.annotate(r.iso3, (r.clean_generation_twh_pct, r.ei_coal_generation_twh_pct), xytext=(5, 5), textcoords="offset points", fontsize=9)
    ax.axhline(0, color=INK, lw=.8)
    ax.axvline(0, color=INK, lw=.8)
    ax.set(title="Country pathways: clean growth does not guarantee coal decline", xlabel="Clean generation change, % (Ember)", ylabel="Coal generation change, % (EI)")
    ax.legend(fontsize=8, loc="upper right", ncol=2)
    save(fig, "02_country_pathways", f"2020–2024 endpoints. {len(material)} countries with >20 TWh clean AND coal in both years; ±5% classification thresholds. Bubble area increases with 2024 coal TWh.")

    fig, ax = plt.subplots(figsize=(12, 5))
    selected = summary.set_index("iso3").loc[CORE]
    xp = np.arange(len(CORE))
    for offset, col, label, color in [(-.25, "demand_twh_delta", "Demand", INK), (0, "clean_generation_twh_delta", "Clean", BLUE),
                                      (.25, "ei_coal_generation_twh_delta", "Coal (EI)", ORANGE)]:
        ax.bar(xp + offset, selected[col], width=.24, label=label, color=color)
    ax.set_xticks(xp, CORE)
    ax.axhline(0, color=INK, lw=.8)
    ax.set(title="China and India added clean generation alongside coal", ylabel="2020–2024 change, TWh")
    ax.legend(fontsize=9)
    save(fig, "03_core_additions", "Sources: Ember demand/clean; EI coal. Side-by-side measures, not an additive fuel decomposition. Country detail figures use local scales.")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7))
    axes[0].plot(nat.year, nat.consumption_million_short_tons, "o-", color=ORANGE, lw=2)
    axes[0].set(title="U.S. power coal: decline, then rebound", ylabel="Million short tons")
    axes[1].plot(nat.year, nat.delivered_price_usd_per_short_ton, "o-", color=INK, lw=2)
    axes[1].set(title="Delivered prices did not rise with the rebound", ylabel="USD per short ton (nominal)")
    save(fig, "04_us_coal_volume_price", "Source: supplied EIA extract; national sector 98 only. 2021 price is missing. Delivered price is not mine revenue or profit.")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7))
    for iso, color in [("USA", ORANGE), ("DEU", BLUE)]:
        d = cy[cy.iso3.eq(iso)].set_index("year").reindex(YEARS)
        axes[0].plot(YEARS, d.clean_generation_twh / d.at[2020, "clean_generation_twh"] * 100, "o-", label=iso + " clean", color=color)
        axes[0].plot(YEARS, d.demand_twh / d.at[2020, "demand_twh"] * 100, "--", label=iso + " demand", color=color)
    axes[0].set(title="Germany: lower coal is not the whole story", ylabel="2020 = 100")
    axes[0].legend(fontsize=8, ncol=2)
    for iso, color in [("IDN", ORANGE), ("AUS", BLUE)]:
        d = cy[cy.iso3.eq(iso)].set_index("year").reindex(YEARS)
        axes[1].plot(YEARS, d.ei_coal_production_mt / d.at[2020, "ei_coal_production_mt"] * 100, "o-", label=iso + " production", color=color)
        axes[1].plot(YEARS, d.ei_coal_generation_twh / d.at[2020, "ei_coal_generation_twh"] * 100, "--", label=iso + " coal gen", color=color)
    axes[1].set(title="Production and domestic generation can diverge", ylabel="2020 = 100 (EI)")
    axes[1].legend(fontsize=8, ncol=2)
    save(fig, "05_counterexamples", "Sources: Ember (left), EI (right). Indonesia Ember coverage stops in 2024, so joined country series stop there. Indices do not measure coal exports.")

    fig, ax = plt.subplots(figsize=(12, 4.7))
    dy = g25["demand_twh"].diff()
    cx = g25["clean_generation_twh"].diff()
    fx = g25["fossil_generation_twh"].diff()
    ax.bar(g25.index - .22, dy, width=.22, color=INK, label="Demand additions")
    ax.bar(g25.index, cx, width=.22, color=BLUE, label="Clean additions")
    ax.bar(g25.index + .22, fx, width=.22, color=ORANGE, label="Fossil additions")
    ax.axhline(0, color=INK, lw=.7)
    ax.set(title="2025 watch: clean additions exceeded demand additions", ylabel="Year-on-year change, TWh")
    ax.legend(fontsize=9)
    save(fig, "06_2025_watch", f"Source: Ember, fixed {len(panel25.iso3.unique())}-country panel. {observed_share:.1f}% of observed 2024 extract generation; not full-world coverage. Trade explains demand/generation differences.")

    # 2025 in the main pitch: matched Ember additions beside distinct EI
    # coal-generation changes, without mixing the sources into one identity.
    watch = []
    for col, label in [("demand_twh", "Demand"), ("clean_generation_twh", "Clean"), ("fossil_generation_twh", "All fossil")]:
        watch.append({"source": "Ember", "geography": "91-country matched panel", "measure": label,
                      "value_2024": g25.at[2024, col], "value_2025": g25.at[2025, col],
                      "change_twh": g25.at[2025, col] - g25.at[2024, col]})
    for iso in ["CHN", "IND", "USA"]:
        d = cy[cy.iso3.eq(iso)].set_index("year")
        watch.append({"source": "EI", "geography": iso, "measure": "Coal generation",
                      "value_2024": d.at[2024, "ei_coal_generation_twh"], "value_2025": d.at[2025, "ei_coal_generation_twh"],
                      "change_twh": d.at[2025, "ei_coal_generation_twh"] - d.at[2024, "ei_coal_generation_twh"]})
    watch.append({"source": "EI", "geography": "World", "measure": "Coal generation",
                  "value_2024": world.at[2024, "electbyfuel_coal"], "value_2025": world.at[2025, "electbyfuel_coal"],
                  "change_twh": world.at[2025, "electbyfuel_coal"] - world.at[2024, "electbyfuel_coal"]})
    watch = pd.DataFrame(watch)
    save_table(watch, "2025_watch_evidence.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7))
    v = watch[watch.source.eq("Ember")]
    axes[0].bar(v.measure, v.change_twh, color=[INK, BLUE, ORANGE])
    axes[0].axhline(0, color=INK, lw=.7)
    axes[0].set(title="Clean additions exceeded demand additions", ylabel="2024–2025 change, TWh (91 countries)")
    axes[0].set_ylim(-220, 1050)
    for i, value in enumerate(v.change_twh):
        axes[0].annotate(f"{value:+,.0f}", (i, value), xytext=(0, 5 if value >= 0 else -13), textcoords="offset points", ha="center", fontsize=10)
    v = watch[watch.source.eq("EI")].set_index("geography")
    deltas = [v.at[iso, "change_twh"] for iso in ["CHN", "IND", "USA"]]
    axes[1].bar(["China", "India", "U.S."], deltas, color=[BLUE, BLUE, ORANGE])
    axes[1].axhline(0, color=INK, lw=.7)
    axes[1].set(title="Coal generation moved in different directions", ylabel="2024–2025 change, TWh (EI)")
    axes[1].set_ylim(min(deltas) - 25, max(deltas) + 25)
    for i, value in enumerate(deltas):
        axes[1].annotate(f"{value:+,.1f}", (i, value), xytext=(0, 5 if value >= 0 else -13), textcoords="offset points", ha="center", fontsize=10)
    save(fig, "10_2025_global_divergence", f"Left: Ember fixed 91-country panel; {observed_share:.1f}% of observed 2024 extract generation, not full-world coverage.\nRight: EI coal only; Total World change {v.at['World', 'change_twh']:+.1f} TWh ({metrics['ei_world_coal_2025_yoy_pct']:+.2f}%). Different fuels/panels; no durable peak is established.")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7))
    axes[0].bar(coverage.index, coverage.n_countries, color=BLUE)
    axes[0].set(title="Ember country coverage shrinks", ylabel="Countries reporting in supplied extract")
    gap = (world.electbyfuel_coal - ei[(~ei.is_aggregate) & ei.Year.isin(YEARS) & ei.variable.eq("electbyfuel_coal")].groupby("Year").value.sum())
    axes[1].bar(gap.index, gap, color=ORANGE)
    axes[1].set(title="Listed EI countries do not cover Total World", ylabel="Coal generation gap, TWh")
    save(fig, "07_coverage", "Use fixed membership for trends; EI Total World alone for world totals. Never sum overlapping world/region/country rows.")

    # Compare exactly the same state/sector observations at both endpoints.
    states = pd.read_csv(ROOT / "data/processed/us_state_year_sector.csv")
    power = states[states.sector_code.isin([1, 2, 3]) & states.year.isin([2024, 2025])]
    pairs = power.pivot(index=["state_code", "sector_code"], columns="year", values="coal_consumption_short_tons")
    pairs = pairs.dropna(subset=[2024, 2025]).copy()
    pairs["change_million_short_tons"] = (pairs[2025] - pairs[2024]) / 1e6
    save_table(pairs.reset_index(), "us_matched_state_sector_changes.csv")
    state_changes = pairs.groupby("state_code").change_million_short_tons.sum().sort_values()
    save_table(state_changes.rename_axis("state_code").reset_index(), "us_matched_state_changes.csv")
    chosen = pd.concat([state_changes.head(5), state_changes.tail(10)]).loc[lambda x: ~x.index.duplicated()].sort_values()
    fig, ax = plt.subplots(figsize=(12, 5.4))
    ax.barh(chosen.index, chosen.values, color=[ORANGE if v > 0 else BLUE for v in chosen])
    ax.axvline(0, color=INK, lw=.8)
    ax.set(title="Where U.S. power-sector coal consumption changed", xlabel="2024–2025 change, million short tons (matched reported rows)")
    save(fig, "08_us_state_changes", "Source: supplied EIA. Base power sectors 1/2/3 only; same state-sector pair observed in both years. Selected five smallest and ten largest changes; consuming states, not mines.")

    quality = states[states.year.eq(2024) & states.sector_code.eq(1)].dropna(
        subset=["sulfur_content_pct", "ash_content_pct", "coal_consumption_short_tons"])
    quality = quality[quality.coal_consumption_short_tons > 1e6].copy()
    save_table(quality, "us_utility_coal_quality_2024.csv")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.scatter(quality.sulfur_content_pct, quality.ash_content_pct,
               s=40 + quality.coal_consumption_short_tons / quality.coal_consumption_short_tons.max() * 280,
               color=BLUE, alpha=.7)
    for r in quality.itertuples():
        ax.annotate(r.state_code, (r.sulfur_content_pct, r.ash_content_pct), xytext=(4, 4), textcoords="offset points", fontsize=8)
    ax.set(title="Reported coal quality differs across consuming states", xlabel="Sulfur content, %", ylabel="Ash content, %")
    save(fig, "09_us_coal_quality", "Source: EIA, 2024 utility sector 1, consumption >1 million short tons and reported sulfur/ash. Bubble area scales with consumption. No heat-unit conversion or margin claim.")

    core_table = summary.set_index("iso3").loc[CORE].reset_index()[
        ["iso3", "country", "clean_generation_twh_pct", "ei_coal_generation_twh_pct", "demand_twh_pct", "pathway"]]
    core_table.columns = ["ISO", "Country", "Clean change %", "Coal change %", "Demand change %", "Pathway"]
    reviews = ["# Country review and chart guide", "", "Primary comparison: 2020–2024. Missing years and metrics stay missing; 2025 is a watch year, not assumed final or uniformly preliminary.",
               "", "Eight core markets were identified in the existing Research D script. All 213 Ember geographies are reviewed below and in individual files. Sixteen material coal/clean markets receive six-panel figures.",
               "", "## The eight existing focus markets", "", md(core_table), "",
               "Sources: Ember clean/demand; EI coal. Percentages use positive 2020 bases. Detailed profiles below explain useful charts and limitations.", ""]
    overview = []
    for r in summary.itertuples(index=False):
        d = cy[cy.iso3.eq(r.iso3)].sort_values("year")
        exists = r.iso3 in set(material.iso3)
        headline, priority = SPECIAL.get(r.iso3, (
            f"2020–2024 pathway: {r.pathway.replace('_', ' ')}.",
            "Prioritize demand, clean/fossil additions, net imports and emissions. Add coal comparisons only where EI reports both endpoints; avoid percentage changes from zero bases."))
        proposed = ["Annual clean/fossil additions plus demand change and net imports (Ember accounting identity).",
                    "Power emissions and carbon intensity in separate panels or clearly labelled 2020 indices."]
        if pd.notna(r.ei_coal_generation_twh_2024):
            proposed += ["Coal and gas generation (EI only); clean share separately (Ember)."]
        if pd.notna(r.ei_coal_production_mt_2020) and r.ei_coal_production_mt_2020 > 0:
            proposed += ["Coal production and generation indices; do not infer exports or compare Mt directly with TWh."]
        if pd.notna(r.net_imports_twh_2024) and abs(r.net_imports_twh_2024) > .05 * r.demand_twh_2024:
            proposed.insert(0, "Net imports as a share of demand: trade is material (>5% absolute in 2024).")
        if r.demand_twh_delta <= 0:
            proposed.insert(0, "Demand-contraction panel: do not report a clean-growth/demand-growth ratio when demand fell.")
        series_cols = ["year", "demand_twh", "clean_generation_twh", "fossil_generation_twh", "ei_coal_generation_twh", "net_imports_twh", "power_emissions_mtco2e"]
        body = [f"# {r.country} ({r.iso3})", "", headline, "", f"Available Ember years: {r.ember_years}. Core research market: {r.core_market}.", "",
                f"Clean generation change: {fmt_rate(r.clean_generation_twh_pct)}; coal generation change: {fmt_rate(r.ei_coal_generation_twh_pct)}; demand change: {fmt_rate(r.demand_twh_pct)} (2020–2024).", "",
                priority, "", "## Recommended charts", ""] + [f"- {x}" for x in proposed]
        body += ["", "## Evidence", "", md(d[series_cols]), "", "Sources: supplied Ember extract; local Energy Institute snapshot, joined by normalized country/year. Coal and all-fossil are different measures. No causal or security-return claim follows from these series alone.", ""]
        if exists:
            country_figure(r.iso3, d)
            body += [f"![Six-panel country review](../figures/country_{r.iso3}.png)", ""]
        (COUNTRIES / f"{r.iso3}.md").write_text("\n".join(body))
        reviews += [f"## [{r.country} ({r.iso3})](countries/{r.iso3}.md)", "", headline,
                    f"Clean {fmt_rate(r.clean_generation_twh_pct)}; coal {fmt_rate(r.ei_coal_generation_twh_pct)}; demand {fmt_rate(r.demand_twh_pct)} (2020–2024).", "", priority, ""]
        overview.append({"iso3": r.iso3, "country": r.country, "pathway": r.pathway,
                         "priority": priority, "charts": " | ".join(proposed), "six_panel_figure": exists})
    save_table(pd.DataFrame(overview), "country_chart_priorities.csv")
    (OUT / "COUNTRY_REVIEW.md").write_text("\n".join(reviews))

    # Exact claim lineage: this table is the source for the presentation's numerical claims.
    claims = [
        ("E01", f"Clean generation rose {metrics['clean_growth_2020_2024_pct']:.1f}% in 2020–2024", "matched_2020_2024.csv", "clean_2024 / clean_2020 - 1", "Fixed 196-country panel; not complete world"),
        ("E02", f"All-fossil generation rose {metrics['fossil_growth_2020_2024_pct']:.1f}% in 2020–2024", "matched_2020_2024.csv", "fossil_2024 / fossil_2020 - 1", "All fossil, not coal"),
        ("E03", f"World coal generation rose {metrics['ei_world_coal_growth_2020_2024_pct']:.1f}% in 2020–2024", "ei_world_totals.csv", "coal_2024 / coal_2020 - 1", "EI Total World row; local snapshot"),
        ("E04", f"U.S. power coal consumption fell {abs(metrics['us_coal_2020_2024_pct']):.1f}% in 2020–2024", "us_electric_power_coal.csv", "consumption_2024 / consumption_2020 - 1", "National sector 98 only"),
        ("E05", f"U.S. power coal consumption rose {metrics['us_coal_2025_yoy_pct']:.1f}% in 2025", "us_electric_power_coal.csv", "consumption_2025 / consumption_2024 - 1", "Supplied snapshot; external vintage differs"),
        ("E06", f"2025 clean additions were {metrics['matched_2025_clean_vs_demand_additions_pct']:.1f}% of demand additions", "matched_2020_2025.csv", "delta_clean / delta_demand", "91-country fixed panel; descriptive, not causal"),
        ("E07", "16 material markets have divergent pathways", "material_country_pathways.csv", ">20 TWh clean and coal at both endpoints; ±5% change", "Selected population, not all-country frequencies"),
        ("E08", "China, India and Indonesia grew both clean and coal through 2024", "country_review_all.csv", "Positive clean and coal endpoint changes", "Cross-source side-by-side comparison"),
        ("E09", "Germany's clean, coal and demand all fell through 2024", "country_review_all.csv", "Negative endpoint changes", "Does not identify causes"),
        ("E10", f"2021–2024 clean grew {metrics['clean_growth_2021_2024_pct']:.1f}% versus {metrics['fossil_growth_2021_2024_pct']:.1f}% for all fossil", "baseline_sensitivity.csv", "2024 / 2021 - 1 on fixed panel", "Sensitivity to pandemic-affected 2020 base; not annual forecasts"),
        ("E11", "2025 coal generation fell in China and India but rose in the U.S.", "2025_watch_evidence.csv", "2025 coal TWh minus 2024 coal TWh", "EI country observations; separate from the Ember matched panel"),
    ]
    save_table(pd.DataFrame(claims, columns=["claim_id", "claim", "table", "calculation", "caveat"]), "claim_evidence.csv")

    audit = f"""# Review of the existing project

The reproducible pipeline, missing-value handling, separation of overlapping EIA sectors and dashboard are strong foundations. The existing research was not submission-complete: it intentionally omitted ratings, had no deck/script, and contained several inconsistent conclusions. This package supplies a scoped investment judgment and preserves the source snapshots.

## Corrections and limits

| Issue in prior material | Resolution |
|---|---|
| Ember described as 213 countries in every year through 2024 | Actual counts: 213, 213, 213, 212, 196, 91. Main analysis uses {metrics['panel24_n']} countries present with required metrics throughout 2020–2024; watch panel uses {metrics['panel25_n']} throughout 2020–2025. |
| Fossil and coal declines described as a 2025 contradiction | They have the same sign and measure different fuels/panels. No contradiction is established. |
| A single annual decline called a durable global peak | Describe an observed sample decline only. A durable peak remains a hypothesis. |
| 'Coal share falling everywhere' | Removed. Country trajectories differ; the world share did not decline in every year either. |
| Brazil/Indonesia labelled exporters from production versus generation | Divergence is descriptive. Trade, stock changes, quality, and non-power use cannot be identified from these two series. |
| Grid called a proven bottleneck and 'regime-proof' | Removed from the recommendation: no grid-constraint or spending evidence supports that causal claim. |
| Nuclear availability inferred from aggregate clean data | No attribution without technology-level checks. Clean is renewables plus nuclear. |
| Coal-producing states inferred from EIA consuming states | State EIA table identifies consumption location, not mine exposure. |
| consumption_mt export divided by 1,000 | Fixed to divide short tons ×0.90718474 by 1,000,000 for million metric tonnes. |
| Quality report claimed ~1,128 intensity discrepancies | Current calculation flags {metrics['ci_flags']}; generator corrected and report regenerated. |
| Receipts minus consumption labelled inventory change | Treat as a partial flow balance only; compare the same reported rows and do not infer stock levels. |
| 2025 universally preliminary; earlier years universally final | Snapshot release metadata is not provided. Coverage and revision status are different. Current official releases can be newer; avoid blanket finality claims. |
| Listed-country sum called world | Use EI's WLD row alone for world totals; country sums are explicitly partial and never mixed with overlapping aggregates. |
| Two pathway taxonomies with different thresholds | Submission uses one definition: >20 TWh clean/coal in both endpoint years and >5% directional changes. |
| 2020 is a pandemic-affected base year | `baseline_sensitivity.csv` also compares 2021–2024 on the same fixed panel. Endpoint growth is descriptive, not a forecast of normal annual growth. |

## Remaining accuracy checks

The supplied files are the assignment basis, not byte-for-byte certified copies of today's official releases. The additional EI CSV is hash-pinned locally, but its original download date/edition is not recorded. The official site confirms a narrow-format dataset exists; the exact local vintage is not independently certified. Do not describe the three sources as fully independent: EI lists Ember as a partner.

External EIA Table 1.1 gives 2024/2025 all-sector utility-scale electricity coal consumption of 372.931/415.103 million short tons. These differ from supplied sector-98 values and definitions. Direction agrees, but they must not be silently substituted or called an exact match. Current official net coal generation also differs from the local EI series: scope/vintage reconciliation remains open. See SOURCES.md.

The recommendations are forward-looking industry judgments, not demonstrated equity excess returns. No historical multiples, valuation spreads, developer margins or security prices are in this package. The assignment permits a judgment; those limitations constrain confidence and selection of securities.
"""
    (OUT / "PROJECT_AUDIT.md").write_text(audit)
    manifest = {}
    for p in [ROOT / "data/processed/analysis_country_year.csv", ROOT / "data/processed/eia_us_aggregates.csv", ROOT / "data/cleaned/energy_institute_global_energy.csv"]:
        manifest[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    (OUT / "input_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    build()
