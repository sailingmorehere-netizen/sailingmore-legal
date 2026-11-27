import json,collections
o=json.load(open('projets/sailingmore/stages.json'))['offres']
print(collections.Counter(e.get('niveau') for e in o))
m=[e for e in o if not e.get('niveau')]
for s,n in collections.Counter(e['ecole_slug'] for e in m).most_common(15):
    ex=[e for e in m if e['ecole_slug']==s][0]
    print(s,n,ex['titre'],ex['lien'])
