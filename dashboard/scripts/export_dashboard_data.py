"""Exports analysis-ready tables to strict JSON for the Energy Atlas dashboard.

Run from the project root:
    python3 dashboard/scripts/export_dashboard_data.py

Reads data/processed/*.csv (plus the cleaned EI table for the geo mapping)
and writes dashboard/public/data/*.json.

JSON contract (enforced, not just hoped for):
* All non-finite numbers (NaN, +Infinity, -Infinity) are serialized as
  JSON `null` - missing stays missing, NEVER as 0 and never as a bare
  `NaN` token (which Python's json module would emit by default and which
  browser JSON.parse rejects with "Unexpected token 'N'").
* Serialization runs with allow_nan=False, so any non-finite value that
  slips past _sanitize makes the export fail loudly instead of writing an
  unparseable file.
* Every file is re-read and parsed with a standards-compliant decoder
  (RFC 8259 - no NaN/Infinity constants) before the run reports success.
* Deterministic: fixed key order, sorted arrays, no timestamps.
"""
from __future__ import annotations

import json
import hashlib
import math
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src import config as C  # noqa: E402
from src.iso3166 import std_geo_key  # noqa: E402

OUT = ROOT / "dashboard" / "public" / "data"
EI_FIELDS = {
    "elect": "elect_twh", "coal_gen": "electbyfuel_coal", "gas_gen": "electbyfuel_gas",
    "nuclear_gen": "electbyfuel_nuclear", "ren_gen": "electbyfuel_ren_power",
    "wind": "wind_twh", "solar": "solar_twh", "hydro": "hydro_twh",
    "coal_prod_mt": "coalprod_mt", "coal_tes_ej": "coal_tes_ej", "tes_ej": "tes_ej",
    "co2_mtco2": "co2_combust_mtco2", "pop": "pop",
}


