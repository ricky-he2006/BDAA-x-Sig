"""Audit-log infrastructure shared by all cleaning modules.

Every observation we drop, correct, or flag is recorded as an AuditEntry so
that the full trail lands in reports/cleaning_log.csv.
"""
from __future__ import annotations

import hashlib
import pandas as pd

SEVERITIES = ("error", "warning", "info")
ACTIONS = ("keep", "flag", "correct", "drop", "verify")

REQUIRED_LOG_FIELDS = [
    "dataset", "check_id", "severity", "action", "record", "field",
    "detail", "before", "after",
]


class AuditLog:
    """Accumulates record-level audit entries; deterministic ordering."""

    def __init__(self, dataset: str):
        self.dataset = dataset
        self.entries: list[dict] = []

    def add(self, check_id: str, severity: str, action: str, record: str,
            field: str = "", detail: str = "", before: str = "", after: str = "") -> None:
        assert severity in SEVERITIES, f"bad severity {severity!r}"
        assert action in ACTIONS, f"bad action {action!r}"
        self.entries.append({
            "dataset": self.dataset,
            "check_id": check_id,
            "severity": severity,
            "action": action,
            "record": record,
            "field": field,
            "detail": detail,
            "before": before,
            "after": after,
        })

    def as_frame(self) -> pd.DataFrame:
        df = pd.DataFrame(self.entries, columns=REQUIRED_LOG_FIELDS)
        if df.empty:
            return df
        return df.sort_values(
            ["dataset", "severity", "check_id", "record", "field"],
            kind="mergesort",
        ).reset_index(drop=True)

    def count(self, severity: str | None = None) -> int:
        if severity is None:
            return len(self.entries)
        return sum(1 for e in self.entries if e["severity"] == severity)


def sha256_of_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_sort(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Deterministic, stable sort used for every output table."""
    return df.sort_values(by, kind="mergesort").reset_index(drop=True)


def write_deterministic_csv(df: pd.DataFrame, path) -> None:
    """CSV writer with fixed options so repeated runs are byte-identical."""
    df.to_csv(
        path,
        index=False,
        float_format=None,      # full repr precision; deterministic
        lineterminator="\n",
        encoding="utf-8",
    )
