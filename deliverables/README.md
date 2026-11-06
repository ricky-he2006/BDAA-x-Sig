# Energy transition submission package

Start with **energy_transition_pitch.pptx** (editable deck) or its PDF export,
then EXECUTIVE_SUMMARY.md, INVESTMENT_THESIS.md and PRESENTER_GUIDE.md.
PRESENTATION_SCRIPT.md and SPEAKER_CUE_CARDS.md support delivery.
[DASHBOARD_WALKTHROUGH.md](DASHBOARD_WALKTHROUGH.md) provides the full post-slide
dashboard demonstration: exact clicks, chart sequence, speaking script and question references.
The deck contains eight slides total, with a 6:15 speaking plan. Detailed country
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
libreoffice --headless --convert-to pdf --outdir deliverables deliverables/energy_transition_pitch.pptx
```

The PDF step requires LibreOffice. Python generates PPTX, tables and figures
without it. No web service is required for rebuilding the analysis.
