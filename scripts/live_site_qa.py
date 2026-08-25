#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
GRAPHIC_PATTERNS = (
    "ep{number:02d}-inventory-map.svg",
    "ep{number:02d}-technical-plate.svg",
    "ep{number:02d}-hotspot-breakdown.svg",
)
CORE_PATHS = {
    "index.html",
    "archive.html",
    "collections.html",
    "compare.html",
    "explore.html",
    "method.html",
    "sources.html",
    "about.html",
    "glossary.html",
    "episodes.json",
    "collections.json",
    "sitemap.xml",
    "robots.txt",
    "site.webmanifest",
    "assets/favicon.svg",
    "assets/style.css",
    "assets/features.css",
    "assets/engagement.css",
    "assets/editorial.css",
    "assets/method.css",
    "assets/phase6.css",
    "assets/telemetry.css",
    "assets/site.js",
    "assets/engagement.js",
    "assets/phase6.js",
    "assets/passport-cleanup.js",
    "assets/telemetry.js",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_url(base_url: str, path: str, cache_key: str) -> str:
    url = urljoin(base_url, quote(path, safe="/"))
    return f"{url}?live-qa={quote(cache_key, safe='')}" if cache_key else url


def fetch(
    base_url: str,
    path: str,
    cache_key: str,
    timeout: float,
    retries: int = 3,
) -> bytes:
    url = build_url(base_url, path, cache_key)
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = Request(
                url,
                headers={
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                    "User-Agent": "LCA-of-the-Impossible-Live-QA",
                },
            )
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                return response.read()
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as exc:
            last_error = exc
            if isinstance(exc, HTTPError) and exc.code < 500:
                break
            if attempt + 1 < retries:
                time.sleep(min(2**attempt, 4))
    raise RuntimeError(f"{path}: {last_error}")


def wait_for_registry(
    base_url: str,
    cache_key: str,
    timeout: float,
    attempts: int,
    delay: float,
) -> None:
    expected = (ROOT / "episodes.json").read_bytes()
    last_detail = "not requested"
    for attempt in range(1, attempts + 1):
        try:
            actual = fetch(base_url, "episodes.json", cache_key, timeout, retries=2)
        except RuntimeError as exc:
            last_detail = str(exc)
        else:
            if actual == expected:
                return
            last_detail = (
                f"registry hash {sha256(actual)}; expected {sha256(expected)}"
            )
        if attempt < attempts:
            time.sleep(delay)
    raise RuntimeError(
        f"Live deployment did not reach the checked-out registry after {attempts} attempts: "
        f"{last_detail}"
    )


def expected_paths(episodes: list[dict[str, object]]) -> set[str]:
    paths = set(CORE_PATHS)
    for episode in episodes:
        number = int(episode["number"])
        paths.add(str(episode["url"]))
        paths.add(str(episode["cover"]))
        for pattern in GRAPHIC_PATTERNS:
            paths.add(f"assets/images/episode-graphics/{pattern.format(number=number)}")
    return paths


def fetch_all(
    base_url: str,
    paths: set[str],
    cache_key: str,
    timeout: float,
    workers: int,
) -> tuple[dict[str, bytes], list[str]]:
    downloaded: dict[str, bytes] = {}
    errors: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(fetch, base_url, path, cache_key, timeout): path
            for path in sorted(paths)
        }
        for future in concurrent.futures.as_completed(futures):
            path = futures[future]
            try:
                downloaded[path] = future.result()
            except Exception as exc:
                errors.append(str(exc))
    return downloaded, errors


