#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPISODES = ROOT / 'episodes.json'
COLLECTIONS = ROOT / 'collections.json'

ENTRY = {
    'number': 67,
    'slug': 'augean-stables',
    'title': 'The Augean Stables',
    'url': 'episodes/augean-stables.html',
    'cover': 'assets/images/episodes/ep67-augean-stables-cover.png',
    'coverAspectPolicy': 'approved-native',
    'categoryLabel': 'Myth & Legend',
    'categories': ['mythology', 'legends', 'structures'],
    'lcaLabel': 'Operation-driven',
    'lcaCharacteristics': ['operation-driven', 'process-energy-driven', 'proxy-sensitive'],
    'result': '181 t CO₂e',
    'hotspot': 'Earthmoving fuel contributes 71.7% of the approved baseline; materials contribute 18.1% and equipment mobilization 10.2%.',
    'featuredDescription': 'One complete river-assisted clearing campaign at Elis: 181 t CO₂e, with earthmoving fuel contributing 71.7% of the approved baseline while gravity-fed river water carries no pumping burden in the model.',
    'functionalUnit': 'One complete river-assisted clearing campaign removing the modelled inherited stock and returning the yard, temporary channels and ordinary river courses to serviceable condition within one daylight period at Elis, including an 8-hour wash.',
    'evidence': {
        'confidence': 'Low',
        'proxyDependence': 'High',
        'assumptionSensitivity': 'High',
        'basis': 'The approved episode freezes a 300 × 120 m stable plan, 2.20 m waste depth, 79,200 m³ inherited stock, 51,480 t wet mass and 52,500 m³ of campaign earthworks. The model includes temporary intake and outlet channels, earthmoving and site restoration, timber gates and metal fittings, foundation breach and repair, equipment mobilization and fuel. The two rivers pass 100 m³/s for eight hours without pumping. Six emitting flows use the episode’s declared 2026 UK Government factors or material-use proxies.',
        'uncertainty': 'Channel geometry and fuel pathway are the published sensitivity levers. Changing only earthwork volume moves the result from 148 to 220 t CO₂e, while changing the 40,550 L fuel pathway moves it from 75.5 t CO₂e with HVO to 184 t CO₂e with 100% mineral diesel. Greece-specific non-road factors were unavailable, so UK 2026 factors are applied transparently outside their native reporting context.'
    },
    'keywords': [
        'Augean Stables', 'Augeas', 'Heracles', 'Hercules', 'Elis',
        'river diversion', 'earthworks', 'earthmoving diesel', 'sluice gates',
        'cypress gatework', 'equipment mobilization', 'concrete repair',
        'aggregates', 'river water', 'on-site soil reuse', 'DEFRA 2026',
        'UK Government 2026', 'operation-driven', 'process-energy-driven',
        'channel volume', 'HVO sensitivity'
    ],
    'related': [43, 40, 64]
}

def patch_episodes() -> None:
    data = json.loads(EPISODES.read_text(encoding='utf-8'))
    episodes = data.setdefault('episodes', [])
    existing = [ep for ep in episodes if ep.get('number') == 67 or ep.get('slug') == 'augean-stables']
    if existing:
        if existing[0] != ENTRY:
            raise SystemExit('Episode #67 already exists but does not match the controlled publication entry.')
        return
    episodes.insert(0, ENTRY)
    EPISODES.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def patch_collections() -> None:
    data = json.loads(COLLECTIONS.read_text(encoding='utf-8'))
    collections = data.get('collections', [])
    required = ['impossible-structures', 'legendary-engineering']
    for slug in required:
        target = next((c for c in collections if c.get('slug') == slug), None)
        if target is None:
            raise SystemExit(f'Required collection {slug} not found.')
        nums = target.setdefault('episodes', [])
        if 67 not in nums:
            nums.insert(0, 67)
    COLLECTIONS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    patch_episodes()
    patch_collections()
    print('Episode #67 registry and collection patch applied.')
