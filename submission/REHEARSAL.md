# Presenter guide and rehearsal

The deck has **eight main slides and 10 evidence appendix slides**. Use the appendix for judging questions or a separate evidence review. Detailed country
research remains in the dashboard and COUNTRY_REVIEW.md. Present the investment
argument; use the repository for follow-up questions.

## Timing and handoffs

The eight-slide main script has **805 spoken words** and a **6:15** plan. Appendix narration for slides 9–18 is included separately in PRESENTATION_SCRIPT.md and adds time. The main pitch runs at about 129
words per minute. Reserve 10–15 seconds for speaker handoffs. Rehearse aloud and
measure the actual recording; keep it below the seven-minute cap.

| Speaker | Slides | Content |
|---|---|---|
| A | 1–2 | Recommendation and aggregate evidence |
| B | 3–4 | Market context and the 2025 signal |
| C | 5–6 | Counterargument and allocation |
| D | 7–8 | Reversal conditions and closing decision |

Adjust the split for your group. The script's final sentence on each topic
prepares the next; keep handoffs to a brief name or a pause. Do not add a new
introduction every time the speaker changes.

## Delivery

- Start with the call. Say “overweight clean energy” and “underweight coal” clearly.
- Explain each chart's meaning before listing numbers. Point to the line or bar.
- On slide 3, use three examples to establish geographic scope; avoid a country tour.
- On slide 4, distinguish the Ember electricity panel from EI coal generation.
- On slide 5, give the coal rebound a fair hearing. It limits conviction in the call.
- On slide 6, explain the investment judgment; avoid suggesting the data proves stock returns.
- On slide 7, name what would change your view. The thresholds are analyst rules.
- On slide 8, repeat both positions and the three-year horizon, then stop.

If you run long, remove supporting adjectives and secondary numbers. Keep the
recommendation, main evidence, 2025 coverage caveat, strongest counterargument
and reversal conditions. The full script is rehearsal material; cue cards are
for delivery. Neither establishes a measured recording duration.

## Likely questions and concise answers

**Why underweight coal after a rebound?** U.S. power coal consumption fell 14.4%
through 2024 and rose 11.3% in 2025. The rebound lowers conviction. Our call is
focused on domestic thermal exposure, with an explicit persistence trigger.

**Does clean growth prove attractive stock returns?** No. The industry preference
is a forward-looking judgment. Security selection still requires valuations,
project returns, contract economics and financing data.

**Are the 2025 numbers global?** The Ember panel contains 91 fixed countries and
93.5% of generation observed in the 2024 extract, not 93.5% of the world. EI's
world coal number uses its WLD row alone; country changes are shown separately.

**Why use a pandemic-affected 2020 baseline?** The same panel's 2021–2024 clean
growth was 18.8% versus 4.2% for all fossil. The faster clean growth persists under that baseline;
these endpoint growth rates are not annual forecasts.

**Does the data identify why coal changed?** No. Generation changes and accounting
identities do not establish policy, weather, fuel-price or grid causality.

**What about exporters or metallurgical coal?** The U.S. thermal-power call cannot
be extended automatically to other business models. Production-versus-generation
divergence does not establish export flows.

**How certain is the third dataset's provenance?** The local file is hash-pinned.
The official EI catalogue and its current edition were checked, but the exact
original local download edition/date remain unverified. State that limitation;
do not substitute the catalogue access date for the original download date.

## Claims to avoid

- A durable global fossil peak has been proven.
- The matched Ember panel represents 93.5% of world electricity.
- Clean generation growth guarantees equity outperformance.
- Delivered fuel prices establish coal-producer profitability.
- Grid constraints or coal exports were measured by these datasets.

## Sources and tools

The two assignment extracts supply Ember electricity and EIA coal observations;
the local Energy Institute file supplies coal-specific country/world context.
Full lineage: tables/claim_evidence.csv, SOURCES.md and PROJECT_AUDIT.md.
Python/pandas generated the evidence; matplotlib generated charts; python-pptx
generated the editable deck; React/TypeScript/ECharts power the dashboard.

## Before recording

Enter actual names in submission.json, rebuild, and check the PDF. Record the
real group with readable slides and clear audio. Verify the actual runtime,
upload as Unlisted, and check signed-out playback. No recording or account upload
is performed by the deck generator.
