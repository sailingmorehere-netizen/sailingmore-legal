import json, collections
d = json.load(open('projets/sailingmore/stages.json'))['offres']
m = [e for e in d if not e.get('debut')]
liens = collections.Counter(e['lien'] for e in d)
c = collections.Counter((e['ecole_slug'], bool(e.get('hors_offre'))) for e in m)
for k, v in c.most_common(40):
    print(k, v, sum(1 for e in m if e['ecole_slug'] == k[0] and liens[e['lien']] > 1))
print(sorted(m[0].keys()))
print({k: m[0][k] for k in m[0]})
