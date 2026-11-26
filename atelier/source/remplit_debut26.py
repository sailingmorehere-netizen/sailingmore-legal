"""Tâche 26 : début = la plus proche date FUTURE publiée sur la page de l'offre (cache/debut53).
Ignore le 31/12, la date du jour+1 et les pages sans date. Une page = une même date pour toutes ses offres
n'est gardée que si la page n'a qu'une URL d'offre.
Usage : python3 scripts/remplit_debut26.py [--ecrit]"""
import json, os, sys, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, R)
import _scan53 as S
F = os.path.join(R, 'projets/sailingmore/site/stages-proches.json')
d = json.load(open(F))
G = json.load(open(os.path.join(R, 'projets/sailingmore/site/go-liens.json')))
pages = collections.Counter()
for o in d['o']:
    if not o[7]:
        pages[G.get(o[10].split('id=')[1].split('&')[0])] += 1
n = 0; par = collections.Counter()
for o in d['o']:
    if o[7]:
        continue
    u = G.get(o[10].split('id=')[1].split('&')[0])
    h = S.page(u) if u else None
    if not h:
        continue
    ds = [x for x in S.dates(h) if x > '2026-11-26' and not x.endswith('-12-31')]
    if ds:
        o[7] = min(ds); n += 1; par[o[4]] += 1
print('remplies', n, par.most_common(10))
tot = sum(1 for o in d['o'] if o[7])
print('total', tot, '/', len(d['o']))
if '--ecrit' in sys.argv:
    json.dump(d, open(F, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('écrit')
