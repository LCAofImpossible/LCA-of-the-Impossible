#!/usr/bin/env python3
"""Validate the registry-driven advanced archive search and filter contract."""

from __future__ import annotations

import json
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FILTER_PARAMS = (
    "q",
    "season",
    "category",
    "lca",
    "subject",
    "hotspot",
    "boundary",
    "confidence",
    "proxy",
    "sensitivity",
)
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def require_token(text: str, token: str, label: str) -> None:
    if token not in text:
        fail(f"{label}: missing advanced-archive contract token {token!r}")


def read_text(relative: str) -> str:
    path = ROOT / relative
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"Unable to read {relative}: {exc}")
        return ""


def normalize(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(character for character in text if not unicodedata.combining(character)).lower()


def searchable_text(episode: dict[str, Any]) -> str:
    metadata = episode.get("structuredMetadata") or {}
    subject = metadata.get("subject") or {}
    assessment = metadata.get("assessment") or {}
    impact = metadata.get("impact") or {}
    model = metadata.get("model") or {}
    evidence = episode.get("evidence") or {}
    values: list[Any] = [
        episode.get("title"),
        f"episode {episode.get('number')}",
        f"#{episode.get('number')}",
        episode.get("result"),
        episode.get("hotspot"),
        episode.get("featuredDescription"),
        episode.get("functionalUnit"),
        episode.get("categoryLabel"),
        episode.get("lcaLabel"),
        episode.get("seasonId"),
        episode.get("seasonLabel"),
        subject.get("narrativeDomain"),
        subject.get("entityType"),
        subject.get("narrativeOrigin"),
        assessment.get("reportingBasisType"),
        assessment.get("referenceFlow"),
        assessment.get("boundaryType"),
        assessment.get("geographicContext"),
        assessment.get("technologyContext"),
        impact.get("hotspotStage"),
        model.get("archetype"),
        model.get("primaryDriver"),
        evidence.get("confidence"),
        evidence.get("proxyDependence"),
        evidence.get("assumptionSensitivity"),
    ]
    for field in (
        episode.get("categories"),
        episode.get("lcaCharacteristics"),
        episode.get("taxonomy"),
        episode.get("collectionSlugs"),
        episode.get("keywords"),
        assessment.get("includedStages"),
        assessment.get("excludedStages"),
        model.get("secondaryDrivers"),
    ):
        if isinstance(field, list):
            values.extend(field)
    return normalize(" ".join(str(value) for value in values if value is not None))


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
        fail("episodes.json contains no episodes for archive filtering")
        episodes = []

    allowed_missing = migration.get("allowedMissingEpisodeNumbers", [])
    missing_metadata = sorted(
        episode.get("number")
        for episode in episodes
        if isinstance(episode, dict) and "structuredMetadata" not in episode
    )
    if missing_metadata != allowed_missing:
        fail("Advanced archive metadata gaps do not match the controlled migration manifest")

    facet_sets: dict[str, set[str]] = {
        "subject": set(),
        "hotspot": set(),
        "boundary": set(),
        "confidence": set(),
        "proxy": set(),
        "sensitivity": set(),
    }
    for episode in episodes:
        metadata = episode.get("structuredMetadata") or {}
        subject = metadata.get("subject") or {}
        assessment = metadata.get("assessment") or {}
        impact = metadata.get("impact") or {}
        evidence = episode.get("evidence") or {}
        candidates = {
            "subject": subject.get("entityType"),
            "hotspot": impact.get("hotspotStage"),
            "boundary": assessment.get("boundaryType"),
            "confidence": evidence.get("confidence"),
            "proxy": evidence.get("proxyDependence"),
            "sensitivity": evidence.get("assumptionSensitivity"),
        }
        for facet, value in candidates.items():
            if value is not None:
                if not isinstance(value, str) or not value.strip():
                    fail(f"Episode #{episode.get('number')}: invalid {facet} filter value")
                else:
                    facet_sets[facet].add(value)

        text = searchable_text(episode)
        if normalize(episode.get("title")) not in text:
            fail(f"Episode #{episode.get('number')}: title is not searchable")
        if f"#{episode.get('number')}" not in text:
            fail(f"Episode #{episode.get('number')}: hash-prefixed number is not searchable")

    for facet, values in facet_sets.items():
        if not values:
            fail(f"Advanced archive facet {facet!r} has no approved values")
    for facet in ("confidence", "proxy", "sensitivity"):
        if not facet_sets[facet].issubset({"High", "Medium", "Low"}):
            fail(f"Evidence facet {facet!r} contains unsupported levels: {sorted(facet_sets[facet])}")

    archive = read_text("archive.html")
    site_js = read_text("assets/site.js")
    style = read_text("assets/style.css")
    readme = read_text("README.md")
    publication = read_text("scripts/publication_qa.py")
    live_qa = read_text("scripts/live_site_qa.py")

    for token in (
        'id="subject-filter"',
        'id="hotspot-filter"',
        'id="boundary-filter"',
        'id="evidence-confidence-filter"',
        'id="proxy-dependence-filter"',
        'id="assumption-sensitivity-filter"',
        'id="clear-filters"',
        'id="active-filters"',
        "data-clear-archive",
        "Search subject, title, episode number, category or keyword",
        "assets/site.js?v=20260829-advanced-archive1",
        "assets/style.css?v=20260829-advanced-archive1",
    ):
        require_token(archive, token, "archive.html")

    for token in (
        "archiveStateFromUrl",
        "writeArchiveToUrl",
        "normalize('NFKD')",
        "metadata.subject?.entityType",
        "metadata.impact?.hotspotStage",
        "metadata.assessment?.boundaryType",
        "episode.evidence?.confidence",
        "episode.evidence?.proxyDependence",
        "episode.evidence?.assumptionSensitivity",
        "activeQuery",
        "activeSubject",
        "activeHotspot",
        "activeBoundary",
        "activeConfidence",
        "activeProxy",
        "activeSensitivity",
        "visibleLimit = 9",
        "visibleLimit += 9",
        "Showing ${shown} of",
        "resetArchive",
        "window.addEventListener('popstate'",
        "writeArchiveToUrl('replace')",
    ):
        require_token(site_js, token, "assets/site.js")
    for parameter in FILTER_PARAMS:
        require_token(site_js, f"'{parameter}'", "assets/site.js URL state")

    syntax = subprocess.run(
        ["node", "--check", str(ROOT / "assets" / "site.js")],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if syntax.returncode:
        fail(f"assets/site.js failed JavaScript syntax validation: {syntax.stdout.strip()}")

    for token in (
        ".advanced-filter-grid",
        ".filter-select-label",
        ".archive-search-row",
        ".archive-active-filters",
        "grid-template-columns:repeat(3",
        "grid-template-columns:repeat(2",
        ".advanced-filter-grid,.archive-search-row{grid-template-columns:1fr}",
    ):
        require_token(style, token, "assets/style.css")

    for token in (
        "Every archive state is shareable",
        "structuredMetadata",
        "Evidence Profile",
        "confidence",
        "sensitivity",
    ):
        require_token(readme, token, "README.md")
    require_token(publication, '"advanced_archive_qa.py"', "scripts/publication_qa.py")
    require_token(live_qa, "Advanced archive", "scripts/live_site_qa.py")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nAdvanced archive QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(
        "Advanced archive QA passed: "
        f"{len(episodes)} episodes; {len(episodes) - len(missing_metadata)} structured records; "
        f"{len(FILTER_PARAMS)} shareable state parameters; 9-case progressive reveal."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
