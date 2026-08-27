#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "episodes.json"
ALLOWED_COVER_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
REQUIRED_GRAPHICS = (
    "ep{number:02d}-inventory-map.svg",
    "ep{number:02d}-technical-plate.svg",
    "ep{number:02d}-hotspot-breakdown.svg",
)
CANONICAL_SEASONS = {
    1: {
        "seasonId": "season-i",
        "seasonNumber": 1,
        "seasonLabel": "Season I — Machines & Worlds",
        "seasonTitle": "Machines & Worlds",
        "seasonDescriptor": "Science fiction, reconstructed through life-cycle logic.",
        "editorialDescriptor": "Impossible technologies, reconstructed as traceable systems.",
        "seasonEpisodeRange": [1, 29],
    },
    2: {
        "seasonId": "season-ii",
        "seasonNumber": 2,
        "seasonLabel": "Season II — Myths & Legends",
        "seasonTitle": "Myths & Legends",
        "seasonDescriptor": "Myths and legends, reconstructed through life-cycle logic.",
        "editorialDescriptor": "Impossible stories, reconstructed as traceable systems.",
        "seasonEpisodeRange": [30, 71],
    },
}

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def check_meaningful_string(number: int, key: str, value: object, minimum: int = 2) -> None:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        fail(f"Episode #{number}: {key} must be a meaningful string")


def check_string_list(number: int, key: str, value: object) -> None:
    if not isinstance(value, list) or not value:
        fail(f"Episode #{number}: {key} must be a non-empty array")
        return
    if any(not isinstance(item, str) or not item.strip() for item in value):
        fail(f"Episode #{number}: {key} must contain only non-empty strings")
    if len(value) != len(set(value)):
        fail(f"Episode #{number}: {key} contains duplicate values")


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


def check_cover(number: int, value: str, aspect_policy: str | None = None) -> None:
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
        if aspect_policy == "approved-native":
            if not (0.5 < ratio < 1.0):
                fail(f"Episode #{number} cover: approved-native asset must remain portrait, found {width}x{height} (ratio {ratio:.4f})")
            else:
                warn(f"Episode #{number} cover: using explicitly approved native aspect ratio {width}x{height}; exact-file rule overrides 4:5 target")
        else:
            fail(f"Episode #{number} cover: expected portrait 4:5, found {width}x{height} (ratio {ratio:.4f})")


