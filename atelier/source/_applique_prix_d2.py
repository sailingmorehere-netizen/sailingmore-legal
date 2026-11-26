import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/site/stages-proches.json')
raw = open(F, encoding='utf-8').read()
d = json.loads(raw)
# indice -> (prix minimal « à partir de », devise), lu le 26/11/2026 sur la page de l'offre
P = {76: (250, 'EUR'), 100: (600, 'EUR'), 101: (995, 'EUR'), 106: (253, 'CHF'),
     209: (1100, 'EUR'), 211: (105, 'EUR'), 291: (550, 'EUR')}
n = 0
for i, (p, dev) in P.items():
    o = d['o'][i]
    assert o[8] in (None, '', 0), i
    o[8] = float(p); o[9] = dev; n += 1
sep = (',', ':') if ', ' not in raw[:300] else (', ', ': ')
open(F, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, separators=sep))
print(n, 'prix posés')
