#!/usr/bin/env python3
from __future__ import annotations

import json
import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"Missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def one(pattern: str, text: str, label: str) -> str | None:
    matches = re.findall(pattern, text, flags=re.I | re.S)
    if len(matches) != 1:
        fail(f"{label}: expected exactly one match, found {len(matches)}")
        return None
    value = matches[0]
    if isinstance(value, tuple):
        value = value[0]
    return value


def meta_content(text: str, kind: str, key: str, label: str) -> str | None:
    if kind == "name":
        pattern = rf'<meta\s+name=["\']{re.escape(key)}["\'][^>]*content=["\']([^"\']+)["\'][^>]*>|<meta\s+content=["\']([^"\']+)["\'][^>]*name=["\']{re.escape(key)}["\'][^>]*>'
    else:
        pattern = rf'<meta\s+property=["\']{re.escape(key)}["\'][^>]*content=["\']([^"\']+)["\'][^>]*>|<meta\s+content=["\']([^"\']+)["\'][^>]*property=["\']{re.escape(key)}["\'][^>]*>'
    matches = re.findall(pattern, text, flags=re.I | re.S)
    values = [a or b for a, b in matches]
    if len(values) != 1:
        fail(f"{label}: expected exactly one {key}, found {len(values)}")
        return None
    return values[0]


def check_public_page(path: Path, canonical: str, image: str, page_type: str, json_type: str) -> None:
    text = read(path)
    label = str(path.relative_to(ROOT))
    if not text:
        return

    canonical_value = one(r'<link\s+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\'][^>]*>', text, f"{label} canonical")
    if canonical_value != canonical:
        fail(f"{label}: canonical is {canonical_value!r}, expected {canonical!r}")

    description = meta_content(text, "name", "description", label)
    if not description or len(description.strip()) < 40:
        fail(f"{label}: meta description is missing or too short")

    robots = meta_content(text, "name", "robots", label)
    if robots != "index,follow,max-image-preview:large":
        fail(f"{label}: unexpected robots directive {robots!r}")

    expected_meta = {
        ("property", "og:site_name"): "LCA of the Impossible",
        ("property", "og:type"): page_type,
        ("property", "og:url"): canonical,
        ("property", "og:image"): image,
        ("name", "twitter:card"): "summary_large_image",
        ("name", "twitter:image"): image,
    }
    for (kind, key), expected in expected_meta.items():
        value = meta_content(text, kind, key, label)
        if value != expected:
            fail(f"{label}: {key} is {value!r}, expected {expected!r}")

    for kind, key in [
        ("property", "og:title"),
        ("property", "og:description"),
        ("property", "og:image:alt"),
        ("name", "twitter:title"),
        ("name", "twitter:description"),
        ("name", "twitter:image:alt"),
    ]:
        value = meta_content(text, kind, key, label)
        if not value:
            fail(f"{label}: missing {key}")

    json_matches = re.findall(r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, flags=re.I | re.S)
    if len(json_matches) != 1:
        fail(f"{label}: expected exactly one JSON-LD block, found {len(json_matches)}")
    else:
        try:
            data = json.loads(json_matches[0])
        except json.JSONDecodeError as exc:
            fail(f"{label}: invalid JSON-LD ({exc})")
        else:
            if data.get("@type") != json_type:
                fail(f"{label}: JSON-LD @type is {data.get('@type')!r}, expected {json_type!r}")
            if data.get("url") != canonical:
                fail(f"{label}: JSON-LD url is {data.get('url')!r}, expected {canonical!r}")

    if not re.search(r'<link\s+rel=["\']icon["\'][^>]*favicon\.svg', text, flags=re.I):
        fail(f"{label}: favicon link missing")
    if not re.search(r'<link\s+rel=["\']manifest["\'][^>]*site\.webmanifest', text, flags=re.I):
        fail(f"{label}: manifest link missing")


