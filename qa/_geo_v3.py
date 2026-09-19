"""V3 geometry audit: first checkpoint vs first pit, challenge entry heights, level rhythm."""
import json
from pathlib import Path

V3 = Path(r'E:\Desktop\BubuYier_V3\public\assets\maps')
LEVELS = ['level_01_commute', 'level_02_park', 'level_03_starlight']

for lv in LEVELS:
    m = json.load(open(V3 / f'{lv}.json', encoding='utf-8'))
    layers = {l['name']: l for l in m['layers']}
    terr, W = layers['terrain']['data'], layers['terrain']['width']
    tops = []
    for col in range(W):
        rows = [r for r in range(16) if terr[r * W + col]]
        tops.append(min(rows) * 48 if rows else None)
    pits = []
    start = None
    for i, t in enumerate(tops):
        if t is None and start is None: start = i
        if t is not None and start is not None:
            pits.append((start * 48, (i) * 48)); start = None
    if start is not None: pits.append((start * 48, 9216))
    cps = [(o['name'], round(o['x']), round(o['y'])) for o in layers['checkpoints']['objects']]
    trg = [(o['name'], o['x'], o.get('width', 0)) for o in layers['challengeTriggers']['objects']]
    props = {o['name']: {p['name']: p['value'] for p in o.get('properties', [])} for o in layers['challengeTriggers']['objects']}
    # entry platform top per challenge
    entrytops = {}
    for o in layers['platforms']['objects']:
        if o['name'].endswith('-entry'):
            entrytops[o['name']] = (round(o['x']), round(o['y']), round(o.get('height', 20)), o.get('width'))
    for o in layers.get('movingPlatforms', {}).get('objects', []):
        if o['name'].endswith('-entry'):
            entrytops[o['name']] = (round(o['x']), round(o['y']), round(o.get('height', 20)), o.get('width'))
    print('=' * 90)
    print(lv)
    print('  pits (x-range):', pits)
    print('  checkpoints   :', cps)
    first_cp = min(c[1] for c in cps)
    first_pit = min([p[0] for p in pits], default=None)
    print(f'  first checkpoint x={first_cp}   first pit x={first_pit}   -> checkpoint before pit: {first_pit is None or first_cp < first_pit}')
    for name, x, w in trg:
        p = props[name]
        print(f"  {name}: entryX={p.get('entryX')} entryY={p.get('entryY')} triggerY={round([o['y'] for o in layers['challengeTriggers']['objects'] if o['name']==name][0])} "
              f"limit={p.get('timeLimitMs')} failOnGround={p.get('failOnGround')}")
    print('  entry platforms:', entrytops)
    # rhythm metrics: terrain step sizes along the main route
    steps = []
    for i in range(1, len(tops)):
        a, b = tops[i - 1], tops[i]
        if a is None or b is None: continue
        if a != b: steps.append((i * 48, b - a))
    ups = [s for s in steps if s[1] < 0]
    downs = [s for s in steps if s[1] > 0]
    print(f'  terrain changes: {len(steps)}  climbs={len(ups)} maxclimb={min([s[1] for s in ups], default=0)}  drops={len(downs)} maxdrop={max([s[1] for s in downs], default=0)}')
    heights = sorted({t for t in tops if t is not None})
    print('  distinct terrain heights (y):', heights)
