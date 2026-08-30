#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
errors: list[str] = []

ROOT_PAGES = [
    "index.html", "archive.html", "compare.html", "explore.html", "collections.html",
    "method.html", "sources.html", "about.html", "glossary.html", "season-i.html", "season-ii.html", "statistics.html",
    "updates.html",
]
NAV_LABELS = ["Episodes", "Explore", "Method", "About"]
EXPLORE_LINKS = ["collections.html", "compare.html", "explore.html", "statistics.html", "updates.html", "sources.html", "glossary.html"]


def fail(message: str) -> None:
    errors.append(message)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"Missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def check_nav(path: Path) -> None:
    text = read(path)
    if not text:
        return
    nav_match = re.search(r'<nav\b[^>]*class=["\'][^"\']*global-nav[^"\']*["\'][^>]*>.*?</nav>', text, flags=re.I | re.S)
    if not nav_match:
        fail(f"{path.relative_to(ROOT)}: canonical global-nav missing")
        return
    nav = nav_match.group(0)
    for label in NAV_LABELS:
        if label not in nav:
            fail(f"{path.relative_to(ROOT)}: navigation missing {label}")
    prefix = "../" if path.parent.name == "episodes" else ""
    expected = [prefix + value for value in EXPLORE_LINKS]
    for href in expected:
        if f'href="{href}"' not in nav and f"href='{href}'" not in nav:
            fail(f"{path.relative_to(ROOT)}: Explore navigation missing {href}")
    if f'href="{prefix}archive.html"' not in nav:
        fail(f"{path.relative_to(ROOT)}: Episodes link is not canonical")
    if f'href="{prefix}method.html"' not in nav:
        fail(f"{path.relative_to(ROOT)}: Method link is not canonical")
    if f'href="{prefix}about.html"' not in nav:
        fail(f"{path.relative_to(ROOT)}: About link is not canonical")


def check_phase5_metadata(filename: str) -> None:
    path = ROOT / filename
    text = read(path)
    if not text:
        return
    canonical = BASE_URL + filename
    required = [
        '<meta name="description"',
        'name="robots" content="index,follow,max-image-preview:large"',
        f'<link rel="canonical" href="{canonical}"',
        'property="og:title"',
        'property="og:description"',
        f'property="og:url" content="{canonical}"',
        'property="og:image"',
        'name="twitter:card" content="summary_large_image"',
        'name="twitter:image"',
        'application/ld+json',
    ]
    for token in required:
        if token not in text:
            fail(f"{filename}: missing metadata token {token}")
    if "assets/editorial.css" not in text:
        fail(f"{filename}: assets/editorial.css missing")


def check_sources() -> None:
    text = read(ROOT / "sources.html")
    required = [
        "Direct evidence", "Engineering reconstruction", "Representative data", "Declared proxy",
        "Specific", "Representative", "Proxy", "UK Government GHG Conversion Factors",
        "WTT", "T&D", "Data-policy version 1.0",
    ]
    for token in required:
        if token not in text:
            fail(f"sources.html: required data-policy concept missing: {token}")


def check_about() -> None:
    text = read(ROOT / "about.html")
    lowered = text.lower()
    required = ["independent", "not a verification claim", "not a comparative claim", "life cycle assessment"]
    for token in required:
        if token not in lowered:
            fail(f"about.html: required project-positioning concept missing: {token}")
    if "certified" not in lowered and "verification" not in lowered:
        fail("about.html: certification/verification limitation is not explicit")


def check_glossary() -> None:
    text = read(ROOT / "glossary.html")
    entries = re.findall(r'<div\s+class=["\']glossary-entry["\']', text, flags=re.I)
    if len(entries) < 20:
        fail(f"glossary.html: expected at least 20 terms, found {len(entries)}")
    for term in ["Functional unit", "System boundary", "Proxy", "Hotspot", "Well-to-tank / WTT"]:
        if term not in text:
            fail(f"glossary.html: required term missing: {term}")
    if 'id="glossary-search"' not in text:
        fail("glossary.html: search enhancement missing")


def check_home() -> None:
    text = read(ROOT / "index.html")
    if "PROJECT INFRASTRUCTURE" not in text:
        fail("index.html: Project Infrastructure block missing")
    for href in ["method.html", "sources.html", "glossary.html", "statistics.html", "updates.html", "about.html"]:
        if f'href="{href}"' not in text:
            fail(f"index.html: Project Infrastructure link missing: {href}")


def check_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = read(path)
    if not text:
        return
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        fail(f"sitemap.xml: invalid XML ({exc})")
        return
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text for loc in root.findall("sm:url/sm:loc", ns) if loc.text]
    for filename in ["method.html", "sources.html", "about.html", "glossary.html"]:
        expected = BASE_URL + filename
        count = urls.count(expected)
        if count != 1:
            fail(f"sitemap.xml: expected exactly one {filename} URL, found {count}")


def main() -> int:
    for filename in ROOT_PAGES:
        check_nav(ROOT / filename)
    for path in sorted((ROOT / "episodes").glob("*.html")):
        check_nav(path)

    for filename in ["sources.html", "about.html", "glossary.html"]:
        check_phase5_metadata(filename)

    for path in [ROOT / "assets/editorial.css", ROOT / "scripts/phase5_sync.py"]:
        if not path.is_file():
            fail(f"Missing Phase 5 file: {path.relative_to(ROOT)}")

    check_sources()
    check_about()
    check_glossary()
    check_home()
    check_sitemap()

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nPhase 5 QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Phase 5 QA passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
