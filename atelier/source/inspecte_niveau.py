import json,collections
d=json.load(open('projets/sailingmore/stages.json',encoding='utf-8'))
L=d if isinstance(d,list) else max([v for v in d.values() if isinstance(v,list)],key=len)
c=collections.Counter(e['lien'] for e in L if not e.get('niveau') and e['ecole'].startswith('Club Nautique'))
print(len(c)); print(c.most_common(8))
