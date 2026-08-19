#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
CURRENT_ASSET_VERSION = "20260819-epic-passport3"
CLEANUP_VERSION = "20260819-passport-cleanup1"


def fail(message: str) -> None:
    errors.append(message)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"Missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def check_episode_assets_and_exports() -> None:
    for path in sorted((ROOT / "episodes").glob("*.html")):
        text = read(path)
        if f"../assets/phase6.css?v={CURRENT_ASSET_VERSION}" not in text:
            fail(f"{path.relative_to(ROOT)}: current Epic Passport CSS missing")
        if f"../assets/phase6.js?v={CURRENT_ASSET_VERSION}" not in text:
            fail(f"{path.relative_to(ROOT)}: current Epic Passport JS missing")
        if f"../assets/passport-cleanup.js?v={CLEANUP_VERSION}" not in text:
            fail(f"{path.relative_to(ROOT)}: defensive export-cleanup JS missing")
        if "episode-pdf-action-static" in text or "assets/pdf/episodes/" in text:
            fail(f"{path.relative_to(ROOT)}: legacy source-PDF download is still exposed")


def check_registry_basis() -> None:
    data = json.loads(read(ROOT / "episodes.json") or "{}")
    for episode in data.get("episodes", []):
        number = episode.get("number")
        if "pdf" in episode:
            fail(f"Episode #{number}: public registry must not expose a pdf field")
        for key in ["title", "cover", "categoryLabel", "functionalUnit", "result", "lcaLabel", "hotspot"]:
            if not episode.get(key):
                fail(f"Episode #{number}: Epic Model Passport requires {key}")
        evidence = episode.get("evidence") or {}
        for key in ["confidence", "proxyDependence", "assumptionSensitivity", "basis", "uncertainty"]:
            if not evidence.get(key):
                fail(f"Episode #{number}: Epic Model Passport requires evidence.{key}")


def check_phase6_js() -> None:
    text = read(ROOT / "assets/phase6.js")
    required = [
        "MODEL PASSPORT", "View epic passport", "Print / Save as PDF",
        "passport-sheet", "passport-overlay", "window.print", "episode.cover",
        "functionalUnit", "result", "lcaLabel", "hotspot", "categoryLabel",
        "proxyDependence", "assumptionSensitivity", "basis", "uncertainty",
        "MutationObserver",
    ]
    for token in required:
        if token not in text:
            fail(f"assets/phase6.js: required implementation token missing: {token}")
    for token in ["Raw text", "downloadRawPassport", "passport-raw", "systemBoundary:", "factorList:", "allocationRule:"]:
        if token in text:
            fail(f"assets/phase6.js: retired or fabricated implementation token detected: {token}")


def check_cleanup_js() -> None:
    text = read(ROOT / "assets/passport-cleanup.js")
    for token in ["episode-pdf-action-static", "assets/pdf/episodes/", "MutationObserver"]:
        if token not in text:
            fail(f"assets/passport-cleanup.js: required cleanup token missing: {token}")
    if "raw text" not in text.lower():
        fail("assets/passport-cleanup.js: raw-text cleanup guard missing")


def check_phase6_css() -> None:
    text = read(ROOT / "assets/phase6.css")
    for token in [".passport-sheet", ".passport-overlay", ".passport-seal", "@media print", "A4 portrait", "print-color-adjust"]:
        if token not in text:
            fail(f"assets/phase6.css: epic/print style missing: {token}")


def check_template() -> None:
    text = read(ROOT / "episodes/template.html")
    if "episode-pdf-action-static" in text or "assets/pdf/episodes/" in text:
        fail("episodes/template.html: legacy source-PDF download guidance remains")


def check_readme() -> None:
    text = read(ROOT / "README.md")
    forbidden = [
        "PDF availability",
        "automatic PDF download actions",
        "navigation/download metadata",
        "episode PDF action",
        "approved downloadable episode carousels",
        "Download episode PDF",
        "Optional field:\n\n- `pdf`",
        "before adding the registry `pdf` field",
        "A text download may be generated client-side",
        "Downloaded passport text contains",
        "## 16. PDF publishing system",
        "PDF availability is **registry-declared**",
        "### PDF download",
        "Live PDF action tested",
        "including `pdf` only after",
        "PDF download buttons are static HTML",
        "A `pdf` registry field is allowed",
        "No broken PDF link is acceptable",
        "any registered PDF download must be checked",
    ]
    for token in forbidden:
        if token in text:
            fail(f"README.md: legacy public-export rule remains: {token}")

    source_note = "The approved PDF is an editorial/technical source, not a public website download."
    if text.count(source_note) != 1:
        fail(f"README.md: source-PDF note must appear exactly once in the introduction; found {text.count(source_note)}")

    required = [
        "## 16. Source PDF archival policy — mandatory",
        "The public registry must **not** contain a `pdf` field",
        "The only episode export is the Epic Model Passport through `Print / Save as PDF`.",
        "## 20. Controlled publishing workflow",
        "**Do not add a `pdf` field.**",
        "**The Epic Model Passport is the only public episode-level export",
        "Source PDF artefacts may remain in the repository as editorial/technical archive material",
        "No raw-text Passport export is exposed.",
    ]
    for token in required:
        if token not in text:
            fail(f"README.md: canonical Passport-only rule missing: {token}")


def check_explore() -> None:
    text = read(ROOT / "explore.html")
    if "assets/phase6.css" not in text or "assets/phase6.js" not in text:
        fail("explore.html: Phase 6 assets missing")
    if "Do not read this as a ranking" not in text:
        fail("explore.html: non-comparability warning missing")


def check_method() -> None:
    text = read(ROOT / "method.html")
    for token in ["METHODOLOGY VERSION", "Methodology version 1.0", "Updated August 2026", "v1.0 · Aug 2026"]:
        if token not in text:
            fail(f"method.html: versioning token missing: {token}")
    if "assets/phase6.css" not in text:
        fail("method.html: Phase 6 CSS missing")


def main() -> int:
    for path in [
        ROOT / "assets/phase6.css",
        ROOT / "assets/phase6.js",
        ROOT / "assets/passport-cleanup.js",
        ROOT / "scripts/phase6_sync.py",
        ROOT / "scripts/epic_passport_sync.py",
    ]:
        if not path.is_file():
            fail(f"Missing Phase 6 file: {path.relative_to(ROOT)}")

    check_episode_assets_and_exports()
    check_registry_basis()
    check_phase6_js()
    check_cleanup_js()
    check_phase6_css()
    check_template()
    check_readme()
    check_explore()
    check_method()

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nPhase 6 QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Phase 6 Epic Model Passport QA passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