def main() -> int:
    registry = json.loads(read(ROOT / "episodes.json") or "{}")
    episodes = sorted(registry.get("episodes", []), key=lambda e: e["number"], reverse=True)
    if not episodes:
        fail("episodes.json contains no episodes")
        latest_image = BASE_URL
    else:
        latest_image = BASE_URL + episodes[0]["cover"]

    check_public_page(ROOT / "index.html", BASE_URL, latest_image, "website", "WebSite")
    check_public_page(ROOT / "archive.html", BASE_URL + "archive.html", latest_image, "website", "CollectionPage")
    check_public_page(ROOT / "method.html", BASE_URL + "method.html", latest_image, "website", "WebPage")
    check_public_page(ROOT / "compare.html", BASE_URL + "compare.html", latest_image, "website", "WebPage")
    check_public_page(ROOT / "explore.html", BASE_URL + "explore.html", latest_image, "website", "CollectionPage")
    check_public_page(ROOT / "collections.html", BASE_URL + "collections.html", latest_image, "website", "CollectionPage")
    check_public_page(ROOT / "sources.html", BASE_URL + "sources.html", latest_image, "website", "WebPage")
    check_public_page(ROOT / "about.html", BASE_URL + "about.html", latest_image, "website", "AboutPage")
    check_public_page(ROOT / "glossary.html", BASE_URL + "glossary.html", latest_image, "website", "DefinedTermSet")

    for season_id, filename in [("season-i", "season-i.html"), ("season-ii", "season-ii.html")]:
        season_episodes = [episode for episode in episodes if episode.get("seasonId") == season_id]
        if not season_episodes:
            fail(f"{filename}: no registered episodes for {season_id}")
            continue
        check_public_page(
            ROOT / filename,
            BASE_URL + filename,
            BASE_URL + season_episodes[0]["cover"],
            "website",
            "CollectionPage",
        )

    for episode in episodes:
        canonical = BASE_URL + episode["url"]
        image = BASE_URL + episode["cover"]
        check_public_page(ROOT / episode["url"], canonical, image, "article", "Article")
        if episode.get("seasonLabel"):
            text = read(ROOT / episode["url"])
            label = f"Episode #{episode['number']} season metadata"
            season_label = episode["seasonLabel"]
            for kind, key in [
                ("property", "og:title"),
                ("property", "og:description"),
                ("name", "twitter:title"),
                ("name", "twitter:description"),
            ]:
                value = html.unescape(meta_content(text, kind, key, label) or "")
                if season_label not in value:
                    fail(f"{label}: {key} does not identify {season_label}")
            json_matches = re.findall(r"<script\s+type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", text, flags=re.I | re.S)
            if len(json_matches) == 1:
                structured = json.loads(json_matches[0])
                if structured.get("isPartOf", {}).get("name") != season_label:
                    fail(f"{label}: JSON-LD isPartOf does not match registered season")
                if structured.get("datePublished") != episode.get("datePublished"):
                    fail(f"{label}: JSON-LD publication date does not match registry")

    template = read(ROOT / "episodes/template.html")
    if template:
        robots = meta_content(template, "name", "robots", "episodes/template.html")
        if robots != "noindex,nofollow":
            fail(f"episodes/template.html: expected noindex,nofollow, found {robots!r}")
        if re.search(r'<link\s+rel=["\']canonical["\']', template, flags=re.I):
            fail("episodes/template.html: template must not publish a canonical URL")

    sitemap_text = read(ROOT / "sitemap.xml")
    expected_urls = {
        BASE_URL,
        BASE_URL + "archive.html",
        BASE_URL + "method.html",
        BASE_URL + "compare.html",
        BASE_URL + "explore.html",
        BASE_URL + "collections.html",
        BASE_URL + "sources.html",
        BASE_URL + "about.html",
        BASE_URL + "glossary.html",
        BASE_URL + "season-i.html",
        BASE_URL + "season-ii.html",
        *[BASE_URL + e["url"] for e in episodes],
    }
    if sitemap_text:
        try:
            root = ET.fromstring(sitemap_text)
        except ET.ParseError as exc:
            fail(f"sitemap.xml: invalid XML ({exc})")
        else:
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = {loc.text for loc in root.findall("sm:url/sm:loc", ns) if loc.text}
            if urls != expected_urls:
                missing = sorted(expected_urls - urls)
                extra = sorted(urls - expected_urls)
                if missing:
                    fail(f"sitemap.xml: missing URLs: {', '.join(missing)}")
                if extra:
                    fail(f"sitemap.xml: unexpected URLs: {', '.join(extra)}")
            if BASE_URL + "episodes/template.html" in urls:
                fail("sitemap.xml: template page must not be indexed")

    robots_text = read(ROOT / "robots.txt")
    if robots_text and f"Sitemap: {BASE_URL}sitemap.xml" not in robots_text:
        fail("robots.txt: canonical sitemap declaration missing")
    if robots_text and "Disallow: /" in robots_text:
        fail("robots.txt: site must not be globally disallowed")

    if not (ROOT / "assets/favicon.svg").is_file():
        fail("Missing assets/favicon.svg")
    manifest_text = read(ROOT / "site.webmanifest")
    if manifest_text:
        try:
            manifest = json.loads(manifest_text)
        except json.JSONDecodeError as exc:
            fail(f"site.webmanifest: invalid JSON ({exc})")
        else:
            if manifest.get("start_url") != "/LCA-of-the-Impossible/":
                fail("site.webmanifest: start_url is incorrect for GitHub Pages project path")

    for episode in episodes:
        image_url = BASE_URL + episode["cover"]
        parsed = urlparse(image_url)
        if parsed.netloc != "lcaofimpossible.github.io":
            fail(f"Episode #{episode['number']}: social image is not on the canonical GitHub Pages host")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nSEO QA failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"SEO QA passed for {len(episodes) + 11} public pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
