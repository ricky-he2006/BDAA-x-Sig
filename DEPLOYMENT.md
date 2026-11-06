# Deploy Energy Atlas

The dashboard is a static site. All JSON, evidence downloads, maps and globe
textures are committed under dashboard/public and copied into the build.
No API key, database, Python runtime or backend is needed to host it.

## Vercel

Import this GitHub repository into Vercel. Keep the project root at the
repository root. The committed vercel.json configures installation, build
and output (dist/). Deploy the main branch; later pushes trigger rebuilds.

If the existing Vercel project uses dashboard as its Root Directory,
dashboard/vercel.json supplies npm ci, npm run build and dist as the output.
Clear any old install/build/output overrides in Vercel Project Settings so
the selected directory’s configuration applies. Both root configurations
are supported. Node is pinned to the 22.x major version.

## Netlify

Import this GitHub repository into Netlify. Keep the base directory at the
repository root. netlify.toml supplies the build command and publish folder.

## Build or host elsewhere

Use Node.js 22.12 or newer and run from the repository root:

```bash
npm ci --prefix dashboard
npm run build --prefix dashboard
npm run preview --prefix dashboard -- --host 0.0.0.0
```

Publish the contents of dashboard/dist at the site's root path. The preview
server is for local verification. This configuration uses root-relative data
URLs; a GitHub Pages project subdirectory is not supported by this setup.
A host must return a real 404 for missing data files rather than HTML.

## Refresh the data

The three original CSVs are committed at the root and copied unchanged into
data/raw, where MANIFEST.json records their hashes. The processed tables and
browser exports are also committed, so deployment does not need to regenerate
them. Source attribution and the unresolved original EI vintage are documented
in deliverables/SOURCES.md and data/provenance/energy_institute.json. No license
for the third-party datasets is asserted by this repository.

To rebuild research and refresh dashboard exports:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m src.pipeline
.venv/bin/python -m analysis.build_deliverables
.venv/bin/python -m analysis.build_presentation
.venv/bin/python dashboard/scripts/export_dashboard_data.py
.venv/bin/python -m pytest -q
.venv/bin/python -m analysis.verify_dashboard_data
npm test --prefix dashboard
npm run build --prefix dashboard
```

Presentation PDF export additionally requires LibreOffice. Browser acceptance
checks additionally require Playwright and Chromium; see deliverables/VERIFICATION.md.
Rebuild the PDF after rebuilding the PowerPoint before running verify_pitch.
The submission/ folder is a presentation handoff copy; refresh it from the
canonical deliverables/ files when changing the presentation.

GitHub Actions validates source/data tests, dashboard data, deck chart parity,
and the dashboard build, then saves the static-site build as a workflow artifact.
Deploying to Vercel or Netlify still requires connecting the repository in that
hosting account; pushing the repository alone does not create a hosted URL.