def validate(
    episodes: list[dict[str, object]],
    downloaded: dict[str, bytes],
    paths: set[str],
) -> list[str]:
    errors: list[str] = []

    for path in sorted(paths):
        local_path = ROOT / path
        if not local_path.is_file():
            errors.append(f"Local publication path is missing: {path}")
            continue
        actual = downloaded.get(path)
        if actual is None:
            continue
        expected = local_path.read_bytes()
        if actual != expected:
            errors.append(
                f"Live bytes differ for {path}: {sha256(actual)}; expected {sha256(expected)}"
            )

    try:
        registry = json.loads(downloaded["episodes.json"])
    except (KeyError, json.JSONDecodeError) as exc:
        errors.append(f"Live episodes.json is unavailable or invalid: {exc}")
        return errors

    live_episodes = registry.get("episodes", [])
    if any(isinstance(episode, dict) and "pdf" in episode for episode in live_episodes):
        errors.append("Live episodes.json contains a prohibited pdf field")

    try:
        sitemap = downloaded["sitemap.xml"].decode("utf-8")
    except (KeyError, UnicodeDecodeError) as exc:
        errors.append(f"Live sitemap.xml is unavailable or invalid: {exc}")
        sitemap = ""

    for episode in episodes:
        number = int(episode["number"])
        url = str(episode["url"])
        title = str(episode["title"])
        result = str(episode["result"])
        try:
            html = downloaded[url].decode("utf-8")
        except (KeyError, UnicodeDecodeError) as exc:
            errors.append(f"Episode #{number} live HTML is unavailable or invalid: {exc}")
            continue

        required = (
            f'data-episode="{number}"',
            title,
            result,
            "application/ld+json",
            "og:image",
            "twitter:image",
            "../assets/site.js",
            "../assets/phase6.js",
            "../assets/passport-cleanup.js",
        )
        for token in required:
            if token not in html:
                errors.append(f"Episode #{number} live HTML is missing {token!r}")

        lower = html.lower()
        if "raw text" in lower:
            errors.append(f"Episode #{number} exposes Raw text")
        if "download episode pdf" in lower or "assets/pdf/episodes/" in lower:
            errors.append(f"Episode #{number} exposes a source-PDF control or link")
        if sitemap.count(f"/{url}") != 1:
            errors.append(f"Episode #{number} does not occur exactly once in the live sitemap")

    phase6 = downloaded.get("assets/phase6.js", b"").decode("utf-8", errors="replace")
    cleanup = downloaded.get("assets/passport-cleanup.js", b"").decode(
        "utf-8", errors="replace"
    )
    for token in ("View epic passport →", "Print / Save as PDF"):
        if token not in phase6:
            errors.append(f"Live Epic Passport runtime is missing {token!r}")
    for token in (
        "Raw text",
        "downloadRawPassport",
        "passport-raw",
        "systemBoundary:",
        "factorList:",
        "allocationRule:",
    ):
        if token in phase6:
            errors.append(f"Live Epic Passport runtime reintroduces {token!r}")
    if "allowedPassportActions" not in cleanup:
        errors.append("Live Passport-only cleanup guard is missing")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that GitHub Pages serves the checked-out static publication exactly."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--cache-key", default="")
    parser.add_argument("--attempts", type=int, default=24)
    parser.add_argument("--delay", type=float, default=5.0)
    parser.add_argument("--verify-attempts", type=int, default=6)
    parser.add_argument("--verify-delay", type=float, default=10.0)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--workers", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/") + "/"
    registry = json.loads((ROOT / "episodes.json").read_text(encoding="utf-8"))
    episodes = registry.get("episodes", [])
    if not isinstance(episodes, list) or not episodes:
        print("ERROR: Local episodes.json contains no episodes", file=sys.stderr)
        return 1

    print("## Live Site QA")
    print()
    print(f"- Target: `{base_url}`")
    print(f"- Registered episodes: **{len(episodes)}**")

    try:
        wait_for_registry(
            base_url,
            args.cache_key,
            args.timeout,
            args.attempts,
            args.delay,
        )
    except RuntimeError as exc:
        print(f"- Result: **FAIL** — {exc}", file=sys.stderr)
        return 1

    paths = expected_paths(episodes)
    errors: list[str] = []
    for attempt in range(1, max(1, args.verify_attempts) + 1):
        downloaded, fetch_errors = fetch_all(
            base_url,
            paths,
            args.cache_key,
            args.timeout,
            max(1, args.workers),
        )
        errors = fetch_errors + validate(episodes, downloaded, paths)
        if not errors:
            break
        if attempt < max(1, args.verify_attempts):
            time.sleep(args.verify_delay)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"- Result: **FAIL** — {len(errors)} error(s)", file=sys.stderr)
        return 1

    print(f"- Exact deployed paths verified: **{len(paths)}**")
    print(f"- Exact cover assets verified: **{len(episodes)}**")
    print("- Registry, collections, sitemap, SEO pages and analytical graphics: **PASS**")
    print("- Epic Passport-only runtime and source-PDF link policy: **PASS**")
    print("- Result: **PASS**")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