def check_graphic(number: int, path: Path) -> None:
    if not path.is_file():
        fail(f"Episode #{number}: missing required graphic {path.relative_to(ROOT)}")
        return
    try:
        root = ElementTree.parse(path).getroot()
    except (ElementTree.ParseError, OSError) as exc:
        fail(f"Episode #{number}: unreadable SVG {path.relative_to(ROOT)} ({exc})")
        return
    if root.tag.rsplit("}", 1)[-1].lower() != "svg":
        fail(f"Episode #{number}: analytical graphic is not an SVG: {path.relative_to(ROOT)}")


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
    cover_image = re.search(
        r"<img\b[^>]*\bsrc=[\"'][^\"']*assets/images/episodes/[^\"']+[\"']",
        text,
        flags=re.I,
    )
    if cover_image:
        fail(f"Episode #{number} page: catalogue cover must not be rendered in the page body")
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
        if data.get("schemaVersion") != 2:
            fail("episodes.json: schemaVersion must be exactly 2")
        if not isinstance(episodes, list):
            fail("episodes.json: 'episodes' must be an array")
            episodes = []

        seen_numbers: set[int] = set()
        seen_slugs: set[str] = set()
        seen_urls: set[str] = set()
        seen_covers: set[str] = set()
        registered_pages: set[Path] = set()

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
            elif url != f"episodes/{slug}.html":
                fail(f"Episode #{number}: url must match the registered slug")
            else:
                registered_pages.add((ROOT / url).resolve())
            seen_urls.add(url)

            for key in (
                "title", "categoryLabel", "lcaLabel", "result", "hotspot",
                "featuredDescription",
            ):
                check_meaningful_string(number, key, episode.get(key), minimum=3)
            for key in ("categories", "lcaCharacteristics", "keywords"):
                check_string_list(number, key, episode.get(key))

            cover = episode.get("cover", "")
            if isinstance(cover, str):
                if not cover.startswith("assets/images/episodes/"):
                    fail(f"Episode #{number}: cover must be stored under assets/images/episodes/")
                if not Path(cover).name.startswith(f"ep{number:02d}-"):
                    fail(f"Episode #{number}: cover filename must start with ep{number:02d}-")
                if cover in seen_covers:
                    fail(f"Episode #{number}: cover path is already used by another episode")
                seen_covers.add(cover)
                check_cover(number, cover, episode.get("coverAspectPolicy"))
                cover_sha = episode.get("coverSha256")
                if cover_sha:
                    cover_path = local_path(cover)
                    if not isinstance(cover_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", cover_sha):
                        fail(f"Episode #{number}: coverSha256 must be a lowercase SHA-256 digest")
                    elif cover_path and cover_path.is_file():
                        actual_sha = hashlib.sha256(cover_path.read_bytes()).hexdigest()
                        if actual_sha != cover_sha:
                            fail(f"Episode #{number}: approved cover checksum mismatch")
            else:
                fail(f"Episode #{number}: cover must be a string")

            if isinstance(url, str):
                check_episode_page(number, url)

            season_keys = {
                "seasonId", "seasonNumber", "seasonLabel", "seasonTitle",
                "seasonDescriptor", "editorialDescriptor", "seasonEpisodeRange",
                "taxonomy", "collectionSlugs",
            }
            if season_keys.intersection(episode):
                missing_season = sorted(season_keys - episode.keys())
                if missing_season:
                    fail(f"Episode #{number}: incomplete season metadata: {', '.join(missing_season)}")
                season_range = episode.get("seasonEpisodeRange")
                if not isinstance(season_range, list) or len(season_range) != 2 or not all(isinstance(value, int) for value in season_range):
                    fail(f"Episode #{number}: seasonEpisodeRange must contain two integers")
                elif not season_range[0] <= number <= season_range[1]:
                    fail(f"Episode #{number}: number is outside registered season range {season_range}")
                if not isinstance(episode.get("seasonId"), str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", episode.get("seasonId", "")):
                    fail(f"Episode #{number}: invalid seasonId")
                for key in ("seasonLabel", "seasonTitle", "seasonDescriptor", "editorialDescriptor"):
                    if not isinstance(episode.get(key), str) or len(episode.get(key, "").strip()) < 5:
                        fail(f"Episode #{number}: missing meaningful {key}")
                for key in ("taxonomy", "collectionSlugs"):
                    check_string_list(number, key, episode.get(key))
                season_number = episode.get("seasonNumber")
                canonical = CANONICAL_SEASONS.get(season_number)
                if canonical is None:
                    fail(f"Episode #{number}: unsupported seasonNumber {season_number!r}")
                else:
                    for key, expected in canonical.items():
                        if episode.get(key) != expected:
                            fail(
                                f"Episode #{number}: {key} conflicts with canonical "
                                f"Season {season_number} identity"
                            )
                    if episode.get("seasonId") not in episode.get("taxonomy", []):
                        fail(f"Episode #{number}: taxonomy must include the registered seasonId")
                if isinstance(url, str):
                    season_page = ROOT / url
                    if season_page.is_file():
                        page_text = season_page.read_text(encoding="utf-8")
                        page_upper = page_text.upper()
                        season_label = episode.get("seasonLabel", "").upper()
                        season_title = episode.get("seasonTitle", "").upper()
                        if season_label not in page_upper and season_title not in page_upper:
                            fail(f"Episode #{number}: page does not display registered season identity")
                        for other_number, marker in ((1, "SEASON I —"), (2, "SEASON II —")):
                            if season_number != other_number and marker in page_upper:
                                fail(f"Episode #{number}: conflicting {marker.rstrip(' —')} identity found in page")

            if "pdf" in episode:
                fail(f"Episode #{number}: public registry must not expose a pdf field")

            related = episode.get("related", [])
            if not isinstance(related, list):
                fail(f"Episode #{number}: related must be an array")
            else:
                if len(related) > 3:
                    warn(f"Episode #{number}: more than 3 related cases")
                if len(related) != len(set(related)):
                    fail(f"Episode #{number}: related contains duplicate episode numbers")
                for related_number in related:
                    if not isinstance(related_number, int):
                        fail(f"Episode #{number}: related values must be episode numbers")
                        continue
                    if related_number == number:
                        fail(f"Episode #{number}: cannot relate to itself")
                    elif related_number not in numbers:
                        fail(f"Episode #{number}: related episode #{related_number} is not published")

            graphics_dir = ROOT / "assets/images/episode-graphics"
            for pattern in REQUIRED_GRAPHICS:
                graphic = graphics_dir / pattern.format(number=number)
                check_graphic(number, graphic)

        actual_pages = {
            path.resolve()
            for path in (ROOT / "episodes").glob("*.html")
            if path.name != "template.html"
        }
        for path in sorted(actual_pages - registered_pages):
            fail(f"Unregistered episode page: {path.relative_to(ROOT)}")
        for path in sorted(registered_pages - actual_pages):
            fail(f"Registered episode page is missing: {path.relative_to(ROOT)}")

    core_html = (ROOT / "index.html", ROOT / "archive.html")
    for path in (*core_html, ROOT / "assets/style.css", ROOT / "assets/site.js"):
        if not path.is_file():
            fail(f"Missing core file: {path.relative_to(ROOT)}")

    for path in sorted(ROOT.glob("*.html")):
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
