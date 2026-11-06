"""Pipeline-level guarantees: raw integrity, determinism, report presence."""
import hashlib
from pathlib import Path

import pytest

from src import config as C


def _hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_raw_files_preserved():
    """data/raw must match the originals byte-for-byte (manifest pinned)."""
    import json
    manifest = json.loads((C.RAW / "MANIFEST.json").read_text())
    for name, m in manifest.items():
        orig = C.ROOT / name
        copy = C.RAW / name
        assert _hash(orig) == m["sha256"], f"original changed: {name}"
        assert _hash(copy) == m["sha256"], f"raw copy differs: {name}"


def test_outputs_exist(pipeline_outputs):
    for f in (C.CLEANED / C.CLEANED_EMBER, C.CLEANED / C.CLEANED_EIA,
              C.CLEANED / C.CLEANED_EI):
        assert f.exists(), f
    for name in (C.PROCESSED_COUNTRY_YEAR, C.PROCESSED_US_STATE,
                 C.PROCESSED_EIA_AGGREGATES, C.PROCESSED_COVERAGE):
        assert (C.PROCESSED / name).exists(), name
    for f in (C.REPORTS / "data_quality_report.md",
              C.REPORTS / "cleaning_log.csv",
              C.REPORTS / "data_dictionary.md"):
        assert f.exists(), f


def test_cleaning_log_fields(pipeline_outputs):
    import pandas as pd
    log = pd.read_csv(C.REPORTS / "cleaning_log.csv")
    for col in ("dataset", "check_id", "severity", "action", "record",
                "detail"):
        assert col in log.columns
    assert set(log.severity) <= {"error", "warning", "info"}
    assert set(log.action) <= {"keep", "flag", "correct", "drop", "verify"}
    # the pipeline found no error-severity entries that it acted on by dropping
    # without a record:
    drops = log[log.action == "drop"]
    assert (drops.record.notna()).all()


def test_idempotent_rerun(pipeline_outputs):
    """Running the pipeline again must produce byte-identical outputs."""
    from src import pipeline

    files = [C.CLEANED / C.CLEANED_EMBER, C.CLEANED / C.CLEANED_EIA,
             C.CLEANED / C.CLEANED_EI,
             C.PROCESSED / C.PROCESSED_COUNTRY_YEAR,
             C.PROCESSED / C.PROCESSED_US_STATE,
             C.PROCESSED / C.PROCESSED_EIA_AGGREGATES,
             C.PROCESSED / C.PROCESSED_COVERAGE,
             C.REPORTS / "cleaning_log.csv"]
    before = {str(f): _hash(f) for f in files}
    pipeline.run()
    after = {str(f): _hash(f) for f in files}
    assert before == after, "pipeline is not deterministic"
