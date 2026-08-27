#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_VERSION = "20260820-telemetry1"
START = "<!-- TELEMETRY-RULES:START -->"
END = "<!-- TELEMETRY-RULES:END -->"
ROOT_PAGES = [
    "index.html", "archive.html", "compare.html", "explore.html", "collections.html",
    "method.html", "sources.html", "about.html", "glossary.html", "season-i.html", "season-ii.html",
]


def write_if_changed(path: Path, content: str, check: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8")
    if current == content:
        return
    changed.append(path)
    if not check:
        path.write_text(content, encoding="utf-8")


def ensure_assets(path: Path, prefix: str, check: bool, changed: list[Path]) -> None:
    text = path.read_text(encoding="utf-8")
    css = f'{prefix}assets/telemetry.css?v={ASSET_VERSION}'
    js = f'{prefix}assets/telemetry.js?v={ASSET_VERSION}'

    css_pattern = r'<link\s+rel="stylesheet"\s+href="[^\"]*assets/telemetry\.css(?:\?v=[^\"]*)?">'
    if re.search(css_pattern, text):
        updated = re.sub(css_pattern, f'<link rel="stylesheet" href="{css}">', text)
    else:
        pos = text.find('</head>')
        if pos == -1:
            raise RuntimeError(f"Missing </head> in {path}")
        updated = text[:pos] + f'  <link rel="stylesheet" href="{css}">\n' + text[pos:]

    js_pattern = r'<script\s+src="[^\"]*assets/telemetry\.js(?:\?v=[^\"]*)?"></script>'
    if re.search(js_pattern, updated):
        updated = re.sub(js_pattern, f'<script src="{js}"></script>', updated)
    else:
        pos = updated.rfind('</body>')
        if pos == -1:
            raise RuntimeError(f"Missing </body> in {path}")
        updated = updated[:pos] + f'  <script src="{js}"></script>\n' + updated[pos:]

    write_if_changed(path, updated, check, changed)


def update_readme(check: bool, changed: list[Path]) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    block = f'''{START}

## 31. Visitor telemetry — mandatory

The public site includes a lightweight visitor counter presented as technical telemetry rather than as a decorative hit counter.

### 31.1 Canonical implementation

Canonical files:

- `assets/telemetry.js` — privacy-light counter client and rendering logic;
- `assets/telemetry.css` — visual integration with the existing dark technical system;
- `scripts/telemetry_sync.py` — deterministic asset propagation and README synchronization;
- `scripts/telemetry_qa.py` — integration and privacy guardrails.

All public root pages and all published episode pages load the versioned telemetry CSS and JavaScript. `episodes/template.html` remains free of live tracking; newly instantiated episode pages receive telemetry through synchronization.

### 31.2 Counter semantics

Telemetry uses the public CounterAPI endpoint under the fixed namespace `lcaofimpossible.github.io` and requests `unique=true` so the displayed values represent provider-filtered unique visitors rather than raw pageview events.

Two counters are maintained:

1. `site-total` — shared across all public pages and displayed in the site footer as `SITE TELEMETRY`;
2. `episode-NN` — one counter per published episode, displayed adjacent to the Model Passport as `CASE TELEMETRY`.

Counts begin from telemetry activation. Do not invent, estimate or backfill historical traffic unless an independently verified legacy count is explicitly supplied.

### 31.3 Privacy and dependency rules

The integration must not use cookies, `localStorage`, `sessionStorage`, fingerprinting code or persistent identifiers implemented by this site. Requests use `credentials: omit` and `referrerPolicy: no-referrer`. No third-party JavaScript library is loaded: the site calls the counter API directly.

Counter failure must never block page rendering. When telemetry cannot be reached, the UI falls back to `LIVE ONLY` rather than presenting a fabricated zero.

The telemetry provider may be replaced in future, but the visible contract — site total in the footer, case total beside the Passport, no intrusive tracking — should remain stable unless explicitly changed.

### 31.4 Visual rules

Telemetry is deliberately subordinate to episode content:

- compact uppercase technical labels;
- restrained gold for the telemetry code and light cyan for the number;
- no animation, badge branding, oversized numerals or gamified treatment;
- responsive wrapping on mobile;
- semantic text remains accessible to assistive technology.

### Visitor telemetry QA

- [ ] Every public root page loads current versioned telemetry CSS and JavaScript.
- [ ] Every published episode loads current versioned telemetry CSS and JavaScript.
- [ ] The site-wide counter uses the `site-total` key.
- [ ] Episode counters use the `episode-NN` key derived from `data-episode`.
- [ ] Counter requests use `unique=true`, `credentials: omit` and `referrerPolicy: no-referrer`.
- [ ] The telemetry client contains no cookie, localStorage or sessionStorage logic.
- [ ] Counter failure falls back without blocking or altering analytical content.
- [ ] `episodes/template.html` is not directly tracked.

{END}'''
    pattern = rf"{re.escape(START)}.*?{re.escape(END)}"
    if re.search(pattern, text, flags=re.S):
        updated = re.sub(pattern, block, text, flags=re.S)
    else:
        updated = text.rstrip() + "\n\n---\n\n" + block + "\n"
    write_if_changed(path, updated, check, changed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed: list[Path] = []

    for name in ROOT_PAGES:
        ensure_assets(ROOT / name, "", args.check, changed)
    for path in sorted((ROOT / "episodes").glob("*.html")):
        if path.name == "template.html":
            continue
        ensure_assets(path, "../", args.check, changed)

    update_readme(args.check, changed)

    if changed:
        for path in changed:
            print(f"Telemetry {'would update' if args.check else 'updated'}: {path.relative_to(ROOT)}")
        return 1 if args.check else 0
    print("Visitor telemetry is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
