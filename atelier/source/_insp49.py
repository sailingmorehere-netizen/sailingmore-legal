import json, collections
d = json.load(open('projets/sailingmore/stages.json'))
L = d['offres'] if isinstance(d, dict) else d
m = [e for e in L if e.get('duree_jours') in (None, '')]
print(collections.Counter((bool(e.get('debut')), bool(e.get('fin'))) for e in m))
print(list(L[0].keys()))
for e in m[:4]:
    print({k: v for k, v in e.items() if k in ('debut', 'fin', 'duree', 'duree_texte', 'titre', 'nom', 'dates')})
