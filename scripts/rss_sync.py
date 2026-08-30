#!/usr/bin/env python3
"""Synchronize the public RSS feed, discovery links and accessory-page rules."""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
FEED_TITLE = "LCA of the Impossible — New episodes"
README_START = "<!-- ACCESSORY-RULES:START -->"
README_END = "<!-- ACCESSORY-RULES:END -->"
ROOT_PAGES = [
    "index.html", "archive.html", "compare.html", "explore.html", "collections.html",
    "method.html", "sources.html", "about.html", "glossary.html", "season-i.html",
    "season-ii.html", "statistics.html", "updates.html",
]


def write_if_changed(path: Path, content: str, check: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return
    changed.append(path)
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def xml(value: object) -> str:
    return html.escape(str(value), quote=False)


def rss_date(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        moment = datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return format_datetime(moment)


def build_feed(episodes: list[dict]) -> str:
    items: list[str] = []
    for episode in episodes:
        canonical = BASE_URL + episode["url"]
        description = f"{episode['subjectDescription']} {episode['featuredDescription']}"
        categories = [episode.get("seasonLabel"), episode.get("categoryLabel"), episode.get("lcaLabel")]
        lines = [
            "    <item>",
            f"      <title>Episode #{episode['number']} — {xml(episode['title'])}</title>",
            f"      <link>{xml(canonical)}</link>",
            f'      <guid isPermaLink="true">{xml(canonical)}</guid>',
            f"      <description>{xml(description)}</description>",
        ]
        published = rss_date(episode.get("datePublished"))
        if published:
            lines.append(f"      <pubDate>{published}</pubDate>")
        for category in categories:
            if category:
                lines.append(f"      <category>{xml(category)}</category>")
        lines.append("    </item>")
        items.append("\n".join(lines))

    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{xml(FEED_TITLE)}</title>",
        f"    <link>{BASE_URL}</link>",
        "    <description>New LCA of the Impossible episodes, reconstructed as transparent life-cycle systems.</description>",
        "    <language>en</language>",
        f'    <atom:link href="{BASE_URL}feed.xml" rel="self" type="application/rss+xml" />',
        "    <generator>LCA of the Impossible registry</generator>",
        "    <ttl>1440</ttl>",
        *items,
        "  </channel>",
        "</rss>",
        "",
    ])


def ensure_feed_link(path: Path, prefix: str, check: bool, changed: list[Path]) -> None:
    text = path.read_text(encoding="utf-8")
    tag = f'  <link rel="alternate" type="application/rss+xml" title="{FEED_TITLE}" href="{prefix}feed.xml">'
    pattern = r'\s*<link\s+rel=["\']alternate["\'][^>]*type=["\']application/rss\+xml["\'][^>]*>\s*'
    updated = re.sub(pattern, "\n", text, flags=re.I)
    manifest = re.search(r'<link\s+rel=["\']manifest["\'][^>]*>', updated, flags=re.I)
    if not manifest:
        raise RuntimeError(f"Cannot add RSS discovery link to {path.relative_to(ROOT)}")
    updated = updated[:manifest.end()] + "\n" + tag + updated[manifest.end():]
    write_if_changed(path, updated, check, changed)


def update_sitemap(check: bool, changed: list[Path]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    url = BASE_URL + "updates.html"
    updated = re.sub(rf'\s*<url><loc>{re.escape(url)}</loc></url>', '', text)
    updated = updated.replace("</urlset>", f"  <url><loc>{url}</loc></url>\n</urlset>")
    write_if_changed(path, updated, check, changed)


def update_readme(check: bool, changed: list[Path]) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    section = f'''{README_START}

## 38. RSS, readership telemetry and accessory routes — mandatory

Priority 12 completes lightweight discovery functions after catalogue navigation and data contracts have stabilized.

### 38.1 Canonical RSS feed

`feed.xml` is an RSS 2.0 feed generated deterministically from the ordered `episodes` array in `episodes.json`. Every item contains the registered episode number, title, canonical URL, `subjectDescription`, `featuredDescription` and registered season/category/LCA labels. Publication dates are emitted only when `datePublished` is explicitly registered; missing dates are never invented.

Every public root page and published episode page exposes one RSS autodiscovery link. `episodes/template.html` remains excluded. The feed must never contain source-PDF URLs, hidden calculation material, comparative rankings or fields that are not present in the approved public registry.

### 38.2 Updates & RSS page

`updates.html` is the canonical human-readable companion to the feed. It is text-only and registry-driven. `assets/updates.js` renders the first twelve ordered registry entries, copies the canonical feed URL and mirrors the single site-wide telemetry value already requested by `assets/telemetry.js`.

The page must not create a second counter request, add cookies, store visitor identifiers or query every episode counter. It explains that counts begin at telemetry activation and are not historical backfill or an episode-performance ranking.

### 38.3 Accessory routes

The page links directly to the canonical `episodes.json`, descriptive catalogue statistics and `site.webmanifest`. The manifest provides shortcuts to Updates and the Archive. These utilities do not expose approved source PDFs or replace the episode audit trail.

### 38.4 Canonical files and QA

- `feed.xml` — generated RSS 2.0 publication feed;
- `updates.html` — feed, latest-entry, telemetry and data-access surface;
- `assets/updates.js` and `assets/updates.css` — registry projection and responsive presentation;
- `scripts/rss_sync.py` — deterministic feed/discovery synchronizer;
- `scripts/rss_qa.py` — feed, page, privacy, SEO and publication validator.

The `SEO Sync` workflow must run `scripts/rss_sync.py` after the other metadata synchronizers and stage `feed.xml`. This final pass restores RSS autodiscovery and the Updates sitemap route after base SEO regeneration.

- [ ] RSS item order and membership exactly match `episodes.json`.
- [ ] Every RSS item uses its canonical episode URL and approved public summaries.
- [ ] Missing publication dates remain omitted, not reconstructed.
- [ ] All public pages expose exactly one correctly prefixed RSS discovery link.
- [ ] Updates uses the existing site counter response and performs no second telemetry request.
- [ ] Updates, navigation, sitemap, manifest shortcuts and live byte verification are synchronized.
- [ ] The automated SEO workflow runs the RSS synchronizer last and stages the generated feed.
- [ ] The feed and page expose no source-PDF link or comparative performance claim.

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
    episodes = registry.get("episodes", [])
    if not isinstance(episodes, list) or not episodes:
        raise RuntimeError("Cannot build RSS feed: episodes.json contains no episodes")
    changed: list[Path] = []

    write_if_changed(ROOT / "feed.xml", build_feed(episodes), args.check, changed)
    for name in ROOT_PAGES:
        ensure_feed_link(ROOT / name, "", args.check, changed)
    for path in sorted((ROOT / "episodes").glob("*.html")):
        if path.name != "template.html":
            ensure_feed_link(path, "../", args.check, changed)
    update_sitemap(args.check, changed)
    update_readme(args.check, changed)

    if changed:
        for path in changed:
            print(f"RSS {'would update' if args.check else 'updated'}: {path.relative_to(ROOT)}")
        return 1 if args.check else 0
    print("RSS and accessory routes are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
