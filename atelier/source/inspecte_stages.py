import json
F = 'projets/sailingmore/stages.json'
d = json.load(open(F, encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
for i, x in enumerate(L):
    if x.get('prix_eur') in (None, '', []) and not x.get('hors_offre'):
        print(i, x.get('ecole'), '|', x.get('titre'), '|', x.get('debut'), x.get('fin'), x.get('duree_jours'), x.get('type'), '|', (x.get('lien') or '')[-50:])
