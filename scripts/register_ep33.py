#!/usr/bin/env python3
"""Idempotently register Episode #33 (Brahmastra) from its approved source episode."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
EPISODES_PATH = ROOT / "episodes.json"
COLLECTIONS_PATH = ROOT / "collections.json"

EP33 = {
    "number": 33,
    "slug": "brahmastra",
    "title": "Brahmastra",
    "url": "episodes/brahmastra.html",
    "cover": "assets/images/episodes/ep33-brahmastra-cover.png",
    "categoryLabel": "Myth & Legend",
    "categories": ["mythology", "legends"],
    "lcaLabel": "Materials-driven",
    "lcaCharacteristics": ["materials-driven", "proxy-sensitive"],
    "result": "82.9 kg CO₂e",
    "hotspot": "Primary metals contribute 76.44 kg CO₂e, or 92.2% of the baseline footprint.",
    "featuredDescription": "One non-functional 2.40 m Brahmastra-inspired ceremonial relic reconstructed as a 22.45 kg delivered artifact: 82.9 kg CO₂e, with primary metals contributing 92.2% and metal-factor selection moving the model from 39.2 to 108.7 kg CO₂e.",
    "functionalUnit": "One non-functional Brahmastra-inspired ceremonial astral relic, 2.40 m long, delivered ready for one display/ritual use.",
    "evidence": {
        "confidence": "Low",
        "proxyDependence": "High",
        "assumptionSensitivity": "High",
        "basis": "The episode constrains the service to one non-functional ceremonial Brahmastra-inspired relic and explicitly states that mythic texts provide no measurable geometry or material specification. The physical model is therefore a modern engineering reconstruction: 2.40 m overall length, 22.45 kg reference mass, 20.00 kg primary metals, hardwood stabilizers and a glass/mineral ornament proxy, using the episode's DEFRA 2026 factor basis.",
        "uncertainty": "Wall thickness moves the result from 68.2 to 97.2 kg CO₂e, while metal-factor selection moves the same mass and boundary from 39.2 to 108.7 kg CO₂e; the episode identifies proxy/model uncertainty as the larger interpretive lever."
    },
    "keywords": [
        "brahmastra",
        "astral relic",
        "ceremonial relic",
        "primary metals",
        "mixed metal",
        "hardwood",
        "glass mineral proxy",
        "DEFRA 2026",
        "wall thickness",
        "metal emission factor",
        "proxy sensitivity",
        "mythology",
        "materials-driven",
        "road freight"
    ],
    "related": [37, 41, 44],
    "coverAspectPolicy": "approved-native"
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_episodes():
    data = load(EPISODES_PATH)
    episodes = data.get("episodes", [])
    existing = [ep for ep in episodes if ep.get("number") == 33]
    if existing:
        if existing[0] != EP33:
            raise SystemExit("Episode #33 already exists with different registry data; refusing silent overwrite.")
        return False
    episodes.append(EP33)
    episodes.sort(key=lambda ep: ep.get("number", -1), reverse=True)
    data["episodes"] = episodes
    dump(EPISODES_PATH, data)
    return True


def update_collections():
    data = load(COLLECTIONS_PATH)
    changed = False
    for collection in data.get("collections", []):
        if collection.get("slug") == "legendary-engineering":
            members = collection.setdefault("episodes", [])
            if 33 not in members:
                members.append(33)
                changed = True
            break
    else:
        raise SystemExit("legendary-engineering collection not found")
    if changed:
        dump(COLLECTIONS_PATH, data)
    return changed


if __name__ == "__main__":
    e = update_episodes()
    c = update_collections()
    print(f"Episode #33 registry updated={e}; collections updated={c}")
