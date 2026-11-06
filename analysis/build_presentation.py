"""Build the eight-slide investment pitch and supporting thesis."""
from __future__ import annotations
import json
from pathlib import Path
from analysis.pitch_design import build_pitch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission"

def build():
    m = json.loads((OUT / "metrics.json").read_text())
    submission = json.loads((OUT / "submission.json").read_text())
    build_pitch(m, submission)
    from analysis.build_investment_memo import build_memo
    build_memo(m)
    (OUT / "README.md").write_text("""# Energy transition submission package

This is the single submission folder. START_HERE.md lists the presentation, scripts and dashboard demonstration.

Start with **energy_transition_pitch.pptx** (editable deck) or its PDF export,
then EXECUTIVE_SUMMARY.md, INVESTMENT_THESIS.md and PRESENTER_GUIDE.md.
PRESENTATION_SCRIPT.md and SPEAKER_CUE_CARDS.md support delivery.
The deck contains eight main slides plus five evidence appendix slides, with a 6:15 main-pitch speaking plan. Detailed country
research stays in separate reference materials.

- COUNTRY_REVIEW.md links all 213 country profiles. `figures/country_*.png`
  contains the 16 material-market reviews, including all eight original core markets.
- `figures/` has PNG and SVG exports; `tables/` has calculation inputs,
  fixed-panel membership, country chart priorities and claim lineage.
- PROJECT_AUDIT.md explains corrections and limitations; SOURCES.md records
  external checks and outstanding provenance gaps.
- SUBMISSION_CHECKLIST.md lists recording, YouTube and repository actions
  that require the group's participation/accounts.

Rebuild from the repository root after installing requirements.txt:

```bash
python -m src.pipeline
python -m analysis.build_deliverables
python -m analysis.build_presentation
libreoffice --headless --convert-to pdf --outdir submission submission/energy_transition_pitch.pptx
```

The PDF step requires LibreOffice. Python generates PPTX, tables and figures
without it. No web service is required for rebuilding the analysis.
""")


if __name__ == "__main__":
    build()
