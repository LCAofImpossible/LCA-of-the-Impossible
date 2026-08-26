#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
SEO_START = "<!-- SEO:START -->"
SEO_END = "<!-- SEO:END -->"
README_START = "<!-- SEO-RULES:START -->"
README_END = "<!-- SEO-RULES:END -->"


def write_if_changed(path: Path, content: str, check: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return
    changed.append(path)
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def clean_head_metadata(text: str) -> str:
    text = re.sub(
        rf"\s*{re.escape(SEO_START)}.*?{re.escape(SEO_END)}\s*",
        "\n",
        text,
        flags=re.S,
    )
    standalone_patterns = [
        r'<meta\s+name=["\']description["\'][^>]*>\s*',
        r'<meta\s+name=["\']robots["\'][^>]*>\s*',
        r'<meta\s+name=["\']theme-color["\'][^>]*>\s*',
        r'<link\s+rel=["\']canonical["\'][^>]*>\s*',
        r'<link\s+rel=["\']icon["\'][^>]*>\s*',
        r'<link\s+rel=["\']manifest["\'][^>]*>\s*',
        r'<meta\s+property=["\']og:[^"\']+["\'][^>]*>\s*',
        r'<meta\s+property=["\']article:[^"\']+["\'][^>]*>\s*',
        r'<meta\s+name=["\']twitter:[^"\']+["\'][^>]*>\s*',
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>.*?</script>\s*',
    ]
    for pattern in standalone_patterns:
        text = re.sub(pattern, "", text, flags=re.I | re.S)
    return text


def insert_after_viewport(text: str, block: str) -> str:
    match = re.search(r'<meta\s+name=["\']viewport["\'][^>]*>', text, flags=re.I)
    if not match:
        raise RuntimeError("Cannot insert SEO metadata: viewport meta tag not found")
    return text[: match.end()] + "\n" + block + text[match.end() :]


def attr(value: str) -> str:
    return html.escape(value, quote=True)


def seo_block(*, title: str, description: str, canonical: str, image: str, image_alt: str,
              page_type: str, prefix: str, json_ld: dict, article_section: str | None = None) -> str:
    lines = [
        SEO_START,
        f'  <meta name="description" content="{attr(description)}">',
        '  <meta name="robots" content="index,follow,max-image-preview:large">',
        '  <meta name="theme-color" content="#071019">',
        f'  <link rel="canonical" href="{attr(canonical)}">',
        f'  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">',
        f'  <link rel="manifest" href="{prefix}site.webmanifest">',
        '  <meta property="og:site_name" content="LCA of the Impossible">',
        f'  <meta property="og:type" content="{attr(page_type)}">',
        f'  <meta property="og:title" content="{attr(title)}">',
        f'  <meta property="og:description" content="{attr(description)}">',
        f'  <meta property="og:url" content="{attr(canonical)}">',
        f'  <meta property="og:image" content="{attr(image)}">',
        f'  <meta property="og:image:alt" content="{attr(image_alt)}">',
        '  <meta property="og:locale" content="en_US">',
    ]
    if article_section:
        lines.append(f'  <meta property="article:section" content="{attr(article_section)}">')
    lines.extend([
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{attr(title)}">',
        f'  <meta name="twitter:description" content="{attr(description)}">',
        f'  <meta name="twitter:image" content="{attr(image)}">',
        f'  <meta name="twitter:image:alt" content="{attr(image_alt)}">',
        '  <script type="application/ld+json">',
        json.dumps(json_ld, ensure_ascii=False, indent=2),
        '  </script>',
        SEO_END,
    ])
    return "\n".join(lines)


def apply_page(path: Path, block: str, check: bool, changed: list[Path]) -> None:
    text = clean_head_metadata(path.read_text(encoding="utf-8"))
    text = insert_after_viewport(text, block)
    write_if_changed(path, text, check, changed)


def apply_template(check: bool, changed: list[Path]) -> None:
    path = ROOT / "episodes/template.html"
    text = clean_head_metadata(path.read_text(encoding="utf-8"))
    block = "\n".join([
        SEO_START,
        '  <meta name="robots" content="noindex,nofollow">',
        '  <meta name="theme-color" content="#071019">',
        '  <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">',
        '  <link rel="manifest" href="../site.webmanifest">',
        '  <!-- Replace this noindex template metadata with registry-derived canonical/Open Graph/Twitter/JSON-LD metadata before publication. -->',
        SEO_END,
    ])
    text = insert_after_viewport(text, block)
    write_if_changed(path, text, check, changed)


def build_sitemap(episodes: list[dict]) -> str:
    urls = [BASE_URL, BASE_URL + "archive.html", BASE_URL + "method.html"] + [BASE_URL + e["url"] for e in episodes]
    body = "\n".join(f"  <url><loc>{html.escape(url)}</loc></url>" for url in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


def build_favicon() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="LCA of the Impossible">
  <rect width="64" height="64" rx="8" fill="#071019"/>
  <rect x="5" y="5" width="54" height="54" rx="5" fill="none" stroke="#d0a563" stroke-width="2"/>
  <path d="M13 45V18h5v22h13v5H13Zm23 0V18h15v5H41v6h9v5h-9v11h-5Z" fill="#eef7fb"/>
  <path d="M10 11h18M36 53h18" stroke="#6de7ff" stroke-width="2"/>
</svg>\n'''


def build_manifest() -> str:
    return json.dumps({
        "name": "LCA of the Impossible",
        "short_name": "LCA Impossible",
        "description": "Where others see fantasy, we see a functional unit.",
        "start_url": "/LCA-of-the-Impossible/",
        "scope": "/LCA-of-the-Impossible/",
        "display": "standalone",
        "background_color": "#071019",
        "theme_color": "#071019",
        "icons": [
            {
                "src": "assets/favicon.svg",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any"
            }
        ]
    }, ensure_ascii=False, indent=2) + "\n"


def update_readme(check: bool, changed: list[Path]) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    section = f'''{README_START}

## 24. SEO, social sharing and discovery — mandatory

Every public page must be self-describing in its static HTML. Do not rely on client-side JavaScript for search-engine or social-preview metadata.

Required on `index.html`, `archive.html`, `method.html` and every published episode page:

- one absolute canonical URL under `https://lcaofimpossible.github.io/LCA-of-the-Impossible/`;
- a concise meta description;
- `robots` set to `index,follow,max-image-preview:large`;
- Open Graph metadata: `og:site_name`, `og:type`, `og:title`, `og:description`, `og:url`, `og:image`, `og:image:alt`, `og:locale`;
- Twitter/X card metadata using `summary_large_image`, with title, description, image and image alt text;
- one parseable JSON-LD block. Use `WebSite` for the homepage, `CollectionPage` for the Archive, `WebPage` for the Method page and `Article` for episode pages;
- shared favicon and web manifest links.

For episode pages, the Open Graph/Twitter image must point to the **exact approved catalogue cover already registered in `episodes.json`**. This use is metadata for link previews and does not change the rule that the cover is not visually displayed in the episode-page hero.

`robots.txt` must allow crawling and reference the canonical `sitemap.xml`. `sitemap.xml` must contain the homepage, Archive, Method page and every published episode URL, and must exclude `episodes/template.html`.

`episodes/template.html` must remain `noindex,nofollow` until instantiated as a real episode.

SEO metadata, sitemap, robots, favicon and manifest are maintained deterministically by `scripts/apply_seo.py`. `scripts/seo_qa.py` verifies that the committed site matches `episodes.json`. When a new episode is added, publication is incomplete until these checks pass and the live deployment contains the updated canonical/social metadata.

### SEO/social QA

- [ ] Canonical URL is absolute and correct.
- [ ] Meta description is present and episode-specific where applicable.
- [ ] Open Graph and Twitter card fields are complete.
- [ ] Episode social image is the exact registered cover path.
- [ ] JSON-LD parses and uses the correct page type.
- [ ] Sitemap contains every published episode exactly once.
- [ ] `robots.txt` references the live sitemap.
- [ ] Favicon and manifest are linked from public pages.
- [ ] Template is excluded from indexing.
- [ ] LinkedIn/social preview metadata exists in static HTML before publication.

{README_END}'''
    pattern = rf"{re.escape(README_START)}.*?{re.escape(README_END)}"
    if re.search(pattern, text, flags=re.S):
        updated = re.sub(pattern, section, text, flags=re.S)
    else:
        updated = text.rstrip() + "\n\n---\n\n" + section + "\n"
    write_if_changed(path, updated, check, changed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Report whether generated SEO files differ without writing them")
    args = parser.parse_args()

    registry = json.loads((ROOT / "episodes.json").read_text(encoding="utf-8"))
    episodes = sorted(registry["episodes"], key=lambda e: e["number"], reverse=True)
    latest = episodes[0]
    latest_image = BASE_URL + latest["cover"]
    changed: list[Path] = []

    home_description = "LCA of the Impossible applies life cycle thinking to myths, legendary structures and fictional systems, translating impossible subjects into transparent inventories, hotspots and carbon footprints."
    home_ld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "LCA of the Impossible",
        "url": BASE_URL,
        "description": home_description,
        "inLanguage": "en"
    }
    home_block = seo_block(
        title="LCA of the Impossible — Where others see fantasy, we see a functional unit",
        description=home_description,
        canonical=BASE_URL,
        image=latest_image,
        image_alt=f"{latest['title']} — latest LCA of the Impossible episode cover",
        page_type="website",
        prefix="",
        json_ld=home_ld,
    )
    apply_page(ROOT / "index.html", home_block, args.check, changed)

    archive_description = "Complete searchable archive of LCA of the Impossible episodes, organized by narrative subject and the life-cycle mechanism that controls each footprint."
    archive_url = BASE_URL + "archive.html"
    archive_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Episode Archive — LCA of the Impossible",
        "url": archive_url,
        "description": archive_description,
        "inLanguage": "en",
        "isPartOf": {"@type": "WebSite", "name": "LCA of the Impossible", "url": BASE_URL},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(episodes),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index,
                    "name": episode["title"],
                    "url": BASE_URL + episode["url"]
                }
                for index, episode in enumerate(episodes, start=1)
            ]
        }
    }
    archive_block = seo_block(
        title="Episode Archive — LCA of the Impossible",
        description=archive_description,
        canonical=archive_url,
        image=latest_image,
        image_alt=f"{latest['title']} — latest LCA of the Impossible episode cover",
        page_type="website",
        prefix="",
        json_ld=archive_ld,
    )
    apply_page(ROOT / "archive.html", archive_block, args.check, changed)

    method_description = "The methodology behind LCA of the Impossible: evidence, functional units, engineering reconstruction, inventories, emission factors, uncertainty and interpretation."
    method_url = BASE_URL + "method.html"
    method_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "Method — LCA of the Impossible",
        "url": method_url,
        "description": method_description,
        "inLanguage": "en",
        "isPartOf": {"@type": "WebSite", "name": "LCA of the Impossible", "url": BASE_URL},
    }
    method_block = seo_block(
        title="Method — LCA of the Impossible",
        description=method_description,
        canonical=method_url,
        image=latest_image,
        image_alt=f"{latest['title']} — latest LCA of the Impossible episode cover",
        page_type="website",
        prefix="",
        json_ld=method_ld,
    )
    apply_page(ROOT / "method.html", method_block, args.check, changed)

    for episode in episodes:
        canonical = BASE_URL + episode["url"]
        image = BASE_URL + episode["cover"]
        season_label = str(episode.get("seasonLabel") or "").strip()
        season_title = str(episode.get("seasonTitle") or "").strip()
        description = episode["featuredDescription"]
        if season_label:
            description = f"{season_label}. {description}"
        social_title = (
            f"{episode['title']} — Episode #{episode['number']} | Season I: {season_title}"
            if season_label and episode.get("seasonNumber") == 1
            else f"{episode['title']} — Episode #{episode['number']} | LCA of the Impossible"
        )
        website_ld = {"@type": "WebSite", "name": "LCA of the Impossible", "url": BASE_URL}
        series_ld = (
            {
                "@type": "CreativeWorkSeries",
                "name": season_label,
                "description": episode.get("seasonDescriptor", ""),
                "isPartOf": website_ld,
            }
            if season_label
            else website_ld
        )
        about = [
            {"@type": "Thing", "name": episode["lcaLabel"]},
            {"@type": "Thing", "name": episode["categoryLabel"]},
        ]
        if season_label:
            about.insert(0, {"@type": "Thing", "name": season_label})
        episode_ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": episode["title"],
            "description": description,
            "url": canonical,
            "mainEntityOfPage": canonical,
            "image": image,
            "identifier": f"Episode #{episode['number']}",
            "articleSection": season_label or episode["categoryLabel"],
            "keywords": episode.get("keywords", []),
            "inLanguage": "en",
            "author": {"@type": "Organization", "name": "LCA of the Impossible"},
            "isPartOf": series_ld,
            "about": about,
        }
        if episode.get("datePublished"):
            episode_ld["datePublished"] = episode["datePublished"]
        if episode.get("dateModified"):
            episode_ld["dateModified"] = episode["dateModified"]
        block = seo_block(
            title=social_title,
            description=description,
            canonical=canonical,
            image=image,
            image_alt=(
                f"{episode['title']} — {season_label} Episode #{episode['number']} cover"
                if season_label
                else f"{episode['title']} — LCA of the Impossible Episode #{episode['number']} cover"
            ),
            page_type="article",
            prefix="../",
            json_ld=episode_ld,
            article_section=season_label or episode["categoryLabel"],
        )
        apply_page(ROOT / episode["url"], block, args.check, changed)

    apply_template(args.check, changed)
    write_if_changed(ROOT / "sitemap.xml", build_sitemap(episodes), args.check, changed)
    write_if_changed(ROOT / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n", args.check, changed)
    write_if_changed(ROOT / "assets/favicon.svg", build_favicon(), args.check, changed)
    write_if_changed(ROOT / "site.webmanifest", build_manifest(), args.check, changed)
    update_readme(args.check, changed)

    if changed:
        label = "would change" if args.check else "updated"
        for path in changed:
            print(f"SEO {label}: {path.relative_to(ROOT)}")
        return 1 if args.check else 0
    print("SEO metadata is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
