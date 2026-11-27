import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/site/stages-proches.json')
raw = open(F, encoding='utf-8').read()
d = json.loads(raw)
# prix relevés en ligne le 27/11/2026 (prix « à partir de », page de l'offre)
P = {75: 250, 90: 600, 91: 560, 147: 190, 194: 1100, 196: 105, 261: 310, 262: 550, 314: 10}
for i, p in P.items():
    assert d['o'][i][8] in (None, '', 0)
    d['o'][i][8] = p
for sep in ((',', ':'), (', ', ': ')):
    for ea in (False, True):
        if json.dumps(json.loads(raw), ensure_ascii=ea, separators=sep) == raw.rstrip('\n'):
            out = json.dumps(d, ensure_ascii=ea, separators=sep) + ('\n' if raw.endswith('\n') else '')
            open(F, 'w', encoding='utf-8').write(out)
            print('écrit', len(P), 'prix, format', sep, ea)
            raise SystemExit
print('format non reconnu, rien écrit')
