#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_VERSION = "20260819-epic-passport1"
START = "<!-- EPIC-PASSPORT-RULES:START -->"
END = "<!-- EPIC-PASSPORT-RULES:END -->"


def write_if_changed(path: Path, content: str, check: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8")
    if current == content:
        return
    changed.append(path)
    if not check:
        path.write_text(content, encoding="utf-8")


def normalize_assets(path: Path, prefix: str, check: bool, changed: list[Path]) -> None:
    text = path.read_text(encoding="utf-8")
    css = f'{prefix}assets/phase6.css?v={ASSET_VERSION}'
    js = f'{prefix}assets/phase6.js?v={ASSET_VERSION}'
    updated = re.sub(
        r'<link\s+rel="stylesheet"\s+href="[^\"]*assets/phase6\.css(?:\?v=[^\"]*)?">',
        f'<link rel="stylesheet" href="{css}">', text,
    )
    updated = re.sub(
        r'<script\s+src="[^\"]*assets/phase6\.js(?:\?v=[^\"]*)?"></script>',
        f'<script src="{js}"></script>', updated,
    )
    write_if_changed(path, updated, check, changed)


def update_readme(check: bool, changed: list[Path]) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    block = f'''{START}

## 30. Epic Model Passport presentation — mandatory

The canonical Model Passport presentation is now the **Epic Passport**. This rule extends Section 29 without changing its data-governance constraints.

Every published episode must expose three Passport actions:

1. `View epic passport →` — opens the full-screen technical dossier;
2. `Print / Save as PDF` — uses the dedicated A4 print layout defined in `assets/phase6.css`;
3. `Raw text ↓` — retained only as a secondary portability/accessibility export.

The Epic Passport uses the registered episode cover and the existing registry fields only. Its visual language is dark technical/blueprint with cyan accents, restrained gold, archive-record identifiers, evidence blocks and a traceability seal. It must feel epic and collectible without weakening methodological readability.

No visual element may introduce an unregistered system boundary, factor list, allocation rule, assumption or numerical value. The Passport remains a transparency summary, not a verification statement, formal data-quality rating or substitute for the approved episode/PDF.

The shared implementation in `assets/phase6.js` and `assets/phase6.css` applies to all currently published and future episode pages. `scripts/epic_passport_sync.py` is responsible for propagating the current versioned Phase 6 assets so browser caching cannot leave older Passport behaviour active after an upgrade.

### Epic Passport QA

- [ ] All episode pages reference the current versioned Phase 6 assets.
- [ ] Full-screen Passport includes registered cover, episode number/title/category/LCA lens and headline result.
- [ ] Reporting basis, hotspot and Evidence Profile remain visible.
- [ ] Evidence basis and main modelling uncertainty remain visible.
- [ ] `Print / Save as PDF` uses the dedicated A4 print stylesheet.
- [ ] `Raw text` is secondary to the visual Passport.
- [ ] Mobile Passport remains readable with no unintended page overflow.

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

    for path in sorted((ROOT / "episodes").glob("*.html")):
        normalize_assets(path, "../", args.check, changed)
    for name in ["explore.html", "method.html"]:
        normalize_assets(ROOT / name, "", args.check, changed)
    update_readme(args.check, changed)

    if changed:
        for path in changed:
            print(f"Epic Passport {'would update' if args.check else 'updated'}: {path.relative_to(ROOT)}")
        return 1 if args.check else 0
    print("Epic Passport is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
