import json, collections
L = json.load(open('projets/sailingmore/site/stages-proches.json'))['o']
c = collections.Counter(); v = collections.Counter(); ex = {}
for o in L:
    c[o[4]] += 1
    if o[7]: v[o[4]] += 1
    elif o[4] not in ex: ex[o[4]] = (o[3], o[10])
for e, n in c.most_common():
    print(n, v[e], e, ex.get(e, ''))
