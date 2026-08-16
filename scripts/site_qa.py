#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "episodes.json"
ALLOWED_COVER_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
REQUIRED_GRAPHICS = (
    "ep{number:02d}-inventory-map.svg",
    "ep{number:02d}-technical-plate.svg",
    "ep{number:02d}-hotspot-breakdown.svg",
)

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def local_path(value: str) -> Path | None:
    parsed = urlparse(value)
    if parsed.scheme or value.startswith("//"):
        return None
    return ROOT / unquote(parsed.path).lstrip("/")


def check_exists(label: str, value: str) -> Path | None:
    path = local_path(value)
    if path is None:
        fail(f"{label}: external URLs are not allowed here: {value}")
        return None
    if not path.is_file():
        fail(f"{label}: missing file: {value}")
        return None
    return path


def check_cover(number: int, value: str) -> None:
    path = check_exists(f"Episode #{number} cover", value)
    if not path:
        return
    if path.suffix.lower() not in ALLOWED_COVER_SUFFIXES:
        fail(f"Episode #{number} cover: unsupported raster extension {path.suffix}")
        return
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
    except (UnidentifiedImageError, OSError) as exc:
        fail(f"Episode #{number} cover: unreadable/corrupt image ({exc})")
        return
    if width <= 0 or height <= 0:
        fail(f"Episode #{number} cover: invalid dimensions {width}x{height}")
        return
    ratio = width / height
    if abs(ratio - 0.8) > 0.012:
        fail(f"Episode #{number} cover: expected portrait 4:5, found {width}x{height} (ratio {ratio:.4f})")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str]] = []
        self.images_without_alt: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value for key, value in attrs}
        if tag.lower() == "a" and values.get("href"):
            self.refs.append(("href", values["href"] or ""))
        if tag.lower() in {"img", "script"} and values.get("src"):
            self.refs.append(("src", values["src"] or ""))
        if tag.lower() == "link" and values.get("href"):
            self.refs.append(("href", values["href"] or ""))
        if tag.lower() == "img":
            alt = values.get("alt")
            if alt is None or not alt.strip():
                self.images_without_alt.append(values.get("src") or "[inline image]")


def check_html_references(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(text)

    for image in parser.images_without_alt:
        fail(f"{path.relative_to(ROOT)}: image missing non-empty alt text: {image}")

    for attr, ref in parser.refs:
        if not ref or ref.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
            continue
        parsed = urlparse(ref)
        if parsed.scheme in {"http", "https"} or ref.startswith("//"):
            continue
        clean_path = unquote(parsed.path)
        if not clean_path:
            continue
        target = (path.parent / clean_path).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            fail(f"{path.relative_to(ROOT)}: {attr} escapes repository root: {ref}")
            continue
        if clean_path.endswith("/"):
            target = target / "index.html"
        if not target.is_file():
            fail(f"{path.relative_to(ROOT)}: broken local {attr}: {ref}")


def check_episode_page(number: int, url: str) -> None:
    path = check_exists(f"Episode #{number} page", url)
    if not path:
        return
    text = path.read_text(encoding="utf-8")
    body_match = re.search(r"<body\b[^>]*\bdata-episode=[\"'](\d+)[\"']", text, flags=re.I)
    if not body_match:
        fail(f"Episode #{number} page: missing body data-episode attribute")
    elif int(body_match.group(1)) != number:
        fail(f"Episode #{number} page: data-episode is #{body_match.group(1)}")
    if "../assets/site.js" not in text:
        fail(f"Episode #{number} page: missing ../assets/site.js")
    if "cover-frame" in text:
        fail(f"Episode #{number} page: legacy cover-frame markup still present")
    check_html_references(path)


def main() -> int:
    if not REGISTRY.is_file():
        fail("Missing episodes.json")
    else:
        try:
            data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"episodes.json is invalid JSON: {exc}")
            data = {}

        episodes = data.get("episodes")
        if not isinstance(episodes, list):
            fail("episodes.json: 'episodes' must be an array")
            episodes = []

        seen_numbers: set[int] = set()
        seen_slugs: set[str] = set()
        seen_urls: set[str] = set()

        required_fields = {
            "number", "slug", "title", "url", "cover", "categoryLabel", "categories",
            "lcaLabel", "lcaCharacteristics", "result", "hotspot", "featuredDescription",
            "keywords", "related",
        }

        numbers = {e.get("number") for e in episodes if isinstance(e, dict)}

        for episode in episodes:
            if not isinstance(episode, dict):
                fail("episodes.json: each episode must be an object")
                continue
            missing = sorted(required_fields - episode.keys())
            number = episode.get("number")
            prefix = f"Episode #{number}" if isinstance(number, int) else "Episode with invalid number"
            if missing:
                fail(f"{prefix}: missing required fields: {', '.join(missing)}")
            if not isinstance(number, int):
                fail(f"{prefix}: number must be an integer")
                continue
            if number in seen_numbers:
                fail(f"Episode #{number}: duplicate number")
            seen_numbers.add(number)

            slug = episode.get("slug", "")
            if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
                fail(f"Episode #{number}: invalid slug {slug!r}")
            elif slug in seen_slugs:
                fail(f"Episode #{number}: duplicate slug {slug}")
            seen_slugs.add(slug)

            url = episode.get("url", "")
            if not isinstance(url, str) or not url.startswith("episodes/") or not url.endswith(".html"):
                fail(f"Episode #{number}: invalid url {url!r}")
            elif url in seen_urls:
                fail(f"Episode #{number}: duplicate url {url}")
            seen_urls.add(url)

            cover = episode.get("cover", "")
            if isinstance(cover, str):
                check_cover(number, cover)
            else:
                fail(f"Episode #{number}: cover must be a string")

            if isinstance(url, str):
                check_episode_page(number, url)

            pdf = episode.get("pdf")
            if pdf is not None:
                if not isinstance(pdf, str) or not pdf.startswith("assets/pdf/episodes/") or not pdf.endswith(".pdf"):
                    fail(f"Episode #{number}: invalid pdf path {pdf!r}")
                else:
                    check_exists(f"Episode #{number} PDF", pdf)

            related = episode.get("related", [])
            if not isinstance(related, list):
                fail(f"Episode #{number}: related must be an array")
            else:
                if len(related) > 3:
                    warn(f"Episode #{number}: more than 3 related cases")
                for related_number in related:
                    if related_number == number:
                        fail(f"Episode #{number}: cannot relate to itself")
                    elif related_number not in numbers:
                        fail(f"Episode #{number}: related episode #{related_number} is not published")

            graphics_dir = ROOT / "assets/images/episode-graphics"
            for pattern in REQUIRED_GRAPHICS:
                graphic = graphics_dir / pattern.format(number=number)
                if not graphic.is_file():
                    fail(f"Episode #{number}: missing required graphic {graphic.relative_to(ROOT)}")

    core_html = (ROOT / "index.html", ROOT / "archive.html")
    for path in (*core_html, ROOT / "assets/style.css", ROOT / "assets/site.js"):
        if not path.is_file():
            fail(f"Missing core file: {path.relative_to(ROOT)}")

    for path in core_html:
        if path.is_file():
            check_html_references(path)

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\nQA failed with {len(errors)} error(s) and {len(warnings)} warning(s).", file=sys.stderr)
        return 1
    print(f"QA passed with {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
