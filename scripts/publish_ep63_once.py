#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPLOADED_COVER = ROOT / "assets/images/episodes/file_00000000a5f481f4b8d4e1adeb1c66d2.png"
COVER = ROOT / "assets/images/episodes/ep63-gungnir-cover.png"
EXPECTED_SHA256 = "6c0b37dfb93204ab4cbc37971207d89b15e67b67bca824bf55b4beef9c74b648"

EPISODE = {
    "number": 63,
    "slug": "gungnir",
    "title": "Gungnir",
    "url": "episodes/gungnir.html",
    "cover": "assets/images/episodes/ep63-gungnir-cover.png",
    "categoryLabel": "Myth & Legend",
    "categories": ["mythology", "legends"],
    "lcaLabel": "Energy-driven",
    "lcaCharacteristics": ["energy-driven", "process-energy-driven", "proxy-sensitive"],
    "result": "3.01 kg CO₂e",
    "hotspot": "Forge heat contributes 51.8% of the approved baseline footprint, more than the iron head at 30.6%.",
    "featuredDescription": "One 2.40 m Gungnir-class spear, manufactured and delivered once: 3.01 kg CO₂e, with forge heat contributing 51.8% and the iron head 30.6% of the approved baseline.",
    "functionalUnit": "Provide one durable Gungnir-class spear, delivered ready for repeated ceremonial and combat use. The model covers one manufacturing-and-delivery event; use and end-of-life remain outside the boundary.",
    "evidence": {
        "confidence": "Medium",
        "proxyDependence": "High",
        "assumptionSensitivity": "High",
        "basis": "The approved episode freezes a 2.40 m, 1.30 kg Gungnir-class spear before inventory, with a 0.370 m / 0.322 kg iron head anchored to British Museum object 1868,0128.2 and a 0.976 kg European ash shaft reconstructed from geometry and density. The five contributing flows use declared 2026 UK Government GHG factor families for a primary ferrous-material proxy, primary wood, propane plus WTT, UK electricity plus T&D and WTT, and average HGV freight plus WTT.",
        "uncertainty": "The 6 kWh forge-heat demand is an engineering assumption and the 500 km delivery distance is a narrative proxy. The published forge-heat sensitivity moves the total from 2.23 to 4.57 kg CO₂e, while the ferrous-material factor sensitivity spans 2.68 to 3.32 kg CO₂e; the heat-demand assumption is the larger uncertainty lever."
    },
    "keywords": [
        "Gungnir",
        "Odin",
        "spear",
        "Norse mythology",
        "Viking spear",
        "iron spearhead",
        "ash shaft",
        "forge heat",
        "propane",
        "road freight",
        "British Museum 1868,0128.2",
        "DEFRA 2026",
        "energy-driven",
        "process-energy-driven",
        "proxy sensitivity"
    ],
    "related": [41, 37, 47]
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_exact_cover() -> None:
    if COVER.exists():
        digest = sha256(COVER)
        if digest != EXPECTED_SHA256:
            raise SystemExit(f"Approved-cover identity failure at canonical path: expected {EXPECTED_SHA256}, got {digest}")
        if UPLOADED_COVER.exists():
            if sha256(UPLOADED_COVER) != EXPECTED_SHA256:
                raise SystemExit("Unexpected non-approved upload remains beside canonical cover")
            UPLOADED_COVER.unlink()
        return

    if not UPLOADED_COVER.exists():
        raise SystemExit(f"Missing exact approved uploaded cover: {UPLOADED_COVER.relative_to(ROOT)}")

    uploaded_digest = sha256(UPLOADED_COVER)
    if uploaded_digest != EXPECTED_SHA256:
        raise SystemExit(f"Approved-cover identity failure: expected {EXPECTED_SHA256}, got {uploaded_digest}")

    # Byte-preserving filesystem rename: no decoding, re-encoding, recompression or image modification.
    UPLOADED_COVER.replace(COVER)
    canonical_digest = sha256(COVER)
    if canonical_digest != EXPECTED_SHA256:
        raise SystemExit(f"Canonical cover changed during rename: expected {EXPECTED_SHA256}, got {canonical_digest}")


def update_registry() -> None:
    path = ROOT / "episodes.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    episodes = [e for e in data.get("episodes", []) if e.get("number") != 63]
    existing_numbers = {e.get("number") for e in episodes}
    missing_related = [n for n in EPISODE["related"] if n not in existing_numbers]
    if missing_related:
        raise SystemExit(f"Related episode(s) missing from registry: {missing_related}")
    episodes.append(EPISODE)
    episodes.sort(key=lambda e: int(e.get("number", -1)), reverse=True)
    data["episodes"] = episodes
    for e in episodes:
        if "pdf" in e:
            raise SystemExit(f"Prohibited pdf field detected in episode #{e.get('number')}")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_collections() -> None:
    path = ROOT / "collections.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    found = False
    for collection in data.get("collections", []):
        if collection.get("slug") == "legendary-engineering":
            nums = [n for n in collection.get("episodes", []) if n != 63]
            collection["episodes"] = [63] + nums
            found = True
    if not found:
        raise SystemExit("legendary-engineering collection not found")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    require_exact_cover()
    update_registry()
    update_collections()
    print("Episode #63 registry and collection integration prepared with exact approved cover verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
