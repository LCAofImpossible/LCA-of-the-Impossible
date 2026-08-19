#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_VERSION = "20260819-epic-passport3"
CLEANUP_VERSION = "20260819-passport-cleanup1"
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


def ensure_cleanup_asset(path: Path, prefix: str, check: bool, changed: list[Path]) -> None:
    text = path.read_text(encoding="utf-8")
    cleanup = f'{prefix}assets/passport-cleanup.js?v={CLEANUP_VERSION}'
    pattern = r'<script\s+src="[^\"]*assets/passport-cleanup\.js(?:\?v=[^\"]*)?"></script>'
    if re.search(pattern, text):
        updated = re.sub(pattern, f'<script src="{cleanup}"></script>', text)
    else:
        marker = text.rfind('</body>')
        if marker == -1:
            raise RuntimeError(f"Missing </body> in {path}")
        updated = text[:marker] + f'<script src="{cleanup}"></script>\n' + text[marker:]
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
        r'\s*<a\b[^>]*href="[^\"]*assets/pdf/episodes/[^\"]+\.pdf(?:\?[^\"]*)?"[^>]*>.*?</a>',
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


def replace_section(text: str, number: int, replacement: str, next_anchor: str) -> str:
    pattern = rf"## {number}\..*?(?=\n---\n\n{re.escape(next_anchor)})"
    return re.sub(pattern, replacement.rstrip(), text, flags=re.S)


