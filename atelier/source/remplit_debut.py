"""Tâche 28 : renseigne le début (col. 7) des offres sans date, à partir des pages d'offre en cache
(cache/debut53, clé = md5 de l'URL réelle donnée par go-liens.json). Dates publiées seulement :
1) balise structurée startDate / start_date / datetime= ; 2) à défaut, une page qui ne publie
qu'UNE seule date future (texte). Ambigu (plusieurs dates sans balise) -> reste vide.
Usage : python3 scripts/remplit_debut.py [--ecrit]"""
import json, os, sys, re, hashlib, collections
RAC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAC)
import _scan53 as S
F = os.path.join(RAC, 'projets/sailingmore/site/stages-proches.json')
G = json.load(open(os.path.join(RAC, 'projets/sailingmore/site/go-liens.json')))
d = json.load(open(F))
P = re.compile(r'(?:startDate|"start_date"|datetime=)["\s:=]+(20(?:26|27)-\d\d-\d\d)')
n_s = n_u = 0
par = collections.Counter()
for o in d['o']:
    if o[7]:
        continue
    u = G.get(o[10].split('id=')[1].split('&')[0])
    if not u:
        continue
    h = S.page(u)
    if not h:
        continue
    ds = sorted({x for x in P.findall(h) if x > S.AUJ})
    if ds:
        o[7] = ds[0]; n_s += 1; par[o[4]] += 1
        continue
    ds = S.dates(h)
    if len(ds) == 1:
        o[7] = ds[0]; n_u += 1; par[o[4]] += 1
orig = {id(o): o[7] for o in d['o']}
# Filtre anti-faux positifs : une date répétée sur >=2 offres d'une même école, la date du jour
# de la page (AUJ) ou un 31/12 sont des repères de page, pas un début de stage -> on les retire.
cnt = collections.Counter((o[4], o[7]) for o in d['o'] if o[7])
for o in d['o']:
    if o[7] and o[7] != orig[id(o)]:
        pass
vides = 0
ancien = json.load(open(F))['o']
for a, o in zip(ancien, d['o']):
    if not a[7] and o[7]:
        if o[7] <= S.AUJ or o[7].endswith('-12-31') or cnt[(o[4], o[7])] > 1:
            o[7] = a[7]; vides += 1
n_u -= vides
print('rejetées (date du jour / 31-12 / répétée)', vides)
print('balisées', n_s, '; date unique en texte', n_u)
print(par.most_common(12))
if '--ecrit' in sys.argv:
    json.dump(d, open(F, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('écrit')
