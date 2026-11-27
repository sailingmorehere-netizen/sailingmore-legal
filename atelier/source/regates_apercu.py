import json, os, collections
B = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/'
print(sorted(os.listdir(B))[:60])
d = json.load(open(B + 'regates.json', encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
print(type(d).__name__, len(L))
print(L[0])
v = [x for x in L if not x.get('lien')]
print(len(v)); print(v[0]); print(v[len(v)//2])
print(collections.Counter(tuple(sorted(x.keys())) for x in L).most_common(3))
if os.path.exists(B + 'regates-clubs.json'):
    print(open(B + 'regates-clubs.json', encoding='utf-8').read()[:800])
