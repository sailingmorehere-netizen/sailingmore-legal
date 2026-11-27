import json
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
n = 0
for i, x in enumerate(L):
    if x.get('duree_jours') == 1 and x.get('fin') and n < 4:
        n += 1
        print(i, x['ecole'], x['debut'], x['fin'], x['duree_jours'])
print(L[70])
