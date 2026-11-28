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
# Tip Top Sailing, prix affichés sur la page de l'offre : 294 « Kosten per examentraining € 165 p.p. », 305 « Kosten: € 275,- p.p.p.d. »
P = {294: (165, 'EUR'), 305: (275, 'EUR')}
for i, (p, c) in P.items():
    o = d['o'][i]
    assert o[8] in (None, '', 0), i
    o[8], o[9] = float(p), c
open(F, 'w', encoding='utf8').write(json.dumps(d, separators=sep, ensure_ascii=asc) + ('\n' if raw.endswith('\n') else ''))
print('ok', len(P))
