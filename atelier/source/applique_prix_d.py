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
# (index, attendu dans le titre, prix, devise) : minimum lu sur la page de l'offre
P = [(117, 'Zürichsee', 253.0, 'CHF'), (173, 'SBF-See', 228.0, 'EUR'),
     (314, 'SKS', 399.0, 'EUR'), (311, 'LAST MINUTE', 310.0, 'EUR')]
for i, t, p, c in P:
    o = d['o'][i]
    assert t in o[3] and o[8] in (None, '', 0), i
    o[8], o[9] = p, c
open(F, 'w', encoding='utf8').write(json.dumps(d, separators=sep, ensure_ascii=asc) + ('\n' if raw.endswith('\n') else ''))
print('ok', len(P))
