#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_VERSION = "20260819-epic-passport2"
START = "<!-- EPIC-PASSPORT-RULES:START -->"
END = "<!-- EPIC-PASSPORT-RULES:END -->"


def write_if_changed(path: Path, content: str, check: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8")
    if current == content:
        return
    changed.append(path)
    if not check:
        path.write_text(content, encoding="utf-8")


def normalize_assets(path: Path, prefix: str, check: bool, changed: list[Path]) -> None:
    text = path.read_text(encoding="utf-8")
    css = f'{prefix}assets/phase6.css?v={ASSET_VERSION}'
    js = f'{prefix}assets/phase6.js?v={ASSET_VERSION}'
    updated = re.sub(
        r'<link\s+rel="stylesheet"\s+href="[^\"]*assets/phase6\.css(?:\?v=[^\"]*)?">',
        f'<link rel="stylesheet" href="{css}">', text,
    )
    updated = re.sub(
        r'<script\s+src="[^\"]*assets/phase6\.js(?:\?v=[^\"]*)?"></script>',
        f'<script src="{js}"></script>', updated,
    )
    write_if_changed(path, updated, check, changed)


def remove_public_pdf_download(path: Path, check: bool, changed: list[Path]) -> None:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'\s*<div\s+class="cta-row\s+episode-pdf-action-static"[^>]*>.*?</div>',
        '', text, flags=re.S,
    )
    updated = re.sub(
        r'\s*<!--\s*If an approved PDF is published, add the standardized static episode-pdf-action-static CTA after the metric\.\s*-->',
        '', updated,
    )
    updated = re.sub(
        r'\s*<a\b[^>]*href="[^\"]*assets/pdf/episodes/[^\"]+\.pdf"[^>]*>.*?</a>',
        '', updated, flags=re.S | re.I,
    )
    write_if_changed(path, updated, check, changed)


def remove_registry_pdf_fields(check: bool, changed: list[Path]) -> None:
    path = ROOT / "episodes.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    modified = False
    for episode in data.get("episodes", []):
        if "pdf" in episode:
            del episode["pdf"]
            modified = True
    if not modified:
        return
    content = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    write_if_changed(path, content, check, changed)


def update_readme(check: bool, changed: list[Path]) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")

    # Section 30 is canonical, but keep the older Phase 6 wording aligned so
    # the preceding synchronization step cannot reintroduce retired exports.
    text = text.replace(
        "A text download may be generated client-side from the same registered fields. The downloaded passport is a convenience summary, not a verification statement, formal data-quality rating or replacement for the approved episode.",
        "The user-facing export is the visual Epic Passport through `Print / Save as PDF`. Raw-text export is retired, and the original episode PDF is not exposed as a website download."
    )
    text = text.replace(
        "- [ ] Downloaded passport text contains the canonical episode URL and the interpretation disclaimer.\n",
        "- [ ] Printed/saved Passport retains the canonical episode URL and the interpretation disclaimer.\n"
    )

    block = f'''{START}

## 30. Epic Model Passport presentation — mandatory

The canonical Model Passport presentation is the **Epic Passport**. This rule extends Section 29 without changing its data-governance constraints.

Every published episode exposes only two Passport actions:

1. `View epic passport →` — opens the full-screen technical dossier;
2. `Print / Save as PDF` — uses the dedicated A4 print layout defined in `assets/phase6.css`.

The former raw-text export is retired. The original episode PDF is also no longer a public website download: episode pages, the episode template and `episodes.json` must not expose or link a source PDF. Source PDF artefacts may remain in the repository as editorial/technical archive material, but they are not part of the public website navigation or registry contract.

The Epic Passport uses the registered episode cover and the existing registry fields only. Its visual language is dark technical/blueprint with cyan accents, restrained gold, archive-record identifiers, evidence blocks and a traceability seal. It must feel epic and collectible without weakening methodological readability.

No visual element may introduce an unregistered system boundary, factor list, allocation rule, assumption or numerical value. The Passport remains a transparency summary, not a verification statement or formal data-quality rating.

The shared implementation in `assets/phase6.js` and `assets/phase6.css` applies to all currently published and future episode pages. `scripts/epic_passport_sync.py` propagates the current versioned assets, removes legacy PDF download CTAs and removes legacy `pdf` fields from the public registry.

### Epic Passport QA

- [ ] All episode pages reference the current versioned Phase 6 assets.
- [ ] Full-screen Passport includes registered cover, episode number/title/category/LCA lens and headline result.
- [ ] Reporting basis, hotspot and Evidence Profile remain visible.
- [ ] Evidence basis and main modelling uncertainty remain visible.
- [ ] `Print / Save as PDF` uses the dedicated A4 print stylesheet.
- [ ] No raw-text Passport export is exposed.
- [ ] No episode page or episode template exposes a source-PDF download link.
- [ ] `episodes.json` contains no public `pdf` field.
- [ ] Mobile Passport remains readable with no unintended page overflow.

{END}'''
    pattern = rf"{re.escape(START)}.*?{re.escape(END)}"
    if re.search(pattern, text, flags=re.S):
        updated = re.sub(pattern, block, text, flags=re.S)
    else:
        updated = text.rstrip() + "\n\n---\n\n" + block + "\n"
    write_if_changed(path, updated, check, changed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed: list[Path] = []

    for path in sorted((ROOT / "episodes").glob("*.html")):
        normalize_assets(path, "../", args.check, changed)
        remove_public_pdf_download(path, args.check, changed)
    for name in ["explore.html", "method.html"]:
        normalize_assets(ROOT / name, "", args.check, changed)

    remove_registry_pdf_fields(args.check, changed)
    update_readme(args.check, changed)

    if changed:
        for path in changed:
            print(f"Epic Passport {'would update' if args.check else 'updated'}: {path.relative_to(ROOT)}")
        return 1 if args.check else 0
    print("Epic Passport is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
