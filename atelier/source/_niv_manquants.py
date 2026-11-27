import json, collections
o = json.load(open('projets/sailingmore/stages.json'))['offres']
m = [e for e in o if not e.get('niveau')]
c = collections.Counter(e['ecole_slug'] for e in m)
print(collections.Counter(e.get('niveau') for e in o))
for s, n in c.most_common(40):
    ex = [e for e in m if e['ecole_slug'] == s][0]
    print(s, n, ex['lien'], '|', ex['titre'])
