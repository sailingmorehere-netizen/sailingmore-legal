import json, collections
d = json.load(open('projets/sailingmore/site/stages-proches.json'))
print(list(d.keys()))
L = d['o']
print(L[0])
m = [o for o in L if not o[11]]
print(len(m))
c = collections.Counter(o[4] for o in m)
print(c.most_common(40))
ok = collections.defaultdict(set)
for o in L:
    if o[11]:
        ok[o[4]].add(o[11])
print({k: len(v) for k, v in ok.items()})
print([k for k in c if k not in ok])
