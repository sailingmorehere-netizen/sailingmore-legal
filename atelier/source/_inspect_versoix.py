import json, collections
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
V = [x for x in L if x.get('ecole') == 'Club Nautique de Versoix' and not x.get('hors_offre')]
print(len(V))
print(json.dumps(V[0], ensure_ascii=False, indent=1))
print(list(V[0].keys()))
print(collections.Counter(str(x.get('niveau')) for x in V))
print(collections.Counter((x.get('titre') or x.get('nom') or '') for x in V).most_common(15))
print(collections.Counter(str(x.get('niveau')) for x in L).most_common(12))
print(set(x.get('url') or x.get('lien') for x in V))
