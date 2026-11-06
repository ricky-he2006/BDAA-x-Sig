"""Shared helpers for the research analysis scripts (analysis/*.py)."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import config as C  # noqa: E402

OUT = ROOT / "analysis" / "output"
OUT.mkdir(parents=True, exist_ok=True)


def load_country_year() -> pd.DataFrame:
    return pd.read_csv(C.PROCESSED / C.PROCESSED_COUNTRY_YEAR)


def load_us_state() -> pd.DataFrame:
    return pd.read_csv(C.PROCESSED / C.PROCESSED_US_STATE)


def load_eia_aggregates() -> pd.DataFrame:
    return pd.read_csv(C.PROCESSED / C.PROCESSED_EIA_AGGREGATES)


def load_eia_clean() -> pd.DataFrame:
    return pd.read_csv(C.CLEANED / C.CLEANED_EIA)


def save_csv(df: pd.DataFrame, name: str) -> Path:
    """Save to analysis/output/. A named index (year, state_code, ...) is
    carried over as a column so no row label is silently dropped; a plain
    positional index is not."""
    out = df if df.index.name is None else df.reset_index()
    p = OUT / name
    p.write_text(out.to_csv(index=False, lineterminator="\n"), encoding="utf-8")
    return p


def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    """Markdown table. A named index (year, state_code, ...) is shown as a
    column; a plain positional index is not."""
    d = df.head(max_rows)
    include = d.index.name is not None
    try:
        return d.to_markdown(index=include)
    except ImportError:
        return "```\n" + d.to_string(index=include) + "\n```"


def write_md(name: str, sections: list[tuple[str, str]]) -> None:
    """sections: list of (heading, body). Appends to analysis/output/<name>."""
    p = OUT / name
    parts = ["# " + name.removesuffix(".md"), ""]
    for h, body in sections:
        parts.append(f"## {h}\n\n{body}\n")
    p.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"wrote {p}")
