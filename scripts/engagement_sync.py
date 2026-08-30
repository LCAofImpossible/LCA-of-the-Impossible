#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
SEO_START = "<!-- ENGAGEMENT-SEO:START -->"
SEO_END = "<!-- ENGAGEMENT-SEO:END -->"
README_START = "<!-- PHASE4-RULES:START -->"
README_END = "<!-- PHASE4-RULES:END -->"
SCRIPT_VERSION = "20260830-subject-descriptions1"


def write_if_changed(path: Path, content: str, check: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return
    changed.append(path)
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def attr(value: str) -> str:
    return html.escape(value, quote=True)


def metadata_block(latest: dict) -> str:
    title = "Collections — LCA of the Impossible"
    description = (
        "Explore LCA of the Impossible through thematic collections and ordered reading paths that "
        "follow recurring modelling questions across selected episodes."
    )
    canonical = BASE_URL + "collections.html"
    image = BASE_URL + latest["cover"]
    image_alt = f"{latest['title']} — latest LCA of the Impossible episode cover"
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "url": canonical,
        "description": description,
        "inLanguage": "en",
        "isPartOf": {"@type": "WebSite", "name": "LCA of the Impossible", "url": BASE_URL},
    }
    return "\n".join([
        SEO_START,
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
        SEO_END,
    ])


def update_collections_page(latest: dict, check: bool, changed: list[Path]) -> None:
    path = ROOT / "collections.html"
    text = path.read_text(encoding="utf-8")
    block = metadata_block(latest)
    pattern = rf"\s*{re.escape(SEO_START)}.*?{re.escape(SEO_END)}\s*"
    text = re.sub(pattern, "\n", text, flags=re.S)
    viewport = re.search(r'<meta\s+name=["\']viewport["\'][^>]*>', text, flags=re.I)
    if not viewport:
        raise RuntimeError("collections.html is missing viewport metadata")
    text = text[: viewport.end()] + "\n" + block + text[viewport.end() :]
    write_if_changed(path, text, check, changed)


def ensure_engagement_script(path: Path, prefix: str, check: bool, changed: list[Path]) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'\s*<script\s+src=["\'][^"\']*assets/engagement\.js[^"\']*["\'][^>]*></script>\s*',
        "\n",
        text,
        flags=re.I,
    )
    tag = f'  <script src="{prefix}assets/engagement.js?v={SCRIPT_VERSION}"></script>'
    if "</body>" not in text:
        raise RuntimeError(f"{path.relative_to(ROOT)} is missing </body>")
    text = text.replace("</body>", tag + "\n</body>")
    write_if_changed(path, text, check, changed)


