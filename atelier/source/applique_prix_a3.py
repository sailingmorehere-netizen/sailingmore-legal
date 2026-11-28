# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Lot A (prix_a) : écrit les prix relevés sur les pages des offres (lecture seule, 25/11/2026).
Prix « à partir de » quand la page donne une fourchette ou une liste de dates. Rien d'estimé."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/site/stages-proches.json')
raw = open(F, encoding='utf8').read()
d = json.loads(raw)
for sep, asc in (((',', ':'), False), ((', ', ': '), False), ((',', ':'), True)):
    if json.dumps(d, separators=sep, ensure_ascii=asc) == raw.rstrip('\n'):
        break
else:
    raise SystemExit('format non reproductible, je n ecris rien')
E, G = 'EUR', 'GBP'
P = {}
# Seven Seas (EUR) : « Costs » de la page ; TTC quand la page donne « plus VAT (total …) »
for i, p in {21: 1150, 22: 1150, 23: 1150, 24: 1150, 26: 695, 27: 875, 28: 830, 30: 1705, 31: 1705, 32: 2130,
             34: 200, 35: 75, 36: 600, 37: 650, 38: 2950, 39: 1250, 41: 1155, 42: 525, 43: 450, 45: 420, 46: 620}.items():
    P[i] = (p, E)
# Solent Boat Training (GBP) : « From £… » / « Cost: … »
for i, p in {231: 299, 234: 99, 235: 299, 245: 699, 247: 99, 248: 125, 255: 49, 256: 89, 257: 299, 258: 349,
             259: 349, 260: 39, 266: 20, 267: 20}.items():
    P[i] = (p, G)
# Tip Top Sailing (EUR)
for i, p in {290: 350, 292: 165, 294: 195, 298: 475, 301: 425, 302: 1295, 303: 275, 305: 125}.items():
    P[i] = (p, E)
# Ultra Sailing (EUR) : tarif affiché dans le tableau des sessions (plus bas tarif plein, hors remise)
for i, p in {341: 890, 342: 850, 343: 890, 344: 1850, 345: 1190, 346: 1190, 347: 690, 349: 1090, 350: 350,
             351: 290, 352: 1090, 353: 590}.items():
    P[i] = (p, E)
n = 0
for i, (p, c) in P.items():
    o = d['o'][i]
    assert o[8] in (None, '', 0), i
    o[8], o[9] = float(p), c
    n += 1
open(F, 'w', encoding='utf8').write(json.dumps(d, separators=sep, ensure_ascii=asc) + ('\n' if raw.endswith('\n') else ''))
print('ok', n)
