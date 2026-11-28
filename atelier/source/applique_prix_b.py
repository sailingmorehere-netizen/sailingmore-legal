# © 2026 Sailing More — tous droits réservés. All rights reserved.
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
E, G, C = 'EUR', 'GBP', 'CHF'
E, G = 'EUR', 'GBP'
# prix minimum lu sur la page de l'offre (lecture en ligne, 25/11/2026). UKSA : 403 (anti-robot), non relevé.
P = {
    # BH Marine (pages calendrier sans prix : on prend celui de la page de cours jumelle)
    57: (430, G), 58: (799, G), 59: (799, G), 60: (430, G), 61: (799, G), 62: (799, G), 63: (13500, G),
    64: (895, G), 65: (13500, G), 66: (799, G), 67: (799, G), 68: (450, G), 69: (799, G), 70: (799, G), 71: (430, G),
    87: (575, E),                                                   # De Bird, herfstvakantie
    173: (39.9, E), 174: (39.9, E), 175: (495, E), 176: (225, E), 177: (225, E), 178: (275, E), 179: (495, E),
    180: (285, E), 181: (65, E), 182: (195, E), 183: (495, E), 184: (595, E), 185: (75, E), 186: (75, E),
    187: (995, E), 188: (435, E), 189: (195, E), 190: (75, E), 191: (65, E), 192: (65, E), 193: (235, E),  # Rückenwind
    400: (400, E), 402: (505, E), 403: (550, E), 404: (585, E), 405: (585, E), 406: (585, E), 407: (585, E),
    408: (575, E), 409: (560, E), 410: (620, E), 411: (400, E), 412: (505, E), 413: (550, E), 414: (585, E),
    415: (585, E), 416: (585, E), 417: (585, E), 418: (560, E), 419: (575, E),                              # Zeilschool Ûp
}
for i, (p, c) in P.items():
    o = d['o'][i]
    assert o[8] in (None, '', 0), i
    assert o[4] in ('BH Marine', 'De Bird', 'Segelschule Rückenwind', 'Zeilschool Ûp'), i
    o[8], o[9] = float(p), c
open(F, 'w', encoding='utf8').write(json.dumps(d, separators=sep, ensure_ascii=asc) + ('\n' if raw.endswith('\n') else ''))
print('ok', len(P))
