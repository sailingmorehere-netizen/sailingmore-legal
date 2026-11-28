# © 2026 Sailing More — tous droits réservés. All rights reserved.
import json, collections, sys
R = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/stages.json'
d = json.load(open(R, encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
m = [(i, x) for i, x in enumerate(L) if not x.get('hors_offre') and not x.get('prix_eur')]
print(len(m), collections.Counter(x.get('ecole') for _, x in m))
print(sorted(L[0].keys()))
for i, x in m:
    print(i, x.get('ecole'), '|', (x.get('titre') or x.get('nom') or '')[:70], '|',
          x.get('date_debut') or x.get('dates') or x.get('date') or '', '|', (x.get('url') or x.get('lien') or '')[-60:])
