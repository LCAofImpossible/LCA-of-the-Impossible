#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EPISODE = {
    "number": 52,
    "slug": "hermes-sandals",
    "title": "Hermes Sandals",
    "url": "episodes/hermes-sandals.html",
    "cover": "assets/images/episodes/ep52-hermes-sandals-cover.png",
    "categoryLabel": "Myth & Legend",
    "categories": ["mythology", "legends"],
    "lcaLabel": "Materials-driven",
    "lcaCharacteristics": ["materials-driven", "proxy-sensitive"],
    "result": "63.5 kg CO₂e",
    "hotspot": "Gold leaf contributes 80.2% of the baseline with only 0.3% of product mass.",
    "featuredDescription": "One 0.682 kg pair of winged talaria reconstructed as engineered footwear: 63.5 kg CO₂e cradle-to-delivered-gate, with two grams of gold leaf driving 80.2% of the footprint.",
    "functionalUnit": "One pair of winged talaria enabling one courier mission.",
    "evidence": {
        "confidence": "Medium",
        "proxyDependence": "High",
        "assumptionSensitivity": "High",
        "basis": "The Greek myth constrains the winged courier footwear. The approved episode reconstructs one 0.682 kg pair with leather, bronze/brass wing frames, feather/textile vanes, a 2.0 g gold-leaf finish, workshop utilities, packaging and road/sea freight, prioritising DEFRA 2026 and declaring an external primary-gold proxy.",
        "uncertainty": "Gold intensity and gilding mass control the baseline: changing gold from 0.5 g to 5.0 g moves the total from 25.3 to 139.9 kg CO₂e. Leather-factor choice is the second material uncertainty, moving the modeled total from 59.3 to 136.0 kg CO₂e."
    },
    "keywords": ["hermes", "talaria", "winged sandals", "gold leaf", "leather", "bronze", "feathers", "courier", "DEFRA 2026", "gilding", "proxy", "mythology"],
    "related": [55, 37, 41],
    "pdf": "assets/pdf/episodes/ep52-hermes-sandals.pdf"
}


def update_registry() -> None:
    path = ROOT / "episodes.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    episodes = [ep for ep in data["episodes"] if ep.get("number") != 52]
    episodes.append(EPISODE)
    episodes.sort(key=lambda ep: ep["number"], reverse=True)
    data["schemaVersion"] = 2
    data["episodes"] = episodes
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def update_collections() -> None:
    path = ROOT / "collections.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    collections = data["collections"]

    for collection in collections:
        if collection.get("slug") == "legendary-engineering":
            members = [n for n in collection["episodes"] if n != 52]
            insert_at = members.index(42) if 42 in members else len(members)
            members.insert(insert_at, 52)
            collection["episodes"] = members

    gilded = {
        "slug": "gilded-hotspots",
        "title": "Gilded Hotspots",
        "eyebrow": "PRECIOUS SURFACES & MATERIAL INTENSITY",
        "description": "Cases where a thin precious-metal surface outweighs much larger material, energy and logistics flows.",
        "episodes": [55, 52]
    }
    collections = [c for c in collections if c.get("slug") != "gilded-hotspots"]
    collections.append(gilded)
    data["collections"] = collections
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    update_registry()
    update_collections()
    print("Episode #52 registry and collections metadata synchronized.")
