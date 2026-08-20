#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPISODES = ROOT / "episodes.json"
COLLECTIONS = ROOT / "collections.json"

entry = {
    "number": 48,
    "slug": "yggdrasil",
    "title": "Yggdrasil",
    "url": "episodes/yggdrasil.html",
    "cover": "assets/images/episodes/ep48-yggdrasil-cover.png",
    "categoryLabel": "Mythic Structure",
    "categories": ["mythology", "structures"],
    "lcaLabel": "Materials-driven",
    "lcaCharacteristics": ["materials-driven", "proxy-sensitive"],
    "result": "797 t CO₂e",
    "hotspot": "The ash-like wood body contributes 441.5 t CO₂e, or 55.4% of the baseline footprint.",
    "featuredDescription": "Yggdrasil reconstructed as one monumental ash-tree analogue installed and maintained for one narrative year: 797 t CO₂e, with the ash-like wood body contributing 55.4% while metal supports and road freight form the next major burdens.",
    "functionalUnit": "One installed world-tree analogue maintained for one narrative year.",
    "evidence": {
        "confidence": "Medium",
        "proxyDependence": "High",
        "assumptionSensitivity": "High",
        "basis": "The approved episode constrains Yggdrasil as a mythic Norse world-tree reconstruction and models it as a terrestrial monumental ash-tree analogue. The physical model uses a 90 m height, 6.0 m trunk diameter, 45% void fraction and 1,638 t ash-like body plus metal supports, concrete anchors, compost and first-year services. DEFRA 2026 factors are used for the disclosed physical flows; tree size, hollow fraction, water and assembly energy are engineering assumptions, while ash density and water-use behaviour are literature-supported physical proxies.",
        "uncertainty": "Physical scale and the wood emission factor materially control interpretation. The height sensitivity spans 624–971 t CO₂e, while the wood-factor sensitivity spans 356–1,018 t CO₂e with all other activities held fixed."
    },
    "keywords": [
        "yggdrasil", "world tree", "ash tree", "norse mythology", "monumental tree",
        "wood", "metal supports", "concrete anchors", "irrigation", "road freight",
        "DEFRA 2026", "materials", "proxy", "sensitivity"
    ],
    "related": [53, 36, 49]
}

registry = json.loads(EPISODES.read_text(encoding="utf-8"))
registry["schemaVersion"] = 2
registry["episodes"] = [ep for ep in registry.get("episodes", []) if ep.get("number") != 48]
registry["episodes"].append(entry)
registry["episodes"].sort(key=lambda ep: ep["number"], reverse=True)
for ep in registry["episodes"]:
    ep.pop("pdf", None)
EPISODES.write_text(json.dumps(registry, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

collections = json.loads(COLLECTIONS.read_text(encoding="utf-8"))
for collection in collections.get("collections", []):
    if collection.get("slug") == "impossible-structures":
        numbers = [n for n in collection.get("episodes", []) if n != 48]
        collection["episodes"] = [48] + numbers
        break
else:
    raise SystemExit("Required collection 'impossible-structures' not found")
COLLECTIONS.write_text(json.dumps(collections, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Episode 48 registry and collection membership synchronized.")
