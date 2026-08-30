#!/usr/bin/env python3
"""Validate the RSS feed and final accessory publication routes."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
VERSION = "20260830-accessories1"
ROOT_PAGES = [
    "index.html", "archive.html", "compare.html", "explore.html", "collections.html",
    "method.html", "sources.html", "about.html", "glossary.html", "season-i.html",
    "season-ii.html", "statistics.html", "updates.html",
]
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"Missing file: {path}")
        return ""
    return target.read_text(encoding="utf-8")


def check_discovery(path: Path, prefix: str) -> None:
    text = path.read_text(encoding="utf-8")
    matches = re.findall(
        r'<link\s+rel=["\']alternate["\'][^>]*type=["\']application/rss\+xml["\'][^>]*>',
        text,
        flags=re.I,
    )
    if len(matches) != 1:
        fail(f"{path.relative_to(ROOT)}: expected one RSS discovery link, found {len(matches)}")
    elif f'href="{prefix}feed.xml"' not in matches[0]:
        fail(f"{path.relative_to(ROOT)}: RSS discovery link has the wrong prefix")


def main() -> int:
    registry = json.loads(read("episodes.json") or "{}")
    episodes = registry.get("episodes")
    if not isinstance(episodes, list) or not episodes:
        fail("episodes.json contains no episodes")
        episodes = []

    feed_text = read("feed.xml")
    try:
        root = ET.fromstring(feed_text)
    except ET.ParseError as exc:
        fail(f"feed.xml is invalid XML: {exc}")
        root = ET.Element("invalid")
    if root.tag != "rss" or root.get("version") != "2.0":
        fail("feed.xml must be RSS 2.0")
    channel = root.find("channel")
    if channel is None:
        fail("feed.xml has no channel")
        items = []
    else:
        if channel.findtext("link") != BASE_URL:
            fail("feed.xml channel link is not canonical")
        atom = channel.find("{http://www.w3.org/2005/Atom}link")
        if atom is None or atom.get("href") != BASE_URL + "feed.xml" or atom.get("rel") != "self":
            fail("feed.xml has no canonical Atom self-link")
        items = channel.findall("item")

    if len(items) != len(episodes):
        fail(f"feed.xml contains {len(items)} items; expected {len(episodes)}")
    for episode, item in zip(episodes, items):
        canonical = BASE_URL + episode["url"]
        if item.findtext("link") != canonical:
            fail(f"Episode #{episode['number']}: RSS link is not canonical")
        guid = item.find("guid")
        if guid is None or guid.text != canonical or guid.get("isPermaLink") != "true":
            fail(f"Episode #{episode['number']}: RSS permalink GUID is invalid")
        if item.findtext("title") != f"Episode #{episode['number']} — {episode['title']}":
            fail(f"Episode #{episode['number']}: RSS title does not match the registry")
        description = item.findtext("description") or ""
        for token in (episode.get("subjectDescription"), episode.get("featuredDescription")):
            if token and token not in description:
                fail(f"Episode #{episode['number']}: RSS description omits approved registry text")
        published = item.find("pubDate")
        if episode.get("datePublished") and published is None:
            fail(f"Episode #{episode['number']}: registered publication date is missing from RSS")
        if not episode.get("datePublished") and published is not None:
            fail(f"Episode #{episode['number']}: RSS invents a publication date")

    if "assets/pdf/episodes/" in feed_text.lower() or ".pdf</link>" in feed_text.lower():
        fail("feed.xml exposes a source PDF")

    for name in ROOT_PAGES:
        check_discovery(ROOT / name, "")
    for path in sorted((ROOT / "episodes").glob("*.html")):
        if path.name != "template.html":
            check_discovery(path, "../")
    template = read("episodes/template.html")
    if "application/rss+xml" in template:
        fail("episodes/template.html must not publish RSS autodiscovery")

    updates = read("updates.html")
    for token in (
        'data-page="updates"',
        'href="feed.xml"',
        'data-copy-feed',
        'data-updates-telemetry',
        'id="updates-case-list"',
        f"assets/updates.css?v={VERSION}",
        f"assets/updates.js?v={VERSION}",
        "Counts begin",
        'href="episodes.json"',
        'href="site.webmanifest"',
    ):
        if token not in updates:
            fail(f"updates.html: required accessory token missing: {token}")

    script = read("assets/updates.js")
    for token in ("registry.episodes", ".slice(0, 12)", "episode.subjectDescription", "episode.result", "data-site-visitors", "MutationObserver", "feed.xml"):
        if token not in script:
            fail(f"assets/updates.js: required token missing: {token}")
    for forbidden in ("counterapi.com", "site-total", "document.cookie", "localStorage", "sessionStorage"):
        if forbidden in script:
            fail(f"assets/updates.js: duplicate telemetry/privacy contract violated by {forbidden}")

    styles = read("assets/updates.css")
    for token in (".updates-hero", ".updates-case", ".updates-utility-grid", "@media(max-width:620px)"):
        if token not in styles:
            fail(f"assets/updates.css: required responsive style missing: {token}")

    syntax = subprocess.run(
        ["node", "--check", str(ROOT / "assets" / "updates.js")],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if syntax.returncode:
        fail(f"assets/updates.js failed JavaScript syntax validation: {syntax.stdout.strip()}")

    sitemap = read("sitemap.xml")
    if sitemap.count(BASE_URL + "updates.html") != 1:
        fail("sitemap.xml must contain updates.html exactly once")
    manifest = json.loads(read("site.webmanifest") or "{}")
    shortcuts = {item.get("url") for item in manifest.get("shortcuts", []) if isinstance(item, dict)}
    for expected in ("/LCA-of-the-Impossible/updates.html", "/LCA-of-the-Impossible/archive.html"):
        if expected not in shortcuts:
            fail(f"site.webmanifest: missing shortcut {expected}")

    for path, token in (
        ("scripts/publication_qa.py", '"rss_sync.py"'),
        ("scripts/publication_qa.py", '"rss_qa.py"'),
        ("scripts/live_site_qa.py", '"feed.xml"'),
        ("scripts/live_site_qa.py", '"updates.html"'),
        (".github/workflows/seo-sync.yml", "python scripts/rss_sync.py"),
        (".github/workflows/seo-sync.yml", "feed.xml"),
        ("README.md", "## 38. RSS, readership telemetry and accessory routes"),
    ):
        if token not in read(path):
            fail(f"{path}: publication integration token missing: {token}")

    if errors:
        print("RSS and accessory QA: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"RSS and accessory QA: PASS ({len(items)} feed items, {len(ROOT_PAGES)} root pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
