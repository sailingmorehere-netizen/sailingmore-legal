import json, collections
o = json.load(open('projets/sailingmore/stages.json'))['offres']
c = collections.Counter()
ex = {}
for e in o:
    if not e.get('niveau'):
        c[e['ecole_slug']] += 1
        ex.setdefault(e['ecole_slug'], []).append((e['titre'], e['lien']))
for s, n in c.most_common():
    print(n, s, ex[s][0])
print(collections.Counter(e.get('niveau') for e in o))
