"""V2 vs V3 map comparison: does the geometry / checkpoint rhythm actually differ now?"""
import json
from pathlib import Path

V2 = Path(r'E:\Desktop\BubuYier_V2\public\assets\maps')
V3 = Path(r'E:\Desktop\BubuYier_V3\public\assets\maps')
LEVELS = ['level_01_commute', 'level_02_park', 'level_03_starlight']


def load(root, lv):
    return json.load(open(root / f'{lv}.json', encoding='utf-8'))


def profile(m):
    """terrain top-row per column + key object positions"""
    layers = {l['name']: l for l in m['layers']}
    terr, W = layers['terrain']['data'], layers['terrain']['width']
    tops = []
    for col in range(W):
        rows = [r for r in range(16) if terr[r * W + col]]
        tops.append(min(rows) * 48 if rows else None)
    def names(layer, prop=None):
        return [(o['name'], round(o['x']), round(o['y']), o.get('width', 0)) for o in layers.get(layer, {}).get('objects', [])]
    return tops, names


print('=' * 100)
for lv in LEVELS:
    m2, m3 = load(V2, lv), load(V3, lv)
    t2, t3 = profile(m2)[0], profile(m3)[0]
    diffcols = [i for i in range(len(t2)) if t2[i] != t3[i]]
    print(f'\n### {lv}')
    print(f'  terrain columns differing: {len(diffcols)} / {len(t2)}  ({len(diffcols)/len(t2)*100:.0f}%)')
    if diffcols:
        runs = []
        start = diffcols[0]
        prev = diffcols[0]
        for i in diffcols[1:]:
            if i != prev + 1:
                runs.append((start, prev)); start = i
            prev = i
        runs.append((start, prev))
        print('  differing terrain spans (px):', [(a * 48, b * 48 + 48) for a, b in runs][:22])

def objpos(m, layer):
    L = [l for l in m['layers'] if l['name'] == layer]
    if not L: return []
    return [(o['name'], round(o['x']), round(o['y'])) for o in L[0].get('objects', [])]

print('\n\n' + '=' * 100)
for lv in LEVELS:
    m2, m3 = load(V2, lv), load(V3, lv)
    print(f'\n### {lv}')
    for layer in ['spawn', 'checkpoints', 'goal', 'challengeTriggers', 'storyTriggers', 'routeBranches', 'perfectZones', 'collectibles', 'springs', 'hazards', 'switches', 'movingPlatforms', 'temporaryPlatforms', 'modifiers', 'platforms']:
        a, b = objpos(m2, layer), objpos(m3, layer)
        same_names = [x[0] for x in a] == [x[0] for x in b]
        moved = sum(1 for x, y in zip(a, b) if x[1:] != y[1:])
        print(f'  {layer:20s} n={len(a):>3} -> {len(b):>3}  sameOrder={same_names}  moved={moved}')
