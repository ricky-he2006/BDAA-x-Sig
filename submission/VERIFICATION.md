# Verification

Checked 6 November 2026.

- Python validation and analysis tests: **62 passed**. Checks include raw-file integrity, pipeline determinism, aggregate separation, missing-data handling, fixed membership, country demand identities, pathway thresholds, independent source years, provenance integrity, 2025 coal comparisons and all plotted fields.
- Dashboard tests: **92 passed**; TypeScript typecheck and production build pass. Coverage includes partial country sidebars, the directory's source/year filtering and country CSV formatting. See DASHBOARD_AUDIT.md for the expanded data and browser audit.
- Chromium browser: all eight existing focus countries, all five research tabs, the new chart cards, 2025 selection and dark theme exercised. **No page runtime errors** in the final run. Results and screenshots are in `previews/`.
- Globe rendering was visually checked. Fixed a missing polygon-geometry field and conflicting Three.js instances; a single pinned Three.js version now serves the globe dependencies.
- PPTX converted to PDF with LibreOffice. All eight redesigned slides rendered and visually reviewed. Charts, recommendation cards and decision rules use a consistent layout; every slide has full speaker notes. The deck has no appendix.
- Artifact checks validate input hashes, 213 country review files, 16 detailed country figures in both formats, claim table references, fixed panel memberships and shape boundaries. Machine results: `verification.json`.
- Speaking plan: **782 words / 6:15**. This is a rehearsal plan, not a measured recording. See REHEARSAL.md; the group must verify actual runtime against the seven-minute cap.

Run:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m analysis.verify_submission
cd dashboard
npm run typecheck
npm test
npm run build
```

Optional browser verification requires Playwright and Chromium installed in the
Python environment. Start Vite, then run from the repository root:

```bash
.venv/bin/python dashboard/scripts/check_browser.py http://127.0.0.1:5173
```

Remaining limitations: exact original EI download edition is unrecorded;
current official source figures differ in scope/vintage; no equity valuation
or return model is included. Repository publication and a recorded/unlisted
YouTube video remain team actions. See SOURCES.md and SUBMISSION_CHECKLIST.md.

Deployment preparation: Node.js 22.12+; Vite 8.3.6, Vitest 5.1.0 and ECharts
6.1.0. Updated dependencies pass all 92 dashboard tests and production build.
The package-lock audit reports zero known vulnerabilities at preparation time.
Hosting configuration is included for Vercel and Netlify; see ../DEPLOYMENT.md.
