import json
p = 'projets/sailingmore/stages.json'
d = json.load(open(p, encoding='utf-8'))
L = d if isinstance(d, list) else max((v for v in d.values() if isinstance(v, list)), key=len)
vide = lambda e, k: e.get(k) in (None, '', [])
v = [e for e in L if not vide(e, 'prix_eur')]  # prix rempli
print('total', len(L), 'avec prix', len(v),
      'prix sans duree', sum(1 for e in v if vide(e, 'duree_jours')),
      'sans duree', sum(1 for e in L if vide(e, 'duree_jours')))
