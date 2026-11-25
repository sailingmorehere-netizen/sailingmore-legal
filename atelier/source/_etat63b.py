import json, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(os.path.join(R, 'projets/sailingmore/stages.json'), encoding='utf-8'))['offres']
m = [e for e in L if not e.get('lieu')]
seen = collections.Counter()
for e in m:
    if seen[e['ecole']] < 2:
        seen[e['ecole']] += 1
        print(e['ecole'], '|', e['titre'], '|', e.get('region'), '|', e['lien'], '|', e.get('precision'), e.get('lat'))
print(collections.Counter(e.get('precision') for e in m))
print(collections.Counter(e['lien'] for e in m).most_common(3), len({e['lien'] for e in m}))
