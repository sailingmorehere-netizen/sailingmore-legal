import json
from collections import Counter
d = json.load(open('projets/sailingmore/chants-de-marin.json'))
print(list(d.keys()))
c = d['chants']
print(len(c))
print(json.dumps(c[0], ensure_ascii=False)[:1200])
print(Counter(x.get('livre') for x in c))
print(Counter(x.get('type') or x.get('famille') for x in c))
print(sorted(set(k for x in c for k in x)))
print([x['titre'] for x in c])
