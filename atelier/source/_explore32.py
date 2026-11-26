import json, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = json.load(open(R + '/projets/sailingmore/stages.json', encoding='utf-8'))['offres']
par = collections.defaultdict(lambda: [0, collections.Counter(), set()])
for o in s:
    e = par[o['ecole']]
    if o.get('lieu'):
        e[1][o['lieu']] += 1
    else:
        e[0] += 1
    e[2].add(o.get('pays_nom'))
for k, (v, c, p) in sorted(par.items(), key=lambda x: -x[1][0]):
    print(f"{v:4} vides | {k[:34]:34} | {dict(c.most_common(3))} | {sorted(x for x in p if x)}")
