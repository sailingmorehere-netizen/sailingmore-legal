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
# prix minimum affiché sur la page de l'offre, relevé en ligne le 24/11/2026
P = {
    74: (220, E), 75: (410, E),                      # Blue Spirit
    80: (150, E), 81: (150, E),                      # Compagnia della Vela (weekend court ; frais de la 2e semaine junior)
    109: (325, E), 110: (450, E), 111: (600, E),     # EZS
    112: (350, E),                                   # Grosse Freiheit (SBF Binnen Motor ab 350)
    117: (50, C),                                    # Lagoo (leçon privée ab CHF 50)
    174: (190, E),                                   # Reichenau étudiants (SBF See théorie)
    228: (1100, E), 230: (105, E),                   # Soleil
    273: (600, G),                                   # Solent Sail (day sail avec skipper, hiver)
    311: (310, E), 312: (550, E), 314: (399, E),     # Überlingen
    369: (35, G), 370: (350, G), 371: (350, G), 372: (559, G), 373: (350, G),   # Urban Truant
    376: (10, E),                                    # Vent du Large (adhésion)
}
for i, (p, c) in P.items():
    o = d['o'][i]
    assert o[8] in (None, '', 0), i
    o[8], o[9] = float(p), c
open(F, 'w', encoding='utf8').write(json.dumps(d, separators=sep, ensure_ascii=asc) + ('\n' if raw.endswith('\n') else ''))
print('ok', len(P))
