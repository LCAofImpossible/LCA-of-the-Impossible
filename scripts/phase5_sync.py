#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
README_START = "<!-- PHASE5-RULES:START -->"
README_END = "<!-- PHASE5-RULES:END -->"
HOME_START = "<!-- PHASE5-HOME:START -->"
HOME_END = "<!-- PHASE5-HOME:END -->"
PHASE5_SEO_START = "<!-- PHASE5-SEO:START -->"
PHASE5_SEO_END = "<!-- PHASE5-SEO:END -->"
ROOT_PAGES = [
    "index.html", "archive.html", "compare.html", "explore.html", "collections.html",
    "method.html", "sources.html", "about.html", "glossary.html", "season-i.html", "season-ii.html", "statistics.html",
]
EXPLORE_PAGES = {"compare.html", "explore.html", "collections.html", "sources.html", "glossary.html", "statistics.html"}


def write_if_changed(path: Path, content: str, check: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return
    changed.append(path)
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def prefix_for(path: Path) -> str:
    return "../" if path.parent.name == "episodes" else ""


def current_page(path: Path) -> str:
    return path.name


def nav_html(prefix: str, current: str) -> str:
    episode_current = ' aria-current="page"' if current in {"archive.html", "season-i.html", "season-ii.html"} else ""
    method_current = ' aria-current="page"' if current == "method.html" else ""
    about_current = ' aria-current="page"' if current == "about.html" else ""
    explore_class = "nav-explore nav-current" if current in EXPLORE_PAGES else "nav-explore"

    def explore_link(filename: str, label: str) -> str:
        current_attr = ' aria-current="page"' if current == filename else ""
        return f'<a href="{prefix}{filename}"{current_attr}>{label}</a>'

    return "\n".join([
        '    <nav class="global-nav" aria-label="Primary navigation">',
        f'      <a href="{prefix}archive.html"{episode_current}>Episodes</a>',
        f'      <details class="{explore_class}">',
        '        <summary>Explore</summary>',
        '        <div class="nav-popover">',
        f'          {explore_link("collections.html", "Collections")}',
        f'          {explore_link("compare.html", "Compare")}',
        f'          {explore_link("explore.html", "Atlas")}',
        f'          {explore_link("statistics.html", "Statistics")}',
        f'          {explore_link("sources.html", "Sources & data")}',
        f'          {explore_link("glossary.html", "Glossary")}',
        '        </div>',
        '      </details>',
        f'      <a href="{prefix}method.html"{method_current}>Method</a>',
        f'      <a href="{prefix}about.html"{about_current}>About</a>',
        '    </nav>',
    ])


def update_navigation(path: Path, check: bool, changed: list[Path]) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    prefix = prefix_for(path)
    nav = nav_html(prefix, current_page(path))
    pattern = r'\s*<nav\b[^>]*aria-label=["\']Primary navigation["\'][^>]*>.*?</nav>'
    if re.search(pattern, text, flags=re.I | re.S):
        updated = re.sub(pattern, "\n" + nav, text, count=1, flags=re.I | re.S)
    else:
        brand = re.search(r'(<a\s+class=["\']brand["\'][^>]*>.*?</a>)', text, flags=re.I | re.S)
        if not brand:
            return
        updated = text[:brand.end()] + "\n" + nav + text[brand.end():]

    css_href = f'{prefix}assets/editorial.css?v=20260819-phase5'
    if "assets/editorial.css" not in updated:
        style_match = list(re.finditer(r'<link\s+rel=["\']stylesheet["\'][^>]*href=["\'][^"\']*assets/style\.css[^"\']*["\'][^>]*>', updated, flags=re.I))
        if style_match:
            insertion = style_match[-1].end()
            updated = updated[:insertion] + f'\n  <link rel="stylesheet" href="{css_href}">' + updated[insertion:]

    write_if_changed(path, updated, check, changed)


def home_block() -> str:
    return f'''{HOME_START}
    <section class="section small-section-title" id="project-infrastructure">
      <div class="section-heading">
        <div><p class="eyebrow">PROJECT INFRASTRUCTURE</p><h2>See what sits behind the episodes</h2></div>
        <p class="section-note">Method, source policy and terminology remain visible so the archive can be read as a technical project, not only as a collection of stories.</p>
      </div>
      <div class="knowledge-grid">
        <a class="knowledge-link" href="method.html"><span>Method</span><strong>How the impossible becomes a model.</strong><small>Evidence → functional unit → reconstruction → inventory → interpretation.</small></a>
        <a class="knowledge-link" href="sources.html"><span>Sources & data</span><strong>Where the numbers come from.</strong><small>Source hierarchy, factor selection, proxies and dataset versioning.</small></a>
        <a class="knowledge-link" href="glossary.html"><span>LCA glossary</span><strong>Technical language without the fog.</strong><small>Functional unit, boundary, hotspot, WTT, proxy and other project terms.</small></a>
        <a class="knowledge-link" href="statistics.html"><span>Statistics</span><strong>What the archive is made of.</strong><small>Seasons, subjects, LCA lenses, model signals and evidence profiles.</small></a>
        <a class="knowledge-link" href="about.html"><span>About</span><strong>Why this project exists.</strong><small>Purpose, limits, independence and the thinking behind the series.</small></a>
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
        marker = '<section id="book"'
        pos = text.find(marker)
        if pos == -1:
            marker = '<section class="section book-section"'
            pos = text.find(marker)
        if pos == -1:
            updated = text
        else:
            updated = text[:pos] + block + "\n\n    " + text[pos:]
    write_if_changed(path, updated, check, changed)


def update_sitemap(check: bool, changed: list[Path]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    required = ["method.html", "sources.html", "about.html", "glossary.html"]
    for filename in required:
        url = BASE_URL + filename
        text = re.sub(rf'\s*<url><loc>{re.escape(url)}</loc></url>', '', text)
    lines = "\n".join(f'  <url><loc>{html.escape(BASE_URL + filename)}</loc></url>' for filename in required)
    updated = text.replace("</urlset>", lines + "\n</urlset>")
    write_if_changed(path, updated, check, changed)


def phase5_seo_block(filename: str, latest_image: str, latest_title: str) -> str:
    config = {
        "sources.html": (
            "Sources & Data — LCA of the Impossible",
            "Sources and data policy for LCA of the Impossible: evidence hierarchy, emission-factor selection, proxies, versioning and traceability.",
            "WebPage",
        ),
        "about.html": (
            "About — LCA of the Impossible",
            "About LCA of the Impossible: an independent editorial and technical project using life-cycle thinking to make impossible systems analyzable, transparent and memorable.",
            "AboutPage",
        ),
        "glossary.html": (
            "LCA Glossary — LCA of the Impossible",
            "A concise glossary of the Life Cycle Assessment terms used throughout LCA of the Impossible, from functional unit and system boundary to proxies, hotspots and WTT.",
            "DefinedTermSet",
        ),
    }
    title, description, json_type = config[filename]
    canonical = BASE_URL + filename
    json_ld = {
        "@context": "https://schema.org",
        "@type": json_type,
        "name": title,
        "url": canonical,
        "description": description,
        "inLanguage": "en",
    }
    if json_type != "DefinedTermSet":
        json_ld["isPartOf"] = {"@type": "WebSite", "name": "LCA of the Impossible", "url": BASE_URL}
    return "\n".join([
        PHASE5_SEO_START,
        f'  <meta name="description" content="{html.escape(description, quote=True)}">',
        '  <meta name="robots" content="index,follow,max-image-preview:large">',
        '  <meta name="theme-color" content="#071019">',
        f'  <link rel="canonical" href="{canonical}">',
        '  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '  <link rel="manifest" href="site.webmanifest">',
        '  <meta property="og:site_name" content="LCA of the Impossible">',
        '  <meta property="og:type" content="website">',
        f'  <meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'  <meta property="og:description" content="{html.escape(description, quote=True)}">',
        f'  <meta property="og:url" content="{canonical}">',
        f'  <meta property="og:image" content="{latest_image}">',
        f'  <meta property="og:image:alt" content="{html.escape(latest_title, quote=True)} — latest LCA of the Impossible episode cover">',
        '  <meta property="og:locale" content="en_US">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{html.escape(title, quote=True)}">',
        f'  <meta name="twitter:description" content="{html.escape(description, quote=True)}">',
        f'  <meta name="twitter:image" content="{latest_image}">',
        f'  <meta name="twitter:image:alt" content="{html.escape(latest_title, quote=True)} — latest LCA of the Impossible episode cover">',
        '  <script type="application/ld+json">',
        json.dumps(json_ld, ensure_ascii=False, indent=2),
        '  </script>',
        PHASE5_SEO_END,
    ])


def update_phase5_metadata(check: bool, changed: list[Path]) -> None:
    registry = json.loads((ROOT / "episodes.json").read_text(encoding="utf-8"))
    episodes = sorted(registry["episodes"], key=lambda item: item["number"], reverse=True)
    latest = episodes[0]
    latest_image = BASE_URL + latest["cover"]
    for filename in ("sources.html", "about.html", "glossary.html"):
        path = ROOT / filename
        text = path.read_text(encoding="utf-8")
        block = phase5_seo_block(filename, latest_image, latest["title"])
        pattern = rf"{re.escape(PHASE5_SEO_START)}.*?{re.escape(PHASE5_SEO_END)}"
        if not re.search(pattern, text, flags=re.S):
            raise RuntimeError(f"Missing Phase 5 SEO marker in {filename}")
        updated = re.sub(pattern, block, text, flags=re.S)
        write_if_changed(path, updated, check, changed)


def update_readme(check: bool, changed: list[Path]) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    section = f'''{README_START}

## 28. Phase 5 — global navigation, Sources & Data, About and LCA Glossary — mandatory

Phase 5 turns the website from an episode archive into a self-explaining editorial and technical project.

### 28.1 Canonical global navigation

Every public page and every episode page uses the same primary navigation:

`Episodes · Explore · Method · About`

`Explore` contains:

- `Collections`;
- `Compare`;
- `Atlas`;
- `Statistics`;
- `Sources & data`;
- `Glossary`.

The brand remains the Home link. Navigation must be keyboard-accessible, responsive and valid without a framework. `scripts/phase5_sync.py` normalizes this header across root pages and all published episode HTML so older pages cannot retain a divergent menu.

### 28.2 Sources & Data

`sources.html` is the canonical public data-policy page. It explains source provenance, emission-factor selection, proxies and versioning without inventing episode-specific source lists.

Canonical hierarchy:

`Direct evidence → Engineering reconstruction → Representative data → Declared proxy`

Canonical emission-factor preference:

`Specific → Representative → Proxy`

Where UK Government / DEFRA factors are used, distinctions such as direct emissions, WTT, T&D, outside-of-scopes and biogenic treatment must remain separate when relevant. The page describes selection logic; it never overrides the factor choices in an approved episode.

Published episodes are not silently recalculated when a newer dataset is released. A methodological or numerical revision must be explicit and traceable.

### 28.3 About

`about.html` explains why the project exists, its independent status and its limits. It must make clear that:

- impossible subjects are used to make LCA reasoning visible and memorable;
- the work is analytical reconstruction, not certification of fictional products;
- Evidence Profile indicators are not formal ISO data-quality ratings or verification statements;
- unlike functional units must not be turned into better/worse environmental rankings;
- storytelling supports the analysis and never replaces it.

### 28.4 LCA Glossary

`glossary.html` is a searchable plain-language glossary of terminology actually used by the project. It must retain precise meanings while remaining readable to non-specialists.

The glossary is explanatory, not normative. It does not replace ISO standards, GHG accounting standards, official dataset documentation or programme rules.

### 28.5 Homepage project infrastructure

The homepage includes a compact `PROJECT INFRASTRUCTURE` block linking to:

- Method;
- Sources & Data;
- LCA Glossary;
- Statistics;
- About.

This block is text-only and must not compete visually with Latest Case or Recent Cases.

### 28.6 Canonical files and automation

Phase 5 canonical files:

- `sources.html`;
- `about.html`;
- `glossary.html`;
- `assets/editorial.css`;
- `scripts/phase5_sync.py`;
- `scripts/phase5_qa.py`.

`SEO Sync` must run `scripts/phase5_sync.py` after Phase 4 synchronization. `Site QA` must run the same Phase 5 synchronization in the QA workspace and then execute `scripts/phase5_qa.py`.

### Phase 5 QA

- [ ] Every public root page uses the canonical global navigation.
- [ ] Every published episode page uses the canonical global navigation after synchronization.
- [ ] `Explore` links to Collections, Compare, Atlas, Statistics, Sources & Data and Glossary.
- [ ] `sources.html`, `about.html` and `glossary.html` are public, responsive and linked from the site.
- [ ] All three pages contain complete static canonical/social metadata.
- [ ] `sources.html` states both source hierarchy and `Specific → Representative → Proxy` factor preference.
- [ ] Glossary contains at least 20 meaningful project terms and remains usable without the search enhancement.
- [ ] Homepage exposes the five Project Infrastructure links.
- [ ] `method.html`, `sources.html`, `about.html` and `glossary.html` each appear exactly once in `sitemap.xml`.
- [ ] Phase 5 pages load `assets/editorial.css` and have no broken local references.

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
    update_phase5_metadata(args.check, changed)

    for filename in ROOT_PAGES:
        update_navigation(ROOT / filename, args.check, changed)
    episode_dir = ROOT / "episodes"
    for path in sorted(episode_dir.glob("*.html")):
        update_navigation(path, args.check, changed)

    update_sitemap(args.check, changed)
    update_readme(args.check, changed)

    if changed:
        verb = "would change" if args.check else "updated"
        for path in changed:
            print(f"Phase 5 {verb}: {path.relative_to(ROOT)}")
        return 1 if args.check else 0
    print("Phase 5 editorial infrastructure is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
