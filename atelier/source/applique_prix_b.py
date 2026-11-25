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
    60: (799, G), 61: (799, G), 62: (430, G), 63: (799, G), 64: (799, G), 65: (13500, G),  # BH Marine : prix des pages de cours jumelles
    66: (895, G), 67: (13500, G), 68: (799, G), 69: (799, G), 70: (450, G), 71: (799, G), 72: (799, G), 73: (430, G),
    89: (575, E),                                                   # De Bird, herfstvakantie
    175: (39.9, E), 176: (39.9, E), 177: (495, E), 178: (225, E), 179: (225, E), 180: (275, E),
    182: (285, E), 183: (65, E), 184: (195, E), 185: (495, E), 186: (595, E), 187: (75, E), 188: (75, E),
    189: (995, E), 190: (435, E), 191: (195, E), 192: (75, E), 193: (65, E), 194: (65, E), 195: (235, E),  # Rückenwind
    402: (400, E), 404: (505, E), 405: (550, E), 406: (585, E), 407: (585, E), 408: (585, E), 409: (585, E),
    410: (575, E), 411: (560, E), 412: (620, E), 413: (400, E), 414: (505, E), 415: (550, E), 416: (585, E),
    417: (585, E), 418: (585, E), 419: (585, E), 420: (560, E), 421: (575, E),                              # Zeilschool Ûp
}
for i, (p, c) in P.items():
    o = d['o'][i]
    assert o[8] in (None, '', 0), i
    o[8], o[9] = float(p), c
open(F, 'w', encoding='utf8').write(json.dumps(d, separators=sep, ensure_ascii=asc) + ('\n' if raw.endswith('\n') else ''))
print('ok', len(P))