def _sanitize(v):
    """Recursively convert a value to strict-JSON-safe Python types.

    * NaN / +Inf / -Inf (Python or NumPy) -> None
    * pd.NA / NaT / nullish pandas objects    -> None
    * NumPy scalars                          -> native Python scalars
    * real 0 stays 0 (zero is data, not missing)
    * dicts / lists are recursed into
    * int / float / str / bool pass through unchanged
    """
    if v is None or isinstance(v, (str, bool)):
        return v
    if isinstance(v, dict):
        return {k: _sanitize(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_sanitize(x) for x in v]
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        v = float(v)
    if isinstance(v, float):
        return None if not math.isfinite(v) else v
    if isinstance(v, int):
        return v
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    return v


def _strict_parse(text: str):
    """Parse with a standards-compliant decoder: RFC 8259 JSON has no
    NaN/Infinity constants, so a bare token means the file is invalid."""
    def _reject(const: str):
        raise ValueError(f"non-strict JSON token {const!r} in generated file")
    json.loads(text, parse_constant=_reject)


def export_country_year():
    cy = pd.read_csv(C.PROCESSED / C.PROCESSED_COUNTRY_YEAR)
    recs = []
    for _, r in cy.iterrows():
        ember = {
            "demand": r.get("demand_twh"),
            "generation": r.get("generation_twh"),
            "clean": r.get("clean_generation_twh"),
            "fossil": r.get("fossil_generation_twh"),
            "renewable": r.get("renewable_generation_twh"),
            "wind_solar": r.get("wind_solar_generation_twh"),
            "clean_share": r.get("clean_share_pct"),
            "net_imports": r.get("net_imports_twh"),
            "ci": r.get("carbon_intensity_gco2e_kwh"),
            "emissions": r.get("power_emissions_mtco2e"),
            "demand_change": r.get("demand_change_twh"),
            "clean_change": r.get("clean_change_twh"),
            "fossil_change": r.get("fossil_change_twh"),
            "has_previous_year": int(r.get("has_previous_year") or 0),
            "growth_status": r.get("growth_status"),
        }
        ei = {
            "elect": r.get("ei_elect_twh"),
            "coal_gen": r.get("ei_coal_generation_twh"),
            "gas_gen": r.get("ei_gas_generation_twh"),
            "nuclear_gen": r.get("ei_nuclear_generation_twh"),
            "ren_gen": r.get("ei_ren_power_generation_twh"),
            "wind": r.get("ei_wind_twh"),
            "solar": r.get("ei_solar_twh"),
            "hydro": r.get("ei_hydro_twh"),
            "coal_prod_mt": r.get("ei_coal_production_mt"),
            "coal_tes_ej": r.get("ei_coal_tes_ej"),
            "tes_ej": r.get("ei_tes_ej"),
            "co2_mtco2": r.get("ei_co2_combust_mtco2"),
            "pop": r.get("ei_population_millions"),
        }
        recs.append({
            "iso3": r.iso3,
            "name": r.country,
            "continent": r.continent,
            "year": int(r.year),
            "ember": ember,
            "ei": ei,
            "coal_share": r.get("coal_share_of_generation_pct"),
            "ember_available": True,
            "ei_available": any(pd.notna(v) for v in ei.values()),
            "zero_generation": bool(r.get("zero_generation_flag")),
            "ci_precision_limited": bool(r.get("carbon_intensity_precision_limited")),
        })
    # The processed country table is Ember-left-joined. Restore independent
    # EI observations (e.g. Indonesia 2025) without inventing Ember values.
    clean_ei = pd.read_csv(C.CLEANED / C.CLEANED_EI)
    e = clean_ei[(~clean_ei.is_aggregate) & clean_ei.Year.isin(C.FOCUS_YEARS)
                 & clean_ei.variable.isin(EI_FIELDS.values())].copy()
    e["geo_key"] = e.iso3.map(std_geo_key)
    wide = e.pivot(index=["geo_key", "Year"], columns="variable", values="value")
    known = cy.drop_duplicates("geo_key").set_index("geo_key")
    present = {(std_geo_key(r["iso3"]), r["year"]) for r in recs}
    missing_ember = {k: None for k in recs[0]["ember"]}
    missing_ember["has_previous_year"] = 0
    for (geo, year), r in wide.iterrows():
        # Only current geographies in the electricity universe. Historical
        # USSR's zero TES rows remain in raw EI, never become a modern country.
        if geo not in known.index or (geo, year) in present:
            continue
        info = known.loc[geo]
        block = {key: r.get(var) for key, var in EI_FIELDS.items()}
        gen, coal = block["elect"], block["coal_gen"]
        recs.append({"iso3": info.iso3, "name": info.country, "continent": info.continent,
                     "year": int(year), "ember": dict(missing_ember), "ei": block,
                     "coal_share": coal / gen * 100 if pd.notna(gen) and gen > 0 and pd.notna(coal) else None,
                     "ember_available": False, "ei_available": True,
                     "zero_generation": False, "ci_precision_limited": False})
    recs.sort(key=lambda x: (x["iso3"], x["year"]))
    recs = _sanitize(recs)
    world = clean_ei[clean_ei.iso3.eq("WLD") & clean_ei.Year.isin(C.FOCUS_YEARS)].pivot(
        index="Year", columns="variable", values="value")
    world_records = []
    for year, r in world.iterrows():
        world_records.append({"year": int(year), "coal_generation_twh": r.electbyfuel_coal,
                              "total_generation_twh": r.electbyfuel_total,
                              "coal_production_mt": r.coalprod_mt, "coal_tes_ej": r.coal_tes_ej,
                              "coal_share_pct": r.electbyfuel_coal / r.electbyfuel_total * 100})
    coverage = [{"year": year,
                 "ember_countries": sum(r["year"] == year and r["ember_available"] for r in recs),
                 "ei_countries": sum(r["year"] == year and r["ei_available"] for r in recs),
                 "ei_coal_countries": sum(r["year"] == year and r["ei"]["coal_gen"] is not None for r in recs)}
                for year in C.FOCUS_YEARS]
    sources = []
    for name, url in [(C.RAW_EMBER, "https://ember-energy.org/data/yearly-electricity-data/"),
                      (C.RAW_EIA, "https://www.eia.gov/coal/data.php"),
                      (C.RAW_EI, "https://www.energyinst.org/statistical-review/resources-and-data-downloads")]:
        path = C.RAW / name
        sources.append({"file": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "url": url})
    return _sanitize({"grain": "iso3 x year; source blocks independently available", "n": len(recs),
                      "records": recs, "ei_world": world_records, "coverage": coverage, "sources": sources})


def export_evidence(payloads):
    """Serve the actual plotted rows and the thesis evidence alongside the app."""
    evidence = OUT.parent / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    pd.json_normalize(payloads["country_year.json"]["records"]).to_csv(evidence / "country_year.csv", index=False)
    pd.DataFrame(payloads["country_year.json"]["ei_world"]).to_csv(evidence / "ei_world.csv", index=False)
    directory = []
    for iso in sorted({r["iso3"] for r in payloads["country_year.json"]["records"]}):
        rows = [r for r in payloads["country_year.json"]["records"] if r["iso3"] == iso]
        directory.append({"iso3": iso, "country": rows[0]["name"],
                          "ember_years": ",".join(str(r["year"]) for r in rows if r["ember_available"]),
                          "ei_years": ",".join(str(r["year"]) for r in rows if r["ei_available"]),
                          "coal_generation_years": ",".join(str(r["year"]) for r in rows if r["ei"]["coal_gen"] is not None)})
    pd.DataFrame(directory).to_csv(evidence / "country_directory.csv", index=False)
    for filename, key in [("us_state_year.csv", "us_state_year.json"), ("us_aggregates.csv", "us_aggregates.json")]:
        pd.DataFrame(payloads[key]["records"]).to_csv(evidence / filename, index=False)
    # Fail if promised evidence is missing; stale dashboards must not silently
    # ship links to absent thesis calculations.
    paths = {
        "claim_evidence.csv": ROOT / "deliverables/tables/claim_evidence.csv",
        "matched_2020_2024.csv": ROOT / "deliverables/tables/matched_2020_2024.csv",
        "matched_2020_2025.csv": ROOT / "deliverables/tables/matched_2020_2025.csv",
        "country_pathways.csv": ROOT / "deliverables/tables/material_country_pathways.csv",
        "thesis.md": ROOT / "deliverables/INVESTMENT_THESIS.md",
        "sources.md": ROOT / "deliverables/SOURCES.md",
        "data_dictionary.md": ROOT / "reports/data_dictionary.md",
        "data_quality.md": ROOT / "reports/data_quality_report.md",
        "ei_provenance.json": ROOT / "data/provenance/energy_institute.json",
    }
    for filename, src in paths.items():
        shutil.copyfile(src, evidence / filename)
    files = [{"file": p.name, "bytes": p.stat().st_size,
              "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in sorted(evidence.iterdir()) if p.is_file() and p.name != "manifest.json"]
    (evidence / "manifest.json").write_text(json.dumps(files, indent=2) + "\n")


def export_us_state():
    us = pd.read_csv(C.PROCESSED / C.PROCESSED_US_STATE)
    recs = []
    for _, r in us.iterrows():
        recs.append({
            "state": r.state_code,
            "state_name": r.state_name,
            "year": int(r.year),
            "sector": int(r.sector_code),
            "sector_name": r.sector_name,
            "consumption": r.get("coal_consumption_short_tons"),
            "receipts": r.get("coal_receipts_short_tons"),
            "stocks": r.get("coal_stocks_short_tons"),
            "price": r.get("delivered_price_usd_per_short_ton"),
            "heat_btu_lb": r.get("heat_content_btu_per_lb"),
            "heat_unit": r.get("heat_content_unit_inferred"),
            "sulfur_pct": r.get("sulfur_content_pct"),
            "ash_pct": r.get("ash_content_pct"),
        })
    recs.sort(key=lambda x: (x["state"], x["year"], x["sector"]))
    return _sanitize({
        "grain": "state x year x base-sector",
        "sectors": {s: C.EIA_SECTORS[s] for s in C.EIA_BASE_SECTORS},
        "n": len(recs),
        "records": recs,
    })


def export_us_aggregates():
    agg = pd.read_csv(C.PROCESSED / C.PROCESSED_EIA_AGGREGATES)
    recs = []
    for _, r in agg.iterrows():
        recs.append({
            "location": r.location_code,
            "location_name": r.location_name,
            "location_type": r.location_type,
            "year": int(r.year),
            "sector": int(r.sector_code),
            "sector_name": r.sector_name,
            "consumption": r.get("coal_consumption_short_tons"),
            "receipts": r.get("coal_receipts_short_tons"),
            "price": r.get("delivered_price_usd_per_short_ton"),
        })
    recs.sort(key=lambda x: (x["location"], x["year"], x["sector"]))
    return _sanitize({"grain": "location x year x aggregate-sector",
                      "n": len(recs), "records": recs})


# Complete ISO 3166-1 numeric -> alpha-3 reference for every feature in the
# bundled world-atlas/countries-110m topology (174 features carry a numeric id;
# the remaining three - N. Cyprus, Somaliland, Kosovo - have no ISO id and are
# matched by name in _GEO_NAME_FALLBACK below). This is a fixed international
# standard (like the dashboard's hardcoded FIPS_TO_STATE), NOT derived from any
# one dataset: building the table from the Energy Institute file (as before)
# left ~70 major countries unmapped because EI carries iso_num for only ~110
# entities. The table is cross-checked against EI's own iso_num in export_geo.
#
# Codes are the dataset's keys, not always the ISO letter. The globe colors a
# feature only when its iso3 joins the data, and the dataset (Ember) keys
# Falkland Islands as FLK (not the ISO FKS); that one entry is FLK on purpose.
# Kosovo has no numeric id and is handled by name in _GEO_NAME_FALLBACK.
_ISO_NUMERIC_TO_ALPHA3 = {
    "004": "AFG", "008": "ALB", "010": "ATA", "012": "DZA", "024": "AGO",
    "031": "AZE", "032": "ARG", "036": "AUS", "040": "AUT", "044": "BHS",
    "050": "BGD", "051": "ARM", "056": "BEL", "064": "BTN", "068": "BOL",
    "070": "BIH", "072": "BWA", "076": "BRA", "084": "BLZ", "090": "SLB",
    "096": "BRN", "100": "BGR", "104": "MMR", "108": "BDI", "112": "BLR",
    "116": "KHM", "120": "CMR", "124": "CAN", "140": "CAF", "144": "LKA",
    "148": "TCD", "152": "CHL", "156": "CHN", "158": "TWN", "170": "COL",
    "178": "COG", "180": "COD", "188": "CRI", "191": "HRV", "192": "CUB",
    "196": "CYP", "203": "CZE", "204": "BEN", "208": "DNK", "214": "DOM",
    "218": "ECU", "222": "SLV", "226": "GNQ", "231": "ETH", "232": "ERI",
    "233": "EST", "238": "FLK", "242": "FJI", "246": "FIN", "250": "FRA",
    "260": "ATF", "262": "DJI", "266": "GAB", "268": "GEO", "270": "GMB",
    "275": "PSE", "276": "DEU", "288": "GHA", "300": "GRC", "304": "GRL",
    "320": "GTM", "324": "GIN", "328": "GUY", "332": "HTI", "340": "HND",
    "348": "HUN", "352": "ISL", "356": "IND", "360": "IDN", "364": "IRN",
    "368": "IRQ", "372": "IRL", "376": "ISR", "380": "ITA", "384": "CIV",
    "388": "JAM", "392": "JPN", "398": "KAZ", "400": "JOR", "404": "KEN",
    "408": "PRK", "410": "KOR", "414": "KWT", "417": "KGZ", "418": "LAO",
    "422": "LBN", "426": "LSO", "428": "LVA", "430": "LBR", "434": "LBY",
    "440": "LTU", "442": "LUX", "450": "MDG", "454": "MWI", "458": "MYS",
    "466": "MLI", "478": "MRT", "484": "MEX", "496": "MNG", "498": "MDA",
    "499": "MNE", "504": "MAR", "508": "MOZ", "512": "OMN", "516": "NAM",
    "524": "NPL", "528": "NLD", "540": "NCL", "548": "VUT", "554": "NZL",
    "558": "NIC", "562": "NER", "566": "NGA", "578": "NOR", "586": "PAK",
    "591": "PAN", "598": "PNG", "600": "PRY", "604": "PER", "608": "PHL",
    "616": "POL", "620": "PRT", "624": "GNB", "626": "TLS", "630": "PRI",
    "634": "QAT", "642": "ROU", "643": "RUS", "646": "RWA", "682": "SAU",
    "686": "SEN", "688": "SRB", "694": "SLE", "703": "SVK", "704": "VNM",
    "705": "SVN", "706": "SOM", "710": "ZAF", "716": "ZWE", "724": "ESP",
    "728": "SSD", "729": "SDN", "732": "ESH", "740": "SUR", "748": "SWZ",
    "752": "SWE", "756": "CHE", "760": "SYR", "762": "TJK", "764": "THA",
    "768": "TGO", "780": "TTO", "784": "ARE", "788": "TUN", "792": "TUR",
    "795": "TKM", "800": "UGA", "804": "UKR", "807": "MKD", "818": "EGY",
    "826": "GBR", "834": "TZA", "840": "USA", "854": "BFA", "858": "URY",
    "860": "UZB", "862": "VEN", "887": "YEM", "894": "ZMB",
}

# Name fallback for world-atlas features that carry no ISO numeric id. The
# bundled topology gives Kosovo no ISO id; the dataset reports it under the UN
# code XKX (not the ISO-reserved XKS), so we map to the code the data actually
# uses. N. Cyprus and Somaliland are left unmapped on purpose - the dataset
# reports no generation for them, so they stay uncolored.
_GEO_NAME_FALLBACK = {
    "Kosovo": "XKX",
}


def export_geo():
    """Numeric ISO 3166-1 code -> alpha-3, from the complete standard table
    above (covers every bundled-topology feature), cross-checked against the
    Energy Institute dataset's own iso_num as an integrity guard. Name aliases
    cover the few features without a numeric id.
    """
    ei = pd.read_csv(C.CLEANED / C.CLEANED_EI)
    ei = ei[ei["is_aggregate"] == False]  # noqa: E712

    # Integrity check: wherever EI records an ISO numeric code, it must agree
    # with the standard table. A disagreement is a data error (or a typo in the
    # reference) and is worth failing loudly on.
    mismatches = []
    for _, r in ei.iterrows():
        if pd.notna(r.iso_num):
            key = str(int(r.iso_num)).zfill(3)
            if key in _ISO_NUMERIC_TO_ALPHA3 and _ISO_NUMERIC_TO_ALPHA3[key] != r.iso3:
                mismatches.append(f"{key}: EI={r.iso3} standard={_ISO_NUMERIC_TO_ALPHA3[key]}")
    if mismatches:
        raise ValueError(f"ISO numeric table disagrees with EI on: {mismatches}")

    return _sanitize({
        "numeric_to_alpha3": dict(_ISO_NUMERIC_TO_ALPHA3),
        "name_to_alpha3": dict(_GEO_NAME_FALLBACK),
    })


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    payloads = {
        "country_year.json": export_country_year(),
        "us_state_year.json": export_us_state(),
        "us_aggregates.json": export_us_aggregates(),
        "geo.json": export_geo(),
    }
    for name, payload in payloads.items():
        # Payloads are sanitized at their source (each export_* returns
        # strict-JSON-safe data). allow_nan=False is the hard backstop: if a
        # non-finite value ever survives, json.dumps raises instead of
        # writing an unparseable file.
        body = json.dumps(payload, indent=1, sort_keys=True,
                          allow_nan=False) + "\n"
        path = OUT / name
        path.write_text(body, encoding="utf-8")
        # Standards-compliant re-parse (rejects bare NaN/Infinity tokens) so
        # the run fails loudly if the file on disk is not valid JSON.
        _strict_parse(path.read_text(encoding="utf-8"))
        count = payload.get("n", f"{len(payload['records']) if 'records' in payload else 'ok'}")
        print(f"wrote {OUT / name} ({count} records; strict JSON verified)")
    export_evidence(payloads)


if __name__ == "__main__":
    main()
