#!/usr/bin/env python3
"""Validate The Impossible Atlas registry projection and publication contract."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ROOT_PAGES = (
    "index.html",
    "archive.html",
    "compare.html",
    "explore.html",
    "collections.html",
    "method.html",
    "sources.html",
    "about.html",
    "glossary.html",
    "season-i.html",
    "season-ii.html",
    "statistics.html",
)
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(relative: str) -> str:
    try:
        return (ROOT / relative).read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"Unable to read {relative}: {exc}")
        return ""


def require_tokens(text: str, relative: str, tokens: tuple[str, ...]) -> None:
    for token in tokens:
        if token not in text:
            fail(f"{relative}: missing Atlas contract token {token!r}")


def structured_value(episode: dict[str, Any], *path: str) -> Any:
    value: Any = episode.get("structuredMetadata") or {}
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def main() -> int:
    try:
        registry = json.loads((ROOT / "episodes.json").read_text(encoding="utf-8"))
        migration = json.loads(
            (ROOT / "verification" / "structured-metadata-migration.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Registry or migration manifest is unavailable: {exc}")
        registry = {}
        migration = {}

    episodes = registry.get("episodes", [])
    if not isinstance(episodes, list) or not episodes:
        fail("episodes.json contains no episodes for the Atlas")
        episodes = []

    allowed_missing = migration.get("allowedMissingEpisodeNumbers", [])
    actual_missing = sorted(
        episode.get("number")
        for episode in episodes
        if isinstance(episode, dict) and not episode.get("structuredMetadata")
    )
    if actual_missing != allowed_missing:
        fail("Atlas metadata gaps do not match the controlled migration manifest")

    seasons: set[str] = set()
    subjects: set[str] = set()
    hotspots: set[str] = set()
    signals: set[str] = set()
    intersections: set[tuple[str, str]] = set()
    for episode in episodes:
        season = episode.get("seasonId")
        if isinstance(season, str) and season:
            seasons.add(season)
        else:
            fail(f"Episode #{episode.get('number')}: missing Atlas seasonId")

        characteristics = episode.get("lcaCharacteristics")
        if not isinstance(characteristics, list) or not characteristics:
            fail(f"Episode #{episode.get('number')}: missing Atlas LCA model signals")
        else:
            signals.update(value for value in characteristics if isinstance(value, str) and value)

        if episode.get("structuredMetadata"):
            subject = structured_value(episode, "subject", "entityType")
            hotspot = structured_value(episode, "impact", "hotspotStage")
            if not isinstance(subject, str) or not subject:
                fail(f"Episode #{episode.get('number')}: missing structured subject type")
            else:
                subjects.add(subject)
            if not isinstance(hotspot, str) or not hotspot:
                fail(f"Episode #{episode.get('number')}: missing structured hotspot stage")
            else:
                hotspots.add(hotspot)
            if isinstance(subject, str) and subject and isinstance(hotspot, str) and hotspot:
                intersections.add((subject, hotspot))

    for label, values in (
        ("seasons", seasons),
        ("subject types", subjects),
        ("hotspot stages", hotspots),
        ("model signals", signals),
        ("subject × hotspot intersections", intersections),
    ):
        if not values:
            fail(f"Atlas registry projection contains no {label}")

    explore = read("explore.html")
    atlas_js = read("assets/atlas.js")
    atlas_css = read("assets/atlas.css")
    site_js = read("assets/site.js")
    feature_sync = read("scripts/feature_sync.py")
    phase5_sync = read("scripts/phase5_sync.py")
    publication = read("scripts/publication_qa.py")
    live_qa = read("scripts/live_site_qa.py")

    require_tokens(
        explore,
        "explore.html",
        (
            "THE IMPOSSIBLE ATLAS",
            "Compare the reasoning freely.",
            'id="atlas-overview"',
            'id="atlas-routes"',
            'id="atlas-relationships"',
            'id="atlas-season-routes"',
            'id="atlas-subject-routes"',
            'id="atlas-hotspot-routes"',
            'id="atlas-lca-routes"',
            'id="atlas-matrix"',
            'id="impact-scale"',
            "assets/atlas.css?v=20260829-atlas1",
            "assets/atlas.js?v=20260829-atlas1",
            "Do not read this as a ranking",
        ),
    )
    require_tokens(
        atlas_js,
        "assets/atlas.js",
        (
            "episodes.json",
            "structuredMetadata",
            "subject?.entityType",
            "impact?.hotspotStage",
            "lcaCharacteristics",
            "archiveHref",
            "URLSearchParams",
            "renderMatrix",
            "season:",
            "subject:",
            "hotspot:",
            "archiveHref({ lca })",
            "data-atlas-status",
        ),
    )
    if "episode.result" in atlas_js or "resultKg" in atlas_js:
        fail("assets/atlas.js must not aggregate or rank episode headline results")
    require_tokens(
        atlas_css,
        "assets/atlas.css",
        (
            ".atlas-summary-grid",
            ".atlas-route-grid",
            ".atlas-matrix-wrap",
            "overflow-x:auto",
            "@media(max-width:820px)",
            "@media(max-width:580px)",
        ),
    )
    require_tokens(site_js, "assets/site.js", ("resultToKg", "Math.log10", "episode.result", "renderExplore"))
    require_tokens(
        feature_sync,
        "scripts/feature_sync.py",
        ("The Impossible Atlas", "subject-type × hotspot-stage", "assets/atlas.css", "assets/atlas.js"),
    )
    require_tokens(phase5_sync, "scripts/phase5_sync.py", ('explore_link("explore.html", "Atlas")',))
    require_tokens(publication, "scripts/publication_qa.py", ('"atlas_qa.py"',))
    require_tokens(live_qa, "scripts/live_site_qa.py", ("Impossible Atlas", '"assets/atlas.js"', '"assets/atlas.css"'))

    if (ROOT / "atlas.html").exists():
        fail("atlas.html duplicates the canonical explore.html Atlas route")

    nav_pattern = re.compile(r'<a href="(?:\.\./)?explore\.html"(?: aria-current="page")?>Atlas</a>')
    navigation_paths = [ROOT / name for name in ROOT_PAGES] + sorted((ROOT / "episodes").glob("*.html"))
    for path in navigation_paths:
        if path.is_file() and not nav_pattern.search(path.read_text(encoding="utf-8")):
            fail(f"{path.relative_to(ROOT)}: canonical Atlas navigation label missing")

    for relative in ("assets/atlas.js", "assets/site.js"):
        syntax = subprocess.run(
            ["node", "--check", str(ROOT / relative)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if syntax.returncode:
            fail(f"{relative}: JavaScript syntax validation failed: {syntax.stdout.strip()}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nImpossible Atlas QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(
        "Impossible Atlas QA passed: "
        f"{len(episodes)} cases; {len(episodes) - len(actual_missing)} structured; "
        f"{len(seasons)} seasons; {len(subjects)} subject types; {len(hotspots)} hotspot stages; "
        f"{len(signals)} model signals; {len(intersections)} mapped intersections."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