def update_sitemap(check: bool, changed: list[Path]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    url = BASE_URL + "collections.html"
    if text.count(url) == 1:
        return
    text = "\n".join(line for line in text.splitlines() if url not in line) + "\n"
    text = text.replace("</urlset>", f'  <url><loc>{html.escape(url)}</loc></url>\n</urlset>')
    write_if_changed(path, text, check, changed)


def update_readme(check: bool, changed: list[Path]) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    section = f'''{README_START}

## 26. Engagement, collections and sharing — mandatory

Phase 4 improves discovery and sharing without weakening the technical framing of the series.

### 26.1 Curated collections

`collections.json` uses `schemaVersion: 2` and remains the single registry for seasons, thematic collections and guided editorial paths.

Editorial collections are stored in `collections.json`, not hard-coded into individual pages. Every collection must contain:

- a unique lowercase kebab-case `slug`;
- a concise `title`;
- an uppercase editorial `eyebrow`;
- a meaningful `description`;
- at least two unique published episode numbers.

Collections may overlap. They are editorial routes through the archive and are not mutually exclusive classifications.

The canonical Phase 4 collection page is `collections.html`. It renders collection membership from `collections.json` and `episodes.json`. Because the established catalogue-cover rule limits episode covers to Homepage and Archive, **collection cards are text-only**.

### 26.2 Guided editorial paths

`editorialPaths` are ordered reading sequences, separate from seasons and thematic collections. Every path must contain:

- a unique lowercase kebab-case `slug` that does not collide with a season or collection;
- a concise `title`, uppercase editorial `eyebrow`, guiding `question` and meaningful `description`;
- one or more valid `relatedCollections` links;
- at least three unique published steps, each with an episode number, progression `phase` and editorial `note`.

Paths do not create a new taxonomy and must not add or infer `collectionSlugs` on episode records. Episode titles, results, LCA lenses and hotspots remain projected from `episodes.json`; only the reading order and transition notes live in `collections.json`.

`collections.html` renders every path as an ordered text-only sequence. Opening a step adds `?path=<slug>` to the episode URL. While that context is valid, the episode page may show previous/next path navigation and a return link to the path overview. Invalid, unknown or mismatched path parameters must add no interface and must never redirect the visitor.

### 26.3 Random discovery

`Random impossible case` may appear on Homepage, Archive, Collections and episode pages. It must always resolve to an already published registry entry. On an episode page, the current episode should be excluded when another case is available.

A collection-specific random action must select only from the episode numbers registered for that collection.

### 26.4 Sharing

Every episode receives a `Share the case` block generated by `assets/engagement.js`. It may provide:

- native Web Share where supported;
- copy canonical episode link;
- copy a LinkedIn-ready caption containing episode number, title, short description, headline result, LCA lens and canonical URL;
- random next case.

Sharing tools must use the canonical episode URL and must not rewrite the technical result, functional unit or LCA lens.

### 26.5 LinkedIn follow link

`collections.json` contains `socialLinks.linkedin`. Keep it `null` until the exact public LinkedIn profile/page URL is explicitly known. Never guess or infer a profile URL.

When a valid URL is registered, `assets/engagement.js` may expose `Follow on LinkedIn` CTAs. The absence of a LinkedIn URL must not create a broken or placeholder link.

### 26.6 Phase 4 files and automation

Canonical Phase 4 files:

- `collections.json` — season, collection, guided-path and optional social-link registry;
- `collections.html` — curated collection and guided reading-path browser;
- `assets/engagement.js` — guided path navigation, random discovery, collection rendering and episode sharing;
- `assets/engagement.css` — collection, path-progress and sharing presentation;
- `scripts/engagement_sync.py` — synchronizes Phase 4 scripts, metadata, sitemap and these README rules;
- `scripts/engagement_qa.py` — validates collection integrity, sharing hooks and publication wiring.

`SEO Sync` must run `scripts/engagement_sync.py` after Phase 3 synchronization. `Site QA` must run the same synchronization in its temporary workspace and then run `scripts/engagement_qa.py`.

### Phase 4 QA

- [ ] Every collection slug is unique and valid.
- [ ] Every collection contains at least two unique published episodes.
- [ ] Every guided path has a unique slug, at least three ordered published steps and valid related-collection links.
- [ ] Guided paths remain separate from episode taxonomy and do not duplicate episode result or classification data.
- [ ] Valid path context renders ordered previous/next episode navigation; invalid context renders nothing and does not redirect.
- [ ] Collection cards remain text-only.
- [ ] `collections.html` has canonical/social metadata and exactly one sitemap entry.
- [ ] Homepage and Archive expose collection/random discovery entry points.
- [ ] Episode pages load `assets/engagement.js`.
- [ ] Episode sharing uses canonical URLs.
- [ ] Random case selection uses only published episodes.
- [ ] LinkedIn follow CTA is hidden while `socialLinks.linkedin` is null.
- [ ] No placeholder social URL is published.
- [ ] Phase 4 remains usable on mobile and respects existing cover-rendering rules.

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
    changed: list[Path] = []

    update_collections_page(latest, args.check, changed)

    root_pages = [
        ROOT / "index.html",
        ROOT / "archive.html",
        ROOT / "compare.html",
        ROOT / "explore.html",
        ROOT / "collections.html",
    ]
    for page in root_pages:
        ensure_engagement_script(page, "", args.check, changed)

    for episode in episodes:
        ensure_engagement_script(ROOT / episode["url"], "../", args.check, changed)

    template = ROOT / "episodes/template.html"
    if template.is_file():
        ensure_engagement_script(template, "../", args.check, changed)

    update_sitemap(args.check, changed)
    update_readme(args.check, changed)

    if changed:
        verb = "would change" if args.check else "updated"
        for path in changed:
            print(f"Phase 4 {verb}: {path.relative_to(ROOT)}")
        return 1 if args.check else 0

    print("Phase 4 engagement metadata is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
