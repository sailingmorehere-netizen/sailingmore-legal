import json, collections
d = json.load(open('projets/sailingmore/stages.json'))
o = d['offres']
m = [e for e in o if not e.get('debut')]
print(len(m), 'hors_offre:', sum(1 for e in m if e.get('hors_offre')))
print(collections.Counter(e['ecole_slug'] for e in m).most_common(30))
print(sorted(o[0].keys()))
ls = collections.Counter(e['lien'] for e in o)
print('partages:', sum(1 for e in m if ls[e['lien']] > 1))
