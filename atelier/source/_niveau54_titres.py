import json, collections
L = json.load(open('projets/sailingmore/stages.json.bak-avant-54', encoding='utf-8'))['offres']
m = [e for e in L if not e.get('niveau')]
c = collections.Counter((e['ecole_slug'], e['titre'][:70]) for e in m)
for t, n in c.most_common(80):
    print(n, t)
print(len(c))
