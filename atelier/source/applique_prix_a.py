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
# index : (prix, devise) = prix minimum affiché sur la page de l'offre (TTC quand la page donne le total)
P = {
    # Seven Seas
    23: (1150, E), 24: (1150, E), 25: (1150, E), 26: (1150, E), 28: (695, E), 29: (875, E), 30: (830, E),
    32: (1705, E), 33: (1705, E), 34: (2130, E), 36: (200, E), 37: (75, E), 38: (600, E), 39: (650, E),
    40: (2950, E), 41: (1250, E), 43: (1155, E), 44: (525, E), 45: (450, E), 47: (420, E), 48: (620, E),
    # Solent Boat Training
    233: (299, G), 235: (399, G), 236: (99, G), 237: (299, G), 241: (499, G), 242: (3999, G), 247: (699, G),
    249: (99, G), 250: (99, G), 257: (49, G), 258: (89, G), 259: (299, G), 260: (349, G), 261: (349, G),
    262: (39, G), 268: (20, G), 269: (20, G),
    # Tip Top Sailing
    280: (895, E), 296: (195, E), 300: (475, E), 303: (425, E), 304: (1295, E), 307: (125, E),
    # Ultra Sailing
    343: (890, E), 344: (850, E), 345: (890, E), 346: (1850, E), 347: (1190, E), 348: (1190, E),
    349: (690, E), 351: (1090, E), 352: (350, E), 353: (232, E), 354: (1090, E), 355: (590, E), 357: (1990, E),
}
for i, (p, c) in P.items():
    o = d['o'][i]
    assert o[8] in (None, '', 0), i
    o[8], o[9] = float(p), c
open(F, 'w', encoding='utf8').write(json.dumps(d, separators=sep, ensure_ascii=asc) + ('\n' if raw.endswith('\n') else ''))
print('ok', len(P))
