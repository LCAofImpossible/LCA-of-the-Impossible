#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_VERSION = "20260820-telemetry1"
errors: list[str] = []
ROOT_PAGES = [
    "index.html", "archive.html", "compare.html", "explore.html", "collections.html",
    "method.html", "sources.html", "about.html", "glossary.html", "season-i.html", "season-ii.html", "statistics.html",
    "updates.html",
]


def fail(message: str) -> None:
    errors.append(message)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"Missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def check_page(path: Path, prefix: str) -> None:
    text = read(path)
    if f'{prefix}assets/telemetry.css?v={ASSET_VERSION}' not in text:
        fail(f"{path.relative_to(ROOT)}: telemetry CSS missing or stale")
    if f'{prefix}assets/telemetry.js?v={ASSET_VERSION}' not in text:
        fail(f"{path.relative_to(ROOT)}: telemetry JS missing or stale")


def check_client() -> None:
    text = read(ROOT / "assets/telemetry.js")
    required = [
        "https://counterapi.com/api",
        "lcaofimpossible.github.io",
        "site-total",
        "episode-${episodeNumber}",
        "unique=true",
        "credentials: 'omit'",
        "referrerPolicy: 'no-referrer'",
        "SITE TELEMETRY",
        "CASE TELEMETRY",
        "MutationObserver",
    ]
    for token in required:
        if token not in text:
            fail(f"assets/telemetry.js: required token missing: {token}")
    forbidden = ["document.cookie", "localStorage", "sessionStorage"]
    for token in forbidden:
        if token in text:
            fail(f"assets/telemetry.js: privacy guardrail violated: {token}")


def check_styles() -> None:
    text = read(ROOT / "assets/telemetry.css")
    for token in [".site-telemetry", ".case-telemetry", ".telemetry-code", "@media(max-width:760px)"]:
        if token not in text:
            fail(f"assets/telemetry.css: required style missing: {token}")


def check_readme() -> None:
    text = read(ROOT / "README.md")
    for token in [
        "## 31. Visitor telemetry — mandatory",
        "SITE TELEMETRY",
        "CASE TELEMETRY",
        "unique=true",
        "Counts begin from telemetry activation",
    ]:
        if token not in text:
            fail(f"README.md: telemetry rule missing: {token}")


def main() -> int:
    for name in ROOT_PAGES:
        check_page(ROOT / name, "")
    for path in sorted((ROOT / "episodes").glob("*.html")):
        if path.name == "template.html":
            continue
        check_page(path, "../")

    template = read(ROOT / "episodes/template.html")
    if "assets/telemetry.js" in template or "assets/telemetry.css" in template:
        fail("episodes/template.html: live telemetry must be added only after episode instantiation")

    check_client()
    check_styles()
    check_readme()

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nVisitor telemetry QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Visitor telemetry QA passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
