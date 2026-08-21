#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "episodes.json"
COLLECTIONS = ROOT / "collections.json"
COVER = ROOT / "assets/images/episodes/ep32-pegasus-cover.png"

EPISODE = {
    "number": 32,
    "slug": "pegasus",
    "title": "Pegasus",
    "url": "episodes/pegasus.html",
    "cover": "assets/images/episodes/ep32-pegasus-cover.png",
    "categoryLabel": "Myth & Legend",
    "categories": ["mythology", "legends"],
    "lcaLabel": "Operation-driven",
    "lcaCharacteristics": ["operation-driven", "proxy-sensitive"],
    "result": "5.51 kg CO₂e",
    "hotspot": "Feed contributes 2.68 kg CO₂e, or 48.6% of the baseline footprint.",
    "featuredDescription": "One 300 km Pegasus courier flight reconstructed as a one-day mounted airborne service: 5.51 kg CO₂e per mission, with feed at 48.6% and agricultural factor choice shifting the result from 4.46 to 7.86 kg CO₂e.",
    "functionalUnit": "One 300 km courier flight carrying one rider and one sealed message.",
    "evidence": {
        "confidence": "Medium",
        "proxyDependence": "High",
        "assumptionSensitivity": "High",
        "basis": "The approved episode fixes one 650 kg canonical horse body, a ~9 m wingspan proxy, one 300 km direct courier route and one Pegasus service day. The inventory models feed, biological emissions, stable energy, water, tack wear and feed delivery; DEFRA 2026 is used where representative while feed and horse biology use explicitly declared external proxies.",
        "uncertainty": "Body-mass scaling moves the result from 4.80 to 6.57 kg CO₂e across 550–800 kg, while feed-factor choices move it from 4.46 to 7.86 kg CO₂e; the episode identifies agricultural data quality as the stronger sensitivity."
    },
    "keywords": [
        "pegasus", "winged horse", "courier flight", "horse", "feed", "hay", "oats",
        "enteric methane", "manure", "stable electricity", "water", "tack", "feed freight",
        "DEFRA 2026", "IPCC proxy", "CarbonCloud", "body mass sensitivity", "feed factor sensitivity",
        "mythology", "operation-driven", "proxy-sensitive"
    ],
    "related": [54, 52, 44]
}

COLLECTION = {
    "slug": "impossible-flight",
    "title": "Impossible Flight",
    "eyebrow": "WINGS, COURIERS & AIRBORNE SYSTEMS",
    "description": "Cases where mythical flight is translated into physical bodies, wearable systems or airborne service models, making support materials, feeding and proxy choices visible even when magic itself carries no fuel burden.",
    "episodes": [54, 52, 44, 32]
}


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if not COVER.is_file():
        raise SystemExit(f"Approved cover is missing: {COVER.relative_to(ROOT)}")

    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    episodes = data.get("episodes", [])
    episodes = [ep for ep in episodes if ep.get("number") != 32]
    episodes.append(EPISODE)
    episodes.sort(key=lambda ep: ep["number"], reverse=True)
    data["episodes"] = episodes
    write_json(REGISTRY, data)

    cdata = json.loads(COLLECTIONS.read_text(encoding="utf-8"))
    collections = cdata.get("collections", [])
    collections = [c for c in collections if c.get("slug") != COLLECTION["slug"]]
    collections.append(COLLECTION)
    cdata["collections"] = collections
    write_json(COLLECTIONS, cdata)

    print("Episode #32 Pegasus registry and collection metadata synchronized.")


if __name__ == "__main__":
    main()
