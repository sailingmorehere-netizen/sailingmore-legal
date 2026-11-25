import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/site/stages-proches.json')
raw = open(F, encoding='utf-8').read()
d = json.loads(raw)
# indice -> (prix minimal « à partir de », devise), relevé le 25/11/2026 sur la page de tarifs de l'école
P = {166: (410, 'EUR'), 167: (410, 'EUR'), 168: (680, 'EUR'), 170: (210, 'EUR'), 171: (240, 'EUR'),
     165: (200, 'EUR'), 209: (79.5, 'EUR'),
     211: (750, 'EUR'), 212: (400, 'EUR'), 213: (380, 'EUR'),
     76: (150, 'EUR'), 78: (150, 'EUR'), 79: (250, 'EUR'),
     110: (995, 'EUR'), 111: (350, 'EUR'), 112: (350, 'EUR'), 113: (350, 'EUR'),
     228: (105, 'EUR'), 310: (550, 'EUR'), 312: (399, 'EUR'),
     367: (35, 'GBP'), 368: (350, 'GBP'), 369: (350, 'GBP'), 370: (559, 'GBP'), 371: (350, 'GBP'),
     374: (10, 'EUR'), 115: (50, 'CHF'), 399: (130, 'EUR')}
n = 0
for i, (p, dev) in P.items():
    o = d['o'][i]
    assert o[8] in (None, '', 0), i
    o[8] = float(p); o[9] = dev; n += 1
sep = (',', ':') if ', ' not in raw[:300] else (', ', ': ')
open(F, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, separators=sep))
print(n, 'prix posés')
