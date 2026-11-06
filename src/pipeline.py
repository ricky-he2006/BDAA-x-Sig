"""Reproducible end-to-end pipeline.

python -m src.pipeline   (run from the project root)

Guarantees:
* raw sources are copied into data/raw/ exactly once and never modified;
  originals in the project root are left untouched.
* every stage is deterministic; running twice yields byte-identical outputs.
* the full audit trail is written to reports/cleaning_log.csv and the
  human-readable findings to reports/data_quality_report.md.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pandas as pd

from . import clean_eia, clean_ei, clean_ember, config as C, cross_validate, process
from .audit_common import AuditLog, sha256_of_file, stable_sort, write_deterministic_csv

MANIFEST = C.RAW / "MANIFEST.json"


def ensure_raw(force: bool = False) -> dict:
    """Copy originals into data/raw/ and pin their checksums in a manifest."""
    C.RAW.mkdir(parents=True, exist_ok=True)
    sources = [C.RAW_EMBER, C.RAW_EIA, C.RAW_EI]
    manifest: dict = {}
    for name in sources:
        src = C.ROOT / name
        dst = C.RAW / name
        if not src.exists():
            raise FileNotFoundError(f"raw source missing: {src}")
        src_hash = sha256_of_file(src)
        if force or not dst.exists() or sha256_of_file(dst) != src_hash:
            if dst.exists() and sha256_of_file(dst) != src_hash and not force:
                raise RuntimeError(
                    f"{dst} differs from the original {src} and is not identical; "
                    "refusing to overwrite a raw copy (pass --force to replace)")
            shutil.copy2(src, dst)
        manifest[name] = {"sha256": src_hash, "bytes": src.stat().st_size}
    if force or not MANIFEST.exists() or json.loads(MANIFEST.read_text()) != manifest:
        MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def _write_outputs(cleaned: dict, processed: dict, logs: list, summary: dict) -> None:
    C.CLEANED.mkdir(parents=True, exist_ok=True)
    C.PROCESSED.mkdir(parents=True, exist_ok=True)
    C.REPORTS.mkdir(parents=True, exist_ok=True)
    for name, df in cleaned.items():
        write_deterministic_csv(df, C.CLEANED / name)
    for name, df in processed.items():
        write_deterministic_csv(df, C.PROCESSED / name)
    all_entries = pd.concat([log.as_frame() for log in logs], ignore_index=True) \
        if logs else pd.DataFrame(columns=["dataset", "check_id", "severity",
                                           "action", "record", "field", "detail",
                                           "before", "after"])
    all_entries = stable_sort(all_entries,
                              ["dataset", "severity", "check_id", "record", "field"])
    write_deterministic_csv(all_entries, C.REPORTS / "cleaning_log.csv")
    # machine-readable summary for the report/tests (DataFrames -> records)
    def _jsonable(v):
        if isinstance(v, pd.DataFrame):
            return v.to_dict("records")
        return v
    (C.REPORTS / "validation_summary.json").write_text(
        json.dumps({k: _jsonable(v) for k, v in summary.items()},
                   indent=2, sort_keys=True, default=str) + "\n")


def run(force_raw: bool = False) -> dict:
    manifest = ensure_raw(force=force_raw)

    logs = []
    # 1. Ember
    ember = clean_ember.load_raw()
    ember_c, log_ember = clean_ember.audit_and_clean(ember)
    logs.append(log_ember)
    # 2. EIA
    eia = clean_eia.load_raw()
    eia_c, log_eia = clean_eia.audit_and_clean(eia)
    logs.append(log_eia)
    # 3. Energy Institute
    ei = clean_ei.load_raw()
    ei_c, log_ei = clean_ei.audit_and_clean(ei)
    logs.append(log_ei)

    # 4. cross validation
    log_x, summary = cross_validate.run(ember_c, eia_c, ei_c)
    logs.append(log_x)
    summary["manifest"] = manifest
    summary["pipeline_version"] = C.PIPELINE_VERSION
    summary["row_counts"] = {
        "ember": {"raw": int(len(ember)), "cleaned": int(len(ember_c))},
        "eia": {"raw": int(len(eia)), "cleaned": int(len(eia_c))},
        "energy_institute": {"raw": int(len(ei)), "cleaned": int(len(ei_c))},
    }
    for ds, log in (("ember", log_ember), ("eia", log_eia),
                    ("energy_institute", log_ei), ("cross_dataset", log_x)):
        summary[f"audit_{ds}"] = {
            "errors": log.count("error"),
            "warnings": log.count("warning"),
            "info": log.count("info"),
        }

    # 5. processed tables
    log_p = AuditLog("processed")
    processed = process.process(ember_c, eia_c, ei_c, log_p)
    logs.append(log_p)
    summary["audit_processed"] = {
        "errors": log_p.count("error"), "warnings": log_p.count("warning"),
        "info": log_p.count("info"),
    }
    for name, df in processed.items():
        summary["row_counts"][name] = int(len(df))

    _write_outputs({"ember_country_year.csv": ember_c,
                    "eia_us_coal.csv": eia_c,
                    "energy_institute_global_energy.csv": ei_c},
                   processed, logs, summary)

    # 6. report
    from .make_reports import write_reports
    write_reports(summary, processed, C.RAW, C.CLEANED, C.PROCESSED)

    print("pipeline complete.")
    print(f"  ember   : {summary['row_counts']['ember']['raw']:>6} -> "
          f"{summary['row_counts']['ember']['cleaned']} rows")
    print(f"  eia     : {summary['row_counts']['eia']['raw']:>6} -> "
          f"{summary['row_counts']['eia']['cleaned']} rows")
    print(f"  ei      : {summary['row_counts']['energy_institute']['raw']:>6} -> "
          f"{summary['row_counts']['energy_institute']['cleaned']} rows")
    for k, v in summary["row_counts"].items():
        if isinstance(v, int):
            print(f"  {k:35s} {v:>7} rows")
    for ds in ("ember", "eia", "energy_institute", "cross_dataset", "processed"):
        a = summary[f"audit_{ds}"]
        print(f"  audit[{ds:16s}] errors={a['errors']} warnings={a['warnings']} "
              f"info={a['info']}")
    return summary


def main() -> None:
    force = "--force-raw" in sys.argv
    run(force_raw=force)


if __name__ == "__main__":
    main()
