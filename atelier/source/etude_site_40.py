import json, collections
b = 'projets/sailingmore/'
L = json.load(open(b + 'site/stages-proches.json'))['o']
m = collections.Counter(); t = collections.Counter(); dom = collections.defaultdict(set)
for o in L:
    t[o[4]] += 1
    dom[o[4]].add(o[10].split('/')[2] if o[10].startswith('http') else o[10])
    if o[8] is None or o[8] == '': m[o[4]] += 1
for e, n in m.most_common(): print(n, t[e], e, sorted(dom[e])[:2])
print(sum(m.values()), len(m))
