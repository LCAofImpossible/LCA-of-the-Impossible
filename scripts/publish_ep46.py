import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]

import base64
import hashlib

cover_parts = sorted((root / "scripts").glob(".ep46-cover.part*"))
if cover_parts:
    encoded = "".join(part.read_text(encoding="ascii") for part in cover_parts)
    cover_bytes = base64.b64decode(encoded.encode("ascii"), validate=True)
    digest = hashlib.sha256(cover_bytes).hexdigest()
    expected = "97192d9ffff4b3f5da9653e53877afb5c48ab15eb1b14a706108ea18fbf85928"
    if digest != expected:
        raise SystemExit(f"Approved cover hash mismatch: {digest}")
    cover_path = root / "assets" / "images" / "episodes" / "ep46-nautilus-cover.png"
    cover_path.parent.mkdir(parents=True, exist_ok=True)
    cover_path.write_bytes(cover_bytes)
    print(f"Approved cover reconstructed byte-for-byte: {digest}")
elif not (root / "assets" / "images" / "episodes" / "ep46-nautilus-cover.png").exists():
    raise SystemExit("Approved Episode 46 cover is missing and no transfer chunks are available.")

registry_path = root / "episodes.json"
collections_path = root / "collections.json"

entry = {
    "number": 46,
    "slug": "nautilus",
    "title": "Nautilus",
    "url": "episodes/nautilus.html",
    "cover": "assets/images/episodes/ep46-nautilus-cover.png",
    "coverAspectPolicy": "approved-native",
    "categoryLabel": "Science Fiction",
    "categories": ["science-fiction"],
    "lcaLabel": "Materials-driven",
    "lcaCharacteristics": ["materials-driven", "proxy-sensitive"],
    "result": "4.69 kt CO₂e",
    "hotspot": "Machinery metals contribute 2,599 t CO₂e (55.5%); hull, machinery and battery together represent 91.5% of the baseline footprint.",
    "featuredDescription": "Captain Nemo’s 70 m Nautilus reconstructed cradle-to-launch: 4.69 kt CO₂e before the voyage begins, with hull, machinery and battery blocks contributing 91.5% of the baseline and material origin controlling the main sensitivity.",
    "functionalUnit": "One launch-ready Nautilus, 70 m long and 8 m wide, at the first ocean-trial condition; cradle-to-launch construction only.",
    "evidence": {
        "confidence": "Medium",
        "proxyDependence": "High",
        "assumptionSensitivity": "High",
        "basis": "Verne supplies the 70 m × 8 m geometry and 1,356.48 t dry displacement used by the approved episode. The reconstruction translates that narrative vessel into a modern cradle-to-launch inventory of primary metals, electric storage, interiors, shipyard energy, auxiliary marine gas oil and component freight using declared DEFRA 2026 proxies.",
        "uncertainty": "The unknown allocation inside the residual 961.52 t materially affects the result: the mass sensitivity spans 4.04–5.54 kt CO₂e. Material origin is also decisive, with the approved routes spanning 2.63–5.76 kt CO₂e."
    },
    "keywords": [
        "nautilus", "captain nemo", "twenty thousand leagues under the seas", "submarine", "steel", "machinery metals", "battery stack", "shipyard electricity", "marine gas oil", "sea freight", "road freight", "DEFRA 2026", "cradle-to-launch", "materials-driven", "science fiction"
    ],
    "related": [49, 42, 35]
}

registry = json.loads(registry_path.read_text(encoding="utf-8"))
episodes = registry.get("episodes", [])
existing = [ep for ep in episodes if ep.get("number") == 46]
if existing:
    episodes = [entry if ep.get("number") == 46 else ep for ep in episodes]
else:
    episodes.append(entry)
episodes.sort(key=lambda ep: ep.get("number", -1), reverse=True)
registry["schemaVersion"] = 2
registry["episodes"] = episodes
registry_path.write_text(json.dumps(registry, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

collections = json.loads(collections_path.read_text(encoding="utf-8"))
for collection in collections.get("collections", []):
    if collection.get("slug") == "legendary-engineering":
        nums = [n for n in collection.get("episodes", []) if n != 46]
        nums.append(46)
        collection["episodes"] = sorted(nums, reverse=True)
collections_path.write_text(json.dumps(collections, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Episode 46 registry and collection integration complete.")
