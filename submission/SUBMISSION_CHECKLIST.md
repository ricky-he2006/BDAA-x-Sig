# Submission and recording checklist

## Prepared in this repository

- Audited evidence tables and claim-to-calculation references.
- An explicit industry allocation recommendation, horizon, risk triggers and scope.
- Individual reviews for all 213 Ember geographies; detailed figures for all 16 material coal/clean markets, including the eight existing core markets.
- Eight-slide presentation, matching script, presenter guide and speaker cue cards. Country and methodology references remain separate.
- Exportable PNG/SVG charts and reproducible Python code.
- Additional diagnostics in the existing country explorer.

## Team actions still required

Current unresolved inputs are tracked in `SUBMISSION_STATUS.md`. Put team names,
repository URL, recording path and YouTube URL in `submission.json`; rebuild the
deck after entering names. The ZIP builder prepares files locally and does not
publish to accounts or produce a recording of the group.

1. Confirm team names and assign speakers. Suggested split: speaker A slides 1–2, B slides 3–4, C slides 5–6, D slides 7–8; combine for smaller teams.
2. Rehearse the eight-slide deck at roughly six minutes. Use separate country research for follow-up questions. Check the actual recording length; seven minutes is a hard cap.
3. Record your group presenting with the final slides, readable charts and clear audio. The script is preparation, not a substitute for the required group video.
4. Upload the actual recording to YouTube, choose **Unlisted**, copy its watch URL, and verify playback while signed out. No video is uploaded by this project build.
5. Document the EI file's original download/edition if available. If unavailable, disclose that exact-vintage verification is incomplete.
6. Publish the source repository under your account. The configured destination is https://github.com/ricky-he2006/BDAA-x-Sig; verify the final pushed repository and its Actions checks. Exclude `.venv`, `node_modules`, secrets and machine-local files. Check data redistribution terms before publishing source CSVs; otherwise document how graders obtain the supplied files.
7. Run the reproduction commands in README from a clean environment, open the PPTX/PDF, and check slide labels, units, sources and team names.
8. Put the deck link, unlisted video URL and repository URL in the submission. Verify all links with another group member.

Optional enhancements that require more data: valuations for investable baskets,
developer margins, actual coal trade flows, gas prices, grid constraints and
project economics. They are not silently inferred from generation trends.