def clean_legacy_readme(text: str) -> str:
    """Collapse the historical PDF-download model into one Passport-only contract."""
    source_sentence = "If a new approved episode PDF and this repository are available, the website episode and its catalogue metadata must be rebuildable without relying on memory."
    source_note = "The approved PDF is an editorial/technical source, not a public website download."
    text = re.sub(
        re.escape(source_sentence) + rf"(?: {re.escape(source_note)})*",
        source_sentence + " " + source_note,
        text,
    )

    replacements = {
        "**An explicitly user-approved replacement image** — overrides the PDF cover only when the user has specifically selected it as the catalogue cover.":
            "**An explicitly user-approved replacement image** — overrides the source PDF/carousel cover only when the user has specifically selected it as the catalogue cover.",
        "**`episodes.json`** — canonical website registry for published episode metadata, ordering, catalogue assets, PDF availability, taxonomy, related cases and navigation relationships.":
            "**`episodes.json`** — canonical website registry for published episode metadata, ordering, catalogue assets, taxonomy, Evidence Profile data, related cases and navigation relationships. It must not contain public source-PDF fields.",
        "**`assets/site.js`** — source of truth for registry-driven homepage/archive rendering, text-only episode heroes, automatic PDF download actions, Related Cases and Previous/Next behaviour.":
            "**`assets/site.js`** — source of truth for registry-driven homepage/archive rendering, text-only episode heroes, Related Cases and Previous/Next behaviour.",
        "- `episodes.json` — central episode registry and navigation/download metadata":
            "- `episodes.json` — central episode registry, taxonomy, evidence and navigation metadata; no public source-PDF fields",
        "- `assets/pdf/episodes/` — approved downloadable episode carousels":
            "- `assets/pdf/episodes/` — optional editorial/technical archive for approved source PDFs; these files are not exposed by the public website",
        "`episodes.json` is the single catalogue record used by the homepage, full archive, episode PDF action and episode-to-episode navigation.":
            "`episodes.json` is the single catalogue record used by the homepage, full archive, Evidence Profile / Epic Passport data and episode-to-episode navigation.",
        "- `epNN-short-slug.pdf` — approved downloadable carousel.":
            "- `epNN-short-slug.pdf` — optional approved source PDF retained only as editorial/technical archive material; never linked from the public site or registry.",
        "Canonical PDF naming must be stable and simple. Do not publish PDFs with temporary suffixes such as `(1)`, `rev-final`, `v2`, `copy` or similar. Normalize them to `epNN-short-slug.pdf` before adding the registry `pdf` field.":
            "If a source PDF is retained in the repository archive, use a stable canonical name such as `epNN-short-slug.pdf`. Do not expose it through episode pages, navigation, `episodes.json`, metadata or public download controls.",
        "- static **Download episode PDF ↓** action when the registry contains a valid `pdf` field and the PDF exists in the repository.":
            "- no source-PDF download action. The only episode export is the Epic Model Passport through `Print / Save as PDF`.",
        "The PDF button is intentionally hard-coded in the individual episode HTML so it remains visible even if JavaScript is cached, blocked or unavailable. Use the standardized wording and button class defined in this README.":
            "Do not hard-code or dynamically inject links to the source episode PDF. Legacy source-PDF controls must be removed by synchronization and defensively suppressed by `assets/passport-cleanup.js`.",
        "- PDF button text clearly states that the action downloads the episode PDF.":
            "- Epic Passport controls remain readable and usable on mobile; the print action clearly identifies `Print / Save as PDF`.",
        "Readers are directed to the episode inventory and approved PDF for the full model.":
            "Readers are directed to the episode inventory and registered source/model notes for the full public interpretation.",
        "A text download may be generated client-side from the same registered fields. The downloaded passport is a convenience summary, not a verification statement, formal data-quality rating or replacement for the approved episode.":
            "The user-facing export is the visual Epic Passport through `Print / Save as PDF`. Raw-text export is retired, and the original episode PDF is not exposed as a website download.",
        "- [ ] Downloaded passport text contains the canonical episode URL and the interpretation disclaimer.\n":
            "- [ ] Printed/saved Passport retains the canonical episode URL and the interpretation disclaimer.\n",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r'\nOptional field:\n\n- `pdf` — relative path to the approved carousel in `assets/pdf/episodes/`\. \*\*Add this field only after the PDF file exists at that exact path\.\*\*\n',
        '\nThe public registry must **not** contain a `pdf` field or any other source-PDF download reference. Source PDFs may exist only as editorial/technical archive material outside the public registry contract.\n',
        text,
    )

    section16 = '''## 16. Source PDF archival policy — mandatory

The approved episode PDF / LinkedIn carousel is a **source-of-truth input**, not a public website product.

### 16.1 Public website rule

The public site must not expose the original episode PDF through episode heroes, navigation, metadata, registry fields, download buttons or dynamically injected links. `episodes.json` must not contain a `pdf` field.

The only episode-level export offered to readers is the **Epic Model Passport** through `Print / Save as PDF`. Raw-text export is retired.

### 16.2 Repository archive rule

An exact approved source PDF may remain in `assets/pdf/episodes/` solely as editorial/technical archive material. Keeping such a file does not make it a public website asset and does not authorize a link to it.

If retained, preserve the approved file and use a stable canonical filename such as `epNN-short-slug.pdf`. Do not regenerate, recompress, rasterize or redesign it merely for repository storage unless the user explicitly approves that change.

### 16.3 Defensive enforcement

`scripts/epic_passport_sync.py` removes legacy source-PDF CTAs and legacy `pdf` registry fields. `assets/passport-cleanup.js` removes stale or injected source-PDF controls and raw-text controls at runtime.

### Source-PDF / Passport QA

- [ ] No episode page or template links to `assets/pdf/episodes/*.pdf`.
- [ ] `episodes.json` contains no `pdf` field.
- [ ] No `Download episode PDF` control is visible.
- [ ] No raw-text Passport export is visible.
- [ ] `View epic passport →` and `Print / Save as PDF` are the only Passport output actions.
- [ ] Any archived source PDF remains editorial/technical material only.'''
    text = replace_section(text, 16, section16, "## 17.")

    section19 = '''## 19. Quality-assurance checklist before publication

### Content

- [ ] Main result matches the approved source PDF/carousel.
- [ ] Functional unit/reporting slice matches.
- [ ] Hotspot percentage reconciles.
- [ ] Sensitivities are correct and labelled.
- [ ] Facts and assumptions are not conflated.
- [ ] Separate disclosures are handled correctly.

### Catalogue cover — homepage/archive only

- [ ] Cover is portrait 4:5 and follows the canonical #35/#36/#38/#40/#41/#42/#43 visual family.
- [ ] Central subject is realistically rendered with credible form, materiality, depth and construction detail; technical graphics remain secondary.
- [ ] Title, episode number, diacritics and principal LCA lens are correct.
- [ ] Bronze/gold + ivory remain the common palette; episode accent is restrained.
- [ ] The published cover is the exact image approved during the creation/approval step, not a subsequent regeneration or look-alike.
- [ ] Full artwork renders in Homepage and Archive without cropping on desktop and mobile.
- [ ] The live GitHub Pages image has been visually checked against the approved source image.

### Registry

- [ ] Exactly one registry entry exists for the episode.
- [ ] Number, title, URL, cover, functional unit, result and hotspot reconcile.
- [ ] Categories/LCA lenses are meaningful.
- [ ] Evidence Profile fields are complete and defensible.
- [ ] Related episode numbers exist.
- [ ] No `pdf` field or source-PDF URL is present.

### Episode page and Passport

- [ ] `<body data-episode="NN">` matches registry number.
- [ ] `../assets/site.js`, current Phase 6 assets and `../assets/passport-cleanup.js` load.
- [ ] Hero is text-only and contains no source-PDF download control.
- [ ] Evidence Profile and Epic Model Passport render in canonical order.
- [ ] Passport exposes `View epic passport →` and `Print / Save as PDF` only.
- [ ] No Raw text control is present.
- [ ] Jump navigation, Related Cases and Previous/Next navigation work.

### Inventory and graphics

- [ ] Standard inventory columns are present.
- [ ] Major flows reconcile.
- [ ] Proxies and exclusions are disclosed.
- [ ] Inventory Map, Technical Plate and Hotspot Breakdown render.
- [ ] Analytical SVGs are self-contained and legible.

### Homepage/archive and discovery

- [ ] Highest episode number is Latest Case.
- [ ] Recent Cases and Archive render from registry.
- [ ] Ordering, filters, search, count and Load More work.
- [ ] Collections, Compare and Impact Map reflect the new episode where applicable.

### Deployment

- [ ] Changes are on `main`.
- [ ] Synchronization scripts complete without reintroducing retired exports.
- [ ] Site QA, SEO QA, Phase 3/4/5/6 QA pass.
- [ ] GitHub Pages deploys the latest synchronized commit.
- [ ] Live homepage, archive and episode are inspected.
- [ ] Live episode has no source-PDF or raw-text control and the Epic Passport works.

A green build alone is not sufficient evidence that the page is correct.'''
    text = replace_section(text, 19, section19, "## 20.")

    section20 = '''## 20. Controlled publishing workflow

For each new episode:

1. Read the approved episode PDF/carousel completely; treat it as the episode-specific technical and editorial source of truth.
2. Extract title, number, series, functional unit/reporting basis, result, hotspot, inventory, exclusions, sensitivities, evidence basis, modelling uncertainty and verdict without inventing missing facts.
3. Create the 4:5 catalogue cover in the canonical visual family with a realistic central illustration, unless the user supplied an explicitly approved exact cover.
4. Validate title, episode number, diacritics, LCA lens, style continuity, realism and no-crop rendering.
5. Obtain approval of the displayed cover and freeze that exact raster file. Do not regenerate, reinterpret or recompress it after approval.
6. Publish that exact approved image to `assets/images/episodes/` and verify the repository/live asset identity.
7. Add/update the episode object in `episodes.json` with all required catalogue, functional-unit and Evidence Profile fields. **Do not add a `pdf` field.**
8. Create the Inventory Map, Technical Plate and Hotspot Breakdown analytical graphics.
9. Build the episode page from `episodes/template.html`, set `data-episode="NN"`, retain a text-only hero and reconcile inventory/results/sensitivities/verdict.
10. Ensure Related Cases, Collections and applicable taxonomy relationships are editorially correct.
11. Let the shared scripts generate Evidence Profile, Epic Model Passport, navigation, Related Cases, sharing and discovery features; do not duplicate registry-driven blocks manually.
12. Confirm the Epic Passport offers only `View epic passport →` and `Print / Save as PDF`; never expose Raw text or the original source PDF.
13. If the source PDF is retained in `assets/pdf/episodes/`, treat it solely as editorial/technical archive material with no public link or registry reference.
14. Run SEO, feature, engagement, Phase 5, Phase 6 and Epic Passport synchronization.
15. Run structural, SEO/social, feature, engagement, Phase 5 and Phase 6 QA.
16. Verify Homepage Latest/Recent, Archive, Collections, Compare/Impact Map where applicable, metadata, sitemap and all episode paths.
17. Commit the controlled release to `main` and verify the synchronized commit.
18. Inspect the live GitHub Pages homepage, archive and episode. Confirm the exact approved cover, working Epic Passport and absence of source-PDF/raw-text controls.
19. Only then consider publication complete.'''
    text = replace_section(text, 20, section20, "## 21.")

    section23 = '''## 23. Non-negotiable principles

1. **The approved source PDF/carousel controls episode-specific facts, numbers, assumptions, sensitivities and wording; it is not a public website download.**
2. **Approved catalogue covers are 4:5 assets in the canonical #35/#36/#38/#40/#41/#42/#43 visual family and are displayed only on Homepage and Archive.**
3. **The central cover illustration must be realistic; blueprint/technical graphics support it but do not replace it.**
4. **Once a cover is approved during the image-creation step, that exact image file is the publication asset. Never regenerate a substitute merely to upload it to GitHub.**
5. **If direct connector transfer of the approved image is unavailable, the user uploads the exact image and the publishing workflow links that exact repository file without re-encoding or reinterpretation.**
6. **Individual episode heroes are text-only.**
7. **The README controls the web editorial system.**
8. **`episodes.json` is the single public registry for catalogue metadata, Evidence Profile data, taxonomy, related cases and navigation; it must not contain a `pdf` field.**
9. **The Epic Model Passport is the only public episode-level export and exposes only `View epic passport →` and `Print / Save as PDF`.**
10. **Raw-text export and source-PDF download controls are prohibited.**
11. **Source PDFs may remain only as editorial/technical repository archive material and must not be linked by the public site.**
12. **Registry data must reconcile with the approved episode.**
13. **The homepage is concise; the full searchable catalogue belongs on `archive.html`.**
14. **Every episode receives the three standard analytical graphics.**
15. **Every published episode participates in automatic navigation, Evidence Profile, Epic Model Passport and text-only Related Cases.**
16. **Every assumption remains recognizable as an assumption.**
17. **Analytical graphics must be browser-safe, self-contained and legible.**
18. **A successful GitHub Pages build is necessary but not sufficient: live pages, the exact live cover asset and the Passport-only interaction model must be checked.**
19. **Where others see fantasy, we see a functional unit.**

### Catalogue-cover QA

- Verify the `cover` path in `episodes.json`.
- Verify the high-resolution 4:5 cover asset exists and renders correctly.
- Compare it side-by-side with the canonical reference covers #35, #36, #38, #40, #41, #42 and #43.
- Verify that the central subject is realistically rendered; reject a flat, schematic-only or icon-like replacement.
- Verify the full artwork is visible with no square crop or `object-fit: cover` loss.
- Inspect Latest Case, Recent Cases and Archive on desktop and mobile.
- Verify that the repository/live asset is the exact image approved in the creation step.
- When replacing a live cover, use a cache-safe publication path and confirm the new asset is what GitHub Pages serves.'''
    text = replace_section(text, 23, section23, "<!-- SEO-RULES:START -->")

    return text


