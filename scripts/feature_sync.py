#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
START = "<!-- FEATURE-SEO:START -->"
END = "<!-- FEATURE-SEO:END -->"
README_START = "<!-- PHASE3-RULES:START -->"
README_END = "<!-- PHASE3-RULES:END -->"


def write_if_changed(path: Path, content: str, check: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return
    changed.append(path)
    if not check:
        path.write_text(content, encoding="utf-8")


def attr(value: str) -> str:
    return html.escape(value, quote=True)


def feature_block(*, title: str, description: str, canonical: str, image: str, image_alt: str, page_type: str) -> str:
    json_ld = {
        "@context": "https://schema.org",
        "@type": page_type,
        "name": title,
        "url": canonical,
        "description": description,
        "inLanguage": "en",
        "isPartOf": {"@type": "WebSite", "name": "LCA of the Impossible", "url": BASE_URL},
    }
    return "\n".join([
        START,
        f'  <meta name="description" content="{attr(description)}">',
        '  <meta name="robots" content="index,follow,max-image-preview:large">',
        '  <meta name="theme-color" content="#071019">',
        f'  <link rel="canonical" href="{attr(canonical)}">',
        '  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '  <link rel="manifest" href="site.webmanifest">',
        '  <meta property="og:site_name" content="LCA of the Impossible">',
        '  <meta property="og:type" content="website">',
        f'  <meta property="og:title" content="{attr(title)}">',
        f'  <meta property="og:description" content="{attr(description)}">',
        f'  <meta property="og:url" content="{attr(canonical)}">',
        f'  <meta property="og:image" content="{attr(image)}">',
        f'  <meta property="og:image:alt" content="{attr(image_alt)}">',
        '  <meta property="og:locale" content="en_US">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{attr(title)}">',
        f'  <meta name="twitter:description" content="{attr(description)}">',
        f'  <meta name="twitter:image" content="{attr(image)}">',
        f'  <meta name="twitter:image:alt" content="{attr(image_alt)}">',
        '  <script type="application/ld+json">',
        json.dumps(json_ld, ensure_ascii=False, indent=2),
        '  </script>',
        END,
    ])


def update_feature_page(path: Path, block: str, check: bool, changed: list[Path]) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = rf"{re.escape(START)}.*?{re.escape(END)}"
    if re.search(pattern, text, flags=re.S):
        updated = re.sub(pattern, block, text, flags=re.S)
    else:
        viewport = re.search(r'<meta\s+name=["\']viewport["\'][^>]*>', text, flags=re.I)
        if not viewport:
            raise RuntimeError(f"Viewport metadata missing in {path.name}")
        updated = text[:viewport.end()] + "\n" + block + text[viewport.end():]
    write_if_changed(path, updated, check, changed)


def update_sitemap(check: bool, changed: list[Path]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    required = [BASE_URL + "compare.html", BASE_URL + "explore.html"]
    lines = []
    for url in required:
        if url not in text:
            lines.append(f"  <url><loc>{html.escape(url)}</loc></url>")
    if not lines:
        return
    updated = text.replace("</urlset>", "\n".join(lines) + "\n</urlset>")
    write_if_changed(path, updated, check, changed)


def update_readme(check: bool, changed: list[Path]) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    section = f'''{README_START}

## 25. Interactive exploration, comparison and evidence profiles — mandatory

Phase 3 adds analytical exploration without turning unlike functional units into comparative environmental claims.

### 25.1 Registry fields

`episodes.json` uses `schemaVersion: 2`. Every published episode must additionally contain:

- `functionalUnit` — the exact or faithfully normalized functional unit / reporting basis shown in the episode hero;
- `evidence.confidence` — `Low`, `Medium` or `High` qualitative confidence in the narrative, historical or physical evidence constraining the reconstruction;
- `evidence.proxyDependence` — `Low`, `Medium` or `High` dependence on analogue processes or modern emission-factor proxies;
- `evidence.assumptionSensitivity` — `Low`, `Medium` or `High` sensitivity to key engineering assumptions, boundaries or scenario choices;
- `evidence.basis` — concise description of the source/analogue basis and what is reconstructed;
- `evidence.uncertainty` — the main modelling uncertainty that materially affects interpretation.

These evidence fields are editorial transparency indicators. They are **not** a formal ISO data-quality rating, uncertainty analysis or verification statement.

### 25.2 Compare Cases

`compare.html` allows selection of two or three published episodes. The table may compare functional unit, headline result, narrative category, LCA lens, hotspot, evidence confidence, proxy dependence, assumption sensitivity and principal modelling uncertainty.

The comparison must always display an explicit warning that headline results have different functional units and system boundaries. Do not calculate ratios, rankings, winners/losers or comparative environmental claims between unlike cases.

The selected episode numbers may be encoded in the URL as `compare.html?cases=43,42,41` so a comparison can be shared. Archive cards may expose `+ Compare`; no more than three cases may be selected at once.

### 25.3 Explore the Impossible / impact map

`explore.html` places published headline results on a logarithmic climate-impact scale. Result strings may be normalized internally to kg CO₂e **only to calculate position on the logarithmic axis**. This normalization does not harmonize functional units and must never be described as a like-for-like comparison.

The map must:

- retain the published result text beside each point;
- link every point back to the episode;
- allow filtering by principal LCA lens;
- display a persistent explanation that scale position is descriptive, not a ranking;
- remain usable on mobile without horizontal page overflow.

### 25.4 Episode Evidence Profile

Every episode receives an Evidence Profile immediately after Quick Facts and before the Visual Model. It displays Evidence confidence, Proxy dependence and Assumption sensitivity plus expandable Evidence basis and Main modelling uncertainty notes.

The Evidence Profile is generated from `episodes.json` by `assets/site.js`; do not duplicate these values manually inside individual episode HTML. The episode jump navigation must include `Evidence` when the profile is present.

### 25.5 Phase 3 files and QA

Canonical Phase 3 files:

- `compare.html` — side-by-side technical comparison;
- `explore.html` — logarithmic impact-scale exploration;
- `assets/features.css` — styles for comparison, impact map and evidence profiles;
- `scripts/feature_sync.py` — synchronizes Phase 3 metadata, sitemap entries and these README rules;
- `scripts/feature_qa.py` — validates registry evidence fields and Phase 3 page integrity.

`SEO Sync` must run `scripts/feature_sync.py` after `scripts/apply_seo.py`. `Site QA` must run both feature synchronization in its temporary QA workspace and `scripts/feature_qa.py`.

### Phase 3 QA

- [ ] Every published episode has a meaningful `functionalUnit`.
- [ ] Every published episode has all five `evidence` fields.
- [ ] Evidence levels use only `Low`, `Medium` or `High`.
- [ ] Compare Cases accepts 2–3 unique cases and never presents a better/worse ranking.
- [ ] Archive compare selection is capped at three cases.
- [ ] Impact map uses a logarithmic magnitude scale and retains original published result labels.
- [ ] Both interactive pages contain the functional-unit/non-comparability warning.
- [ ] Every episode renders its Evidence Profile before the Visual Model.
- [ ] `compare.html` and `explore.html` are present exactly once in `sitemap.xml`.
- [ ] Phase 3 pages carry canonical/social metadata and remain responsive.

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

    registry = json.loads((ROOT / "episodes.json").read_text(encoding="utf-8"))
    episodes = sorted(registry["episodes"], key=lambda item: item["number"], reverse=True)
    latest = episodes[0]
    latest_image = BASE_URL + latest["cover"]
    changed: list[Path] = []

    compare_description = "Compare two or three LCA of the Impossible cases side by side by functional unit, hotspot, modelling evidence, proxy dependence and assumption sensitivity without treating unlike systems as direct environmental comparisons."
    update_feature_page(
        ROOT / "compare.html",
        feature_block(
            title="Compare Cases — LCA of the Impossible",
            description=compare_description,
            canonical=BASE_URL + "compare.html",
            image=latest_image,
            image_alt=f"{latest['title']} — latest LCA of the Impossible episode cover",
            page_type="WebPage",
        ),
        args.check,
        changed,
    )

    explore_description = "Explore every LCA of the Impossible headline result on a logarithmic climate-impact scale while keeping different functional units, service lives and system boundaries explicit."
    update_feature_page(
        ROOT / "explore.html",
        feature_block(
            title="Explore the Impossible — LCA impact scale",
            description=explore_description,
            canonical=BASE_URL + "explore.html",
            image=latest_image,
            image_alt=f"{latest['title']} — latest LCA of the Impossible episode cover",
            page_type="CollectionPage",
        ),
        args.check,
        changed,
    )

    update_sitemap(args.check, changed)
    update_readme(args.check, changed)

    if changed:
        verb = "would change" if args.check else "updated"
        for path in changed:
            print(f"Phase 3 {verb}: {path.relative_to(ROOT)}")
        return 1 if args.check else 0
    print("Phase 3 feature metadata is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
