#!/usr/bin/env python3
"""Synchronize the registry-driven Impossible Lab route and its homepage entry point."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://lcaofimpossible.github.io/LCA-of-the-Impossible/"
LAB_CSS_VERSION = "20260911-run1"
HUB_VERSION = "20260911-run1"
GUESS_VERSION = "20260911-results1"
ACTION_VERSION = "20260911-navigation1"
CROSSWORD_VERSION = "20260911-score1"
NAV_VERSION = "20260911-navigation1"
RESULTS_VERSION = "20260911-run1"
PROGRESS_VERSION = "20260911-score1"
RUN_VERSION = "20260911-run1"
ALPHABET_VERSION = "20260911-results1"
SPIN_VERSION = "20260911-results1"
HOME_START = "<!-- LAB-HOME:START -->"
HOME_END = "<!-- LAB-HOME:END -->"
SEO_START = "<!-- LAB-SEO:START -->"
SEO_END = "<!-- LAB-SEO:END -->"
HUB_SEO_START = "<!-- LAB-HUB-SEO:START -->"
HUB_SEO_END = "<!-- LAB-HUB-SEO:END -->"
RUN_SEO_START = "<!-- LAB-RUN-SEO:START -->"
RUN_SEO_END = "<!-- LAB-RUN-SEO:END -->"
CROSSWORD_SEO_START = "<!-- CROSSWORD-SEO:START -->"
CROSSWORD_SEO_END = "<!-- CROSSWORD-SEO:END -->"
ALPHABET_SEO_START = "<!-- ALPHABET-SEO:START -->"
ALPHABET_SEO_END = "<!-- ALPHABET-SEO:END -->"
SPIN_SEO_START = "<!-- SPIN-SEO:START -->"
SPIN_SEO_END = "<!-- SPIN-SEO:END -->"
README_START = "<!-- IMPOSSIBLE-LAB-RULES:START -->"
README_END = "<!-- IMPOSSIBLE-LAB-RULES:END -->"


def write_if_changed(path: Path, content: str, check: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return
    changed.append(path)
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def home_block() -> str:
    return f'''{HOME_START}
    <section class="section small-section-title lab-home-preview" id="impossible-lab">
      <div class="section-heading">
        <div><p class="eyebrow">IMPOSSIBLE LAB</p><h2>Play the archive.</h2></div>
        <p class="section-note">Four registry-driven experiments. Every published episode. Challenges are assembled automatically.</p>
      </div>
      <div class="lab-home-grid">
        <div class="lab-home-copy">
          <p class="eyebrow">EXPERIMENTS 01–04</p>
          <h3>Guess it. Cross it. Race it. Spin it.</h3>
          <p>Identify a case, solve a connected grid, race through the alphabet or rebuild a hidden narrative phrase.</p>
          <div class="lab-home-actions">
            <a class="button" href="impossible-lab.html">Enter Impossible Lab →</a>
          </div>
        </div>
        <div class="lab-home-terminal" aria-label="Impossible Lab experiment summary">
          <span><b>01</b> FIVE PROGRESSIVE SIGNALS</span>
          <span><b>01</b> UP TO 500 POINTS</span>
          <span><b>02</b> TEN CONNECTED CASES</span>
          <span><b>03</b> THREE-MINUTE LETTER CIRCUIT</span>
          <span><b>04</b> FIVE HIDDEN PHRASES</span>
          <span><b>LAB</b> LCA RECORD AFTER SOLUTION</span>
        </div>
      </div>
    </section>
{HOME_END}'''


def update_home(check: bool, changed: list[Path]) -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    block = home_block()
    pattern = rf"{re.escape(HOME_START)}.*?{re.escape(HOME_END)}"
    if re.search(pattern, text, flags=re.S):
        updated = re.sub(pattern, block, text, flags=re.S)
    else:
        marker = '<section class="section small-section-title season-route-shell">'
        position = text.find(marker)
        if position == -1:
            raise RuntimeError("Cannot place the Impossible Lab homepage block")
        updated = text[:position] + block + "\n\n    " + text[position:]

    css = f'assets/lab.css?v={LAB_CSS_VERSION}'
    css_pattern = r'<link\s+rel="stylesheet"\s+href="[^"]*assets/lab\.css(?:\?v=[^"]*)?">'
    if re.search(css_pattern, updated):
        updated = re.sub(css_pattern, f'<link rel="stylesheet" href="{css}">', updated)
    else:
        anchor = re.search(r'<link\s+rel="stylesheet"\s+href="assets/editorial\.css[^"]*">', updated)
        if not anchor:
            raise RuntimeError("Cannot add Impossible Lab styles to the homepage")
        updated = updated[:anchor.end()] + f'\n  <link rel="stylesheet" href="{css}">' + updated[anchor.end():]

    write_if_changed(path, updated, check, changed)


def seo_block(latest: dict) -> str:
    title = "Impossible Lab — Guess the Impossible"
    description = "Enter the Impossible Lab and play Guess the Impossible: identify a published LCA case from five progressively revealed life-cycle clues."
    social_description = "Identify a published LCA of the Impossible case from season, inventory, impact, function and final clues."
    canonical = BASE_URL + "lab.html"
    image = BASE_URL + latest["cover"]
    image_alt = f"{latest['title']} — latest LCA of the Impossible episode cover"
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "url": canonical,
        "description": social_description,
        "inLanguage": "en",
        "isPartOf": {
            "@type": "WebSite",
            "name": "LCA of the Impossible",
            "url": BASE_URL,
        },
    }
    return "\n".join([
        SEO_START,
        f'  <meta name="description" content="{html.escape(description, quote=True)}">',
        '  <meta name="robots" content="index,follow,max-image-preview:large">',
        '  <meta name="theme-color" content="#071019">',
        f'  <link rel="canonical" href="{canonical}">',
        '  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '  <link rel="manifest" href="site.webmanifest">',
        '  <link rel="alternate" type="application/rss+xml" title="LCA of the Impossible — New episodes" href="feed.xml">',
        '  <meta property="og:site_name" content="LCA of the Impossible">',
        '  <meta property="og:type" content="website">',
        f'  <meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'  <meta property="og:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta property="og:url" content="{canonical}">',
        f'  <meta property="og:image" content="{image}">',
        f'  <meta property="og:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <meta property="og:locale" content="en_US">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{html.escape(title, quote=True)}">',
        f'  <meta name="twitter:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta name="twitter:image" content="{image}">',
        f'  <meta name="twitter:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <script type="application/ld+json">',
        json.dumps(json_ld, ensure_ascii=False, indent=2),
        '  </script>',
        SEO_END,
    ])


def hub_seo_block(latest: dict) -> str:
    title = "Impossible Lab — Play the archive"
    description = "Enter Impossible Lab and choose among four games built automatically from the published LCA of the Impossible archive."
    social_description = "Choose a deduction game, crossword, speed quiz or hidden-phrase challenge powered by the published archive."
    canonical = BASE_URL + "impossible-lab.html"
    image = BASE_URL + latest["cover"]
    image_alt = f"{latest['title']} — latest LCA of the Impossible episode cover"
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "url": canonical,
        "description": social_description,
        "inLanguage": "en",
        "isPartOf": {
            "@type": "WebSite",
            "name": "LCA of the Impossible",
            "url": BASE_URL,
        },
    }
    return "\n".join([
        HUB_SEO_START,
        f'  <meta name="description" content="{html.escape(description, quote=True)}">',
        '  <meta name="robots" content="index,follow,max-image-preview:large">',
        '  <meta name="theme-color" content="#071019">',
        f'  <link rel="canonical" href="{canonical}">',
        '  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '  <link rel="manifest" href="site.webmanifest">',
        '  <link rel="alternate" type="application/rss+xml" title="LCA of the Impossible — New episodes" href="feed.xml">',
        '  <meta property="og:site_name" content="LCA of the Impossible">',
        '  <meta property="og:type" content="website">',
        f'  <meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'  <meta property="og:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta property="og:url" content="{canonical}">',
        f'  <meta property="og:image" content="{image}">',
        f'  <meta property="og:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <meta property="og:locale" content="en_US">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{html.escape(title, quote=True)}">',
        f'  <meta name="twitter:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta name="twitter:image" content="{image}">',
        f'  <meta name="twitter:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <script type="application/ld+json">',
        json.dumps(json_ld, ensure_ascii=False, indent=2),
        '  </script>',
        HUB_SEO_END,
    ])


def run_seo_block(latest: dict) -> str:
    title = "Impossible Lab Run — Four games. One run."
    description = "Take the Impossible Lab Run: complete one consecutive round of all four archive-powered games and combine their normalized scores."
    social_description = "Complete Guess, Cross, Alphabet and Spin in sequence, then combine the four normalized results into one Run Score."
    canonical = BASE_URL + "impossible-lab-run.html"
    image = BASE_URL + latest["cover"]
    image_alt = f"{latest['title']} — latest LCA of the Impossible episode cover"
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Game",
        "name": "Impossible Lab Run",
        "url": canonical,
        "description": social_description,
        "inLanguage": "en",
        "isPartOf": {
            "@type": "WebSite",
            "name": "LCA of the Impossible",
            "url": BASE_URL,
        },
    }
    return "\n".join([
        RUN_SEO_START,
        f'  <meta name="description" content="{html.escape(description, quote=True)}">',
        '  <meta name="robots" content="index,follow,max-image-preview:large">',
        '  <meta name="theme-color" content="#071019">',
        f'  <link rel="canonical" href="{canonical}">',
        '  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '  <link rel="manifest" href="site.webmanifest">',
        '  <link rel="alternate" type="application/rss+xml" title="LCA of the Impossible — New episodes" href="feed.xml">',
        '  <meta property="og:site_name" content="LCA of the Impossible">',
        '  <meta property="og:type" content="website">',
        f'  <meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'  <meta property="og:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta property="og:url" content="{canonical}">',
        f'  <meta property="og:image" content="{image}">',
        f'  <meta property="og:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <meta property="og:locale" content="en_US">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{html.escape(title, quote=True)}">',
        f'  <meta name="twitter:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta name="twitter:image" content="{image}">',
        f'  <meta name="twitter:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <script type="application/ld+json">',
        json.dumps(json_ld, ensure_ascii=False, indent=2),
        '  </script>',
        RUN_SEO_END,
    ])


def crossword_seo_block(latest: dict) -> str:
    title = "Cross the Impossible — Impossible Lab"
    description = "Play Cross the Impossible: solve an automatically generated crossword built from narrative and cultural descriptions of published cases."
    social_description = "Solve ten connected subjects through narrative clues, then discover the life-cycle model behind every answer."
    canonical = BASE_URL + "lab-crossword.html"
    image = BASE_URL + latest["cover"]
    image_alt = f"{latest['title']} — latest LCA of the Impossible episode cover"
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Game",
        "name": "Cross the Impossible",
        "url": canonical,
        "description": description,
        "inLanguage": "en",
        "isPartOf": {
            "@type": "WebSite",
            "name": "LCA of the Impossible",
            "url": BASE_URL,
        },
    }
    return "\n".join([
        CROSSWORD_SEO_START,
        f'  <meta name="description" content="{html.escape(description, quote=True)}">',
        '  <meta name="robots" content="index,follow,max-image-preview:large">',
        '  <meta name="theme-color" content="#071019">',
        f'  <link rel="canonical" href="{canonical}">',
        '  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '  <link rel="manifest" href="site.webmanifest">',
        '  <link rel="alternate" type="application/rss+xml" title="LCA of the Impossible — New episodes" href="feed.xml">',
        '  <meta property="og:site_name" content="LCA of the Impossible">',
        '  <meta property="og:type" content="website">',
        f'  <meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'  <meta property="og:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta property="og:url" content="{canonical}">',
        f'  <meta property="og:image" content="{image}">',
        f'  <meta property="og:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <meta property="og:locale" content="en_US">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{html.escape(title, quote=True)}">',
        f'  <meta name="twitter:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta name="twitter:image" content="{image}">',
        f'  <meta name="twitter:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <script type="application/ld+json">',
        json.dumps(json_ld, ensure_ascii=False, indent=2),
        '  </script>',
        CROSSWORD_SEO_END,
    ])


def alphabet_seo_block(latest: dict) -> str:
    title = "The Impossible Alphabet — Impossible Lab"
    description = "Play The Impossible Alphabet: race through narrative clues drawn automatically from every published case in the LCA of the Impossible archive."
    social_description = "Answer, pass and return: identify an impossible subject for every active initial before three minutes expire."
    canonical = BASE_URL + "lab-alphabet.html"
    image = BASE_URL + latest["cover"]
    image_alt = f"{latest['title']} — latest LCA of the Impossible episode cover"
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Game",
        "name": "The Impossible Alphabet",
        "url": canonical,
        "description": description,
        "inLanguage": "en",
        "isPartOf": {
            "@type": "WebSite",
            "name": "LCA of the Impossible",
            "url": BASE_URL,
        },
    }
    return "\n".join([
        ALPHABET_SEO_START,
        f'  <meta name="description" content="{html.escape(description, quote=True)}">',
        '  <meta name="robots" content="index,follow,max-image-preview:large">',
        '  <meta name="theme-color" content="#071019">',
        f'  <link rel="canonical" href="{canonical}">',
        '  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '  <link rel="manifest" href="site.webmanifest">',
        '  <link rel="alternate" type="application/rss+xml" title="LCA of the Impossible — New episodes" href="feed.xml">',
        '  <meta property="og:site_name" content="LCA of the Impossible">',
        '  <meta property="og:type" content="website">',
        f'  <meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'  <meta property="og:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta property="og:url" content="{canonical}">',
        f'  <meta property="og:image" content="{image}">',
        f'  <meta property="og:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <meta property="og:locale" content="en_US">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{html.escape(title, quote=True)}">',
        f'  <meta name="twitter:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta name="twitter:image" content="{image}">',
        f'  <meta name="twitter:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <script type="application/ld+json">',
        json.dumps(json_ld, ensure_ascii=False, indent=2),
        '  </script>',
        ALPHABET_SEO_END,
    ])


def spin_seo_block(latest: dict) -> str:
    title = "Spin the Impossible — Impossible Lab"
    description = "Play Spin the Impossible: reveal an approved narrative phrase letter by letter, then discover the impossible subject and its life-cycle record."
    social_description = "Spin, choose consonants, buy vowels and reconstruct a hidden narrative phrase from the archive."
    canonical = BASE_URL + "lab-spin.html"
    image = BASE_URL + latest["cover"]
    image_alt = f"{latest['title']} — latest LCA of the Impossible episode cover"
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Game",
        "name": "Spin the Impossible",
        "url": canonical,
        "description": description,
        "inLanguage": "en",
        "isPartOf": {
            "@type": "WebSite",
            "name": "LCA of the Impossible",
            "url": BASE_URL,
        },
    }
    return "\n".join([
        SPIN_SEO_START,
        f'  <meta name="description" content="{html.escape(description, quote=True)}">',
        '  <meta name="robots" content="index,follow,max-image-preview:large">',
        '  <meta name="theme-color" content="#071019">',
        f'  <link rel="canonical" href="{canonical}">',
        '  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">',
        '  <link rel="manifest" href="site.webmanifest">',
        '  <link rel="alternate" type="application/rss+xml" title="LCA of the Impossible — New episodes" href="feed.xml">',
        '  <meta property="og:site_name" content="LCA of the Impossible">',
        '  <meta property="og:type" content="website">',
        f'  <meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'  <meta property="og:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta property="og:url" content="{canonical}">',
        f'  <meta property="og:image" content="{image}">',
        f'  <meta property="og:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <meta property="og:locale" content="en_US">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{html.escape(title, quote=True)}">',
        f'  <meta name="twitter:description" content="{html.escape(social_description, quote=True)}">',
        f'  <meta name="twitter:image" content="{image}">',
        f'  <meta name="twitter:image:alt" content="{html.escape(image_alt, quote=True)}">',
        '  <script type="application/ld+json">',
        json.dumps(json_ld, ensure_ascii=False, indent=2),
        '  </script>',
        SPIN_SEO_END,
    ])


def update_lab_metadata(check: bool, changed: list[Path]) -> None:
    registry = json.loads((ROOT / "episodes.json").read_text(encoding="utf-8"))
    latest = max(registry["episodes"], key=lambda episode: episode["number"])
    hub_path = ROOT / "impossible-lab.html"
    hub_text = hub_path.read_text(encoding="utf-8")
    hub_block = hub_seo_block(latest)
    hub_pattern = rf"{re.escape(HUB_SEO_START)}.*?{re.escape(HUB_SEO_END)}"
    if not re.search(hub_pattern, hub_text, flags=re.S):
        raise RuntimeError("Missing Impossible Lab hub SEO markers")
    hub_updated = re.sub(hub_pattern, hub_block, hub_text, flags=re.S)
    write_if_changed(hub_path, hub_updated, check, changed)

    run_path = ROOT / "impossible-lab-run.html"
    run_text = run_path.read_text(encoding="utf-8")
    run_block = run_seo_block(latest)
    run_pattern = rf"{re.escape(RUN_SEO_START)}.*?{re.escape(RUN_SEO_END)}"
    if not re.search(run_pattern, run_text, flags=re.S):
        raise RuntimeError("Missing Impossible Lab Run SEO markers")
    run_updated = re.sub(run_pattern, run_block, run_text, flags=re.S)
    write_if_changed(run_path, run_updated, check, changed)

    path = ROOT / "lab.html"
    text = path.read_text(encoding="utf-8")
    block = seo_block(latest)
    pattern = rf"{re.escape(SEO_START)}.*?{re.escape(SEO_END)}"
    if not re.search(pattern, text, flags=re.S):
        raise RuntimeError("Missing Impossible Lab SEO markers")
    updated = re.sub(pattern, block, text, flags=re.S)
    write_if_changed(path, updated, check, changed)

    crossword_path = ROOT / "lab-crossword.html"
    crossword_text = crossword_path.read_text(encoding="utf-8")
    crossword_block = crossword_seo_block(latest)
    crossword_pattern = rf"{re.escape(CROSSWORD_SEO_START)}.*?{re.escape(CROSSWORD_SEO_END)}"
    if not re.search(crossword_pattern, crossword_text, flags=re.S):
        raise RuntimeError("Missing Cross the Impossible SEO markers")
    crossword_updated = re.sub(crossword_pattern, crossword_block, crossword_text, flags=re.S)
    write_if_changed(crossword_path, crossword_updated, check, changed)

    alphabet_path = ROOT / "lab-alphabet.html"
    alphabet_text = alphabet_path.read_text(encoding="utf-8")
    alphabet_block = alphabet_seo_block(latest)
    alphabet_pattern = rf"{re.escape(ALPHABET_SEO_START)}.*?{re.escape(ALPHABET_SEO_END)}"
    if not re.search(alphabet_pattern, alphabet_text, flags=re.S):
        raise RuntimeError("Missing The Impossible Alphabet SEO markers")
    alphabet_updated = re.sub(alphabet_pattern, alphabet_block, alphabet_text, flags=re.S)
    write_if_changed(alphabet_path, alphabet_updated, check, changed)

    spin_path = ROOT / "lab-spin.html"
    spin_text = spin_path.read_text(encoding="utf-8")
    spin_block = spin_seo_block(latest)
    spin_pattern = rf"{re.escape(SPIN_SEO_START)}.*?{re.escape(SPIN_SEO_END)}"
    if not re.search(spin_pattern, spin_text, flags=re.S):
        raise RuntimeError("Missing Spin the Impossible SEO markers")
    spin_updated = re.sub(spin_pattern, spin_block, spin_text, flags=re.S)
    write_if_changed(spin_path, spin_updated, check, changed)


def update_game_assets(check: bool, changed: list[Path]) -> None:
    contracts = {
        "impossible-lab.html": {
            "assets/lab.css": LAB_CSS_VERSION,
            "assets/lab-hub.css": HUB_VERSION,
            "assets/lab-progress.js": PROGRESS_VERSION,
            "assets/lab-hub.js": HUB_VERSION,
        },
        "impossible-lab-run.html": {
            "assets/lab.css": LAB_CSS_VERSION,
            "assets/lab-run.css": RUN_VERSION,
            "assets/lab-progress.js": PROGRESS_VERSION,
            "assets/lab-run.js": RUN_VERSION,
            "assets/lab-run-page.js": RUN_VERSION,
        },
        "lab.html": {
            "assets/lab.css": LAB_CSS_VERSION,
            "assets/lab.js": GUESS_VERSION,
            "assets/lab-nav.js": NAV_VERSION,
            "assets/lab-actions.js": ACTION_VERSION,
            "assets/lab-progress.js": PROGRESS_VERSION,
            "assets/lab-run.js": RUN_VERSION,
            "assets/lab-results.js": RESULTS_VERSION,
        },
        "lab-crossword.html": {
            "assets/lab.css": LAB_CSS_VERSION,
            "assets/crossword.css": CROSSWORD_VERSION,
            "assets/lab-nav.js": NAV_VERSION,
            "assets/lab-actions.js": ACTION_VERSION,
            "assets/lab-progress.js": PROGRESS_VERSION,
            "assets/lab-run.js": RUN_VERSION,
            "assets/lab-results.js": RESULTS_VERSION,
            "assets/crossword-generator.js": CROSSWORD_VERSION,
            "assets/crossword.js": CROSSWORD_VERSION,
        },
        "lab-alphabet.html": {
            "assets/lab.css": LAB_CSS_VERSION,
            "assets/alphabet.css": ALPHABET_VERSION,
            "assets/lab-nav.js": NAV_VERSION,
            "assets/lab-actions.js": ACTION_VERSION,
            "assets/lab-progress.js": PROGRESS_VERSION,
            "assets/lab-run.js": RUN_VERSION,
            "assets/lab-results.js": RESULTS_VERSION,
            "assets/alphabet.js": ALPHABET_VERSION,
        },
        "lab-spin.html": {
            "assets/lab.css": LAB_CSS_VERSION,
            "assets/spin.css": SPIN_VERSION,
            "assets/lab-nav.js": NAV_VERSION,
            "assets/lab-actions.js": ACTION_VERSION,
            "assets/lab-progress.js": PROGRESS_VERSION,
            "assets/lab-run.js": RUN_VERSION,
            "assets/lab-results.js": RESULTS_VERSION,
            "assets/spin.js": SPIN_VERSION,
        },
    }
    for filename, assets in contracts.items():
        path = ROOT / filename
        updated = path.read_text(encoding="utf-8")
        for asset, version in assets.items():
            pattern = rf'{re.escape(asset)}(?:\?v=[^"\']*)?'
            updated = re.sub(pattern, f"{asset}?v={version}", updated)
        write_if_changed(path, updated, check, changed)


def update_sitemap(check: bool, changed: list[Path]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    urls = [
        BASE_URL + "impossible-lab.html",
        BASE_URL + "impossible-lab-run.html",
        BASE_URL + "lab.html",
        BASE_URL + "lab-crossword.html",
        BASE_URL + "lab-alphabet.html",
        BASE_URL + "lab-spin.html",
    ]
    updated = text
    for url in urls:
        updated = re.sub(rf'\s*<url><loc>{re.escape(url)}</loc></url>', '', updated)
    lines = "\n".join(f"  <url><loc>{url}</loc></url>" for url in urls)
    updated = updated.replace("</urlset>", f"{lines}\n</urlset>")
    write_if_changed(path, updated, check, changed)


def update_readme(check: bool, changed: list[Path]) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    section = f'''{README_START}

## 39. Impossible Lab and registry-driven games — mandatory

`impossible-lab.html` is the canonical entry point for **Impossible Lab**. It presents every live experiment and the separate **Impossible Lab Run** mode before play, while the existing game URLs remain stable. The published experiments are **Guess the Impossible**, **Cross the Impossible**, **The Impossible Alphabet** and **Spin the Impossible**. Games operate across the complete published archive rather than create separate implementations for individual episodes.

The hub catalogue is generated from `lab-games.json`. Every game record includes a concise navigation label plus a complete `summary`, estimated `duration` and `category`, all displayed directly in the game card. The static HTML retains the same four cards as an accessible fallback. The global `Lab` navigation always opens the hub. Every game page provides the same route bar, marks the current experiment in the shared selector and ends with `Play again`, `Choose another game` and `Return to the Lab` actions. The random alternative is selected from live `lab-games.json` records and never repeats the current game.

### 39.1 Guess the Impossible

The game selects one eligible record from `episodes.json` and reveals five clues in this fixed order:

1. `Season` — the registered `seasonLabel`;
2. `Inventory` — registered model drivers or, where structured metadata is unavailable, the approved LCA lens and characteristics;
3. `Impact` — the registered headline `result` and `hotspot`;
4. `Function` — the registered `functionalUnit` or reporting basis;
5. `Final clue` — the registered `subjectDescription`, with the episode title redacted where it occurs.

Available points are `500 → 400 → 300 → 200 → 100`. A wrong answer unlocks the next clue. Revealing the answer scores zero and resets the current streak. The running score and streak remain session-only; a completed round may update the device-local personal record described in Section 39.5.

### 39.2 Cross the Impossible

`lab-crossword.html` generates a connected crossword from `crossword.json` and the current `episodes.json` registry:

- every grid contains exactly ten unique published subjects and represents both seasons;
- definitions describe narrative, historical or cultural identity without disclosing the answer or using numerical/LCA clues;
- a correct word awards `50` points and each revealed letter removes `10` points from the maximum score of `500`;
- once a word is correct, its episode card reveals only the approved `subjectDescription`, `result`, `hotspot`, season and canonical URL;
- generated grids rotate through the available pool and require no episode-specific page implementation;
- the generator remains deterministic for a given seed and includes a validated fallback layout.

The in-progress crossword score remains session-only. Only a completed grid may update the device-local personal record described in Section 39.5.

### 39.3 The Impossible Alphabet

`lab-alphabet.html` joins `crossword.json` with `episodes.json`, groups every eligible subject by the initial of its approved crossword answer and selects one case for up to `18` active initials per round:

- available initials rotate automatically when the archive eventually contains more than `18` distinct letters;
- the timer begins only after an explicit start and lasts exactly `180` seconds;
- a correct answer awards `100` base points;
- consecutive correct answers add `25` points per streak step, capped at a `100`-point bonus for one answer;
- a wrong answer reveals the approved answer and resets the streak;
- `Pass` keeps the letter unresolved and returns it after the rest of the circuit;
- the round ends when every letter is resolved or time expires;
- the final review reveals every answer and links to the canonical episode page.

Every published episode remains eligible for selection. New episodes require no alphabet-specific record: the approved narrative definition already maintained for `crossword.json` supplies the clue, while the registered episode supplies title, season and canonical URL. Round state and selection history remain in memory for the current page session; only the completed circuit's personal records persist locally as described in Section 39.5.

### 39.4 Spin the Impossible

`lab-spin.html` joins every approved narrative definition in `crossword.json` to its episode in `episodes.json`. The definition itself becomes a hidden phrase; the subject title remains classified until the phrase is solved, revealed or purchased as a hint.

- one session contains exactly `5` non-repeating phrases where the available registry permits;
- each round begins with `15` wheel spins and `3` solution attempts, with no timer;
- numerical sectors award their value for every occurrence of a correctly selected consonant;
- the `×2` sector awards `400` points per consonant occurrence, `FREE VOWEL` permits one vowel without charge, `MISS` consumes the spin and `RESET` clears only the current round score;
- buying a vowel costs `150` points, revealing the subject hint costs `300` points and an incorrect full-phrase solution costs `200` points;
- a correct solution awards a base `500`-point bonus multiplied by phrase length, plus `25` points for every letter still hidden;
- the completed round reveals the approved subject description, result, hotspot and canonical episode URL.

The hidden phrase is never duplicated in a Spin-specific dataset. Phrase selection and active-round state remain in memory for the current page session; only completed-round personal records persist locally as described in Section 39.5.

### 39.5 Shared result system

All four games retain their original scoring rules and render the same final performance card through `assets/lab-results.js`. The card exposes the original game or round score, the maximum obtainable score, completion, accuracy and a normalized score from `0` to `1,000`.

- normalized score = `round(clamp(original score / maximum obtainable, 0, 1) × 1,000)`;
- Guess uses a `500`-point maximum; completion is `100%` only when the case is identified, and accuracy is correct guesses divided by submitted guesses;
- Cross uses its original `500`-point maximum; completion is solved words divided by grid words, and accuracy is solved words divided by completed answer submissions;
- Alphabet calculates its maximum from a perfect uninterrupted streak across the active letters; completion is answered letters divided by active letters, and accuracy is correct answers divided by submitted answers;
- Spin calculates a phrase-specific theoretical maximum from its existing wheel, occurrence and solve-bonus rules; completion is the share of letters uncovered unless the complete phrase is solved, and accuracy combines letter selections and full-phrase attempts;
- multi-case games retain their complete answer review and present one clearly labelled subject debrief without ranking or comparing episode impacts.

`assets/lab-progress.js` stores two independent personal bests for each of the four game identifiers:

- the highest original score, preserving the scoring language of that specific game;
- the highest normalized score, limited to `0–1,000`, which becomes that game's contribution to the Lab Score.

The **Lab Score** is `best normalized Guess + best normalized Cross + best normalized Alphabet + best normalized Spin`, for a fixed maximum of `4,000`. An experiment without a completed record contributes zero. A lower later result never reduces either personal best. The original-score record and normalized-score record may come from different rounds when a game's theoretical maximum varies.

The hub displays the Lab Score, completion count, percentage and four normalized contributions. Result cards display the current result, game record, best normalized contribution and updated Lab Score. Records use the single device-local `localStorage` key `lca-impossible-lab-progress-v1`; the payload contains scores and play counts only, creates no account or visitor identifier, is never transmitted by the site and can be deleted with `Reset records`. When browser storage is unavailable, gameplay continues and the interface states that records cannot be retained.

The normalized score compares game performance only. It must never be presented as a comparison, ranking or normalization of the environmental results, footprints or functional units of different episodes.

### 39.6 Impossible Lab Run

`impossible-lab-run.html` orchestrates one consecutive circuit through the four existing experiments in their canonical order: Guess, Cross, Alphabet and Spin. Starting a Run clears only the previous Run state and opens the first game with `?run=1`. Each game accepts exactly one completed result when it is the expected stage; out-of-order pages and repeated results cannot alter the circuit.

Each accepted result contributes its current normalized score from `0` to `1,000`. The **Run Score** is their sum, for a fixed maximum of `4,000`. It is intentionally different from the persistent Lab Score: the Run Score uses the four results achieved in that single circuit, whereas the Lab Score uses the all-time best normalized result for each game. Completing a Run stage may still improve the independent game record and Lab Score through the shared result system.

The route displays stage order, current stage, completed contributions, total Run Score and a direct continuation action. Progress survives ordinary page changes and reloads through the separate device-local key `lca-impossible-lab-run-v1`. Restarting or clearing a Run never deletes game records or the Lab Score. The Run creates no new clue dataset and therefore inherits the existing registry-driven maintenance model.

### 39.7 Registry and editorial guardrails

- Every currently eligible episode and every future complete registry record enters the game automatically.
- Episode titles, results, links and counts must never be duplicated in the game pages or hard-coded in runtime JavaScript.
- Each newly published episode adds one approved narrative definition to `crossword.json`; the grid and navigation require no manual layout work.
- The alphabet circuit derives both its letters and questions from `crossword.json`; do not create or maintain a parallel alphabet clue registry.
- Spin the Impossible uses the complete approved definition as its hidden phrase; do not create or maintain a parallel wheel phrase registry.
- The game may reformat approved registry values for readability but must not invent a result, assumption, inventory flow, comparison or ranking.
- Guessing performance scores the player only. It never ranks cases or implies that unlike functional units are environmentally comparable.
- Catalogue covers remain limited to Homepage and Archive. Impossible Lab results are text-only and link to the canonical episode page.
- The game must remain keyboard-accessible, responsive, readable at enlarged text sizes and usable on touch devices.
- A registry failure must leave a clear error state and a working link to the Archive.

### 39.8 Canonical files and automation

- `impossible-lab.html`, `assets/lab-hub.css` and `assets/lab-hub.js` — canonical game catalogue, combined Lab Score, responsive cards and random experiment selection;
- `impossible-lab-run.html`, `assets/lab-run.css`, `assets/lab-run.js` and `assets/lab-run-page.js` — four-stage circuit, sequential state, Run Score and responsive progress route;
- `lab.html` and `assets/lab.js` — Guess the Impossible interface and runtime;
- `lab-crossword.html`, `assets/crossword.css` and `assets/crossword.js` — crossword interface, scoring and result-card runtime;
- `assets/crossword-generator.js` — seeded connected-grid generation and validation;
- `lab-alphabet.html`, `assets/alphabet.css` and `assets/alphabet.js` — timed letter circuit, scoring, pass/return flow and answer review;
- `lab-spin.html`, `assets/spin.css` and `assets/spin.js` — hidden-phrase wheel, letter controls, session scoring and LCA reveal;
- `lab-games.json`, `assets/lab-nav.js`, `assets/lab-actions.js`, `assets/lab-results.js` and `assets/lab-progress.js` — shared experiment registry, navigation, end-of-game routing, normalized result card and device-local personal records;
- `crossword.json` — approved answer/definition pairs joined to `episodes.json` by episode number;
- `assets/lab.css` — shared responsive Lab presentation and homepage entry point;
- `scripts/lab_sync.py` — homepage entry point, metadata, sitemap and README synchronization;
- `scripts/lab_qa.py` — Guess the Impossible registry coverage, gameplay, accessibility, privacy and publication checks;
- `scripts/crossword_qa.py` and `scripts/crossword_generator_qa.js` — definition coverage, layout generation, scoring and integration checks.
- `scripts/alphabet_qa.py` — alphabet derivation, timing, scoring, privacy and publication checks.
- `scripts/spin_qa.py` — hidden-phrase derivation, wheel outcomes, scoring, privacy and publication checks.

`scripts/publication_qa.py` runs `lab_sync.py` after global navigation synchronization and runs all four game QA suites as part of the mandatory read-only publication gate. GitHub Pages live QA compares the hub, four game pages, registries and runtime assets byte-for-byte with the checked-out publication.

### Impossible Lab QA

- [ ] Every eligible registry record supplies all five clue sources.
- [ ] The first clue is available as soon as the registry loads.
- [ ] Five scoring levels are exactly `500`, `400`, `300`, `200` and `100`.
- [ ] Wrong answers and manual reveals progress through the same ordered clue sequence.
- [ ] The title is redacted from the final clue where present.
- [ ] No episode title or clue dataset is hard-coded into the game runtime.
- [ ] The answer and case result use text-only registry data and the canonical episode URL.
- [ ] Every crossword definition covers one published episode, matches its title and contains no numerical or LCA terminology.
- [ ] Generated crosswords contain ten unique cases, both seasons, valid intersections and no adjacent-word collisions.
- [ ] Crossword scoring is exactly `50` per correct word and `−10` per revealed letter, with a maximum of `500`.
- [ ] The alphabet circuit includes one case per available initial, starts only on request and lasts exactly `180` seconds.
- [ ] Alphabet scoring is `100` base points plus `25` per consecutive-answer streak step, capped at a `100`-point bonus.
- [ ] Each round contains no more than 18 active initials; passed letters return, wrong answers reset the streak and the final review links every answer to its canonical episode.
- [ ] The alphabet reuses `crossword.json` and introduces no duplicate clue registry.
- [ ] Spin the Impossible uses five non-repeating phrases per session, fifteen spins per round and three solution attempts without a timer.
- [ ] Spin wheel values, special sectors, vowel cost, hint cost, incorrect-solution penalty and solve bonus match the canonical constants.
- [ ] Spin phrases come directly from `crossword.json`; completed rounds reveal only approved episode registry fields and the canonical URL.
- [ ] Every hub card exposes its game summary, challenge category and estimated duration without requiring navigation into the game.
- [ ] Every game exposes the same Lab route bar, a visible current-game marker and the three standard completion actions on desktop and mobile.
- [ ] `Choose another game` selects only a different live registry entry and falls back safely to the Lab hub if the registry is unavailable.
- [ ] Every final result retains the original score and exposes maximum obtainable, completion, accuracy and a normalized score limited to `0–1,000`.
- [ ] A completed result can improve the independent original-score record and normalized-score record without a lower result reducing either record.
- [ ] The hub Lab Score equals the sum of the four best normalized contributions, treats unplayed games as zero and never exceeds `4,000`.
- [ ] Impossible Lab Run accepts one result from each game in canonical order, ignores out-of-order or duplicate completions and never exceeds `4,000`.
- [ ] The Run Score uses only the four results achieved in the current circuit; restarting or clearing it preserves all personal game records and the persistent Lab Score.
- [ ] Device-local progress contains no account or visitor identifier, survives navigation and reloads, can be reset by the player and fails gracefully when browser storage is unavailable.
- [ ] The result card states that normalization applies to game performance only and never compares environmental results between episodes.
- [ ] Every completed game retains a subject and LCA debrief using only approved registry fields and canonical episode links.
- [ ] Homepage and global `Lab` navigation lead to `impossible-lab.html`; sitemap, RSS discovery and telemetry include the hub, Run and all four game routes.
- [ ] Failure and no-JavaScript states retain access to the Archive.
- [ ] Desktop and mobile layouts have no unintended horizontal overflow.

{README_END}'''
    pattern = rf"{re.escape(README_START)}.*?{re.escape(README_END)}"
    if re.search(pattern, text, flags=re.S):
        updated = re.sub(pattern, section, text, flags=re.S)
    else:
        updated = text.rstrip() + "\n\n---\n\n" + section + "\n"
    write_if_changed(path, updated, check, changed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed: list[Path] = []

    update_home(args.check, changed)
    update_lab_metadata(args.check, changed)
    update_game_assets(args.check, changed)
    update_sitemap(args.check, changed)
    update_readme(args.check, changed)

    if changed:
        verb = "would update" if args.check else "updated"
        for path in changed:
            print(f"Impossible Lab {verb}: {path.relative_to(ROOT)}")
        return 1 if args.check else 0
    print("Impossible Lab is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
