#!/usr/bin/env python3
"""Validate the non-ranking visual synthesis in Compare Cases."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
LEVELS = {"Low", "Medium", "High"}


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
            fail(f"{relative}: missing visual-synthesis token {token!r}")


def result_to_kg(result: str) -> float | None:
    number_match = re.search(r"[\d.,]+", result)
    unit_match = re.search(r"\b(Mt|kt|t|kg)\s*CO", result, flags=re.I)
    if not number_match or not unit_match:
        return None
    try:
        value = float(number_match.group(0).replace(",", ""))
    except ValueError:
        return None
    multiplier = {"mt": 1e9, "kt": 1e6, "t": 1e3, "kg": 1.0}[unit_match.group(1).lower()]
    return value * multiplier


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
        fail("At least two registered episodes are required for visual synthesis")
        episodes = []

    positionable = 0
    structured_shares = 0
    actual_missing: list[int] = []
    for episode in episodes:
        number = episode.get("number")
        result = str(episode.get("result", ""))
        result_kg = result_to_kg(result)
        if result_kg is None or result_kg <= 0:
            fail(f"Episode #{number}: published result cannot be positioned on the magnitude axis")
        else:
            positionable += 1

        evidence = episode.get("evidence")
        if not isinstance(evidence, dict):
            fail(f"Episode #{number}: Evidence Profile is unavailable")
        else:
            for field in ("confidence", "proxyDependence", "assumptionSensitivity"):
                if evidence.get(field) not in LEVELS:
                    fail(f"Episode #{number}: {field} is not a controlled ordinal level")

        metadata = episode.get("structuredMetadata")
        if not isinstance(metadata, dict):
            if isinstance(number, int):
                actual_missing.append(number)
            continue
        hotspot_stage = nested(metadata, "impact", "hotspotStage")
        hotspot_share = nested(metadata, "impact", "hotspotSharePercent")
        if not isinstance(hotspot_stage, str) or not hotspot_stage.strip():
            fail(f"Episode #{number}: registered hotspot stage is unavailable")
        if not isinstance(hotspot_share, (int, float)) or isinstance(hotspot_share, bool):
            fail(f"Episode #{number}: registered hotspot share is not numeric")
        elif not 0 <= float(hotspot_share) <= 100:
            fail(f"Episode #{number}: registered hotspot share is outside 0–100%")
        else:
            structured_shares += 1

    if sorted(actual_missing) != migration.get("allowedMissingEpisodeNumbers", []):
        fail("Visual-synthesis metadata gaps do not match the controlled migration manifest")

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
            "visual synthesis adds headline magnitude",
            "assets/compare.css?v=20260829-compare-synthesis1",
            "assets/site.js?v=20260830-subject-descriptions1",
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
            "magnitudeBand",
            "evidenceSignal",
            "visualSummaryCard",
            "resultToKg(episode.result)",
            "const minLog = 0",
            "const maxLog = 10",
            "Math.log10(resultKg)",
            "comparison-visual-summary",
            "Magnitude, hotspot and evidence signals",
            "Three separate readings. No composite score.",
            "comparison-magnitude-axis",
            "comparison-hotspot-track",
            "Registered hotspot share",
            "Evidence signals · separate ordinal fields",
            "level === registered",
            "only to place each published headline result",
            "Functional units, time horizons and boundaries are not harmonized",
            "never combined into a score",
        ),
    )
    for forbidden in (
        "compositeScore",
        "evidenceScore",
        "rankScore",
        "chosen.sort(",
        "winnerCase",
        "loserCase",
        "Math.max(...chosen",
        "Math.min(...chosen",
    ):
        if forbidden in compare_block:
            fail(f"assets/site.js renderCompare: prohibited visual comparison operation {forbidden!r}")

    require_tokens(
        compare_css,
        "assets/compare.css",
        (
            ".comparison-visual-summary",
            ".comparison-magnitude-axis",
            ".comparison-signal-grid",
            ".comparison-magnitude-track",
            ".comparison-magnitude-point",
            ".comparison-hotspot-track",
            ".comparison-level-scale",
            '.comparison-level-scale span[data-selected="true"]',
            ".comparison-visual-guardrail",
            "@media(max-width:980px)",
            "@media(max-width:620px)",
        ),
    )
    require_tokens(
        feature_sync,
        "scripts/feature_sync.py",
        (
            "published headline magnitude on one fixed logarithmic axis",
            "Hotspot shares remain contributions within their own cases",
            "produce no composite score",
        ),
    )
    require_tokens(publication, "scripts/publication_qa.py", ('"comparison_synthesis_qa.py"',))
    require_tokens(live_qa, "scripts/live_site_qa.py", ("Comparison visual synthesis", "comparison-visual-summary"))

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
        print(f"\nComparison visual-synthesis QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(
        "Comparison visual-synthesis QA passed: "
        f"{positionable} magnitude positions; {structured_shares} registered hotspot shares; "
        "3 separate Evidence Profile signals; fixed axis; no composite score or ranking."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
