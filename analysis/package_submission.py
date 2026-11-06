"""Build a reviewable code/deliverable bundle and report unresolved submission inputs.

No account writes, fabricated recording, or inferred team identity. The ZIP
excludes source CSVs, environments, local settings, dependencies and caches.
Graders place the three original CSVs in the root, per README/MANIFEST.json.
"""
from __future__ import annotations
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"


def package():
    config = json.loads((OUT / "submission.json").read_text())
    record = json.loads((ROOT / "data/provenance/energy_institute.json").read_text())
    archive = OUT / "energy_transition_submission.zip"
    included = []
    fixed = ["README.md", "requirements.txt", "pyproject.toml", "conftest.py", ".gitignore", "data/raw/MANIFEST.json"]
    roots = ["src", "analysis", "tests", "data/provenance", "deliverables", "dashboard/src", "dashboard/scripts", "dashboard/public"]
    paths = {ROOT / name for name in fixed}
    for directory in roots:
        paths.update(p for p in (ROOT / directory).rglob("*") if p.is_file())
    paths.update(p for p in (ROOT / "dashboard").iterdir() if p.is_file())
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(paths):
            relative = p.relative_to(ROOT)
            if any(part in {"__pycache__", ".pytest_cache", "node_modules", ".venv", "dist"} for part in relative.parts): continue
            if p.suffix in {".zip", ".pyc", ".tsbuildinfo"} or "previews" in relative.parts: continue
            if relative.as_posix() in {"deliverables/SUBMISSION_STATUS.md", "deliverables/submission_bundle_files.txt"}: continue
            if not p.exists(): raise FileNotFoundError(p)
            z.write(p, relative.as_posix())
            included.append(relative.as_posix())
    unresolved = []
    if not config.get("members"): unresolved.append("Team/member names: supply them in deliverables/submission.json, then rebuild the deck.")
    if not config.get("repository_url"): unresolved.append("Repository publication: destination and account access not supplied; the local ZIP is ready to publish.")
    if not config.get("recording_path"): unresolved.append("Group recording: the group must record the eight main slides; no recording has been supplied.")
    if not config.get("youtube_url"): unresolved.append("Unlisted YouTube URL: upload the real recording and verify signed-out playback and runtime.")
    if not record.get("local_edition_verified") or not record.get("original_download_date"):
        unresolved.append("EI local-file provenance: exact original edition/date needs the download receipt or a fresh authenticated publisher download for comparison.")
    report = ["# Submission status", "", "## Prepared locally", "",
              "- Eight-slide main pitch, editable PPTX and PDF, speaker notes and timed script.",
              "- Global 2025 comparison, allocation cards, decision rules and separate country research.",
              "- Data dashboard, country directory, per-country CSV downloads and source-field audit.",
              "- energy_transition_submission.zip: code and deliverables, excluding raw source CSVs and machine-local files.",
              "", "## Inputs/actions still needed", ""] + [f"- {item}" for item in unresolved]
    report += ["", "Source access dates are not original download dates. A script is not a recorded group presentation. The archive is prepared locally. Repository publication is tracked in submission.json; this packaging command does not push commits or publish a video.", ""]
    (OUT / "SUBMISSION_STATUS.md").write_text("\n".join(report))
    included += ["deliverables/SUBMISSION_STATUS.md", "deliverables/submission_bundle_files.txt"]
    (OUT / "submission_bundle_files.txt").write_text("\n".join(sorted(included)) + "\n")
    with zipfile.ZipFile(archive, "a", compression=zipfile.ZIP_DEFLATED) as z:
        for name in ["SUBMISSION_STATUS.md", "submission_bundle_files.txt"]:
            z.write(OUT / name, "deliverables/" + name)
    print(f"Packaged {len(included)} files: {archive.name}; {len(unresolved)} submission inputs/actions remain")


if __name__ == "__main__":
    package()
