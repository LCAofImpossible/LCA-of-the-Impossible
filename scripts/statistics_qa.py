#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"Missing file: {relative}")
        return ""
    return path.read_text(encoding="utf-8")


def check_registry(episodes: list[dict]) -> dict[str, int]:
    if not episodes:
        fail("episodes.json contains no published episodes")
        return {}
    for episode in episodes:
        number = episode.get("number", "?")
        for key in ("seasonId", "seasonLabel", "lcaLabel"):
            if not isinstance(episode.get(key), str) or not episode[key].strip():
                fail(f"Episode #{number}: statistics field {key} is missing")
        for key in ("categories", "lcaCharacteristics"):
            values = episode.get(key)
            if not isinstance(values, list) or not values or not all(isinstance(value, str) and value.strip() for value in values):
                fail(f"Episode #{number}: statistics field {key} must be a non-empty string list")
        evidence = episode.get("evidence")
        if not isinstance(evidence, dict):
            fail(f"Episode #{number}: evidence profile is missing")
            continue
        for key in ("confidence", "proxyDependence", "assumptionSensitivity"):
            if evidence.get(key) not in {"Low", "Medium", "High"}:
                fail(f"Episode #{number}: evidence.{key} is not Low, Medium or High")
    return {
        "episodes": len(episodes),
        "seasons": len({episode.get("seasonId") for episode in episodes}),
        "lenses": len({episode.get("lcaLabel") for episode in episodes}),
        "signals": len({value for episode in episodes for value in episode.get("lcaCharacteristics", [])}),
        "subjects": len({value for episode in episodes for value in episode.get("categories", [])}),
    }


def check_page() -> None:
    raw = read("statistics.html")
    text = html.unescape(raw)
    if not raw:
        return
    required = [
        'data-page="statistics"',
        'id="stat-total">—</strong>',
        'id="stat-seasons">—</strong>',
        'id="stat-lenses">—</strong>',
        'id="stat-signals">—</strong>',
        'id="season-distribution"',
        'id="lens-distribution"',
        'id="characteristic-distribution"',
        'id="evidence-profiles"',
        'id="subject-distribution"',
        "DESCRIPTIVE, NOT COMPARATIVE",
        "NO SUMMED FOOTPRINT",
        "NO AVERAGE RESULT",
        "NO PERFORMANCE RANKING",
        "Subject tags are non-exclusive",
        'assets/statistics.css?v=20260828-statistics1',
        'assets/statistics.js?v=20260828-statistics1',
        'assets/telemetry.css?v=20260820-telemetry1',
        'assets/telemetry.js?v=20260820-telemetry1',
        BASE_URL + "statistics.html",
        '<!-- FEATURE-SEO:START -->',
        '<!-- FEATURE-SEO:END -->',
    ]
    for token in required:
        if token not in text:
            fail(f"statistics.html: required token missing: {token}")
    if re.search(r'<strong\s+id=["\']stat-(?:total|seasons|lenses|signals)["\']>\d+', raw):
        fail("statistics.html: summary values must not be hard-coded")

    blocks = re.findall(
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        raw,
        flags=re.I | re.S,
    )
    if len(blocks) != 1:
        fail(f"statistics.html: expected one JSON-LD block, found {len(blocks)}")
    else:
        try:
            data = json.loads(blocks[0])
        except json.JSONDecodeError as exc:
            fail(f"statistics.html: invalid JSON-LD ({exc})")
        else:
            if data.get("@type") != "CollectionPage":
                fail("statistics.html: JSON-LD must be a CollectionPage")
            if data.get("url") != BASE_URL + "statistics.html":
                fail("statistics.html: JSON-LD canonical URL is incorrect")


def check_client() -> None:
    script = read("assets/statistics.js")
    for token in [
        "fetch('episodes.json', { cache: 'no-store' })",
        "episode.seasonId",
        "episode.seasonLabel",
        "episode.lcaLabel",
        "episode.lcaCharacteristics",
        "episode.categories",
        "episode.evidence?.[field]",
        "Evidence confidence",
        "Proxy dependence",
        "Assumption sensitivity",
        "statistics-error",
    ]:
        if token not in script:
            fail(f"assets/statistics.js: required registry projection missing: {token}")
    for forbidden in [
        "episode.result",
        "impactValueKg",
        "parseResult",
        "averageFootprint",
        "totalFootprint",
        "localStorage",
        "sessionStorage",
    ]:
        if forbidden in script:
            fail(f"assets/statistics.js: forbidden aggregation or persistence token: {forbidden}")

    styles = read("assets/statistics.css")
    for token in [
        ".statistics-summary-grid",
        ".statistics-bar-track",
        ".statistics-signal-grid",
        ".statistics-evidence-grid",
        ".statistics-guardrail",
        "@media(max-width:820px)",
        "@media(max-width:580px)",
    ]:
        if token not in styles:
            fail(f"assets/statistics.css: required responsive style missing: {token}")


def check_integration() -> None:
    home = read("index.html")
    if 'href="statistics.html"' not in home or "What the archive is made of." not in home:
        fail("index.html: Statistics entry point is missing from Project Infrastructure")

    integration_files = {
        "scripts/feature_sync.py": ["statistics.html", "Catalogue Statistics"],
        "scripts/feature_qa.py": ["statistics.html", "assets/statistics.js"],
        "scripts/phase5_sync.py": ["statistics.html", 'explore_link("statistics.html", "Statistics")'],
        "scripts/phase5_qa.py": ["statistics.html"],
        "scripts/telemetry_sync.py": ["statistics.html"],
        "scripts/telemetry_qa.py": ["statistics.html"],
        "scripts/live_site_qa.py": ["statistics.html", "assets/statistics.css", "assets/statistics.js"],
        "scripts/publication_qa.py": ["statistics_qa.py"],
    }
    for filename, tokens in integration_files.items():
        text = read(filename)
        for token in tokens:
            if token not in text:
                fail(f"{filename}: Statistics integration missing: {token}")

    sitemap = read("sitemap.xml")
    try:
        root = ET.fromstring(sitemap)
    except ET.ParseError as exc:
        fail(f"sitemap.xml: invalid XML ({exc})")
    else:
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [loc.text for loc in root.findall("sm:url/sm:loc", ns) if loc.text]
        if urls.count(BASE_URL + "statistics.html") != 1:
            fail("sitemap.xml: Statistics URL must appear exactly once")

    readme = read("README.md")
    for token in ["## 34. Catalogue Statistics — mandatory", "scripts/statistics_qa.py", "No summed footprint"]:
        if token not in readme:
            fail(f"README.md: Statistics contract missing: {token}")


def main() -> int:
    registry = json.loads(read("episodes.json") or "{}")
    episodes = registry.get("episodes", [])
    summary = check_registry(episodes)
    check_page()
    check_client()
    check_integration()

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nStatistics QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    primary_lenses = Counter(episode["lcaLabel"] for episode in episodes)
    dominant_lens, dominant_count = primary_lenses.most_common(1)[0]
    print(
        "Statistics QA passed: "
        f"{summary['episodes']} episodes, {summary['seasons']} seasons, "
        f"{summary['lenses']} primary lenses, {summary['signals']} model signals; "
        f"largest lens {dominant_lens} ({dominant_count})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
