import json, os, sys, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, R)
import _scan53 as S
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
G = json.load(open(os.path.join(R, 'projets/sailingmore/site/go-liens.json')))
n = collections.Counter(); ex = {}
for o in d['o']:
    if o[7]: continue
    u = G.get(o[10].split('id=')[1].split('&')[0])
    h = S.page(u) if u else None
    if not h: n['nopage'] += 1; continue
    ds = [x for x in S.dates(h) if x > S.AUJ]
    k = 0 if not ds else (1 if len(ds) == 1 else 2)
    n[k] += 1
    if k == 2: ex.setdefault(o[4], (o[3], u, ds[:5]))
print(dict(n))
for e, v in list(ex.items())[:15]: print(e, v)
