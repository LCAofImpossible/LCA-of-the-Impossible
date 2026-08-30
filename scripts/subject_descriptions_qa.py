#!/usr/bin/env python3
"""Validate the short, registry-driven descriptions of analysed subjects."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def require_tokens(path: str, tokens: tuple[str, ...]) -> None:
    source = (ROOT / path).read_text(encoding="utf-8")
    for token in tokens:
        if token not in source:
            fail(f"{path}: missing subject-description contract token {token!r}")


def main() -> int:
    try:
        registry = json.loads((ROOT / "episodes.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"episodes.json is unavailable or invalid: {exc}")
        registry = {}

    episodes = registry.get("episodes")
    if not isinstance(episodes, list) or not episodes:
        fail("episodes.json must contain a non-empty episodes array")
        episodes = []

    seen: dict[str, int] = {}
    for episode in episodes:
        number = episode.get("number")
        description = episode.get("subjectDescription")
        prefix = f"Episode #{number}"
        if not isinstance(description, str):
            fail(f"{prefix}: subjectDescription must be a string")
            continue
        normalized = " ".join(description.split())
        if description != normalized:
            fail(f"{prefix}: subjectDescription must use single-line normalized whitespace")
        if not 100 <= len(normalized) <= 190:
            fail(f"{prefix}: subjectDescription must be 100–190 characters, found {len(normalized)}")
        if not normalized.endswith((".", "!", "?")):
            fail(f"{prefix}: subjectDescription must be a complete sentence")
        if re.search(r"<[^>]+>", normalized):
            fail(f"{prefix}: subjectDescription must not contain HTML")
        if re.search(r"\b(?:kg|t|kt|Mt)\s*CO(?:2|₂)e\b", normalized, flags=re.I):
            fail(f"{prefix}: subjectDescription must not repeat the headline footprint")
        if normalized == episode.get("featuredDescription"):
            fail(f"{prefix}: subjectDescription must remain distinct from the LCA summary")
        key = normalized.casefold()
        if key in seen:
            fail(f"{prefix}: subjectDescription duplicates Episode #{seen[key]}")
        seen[key] = number
        page_path = ROOT / str(episode.get("url", ""))
        page_source = page_path.read_text(encoding="utf-8") if page_path.is_file() else ""
        for token in (
            "../assets/style.css?v=20260830-subject-descriptions1",
            "../assets/site.js?v=20260830-subject-descriptions1",
            "../assets/engagement.js?v=20260830-subject-descriptions1",
        ):
            if token not in page_source:
                fail(f"{prefix}: episode page is missing current subject-description asset {token!r}")

    require_tokens("assets/site.js", (
        'class="card-subject"',
        'class="featured-subject"',
        "episode.subjectDescription",
        "current.subjectDescription",
        "Subject in brief",
    ))
    require_tokens("assets/seasons.js", ("episode.subjectDescription", 'class="card-subject"'))
    require_tokens("assets/engagement.js", ("episode.subjectDescription", 'class="engagement-case-subject"'))
    require_tokens("assets/style.css", (".card-subject", ".featured-subject", ".episode-subject-summary"))
    require_tokens("assets/engagement.css", (".engagement-case-subject",))
    require_tokens("index.html", ("assets/site.js?v=20260830-subject-descriptions1",))
    require_tokens("archive.html", ("assets/site.js?v=20260830-subject-descriptions1",))
    require_tokens("collections.html", ("assets/engagement.js?v=20260830-subject-descriptions1",))
    require_tokens("season-i.html", ("assets/seasons.js?v=20260830-subject-descriptions1",))
    require_tokens("season-ii.html", ("assets/seasons.js?v=20260830-subject-descriptions1",))
    require_tokens("README.md", ("## 37. Short subject descriptions", "`subjectDescription`"))

    if errors:
        print("Subject descriptions QA: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Subject descriptions QA: PASS ({len(episodes)} concise descriptions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