def update_readme(check: bool, changed: list[Path]) -> None:
    path = ROOT / "README.md"
    text = clean_legacy_readme(path.read_text(encoding="utf-8"))

    block = f'''{START}

## 30. Epic Model Passport presentation — mandatory

The canonical Model Passport presentation is the **Epic Passport**. This rule extends Section 29 without changing its data-governance constraints.

Every published episode exposes only two Passport actions:

1. `View epic passport →` — opens the full-screen technical dossier;
2. `Print / Save as PDF` — uses the dedicated A4 print layout defined in `assets/phase6.css`.

The former raw-text export is retired. The original episode PDF is also no longer a public website download: episode pages, the episode template and `episodes.json` must not expose or link a source PDF. Source PDF artefacts may remain in the repository as editorial/technical archive material, but they are not part of the public website navigation or registry contract.

The Epic Passport uses the registered episode cover and the existing registry fields only. Its visual language is dark technical/blueprint with cyan accents, restrained gold, archive-record identifiers, evidence blocks and a traceability seal. It must feel epic and collectible without weakening methodological readability.

No visual element may introduce an unregistered system boundary, factor list, allocation rule, assumption or numerical value. The Passport remains a transparency summary, not a verification statement or formal data-quality rating.

The shared implementation in `assets/phase6.js` and `assets/phase6.css` applies to all currently published and future episode pages. `scripts/epic_passport_sync.py` propagates the current versioned assets, removes legacy PDF download CTAs and removes legacy `pdf` fields from the public registry. `assets/passport-cleanup.js` is a defensive runtime safeguard: if stale or legacy markup injects a source-PDF CTA or raw-text control, it removes it from the rendered episode page.

### Epic Passport QA

- [ ] All episode pages reference the current versioned Phase 6 assets.
- [ ] Full-screen Passport includes registered cover, episode number/title/category/LCA lens and headline result.
- [ ] Reporting basis, hotspot and Evidence Profile remain visible.
- [ ] Evidence basis and main modelling uncertainty remain visible.
- [ ] `Print / Save as PDF` uses the dedicated A4 print stylesheet.
- [ ] No raw-text Passport export is exposed.
- [ ] No episode page or episode template exposes a source-PDF download link.
- [ ] `episodes.json` contains no public `pdf` field.
- [ ] Every episode loads `assets/passport-cleanup.js` as a defensive safeguard against stale/legacy export controls.
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
        ensure_cleanup_asset(path, "../", args.check, changed)
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
