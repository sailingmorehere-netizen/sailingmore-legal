# © 2026 Sailing More — tous droits réservés. All rights reserved.
import json
d = json.load(open('/opt/data/cache/claude-nuit/travail/projets/sailingmore/stages.json'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
for x in L:
    if x.get('debut') and not x.get('fin') and not x.get('hors_offre'):
        print(x.get('ecole'), '|', x.get('titre') or x.get('nom'), '|', x.get('debut'), '|', x.get('duree_jours'), '|', x.get('url') or x.get('lien'))
