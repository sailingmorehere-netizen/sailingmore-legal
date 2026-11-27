import json,collections
d=json.load(open('projets/sailingmore/stages.json'))['offres']
print(sorted(d[0].keys()))
c=collections.Counter(e.get('ecole_slug') for e in d if not e.get('niveau'))
print(c.most_common(25))
print(collections.Counter(e.get('niveau') for e in d))
print(collections.Counter(e.get('niveau_releve') for e in d))
