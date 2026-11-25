import json, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(R, 'projets/sailingmore/stages.json')
d = json.load(open(p, encoding='utf-8'))
print(type(d).__name__, list(d)[:10] if isinstance(d, dict) else len(d))
L = max([v for v in d.values() if isinstance(v, list)], key=len) if isinstance(d, dict) else d
print(len(L)); print(json.dumps(L[0], ensure_ascii=False)[:600])
m = [e for e in L if e.get('lieu') in (None, '', [])]
print('sans lieu', len(m))
for k in ('ecole', 'école', 'organisme'):
    if k in L[0]:
        print(collections.Counter(e.get(k) for e in m).most_common(10))
print([k for k in L[0]])
