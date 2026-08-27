#!/usr/bin/env python3
"""Validate the public Method & Reading Guide as static, canonical content."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METHOD = ROOT / "method.html"
STYLE = ROOT / "assets" / "method.css"
HOME = ROOT / "index.html"
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"Missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def require_tokens(text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        if token not in text:
            fail(f"{label}: required token missing: {token}")


def require_order(text: str, tokens: list[str], label: str) -> None:
    positions = [text.find(token) for token in tokens]
    missing = [token for token, position in zip(tokens, positions) if position < 0]
    if missing:
        for token in missing:
            fail(f"{label}: ordered token missing: {token}")
        return
    if positions != sorted(positions):
        fail(f"{label}: canonical order changed: {' -> '.join(tokens)}")


def get_section(text: str, section_id: str) -> str:
    pattern = (
        r'<section\b(?=[^>]*\bid=["\']'
        + re.escape(section_id)
        + r'["\'])[^>]*>.*?</section>'
    )
    match = re.search(pattern, text, flags=re.I | re.S)
    if not match:
        fail(f"method.html: section #{section_id} missing")
        return ""
    return match.group(0)


def check_document_structure(text: str) -> None:
    if len(re.findall(r"<h1\b", text, flags=re.I)) != 1:
        fail("method.html: expected exactly one h1")

    ids = re.findall(r'\bid=["\']([^"\']+)["\']', text, flags=re.I)
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        fail(f"method.html: duplicate id values: {', '.join(duplicates)}")

    jumpnav_match = re.search(
        r'<nav\b[^>]*class=["\'][^"\']*method-jumpnav[^"\']*["\'][^>]*>.*?</nav>',
        text,
        flags=re.I | re.S,
    )
    if not jumpnav_match:
        fail("method.html: static method jump navigation missing")
        return
    jumpnav = jumpnav_match.group(0)
    expected_targets = ["read-an-episode", "pipeline", "evidence", "boundary", "meaning"]
    href_targets = re.findall(r'href=["\']#([^"\']+)["\']', jumpnav, flags=re.I)
    if href_targets != expected_targets:
        fail(
            "method.html: method jump navigation must be "
            + " -> ".join(expected_targets)
        )
    for target in href_targets:
        if target not in ids:
            fail(f"method.html: jump navigation target does not exist: #{target}")


def check_reading_guide(text: str) -> None:
    guide = get_section(text, "read-an-episode")
    if not guide:
        return

    scripts_removed = re.sub(r"<script\b.*?</script>", "", text, flags=re.I | re.S)
    if guide not in scripts_removed:
        fail("method.html: reading guide must be present as static HTML, outside scripts")

    steps = re.findall(r'data-reading-step=["\'](\d+)["\']', guide, flags=re.I)
    if steps != ["1", "2", "3", "4", "5", "6"]:
        fail(f"method.html: reading steps must be exactly 1-6 in order; found {steps}")

    require_order(
        guide,
        [
            "HEADLINE &amp; REPORTING BASIS",
            "SUBJECT &amp; RECONSTRUCTION",
            "INVENTORY &amp; SYSTEM BOUNDARY",
            "EMISSION FACTORS &amp; PROXIES",
            "BASELINE, CONTRIBUTIONS &amp; HOTSPOT",
            "SENSITIVITY &amp; INTERPRETATION",
        ],
        "method.html reading guide",
    )
    require_order(
        guide,
        ["Activity data", "Emission factor", "Contribution", "Baseline total"],
        "method.html calculation chain",
    )
    require_tokens(
        guide,
        [
            "TWO-MINUTE ORIENTATION",
            "FULL AUDIT ROUTE",
            "functional unit or reporting basis",
            "reference flow",
            "included and excluded processes",
            "cut-off",
            "source, year, geography and technology",
            "Evidence Profile",
            "one physical or data/model parameter at a time",
            'href="sources.html"',
            'href="glossary.html"',
        ],
        "method.html reading guide",
    )

    passport = re.search(
        r'<aside\b[^>]*class=["\'][^"\']*passport-guide[^"\']*["\'][^>]*>.*?</aside>',
        guide,
        flags=re.I | re.S,
    )
    if not passport:
        fail("method.html: Model Passport reading note missing")
    else:
        require_tokens(
            passport.group(0),
            [
                "quick orientation layer",
                "does not replace the detailed inventory",
                "not a verification statement",
            ],
            "method.html Model Passport note",
        )

    caution = re.search(
        r'<p\b[^>]*class=["\'][^"\']*reading-caution[^"\']*["\'][^>]*>.*?</p>',
        guide,
        flags=re.I | re.S,
    )
    if not caution:
        fail("method.html: cross-episode comparison warning missing")
    else:
        require_tokens(
            caution.group(0),
            [
                "functional units or reporting bases",
                "system boundaries",
                "timeframes",
                "geographic or technological contexts",
                "larger headline number may simply describe a larger service",
            ],
            "method.html comparison warning",
        )


def check_canonical_method(text: str) -> None:
    pipeline = get_section(text, "pipeline")
    require_order(
        pipeline,
        [
            "Define the subject",
            "Establish the evidence",
            "Define the functional unit",
            "Reconstruct the system",
            "Build the inventory",
            "Calculate the footprint",
            "Interpret the result",
        ],
        "method.html methodology pipeline",
    )

    evidence = get_section(text, "evidence")
    ladder = re.findall(
        r'<div\b[^>]*class=["\'][^"\']*evidence-ladder-row[^"\']*["\'][^>]*>\s*<strong>([^<]+)</strong>',
        evidence,
        flags=re.I | re.S,
    )
    if ladder != ["Known", "Reconstructed", "Inferred", "Assumed"]:
        fail(f"method.html: Evidence Ladder changed: {ladder}")
    for level in ["Low", "Medium", "High"]:
        if evidence.count(f"<i>{level}</i>") != 3:
            fail(f"method.html: Evidence Profile must show {level} exactly three times")

    factors = get_section(text, "factors")
    require_order(factors, [">Specific<", ">Representative<", ">Proxy<"], "method.html factor hierarchy")
    boundary = get_section(text, "boundary")
    require_tokens(boundary, ["Illustrative boundary only"], "method.html boundary")
    audit = get_section(text, "audit-trail")
    require_order(
        audit,
        [">Subject<", ">Source<", ">Assumption<", ">Activity data<", ">Factor<", ">Result<"],
        "method.html audit trail",
    )


def check_metadata_and_style(text: str, style: str, home: str) -> None:
    require_tokens(
        text,
        [
            "<title>Method &amp; Reading Guide — LCA of the Impossible</title>",
            'content="Method &amp; Reading Guide — LCA of the Impossible"',
            '"name": "Method & Reading Guide — LCA of the Impossible"',
            'assets/method.css?v=20260827-reading-guide1',
        ],
        "method.html metadata",
    )
    if 'assets/method.css?v=20260827-reading-guide1' not in home:
        fail("index.html: method stylesheet cache key is stale")
    require_tokens(
        style,
        [
            ".method-jumpnav",
            ".reading-equation",
            ".reading-routes",
            ".reader-step",
            ".reader-check",
            ".passport-guide",
            ".reading-caution",
            "@media(max-width:700px)",
            "@media(max-width:460px)",
        ],
        "assets/method.css",
    )


def main() -> int:
    method = read(METHOD)
    style = read(STYLE)
    home = read(HOME)
    if method:
        check_document_structure(method)
        check_reading_guide(method)
        check_canonical_method(method)
        check_metadata_and_style(method, style, home)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nMethod & Reading Guide QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Method & Reading Guide QA passed: 6 reading steps, 7 method stages, static guidance intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
