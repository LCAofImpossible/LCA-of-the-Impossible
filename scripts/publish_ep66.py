#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPISODES = ROOT / 'episodes.json'
COLLECTIONS = ROOT / 'collections.json'

ENTRY = {
    'number': 66,
    'slug': 'cornucopia',
    'title': 'The Cornucopia',
    'url': 'episodes/cornucopia.html',
    'cover': 'assets/images/episodes/ep66-cornucopia-cover.png',
    'coverAspectPolicy': 'approved-native',
    'categoryLabel': 'Myth & Legend',
    'categories': ['mythology', 'legends'],
    'lcaLabel': 'Materials-driven',
    'lcaCharacteristics': ['materials-driven', 'mass-sensitive', 'proxy-sensitive'],
    'result': '3.74 t CO₂e',
    'hotspot': 'Food production contributes 99.1% of the approved baseline; food-waste treatment contributes 0.9%, while vessel, utilities and delivery together remain below 0.01%.',
    'featuredDescription': 'One 24-hour Cornucopia service presenting 1.00 t of mixed food: 3.74 t CO₂e, with food production contributing 99.1% while vessel, utilities and delivery remain below 0.01%.',
    'functionalUnit': 'One 24-hour cornucopia service presenting 1,000 kg of mixed food at the point of use, including treatment of 5% residual food waste.',
    'evidence': {
        'confidence': 'Low',
        'proxyDependence': 'High',
        'assumptionSensitivity': 'High',
        'basis': 'The approved episode defines one 24-hour cornucopia service at the Achelous sanctuary presenting 1.00 t of mixed food and treating 50 kg of residual food waste. It reconstructs a 1.20 m curved horn with a 0.48 m mouth, 8 mm wall, 11.7 kg shell and 13.5 kg total mass, allocated across 100 uses. The broken horn enters at zero burden; bronze, workshop electricity, water, road freight and residual treatment use the episode\'s declared UK Government 2026 factor families. The food-and-drink factor is explicitly a generic material-use proxy, not a product-specific agricultural LCA.',
        'uncertainty': 'The magical mechanism has no assigned flow and is explicitly treated as uncertainty rather than zero impact. The published physical sensitivity moves the result from 1.87 to 7.47 t CO₂e as output changes from 0.50 to 2.00 t, while the published menu-composition cases span 1.11 to 13.4 t CO₂e per service at the same one-tonne output.'
    },
    'keywords': [
        'Cornucopia', 'horn of plenty', 'Achelous', 'mixed food and drink',
        'food production', 'food waste', 'landfill', 'broken horn', 'bronze bands',
        'workshop electricity', 'water supply', 'road freight', 'DEFRA 2026',
        'UK Government 2026', 'materials-driven', 'mass sensitivity',
        'menu composition', 'proxy sensitivity', 'abundance'
    ],
    'related': [62, 60, 64]
}


def patch_episodes() -> None:
    data = json.loads(EPISODES.read_text(encoding='utf-8'))
    episodes = data.setdefault('episodes', [])
    existing = [ep for ep in episodes if ep.get('number') == 66 or ep.get('slug') == 'cornucopia']
    if existing:
        if existing[0] != ENTRY:
            raise SystemExit('Episode #66 already exists but does not match the controlled publication entry.')
        return
    episodes.insert(0, ENTRY)
    EPISODES.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def patch_collections() -> None:
    data = json.loads(COLLECTIONS.read_text(encoding='utf-8'))
    collections = data.get('collections', [])
    target = next((c for c in collections if c.get('slug') == 'systems-that-never-stop'), None)
    if target is None:
        raise SystemExit('Required collection systems-that-never-stop not found.')
    nums = target.setdefault('episodes', [])
    if 66 not in nums:
        nums.insert(0, 66)
    COLLECTIONS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    patch_episodes()
    patch_collections()
    print('Episode #66 registry and collection patch applied.')
