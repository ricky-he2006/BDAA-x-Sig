"""Audit every plotted field against cleaned/processed source observations.

Run after the dashboard exporter. Checks source independence, nulls, world
totals, counts, evidence hashes and on-disk export freshness.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard/scripts"))
import export_dashboard_data as E
from src.iso3166 import std_geo_key

EMBER = {"demand": "demand_twh", "generation": "generation_twh", "clean": "clean_generation_twh",
         "fossil": "fossil_generation_twh", "renewable": "renewable_generation_twh", "wind_solar": "wind_solar_generation_twh",
         "clean_share": "clean_share_pct", "net_imports": "net_imports_twh", "ci": "carbon_intensity_gco2e_kwh",
         "emissions": "power_emissions_mtco2e", "demand_change": "demand_change_twh", "clean_change": "clean_change_twh",
         "fossil_change": "fossil_change_twh", "has_previous_year": "has_previous_year", "growth_status": "growth_status"}
EIA = {"consumption": "coal_consumption_short_tons", "receipts": "coal_receipts_short_tons",
       "price": "delivered_price_usd_per_short_ton"}


def audit() -> dict:
    errors = []
    count = 0
    def same(actual, expected, label):
        nonlocal count
        count += 1
        if expected is None or pd.isna(expected):
            good = actual is None
        elif isinstance(expected, str):
            good = actual == expected
        else:
            good = isinstance(actual, (int, float, bool)) and math.isclose(float(actual), float(expected), rel_tol=1e-10, abs_tol=1e-7)
        if not good:
            errors.append(f"{label}: dashboard={actual!r}, source={expected!r}")

    cy = pd.read_csv(ROOT / "data/processed/analysis_country_year.csv")
    ei = pd.read_csv(ROOT / "data/cleaned/energy_institute_global_energy.csv")
    country = json.loads((E.OUT / "country_year.json").read_text())
    index = {(r["iso3"], r["year"]): r for r in country["records"]}
    same(len(index), len(country["records"]), "unique country keys")
    expected_keys = set()
    for r in cy.to_dict("records"):
        key = r["iso3"], r["year"]
        expected_keys.add(key)
        got = index.get(key)
        if got is None:
            errors.append(f"Missing Ember record {key}"); continue
        for field, col in EMBER.items():
            same(got["ember"][field], r[col], f"{key} Ember {field}")
        same(got["ember_available"], True, f"{key} Ember availability")
    names = cy.drop_duplicates("geo_key").set_index("geo_key").iso3.to_dict()
    ei_rows = ei[(~ei.is_aggregate) & ei.Year.between(2020, 2025) & ei.variable.isin(E.EI_FIELDS.values())].copy()
    ei_rows["geo_key"] = ei_rows.iso3.map(std_geo_key)
    wide = ei_rows.pivot(index=["geo_key", "Year"], columns="variable", values="value")
    for (geo, year), r in wide.iterrows():
        if geo not in names: continue  # historical entity, not current geography
        key = names[geo], int(year)
        expected_keys.add(key)
        got = index.get(key)
        if got is None:
            errors.append(f"Missing independent EI record {key}"); continue
        for field, var in E.EI_FIELDS.items():
            same(got["ei"][field], r.get(var), f"{key} EI {field}")
        same(got["coal_share"], r.get("electbyfuel_coal") / r.get("elect_twh") * 100
             if pd.notna(r.get("elect_twh")) and r.get("elect_twh") > 0 and pd.notna(r.get("electbyfuel_coal")) else None,
             f"{key} EI coal share")
    if set(index) != expected_keys:
        errors.append("Country source union has missing or unexpected keys")
    for r in country["records"]:
        if not r["ember_available"]:
            for field in EMBER:
                if field != "has_previous_year": same(r["ember"][field], None, f"{r['iso3']} {r['year']} not imputed {field}")
        same(r["ei_available"], any(v is not None for v in r["ei"].values()), f"{r['iso3']} {r['year']} EI flag")
    for coverage in country["coverage"]:
        rows = [r for r in country["records"] if r["year"] == coverage["year"]]
        same(coverage["ember_countries"], sum(r["ember_available"] for r in rows), "Ember coverage count")
        same(coverage["ei_countries"], sum(r["ei_available"] for r in rows), "EI coverage count")
        same(coverage["ei_coal_countries"], sum(r["ei"]["coal_gen"] is not None for r in rows), "EI coal coverage count")
    world = ei[ei.iso3.eq("WLD") & ei.Year.between(2020, 2025)].pivot(index="Year", columns="variable", values="value")
    for r in country["ei_world"]:
        src = world.loc[r["year"]]
        for field, col in {"coal_generation_twh": "electbyfuel_coal", "total_generation_twh": "electbyfuel_total",
                           "coal_production_mt": "coalprod_mt", "coal_tes_ej": "coal_tes_ej"}.items():
            same(r[field], src[col], f"World {r['year']} {field}")
    for filename, csvfile, keycols, exportkeys, mapping in [
        ("us_state_year.json", "us_state_year_sector.csv", ["state_code", "year", "sector_code"], ["state", "year", "sector"],
         EIA | {"stocks": "coal_stocks_short_tons", "heat_btu_lb": "heat_content_btu_per_lb", "heat_unit": "heat_content_unit_inferred", "sulfur_pct": "sulfur_content_pct", "ash_pct": "ash_content_pct"}),
        ("us_aggregates.json", "eia_us_aggregates.csv", ["location_code", "year", "sector_code"], ["location", "year", "sector"], EIA),
    ]:
        src = pd.read_csv(ROOT / "data/processed" / csvfile).set_index(keycols)
        rows = json.loads((E.OUT / filename).read_text())["records"]
        same(len(rows), len(src), filename + " row count")
        for r in rows:
            key = tuple(r[col] for col in exportkeys)
            for field, col in mapping.items():
                same(r[field], src.loc[key, col], f"{filename} {key} {field}")
    for filename, producer in [("country_year.json", E.export_country_year), ("us_state_year.json", E.export_us_state),
                               ("us_aggregates.json", E.export_us_aggregates), ("geo.json", E.export_geo)]:
        # JSON object keys are strings (sector labels start as integer keys).
        if json.loads((E.OUT / filename).read_text()) != json.loads(json.dumps(producer(), allow_nan=False)):
            errors.append(f"Stale exported file {filename}")
    evidence = E.OUT.parent / "evidence"
    for r in json.loads((evidence / "manifest.json").read_text()):
        path = evidence / r["file"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != r["sha256"]:
            errors.append(f"Missing/stale evidence {path.name}")
    result = {"errors": errors, "source_field_comparisons": count, "country_records": len(index),
              "ember_records": sum(r["ember_available"] for r in country["records"]),
              "ei_only_records_restored": sum(not r["ember_available"] for r in country["records"]),
              "coverage": country["coverage"], "world_records": len(country["ei_world"])}
    (ROOT / "submission/dashboard_data_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2))
    if result["errors"]: raise SystemExit(1)
