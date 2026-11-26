import json, collections
L = json.load(open('projets/sailingmore/site/stages-proches.json'))['o']
print(L[0])
S = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))['offres']
c = collections.Counter(e['ecole'] for e in S if not e.get('debut'))
d = collections.Counter(e['ecole'] for e in S if e.get('debut'))
for k, v in c.most_common(60):
    ex = next(e for e in S if e['ecole'] == k and not e.get('debut'))
    print(v, d.get(k, 0), k, ex['lien'])
