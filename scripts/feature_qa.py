#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
ALLOWED_LEVELS = {"Low", "Medium", "High"}
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def require_file(relative: str) -> Path:
    path = ROOT / relative
    if not path.is_file():
        fail(f"Missing Phase 3 file: {relative}")
    return path


def main() -> int:
    registry_path = require_file("episodes.json")
    require_file("assets/features.css")
    site_js = require_file("assets/site.js")
    compare = require_file("compare.html")
    explore = require_file("explore.html")
    statistics = require_file("statistics.html")
    statistics_js = require_file("assets/statistics.js")
    require_file("assets/statistics.css")
    sitemap = require_file("sitemap.xml")

    if registry_path.is_file():
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        if data.get("schemaVersion", 0) < 2:
            fail("episodes.json schemaVersion must be >= 2 for Phase 3")
        for episode in data.get("episodes", []):
            number = episode.get("number", "?")
            functional_unit = episode.get("functionalUnit")
            if not isinstance(functional_unit, str) or len(functional_unit.strip()) < 20:
                fail(f"Episode #{number}: missing meaningful functionalUnit")
            evidence = episode.get("evidence")
            if not isinstance(evidence, dict):
                fail(f"Episode #{number}: missing evidence profile")
                continue
            for key in ("confidence", "proxyDependence", "assumptionSensitivity"):
                if evidence.get(key) not in ALLOWED_LEVELS:
                    fail(f"Episode #{number}: evidence.{key} must be Low, Medium or High")
            for key in ("basis", "uncertainty"):
                value = evidence.get(key)
                if not isinstance(value, str) or len(value.strip()) < 30:
                    fail(f"Episode #{number}: evidence.{key} is missing or too short")

    if site_js.is_file():
        text = site_js.read_text(encoding="utf-8")
        for token in ("renderCompare", "renderExplore", "renderEvidenceProfile", "compareStorageKey", "season-filters", "seasonLabel", "renderSeasonSpotlight"):
            if token not in text:
                fail(f"assets/site.js missing Phase 3 function/token: {token}")

    archive = require_file("archive.html")
    if archive.is_file() and 'id="season-filters"' not in archive.read_text(encoding="utf-8"):
        fail("archive.html: season filter container missing")

    for path, canonical, page_name, script_name in (
        (compare, BASE_URL + "compare.html", "compare.html", "assets/site.js"),
        (explore, BASE_URL + "explore.html", "explore.html", "assets/site.js"),
        (statistics, BASE_URL + "statistics.html", "statistics.html", "assets/statistics.js"),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if f'<script src="{script_name}' not in text:
            fail(f"{page_name}: missing {script_name}")
        if canonical not in text:
            fail(f"{page_name}: canonical URL missing")
        if "<!-- FEATURE-SEO:START -->" not in text or "<!-- FEATURE-SEO:END -->" not in text:
            fail(f"{page_name}: Phase 3 SEO block missing")
        if 'name="robots" content="index,follow,max-image-preview:large"' not in text:
            fail(f"{page_name}: robots metadata missing")

    if statistics_js.is_file():
        text = statistics_js.read_text(encoding="utf-8")
        for token in ("episodes.json", "lcaCharacteristics", "proxyDependence", "assumptionSensitivity", "subject-distribution"):
            if token not in text:
                fail(f"assets/statistics.js missing registry statistic token: {token}")
        if "episode.result" in text:
            fail("assets/statistics.js must not aggregate or rank headline results")

    if sitemap.is_file():
        text = sitemap.read_text(encoding="utf-8")
        for url in (BASE_URL + "compare.html", BASE_URL + "explore.html", BASE_URL + "statistics.html"):
            if text.count(url) != 1:
                fail(f"sitemap.xml must contain exactly one entry for {url}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nPhase 3 QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Phase 3 QA passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
