import json
import collections

d = json.load(open('projets/sailingmore/chants-de-marin.json'))
c = d['chants']
print(len(c))
print(collections.Counter(x.get('livre') for x in c))
print(collections.Counter(x.get('lg') for x in c))
print(collections.Counter(x.get('famille') or x.get('type') for x in c))
print(sum(1 for x in c if x.get('paroles')), sum(1 for x in c if x.get('partiel')), sum(1 for x in c if x.get('audio')))
print(json.dumps(c[10], ensure_ascii=False)[:1200])
print(list(c[0].keys()))
print([x['titre'] for x in c])
