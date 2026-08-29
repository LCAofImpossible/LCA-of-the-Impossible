#!/usr/bin/env python3
"""Validate the methodological foundation of the episode comparison tool."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
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
            fail(f"{relative}: missing comparison-foundation token {token!r}")


def nested(record: dict[str, Any], *path: str) -> Any:
    value: Any = record
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
    if not isinstance(episodes, list) or len(episodes) < 2:
        fail("At least two registered episodes are required for comparison")
        episodes = []

    actual_missing = sorted(
        episode.get("number")
        for episode in episodes
        if isinstance(episode, dict) and not episode.get("structuredMetadata")
    )
    if actual_missing != migration.get("allowedMissingEpisodeNumbers", []):
        fail("Comparison metadata gaps do not match the controlled migration manifest")

    structured_paths = (
        ("assessment", "reportingBasisType"),
        ("assessment", "referenceFlow"),
        ("assessment", "boundaryType"),
        ("assessment", "includedStages"),
        ("assessment", "excludedStages"),
        ("assessment", "temporalContext"),
        ("assessment", "geographicContext"),
        ("assessment", "technologyContext"),
        ("assessment", "cutoffSummary"),
        ("impact", "indicator"),
        ("impact", "unit"),
        ("impact", "hotspotStage"),
        ("model", "archetype"),
        ("model", "primaryDriver"),
        ("model", "secondaryDrivers"),
        ("model", "repetitionClass"),
        ("provenance", "missingApprovedFields"),
    )
    optional_paths = {("assessment", "geographicContext")}
    for episode in episodes:
        metadata = episode.get("structuredMetadata")
        if not isinstance(metadata, dict):
            continue
        for path in structured_paths:
            value = nested(metadata, *path)
            if value is None and path not in optional_paths:
                fail(f"Episode #{episode.get('number')}: comparison field {'.'.join(path)} is absent")
            if isinstance(value, str) and not value.strip():
                fail(f"Episode #{episode.get('number')}: comparison field {'.'.join(path)} is blank")

    compare_html = read("compare.html")
    compare_css = read("assets/compare.css")
    site_js = read("assets/site.js")
    feature_sync = read("scripts/feature_sync.py")
    publication = read("scripts/publication_qa.py")
    live_qa = read("scripts/live_site_qa.py")

    require_tokens(
        compare_html,
        "compare.html",
        (
            "METHODOLOGICAL VIEW",
            "assets/compare.css?v=20260829-compare-foundation1",
            "assets/site.js?v=20260829-compare-foundation1",
            'id="compare-picker"',
            'id="comparison-output"',
            'aria-live="polite"',
        ),
    )
    compare_match = re.search(r"  const renderCompare = \(episodes\) => \{.*?\n  const resultToKg", site_js, flags=re.S)
    if not compare_match:
        fail("assets/site.js: unable to isolate renderCompare implementation")
        compare_block = ""
    else:
        compare_block = compare_match.group(0)
    require_tokens(
        compare_block,
        "assets/site.js renderCompare",
        (
            "parseCasesFromUrl",
            "comparisonStatus",
            "comparison-basis-grid",
            "Direct footprint comparison",
            "Not established",
            "Compare the reasoning freely.",
            "calculates no ratios",
            "Functional unit",
            "Reporting-basis type",
            "Reference flow",
            "Boundary type",
            "Included stages",
            "Excluded stages",
            "Temporal context",
            "Geographic context",
            "Technology context",
            "Cut-off summary",
            "Headline result",
            "Hotspot stage",
            "MODEL ARCHITECTURE",
            "Evidence confidence",
            "Missing approved fields",
            "Not structurally registered",
        ),
    )
    for forbidden in ("normalizedKgCO2e", "resultToKg(", "Math.log10", "rankScore", "better case", "worse case"):
        if forbidden in compare_block:
            fail(f"assets/site.js renderCompare: prohibited comparison operation or claim {forbidden!r}")

    require_tokens(
        compare_css,
        "assets/compare.css",
        (
            ".comparison-basis",
            ".comparison-basis-grid",
            '.comparison-basis-card[data-state="different"]',
            '.comparison-basis-card[data-state="incomplete"]',
            '.comparison-basis-card[data-state="aligned"]',
            ".comparison-table-group",
            ".comparison-value-missing",
            "@media(max-width:980px)",
            "@media(max-width:620px)",
        ),
    )
    require_tokens(
        feature_sync,
        "scripts/feature_sync.py",
        ("direct footprint comparison remains **Not established**", "assets/compare.css", "Missing structured fields"),
    )
    require_tokens(publication, "scripts/publication_qa.py", ('"comparison_foundation_qa.py"',))
    require_tokens(live_qa, "scripts/live_site_qa.py", ("Comparison foundation", '"assets/compare.css"'))

    syntax = subprocess.run(
        ["node", "--check", str(ROOT / "assets" / "site.js")],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if syntax.returncode:
        fail(f"assets/site.js: JavaScript syntax validation failed: {syntax.stdout.strip()}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nComparison foundation QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(
        "Comparison foundation QA passed: "
        f"{len(episodes)} selectable cases; {len(episodes) - len(actual_missing)} structured records; "
        f"{len(structured_paths)} controlled structured fields; 2–3 case selection; direct comparability not established."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
