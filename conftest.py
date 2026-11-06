"""Root conftest: makes `src` importable and provides the pipeline fixture."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def pipeline_outputs():
    """Run the full cleaning pipeline once; return (summary, in-memory tables)."""
    import pandas as pd
    from src import pipeline

    summary = pipeline.run()
    cleaned = {
        "ember": pd.read_csv(pipeline.C.CLEANED / pipeline.C.CLEANED_EMBER),
        "eia": pd.read_csv(pipeline.C.CLEANED / pipeline.C.CLEANED_EIA),
        "ei": pd.read_csv(pipeline.C.CLEANED / pipeline.C.CLEANED_EI),
    }
    processed = {
        name: pd.read_csv(pipeline.C.PROCESSED / name)
        for name in (
            pipeline.C.PROCESSED_COUNTRY_YEAR,
            pipeline.C.PROCESSED_US_STATE,
            pipeline.C.PROCESSED_EIA_AGGREGATES,
            pipeline.C.PROCESSED_COVERAGE,
        )
    }
    return {"summary": summary, "cleaned": cleaned, "processed": processed}
