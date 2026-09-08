#!/usr/bin/env python3
"""Synchronize the registry-driven Impossible Lab route and its homepage entry point."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
ASSET_VERSION = "20260908-impossible-lab1"
HOME_START = "<!-- LAB-HOME:START -->"
HOME_END = "<!-- LAB-HOME:END -->"
SEO_START = "<!-- LAB-SEO:START -->"
SEO_END = "<!-- LAB-SEO:END -->"
README_START = "<!-- IMPOSSIBLE-LAB-RULES:START -->"
README_END = "<!-- IMPOSSIBLE-LAB-RULES:END -->"


def write_if_changed(path: Path, content: str, check: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return
    changed.append(path)
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def home_block() -> str:
    return f'''{HOME_START}
    <section class="section small-section-title lab-home-preview" id="impossible-lab">
      <div class="section-heading">
        <div><p class="eyebrow">IMPOSSIBLE LAB</p><h2>Play the archive.</h2></div>
        <p class="section-note">One registry-driven experiment. Every published episode. No additional case-by-case setup.</p>
      </div>
      <div class="lab-home-grid">
        <div class="lab-home-copy">
          <p class="eyebrow">EXPERIMENT 01</p>
          <h3>Guess the Impossible.</h3>
          <p>Identify a case from five progressively revealed signals: season, inventory, impact, function and one final subject clue.</p>
          <a class="button" href="lab.html">Enter the Impossible Lab →</a>
        </div>
        <div class="lab-home-terminal" aria-label="Guess the Impossible clue sequence">
          <span><b>01</b> SEASON SIGNAL</span>
          <span><b>02</b> INVENTORY SIGNAL</span>
          <span><b>03</b> IMPACT SIGNAL</span>
          <span><b>04</b> FUNCTION SIGNAL</span>
          <span><b>05</b> SUBJECT DECLASSIFIED</span>
        </div>
      </div>
    </section>
{HOME_END}'''


def update_home(check: bool, changed: list[Path]) -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    block = home_block()
    pattern = rf"{re.escape(HOME_START)}.*?{re.escape(HOME_END)}"
    if re.search(pattern, text, flags=re.S):
        updated = re.sub(pattern, block, text, flags=re.S)
    else:
        marker = '<section class="section small-section-title season-route-shell">'
        position = text.find(marker)
        if position == -1:
            raise RuntimeError("Cannot place the Impossible Lab homepage block")
        updated = text[:position] + block + "\n\n    " + text[position:]

    css = f'assets/lab.css?v={ASSET_VERSION}'
    css_pattern = r'<link\s+rel="stylesheet"\s+href="[^"]*assets/lab\.css(?:\?v=[^"]*)?">'
    if re.search(css_pattern, updated):
        updated = re.sub(css_pattern, f'<link rel="stylesheet" href="{css}">', updated)
    else:
        anchor = re.search(r'<link\s+rel="stylesheet"\s+href="assets/editorial\.css[^"]*">', updated)
        if not anchor:
            raise RuntimeError("Cannot add Impossible Lab styles to the homepage")
        updated = updated[:anchor.end()] + f'\n  <link rel="stylesheet" href="{css}">' + updated[anchor.end():]

    write_if_changed(path, updated, check, changed)


def seo_block(latest: dict) -> str:
    title = "Impossible Lab — Guess the Impossible"
    description = "Enter the Impossible Lab and play Guess the Impossible: identify a published LCA case from five progressively revealed life-cycle clues."
    social_description = "Identify a published LCA of the Impossible case from season, inventory, impact, function and final clues."
    canonical = BASE_URL + "lab.html"
    image = BASE_URL + latest["cover"]
    image_alt = f"{latest['title']} — latest LCA of the Impossible episode cover"
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "url": canonical,
        "description": social_description,
        "inLanguage": "en",
        "isPartOf": {
            "@type": "WebSite",
            "name": "LCA of the Impossible",
            "url": BASE_URL,
        },
    }
    return "\n".join([
        SEO_START,
        f'  <meta name="description" content="{html.escape(description, quote=True)}">',
        '  <meta name="robots" content="index,follow,max-image-preview:large">',
        '  <meta name="theme-color" content="#071019">',
        f'  <link rel="canonical" href="{canonical}">',
        '  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '  <link rel="manifest" href="site.webmanifest">',
        '  <link rel="alternate" type="application/rss+xml" title="LCA of the Impossible — New episodes" href="feed.xml">',
        '  <meta property="og:site_name" content="LCA of the Impossible">',
        '  <meta property="og:type" content="website">',
        f'  <meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'  <meta property="og:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta property="og:url" content="{canonical}">',
        f'  <meta property="og:image" content="{image}">',
        f'  <meta property="og:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <meta property="og:locale" content="en_US">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{html.escape(title, quote=True)}">',
        f'  <meta name="twitter:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta name="twitter:image" content="{image}">',
        f'  <meta name="twitter:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <script type="application/ld+json">',
        json.dumps(json_ld, ensure_ascii=False, indent=2),
        '  </script>',
        SEO_END,
    ])


def update_lab_metadata(check: bool, changed: list[Path]) -> None:
    registry = json.loads((ROOT / "episodes.json").read_text(encoding="utf-8"))
    latest = max(registry["episodes"], key=lambda episode: episode["number"])
    path = ROOT / "lab.html"
    text = path.read_text(encoding="utf-8")
    block = seo_block(latest)
    pattern = rf"{re.escape(SEO_START)}.*?{re.escape(SEO_END)}"
    if not re.search(pattern, text, flags=re.S):
        raise RuntimeError("Missing Impossible Lab SEO markers")
    updated = re.sub(pattern, block, text, flags=re.S)
    write_if_changed(path, updated, check, changed)


def update_sitemap(check: bool, changed: list[Path]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    url = BASE_URL + "lab.html"
    updated = re.sub(rf'\s*<url><loc>{re.escape(url)}</loc></url>', '', text)
    updated = updated.replace("</urlset>", f"  <url><loc>{url}</loc></url>\n</urlset>")
    write_if_changed(path, updated, check, changed)


def update_readme(check: bool, changed: list[Path]) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    section = f'''{README_START}

## 39. Impossible Lab and registry-driven games — mandatory

`lab.html` is the canonical game hub for **Impossible Lab**. The first published experiment is **Guess the Impossible**. Games must operate across the complete published archive rather than create separate implementations for individual episodes.

### 39.1 Guess the Impossible

The game selects one eligible record from `episodes.json` and reveals five clues in this fixed order:

1. `Season` — the registered `seasonLabel`;
2. `Inventory` — registered model drivers or, where structured metadata is unavailable, the approved LCA lens and characteristics;
3. `Impact` — the registered headline `result` and `hotspot`;
4. `Function` — the registered `functionalUnit` or reporting basis;
5. `Final clue` — the registered `subjectDescription`, with the episode title redacted where it occurs.

Available points are `500 → 400 → 300 → 200 → 100`. A wrong answer unlocks the next clue. Revealing the answer scores zero and resets the current streak. Score and streak are session-only interface state and must not create visitor identifiers, cookies or browser-storage tracking.

### 39.2 Registry and editorial guardrails

- Every currently eligible episode and every future complete registry record enters the game automatically.
- Episode titles, clues, results, links and counts must never be duplicated in `lab.html` or hard-coded in `assets/lab.js`.
- The game may reformat approved registry values for readability but must not invent a result, assumption, inventory flow, comparison or ranking.
- Guessing performance scores the player only. It never ranks cases or implies that unlike functional units are environmentally comparable.
- Catalogue covers remain limited to Homepage and Archive. Impossible Lab results are text-only and link to the canonical episode page.
- The game must remain keyboard-accessible, responsive, readable at enlarged text sizes and usable on touch devices.
- A registry failure must leave a clear error state and a working link to the Archive.

### 39.3 Canonical files and automation

- `lab.html` — Impossible Lab hub and complete game interface;
- `assets/lab.css` — responsive technical game presentation and homepage preview;
- `assets/lab.js` — registry loading, clue generation, scoring and round state;
- `scripts/lab_sync.py` — homepage entry point, metadata, sitemap and README synchronization;
- `scripts/lab_qa.py` — registry coverage, gameplay, accessibility, privacy and publication checks.

`scripts/publication_qa.py` runs `lab_sync.py` after global navigation synchronization and runs `lab_qa.py` as part of the mandatory read-only publication gate. GitHub Pages live QA compares the Lab page and both Lab assets byte-for-byte with the checked-out publication.

### Impossible Lab QA

- [ ] Every eligible registry record supplies all five clue sources.
- [ ] The first clue is available as soon as the registry loads.
- [ ] Five scoring levels are exactly `500`, `400`, `300`, `200` and `100`.
- [ ] Wrong answers and manual reveals progress through the same ordered clue sequence.
- [ ] The title is redacted from the final clue where present.
- [ ] No episode title or clue dataset is hard-coded into the game runtime.
- [ ] The answer and case result use text-only registry data and the canonical episode URL.
- [ ] Homepage, canonical navigation, sitemap, RSS discovery and telemetry include `lab.html`.
- [ ] Failure and no-JavaScript states retain access to the Archive.
- [ ] Desktop and mobile layouts have no unintended horizontal overflow.

{README_END}'''
    pattern = rf"{re.escape(README_START)}.*?{re.escape(README_END)}"
    if re.search(pattern, text, flags=re.S):
        updated = re.sub(pattern, section, text, flags=re.S)
    else:
        updated = text.rstrip() + "\n\n---\n\n" + section + "\n"
    write_if_changed(path, updated, check, changed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed: list[Path] = []

    update_home(args.check, changed)
    update_lab_metadata(args.check, changed)
    update_sitemap(args.check, changed)
    update_readme(args.check, changed)

    if changed:
        verb = "would update" if args.check else "updated"
        for path in changed:
            print(f"Impossible Lab {verb}: {path.relative_to(ROOT)}")
        return 1 if args.check else 0
    print("Impossible Lab is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
