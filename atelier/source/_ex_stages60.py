import json, collections
d = json.load(open('projets/sailingmore/stages.json', encoding='utf8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
print(type(d), len(L), list(d)[:6] if isinstance(d, dict) else '')
ok = [e for e in L if e.get('prix_eur')]
print(ok[0])
print(ok[300])
m = [e for e in L if not e.get('prix_eur')]
print(m[0])
print(collections.Counter((bool(e.get('hors_offre')), e.get('devise')) for e in m))
print(collections.Counter(e.get('prix_publie') for e in L))
