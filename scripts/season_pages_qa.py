#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
errors: list[str] = []
SEASONS = {
    "season-i": {
        "page": "season-i.html",
        "label": "Season I — Machines & Worlds",
        "descriptor": "Science fiction, reconstructed through life-cycle logic.",
        "editorial": "Impossible technologies, reconstructed as traceable systems.",
        "range": (1, 29),
        "scope": "vehicles, robots, machines, devices, infrastructure, habitats, artificial systems and megastructures",
        "other": "season-ii.html",
    },
    "season-ii": {
        "page": "season-ii.html",
        "label": "Season II — Myths & Legends",
        "descriptor": "Myths and legends, reconstructed through life-cycle logic.",
        "editorial": "Impossible stories, reconstructed as traceable systems.",
        "range": (30, 71),
        "scope": "myths, legends, folklore, legendary beings, places, objects, rites, punishments and supernatural systems",
        "other": "season-i.html",
    },
}


def fail(message: str) -> None:
    errors.append(message)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"Missing file: {relative}")
        return ""
    return path.read_text(encoding="utf-8")


def structured_data(text: str, label: str) -> dict:
    blocks = re.findall(
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        text,
        flags=re.I | re.S,
    )
    if len(blocks) != 1:
        fail(f"{label}: expected one JSON-LD block, found {len(blocks)}")
        return {}
    try:
        return json.loads(blocks[0])
    except json.JSONDecodeError as exc:
        fail(f"{label}: invalid JSON-LD ({exc})")
        return {}


def check_page(season_id: str, config: dict, episodes: list[dict]) -> None:
    filename = config["page"]
    raw = read(filename)
    text = html.unescape(raw)
    visible_text = re.sub(r"<[^>]+>", " ", text)
    visible_text = re.sub(r"\s+", " ", visible_text).strip()
    if not raw:
        return
    start, end = config["range"]
    required = [
        f'data-season-id="{season_id}"',
        f'data-range-start="{start}"',
        f'data-range-end="{end}"',
        f'href="archive.html?season={season_id}"',
        'href="method.html#read-an-episode"',
        f'href="{config["other"]}"',
        'id="season-count"',
        'id="season-episode-grid"',
        'id="season-load-more"',
        'assets/seasons.css?v=20260827-season-pages1',
        'assets/seasons.js?v=20260827-season-pages1',
        'assets/telemetry.css?v=20260820-telemetry1',
        'assets/telemetry.js?v=20260820-telemetry1',
    ]
    for token in required:
        if token not in text:
            fail(f"{filename}: required token missing: {token}")
    for token in [config["label"], config["descriptor"], config["editorial"], config["scope"]]:
        if token not in visible_text:
            fail(f"{filename}: required visible editorial text missing: {token}")
    if re.search(r'<img\b', raw, flags=re.I):
        fail(f"{filename}: static episode imagery must come only from episodes.json through seasons.js")

    data = structured_data(raw, filename)
    if data:
        canonical = BASE_URL + filename
        if data.get("@type") != "CollectionPage" or data.get("url") != canonical:
            fail(f"{filename}: JSON-LD must be the canonical CollectionPage")
        item_list = data.get("mainEntity", {})
        if item_list.get("@type") != "ItemList":
            fail(f"{filename}: JSON-LD mainEntity must be an ItemList")
        season_episodes = sorted(
            [episode for episode in episodes if episode.get("seasonId") == season_id],
            key=lambda episode: episode["number"],
            reverse=True,
        )
        if item_list.get("numberOfItems") != len(season_episodes):
            fail(f"{filename}: JSON-LD published count differs from episodes.json")
        expected_urls = [BASE_URL + episode["url"] for episode in season_episodes]
        actual_urls = [item.get("url") for item in item_list.get("itemListElement", [])]
        if actual_urls != expected_urls:
            fail(f"{filename}: JSON-LD catalogue order or membership differs from episodes.json")


def check_entry_points() -> None:
    for filename in ["index.html", "collections.html"]:
        text = html.unescape(read(filename))
        for season_id, config in SEASONS.items():
            if f'href="{config["page"]}"' not in text:
                fail(f"{filename}: missing dedicated {season_id} introduction link")
            if config["descriptor"] not in text:
                fail(f"{filename}: missing canonical {season_id} descriptor")
        if "assets/seasons.css?v=20260827-season-pages1" not in text:
            fail(f"{filename}: season route styles missing")


def check_assets() -> None:
    script = read("assets/seasons.js")
    for token in [
        "episode.seasonId === seasonId",
        ".sort((a, b) => Number(b.number) - Number(a.number))",
        "const pageSize = 9",
        "fetch('episodes.json', { cache: 'no-store' })",
        "visible += pageSize",
        "escapeHtml",
    ]:
        if token not in script:
            fail(f"assets/seasons.js: required registry behaviour missing: {token}")
    for forbidden in ["season-i': [", 'season-ii": [', "localStorage", "sessionStorage"]:
        if forbidden in script:
            fail(f"assets/seasons.js: catalogue must remain registry-driven: {forbidden}")

    styles = read("assets/seasons.css")
    for token in [
        ".season-hero",
        ".season-grammar-grid",
        ".season-route-grid",
        ".season-episode-grid.cards.episode-grid",
        "@media(max-width:900px)",
        "@media(max-width:620px)",
    ]:
        if token not in styles:
            fail(f"assets/seasons.css: required responsive style missing: {token}")


def check_infrastructure() -> None:
    files = {
        "scripts/phase5_sync.py": ["season-i.html", "season-ii.html"],
        "scripts/phase5_qa.py": ["season-i.html", "season-ii.html"],
        "scripts/telemetry_sync.py": ["season-i.html", "season-ii.html"],
        "scripts/telemetry_qa.py": ["season-i.html", "season-ii.html"],
        "scripts/live_site_qa.py": ["season-i.html", "season-ii.html", "assets/seasons.css", "assets/seasons.js"],
        "scripts/publication_qa.py": ["season_pages_qa.py"],
    }
    for filename, tokens in files.items():
        text = read(filename)
        for token in tokens:
            if token not in text:
                fail(f"{filename}: season publication path missing: {token}")

    sitemap = read("sitemap.xml")
    try:
        root = ET.fromstring(sitemap)
    except ET.ParseError as exc:
        fail(f"sitemap.xml: invalid XML ({exc})")
    else:
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [loc.text for loc in root.findall("sm:url/sm:loc", ns) if loc.text]
        for config in SEASONS.values():
            expected = BASE_URL + config["page"]
            if urls.count(expected) != 1:
                fail(f"sitemap.xml: expected exactly one {config['page']} URL")

    readme = read("README.md")
    for token in ["### 33.1 Dedicated season introduction pages", "scripts/season_pages_qa.py"]:
        if token not in readme:
            fail(f"README.md: season-page contract missing: {token}")


def main() -> int:
    registry = json.loads(read("episodes.json") or "{}")
    episodes = registry.get("episodes", [])
    counts: dict[str, int] = {}
    for season_id, config in SEASONS.items():
        season_episodes = [episode for episode in episodes if episode.get("seasonId") == season_id]
        counts[season_id] = len(season_episodes)
        if not season_episodes:
            fail(f"episodes.json: no published episodes for {season_id}")
        check_page(season_id, config, episodes)

    check_entry_points()
    check_assets()
    check_infrastructure()

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nSeason page QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(
        "Season page QA passed: "
        f"Season I {counts['season-i']} published / Season II {counts['season-ii']} published."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
