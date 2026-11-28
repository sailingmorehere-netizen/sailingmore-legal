#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Tâche 43 : complète releve_dates_stages.py (tâche 44) avec des formats de période
supplémentaires (finnois, slovène, tchèque/slovaque, hongrois, néerlandais, ISO).
Mêmes règles strictes : périodes début+fin seulement, début >= aujourd'hui, durée 0..30 j,
lien propre à l'offre, <= MAXP périodes futures distinctes sur la page, sinon champs vides.
debut, fin, duree_jours s'écrivent ensemble. Usage : releve_dates_stages2.py [--ecrit] [MAXP]"""
import json, re, sys, html, datetime as dt, urllib.request, concurrent.futures as cf, collections
F = 'projets/sailingmore/stages.json'
AUJ = dt.date(2026, 11, 27)
MAXP = int(next((a for a in sys.argv[1:] if a.isdigit()), 6))
d = json.load(open(F))
SEP = r'\s*(?:-|–|—|↔|t/m|až|do)\s*'
# d.m.[yyyy] – d.m.yyyy  |  d.–d.m.yyyy  |  d. m. – d. m. yyyy
R_DM = re.compile(r'(?<![\d.])(\d{1,2})\.\s?(?:(\d{1,2})\.?\s?)?(?:(202[67])\s?)?' + SEP + r'(\d{1,2})\.\s?(\d{1,2})\.?\s?(202[67])')
R_ISO = re.compile(r'(202[67])-(\d\d)-(\d\d)' + SEP + r'(202[67])-(\d\d)-(\d\d)')
MOIS = {'jan': 1, 'feb': 2, 'mar': 3, 'maa': 3, 'apr': 4, 'mei': 5, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'okt': 10, 'oct': 10, 'nov': 11, 'dec': 12}
# néerlandais : 11 juli t/m 14 juli 2027  |  (11 juli t/m 14 juli)
R_NL = re.compile(r'(\d{1,2})\s+([a-z]{3,9})\s*(?:t/m|-|–)\s*(\d{1,2})\s+([a-z]{3,9})\)?', re.I)

def D(j, m, a):
    try:
        return dt.date(int(a), int(m), int(j))
    except (ValueError, TypeError):
        return None

def periodes(t):
    out = []
    for m in R_DM.finditer(t):
        j1, m1, a1, j2, m2, a2 = m.groups()
        m1 = m1 or m2
        a1 = a1 or a2
        deb, fin = D(j1, m1, a1), D(j2, m2, a2)
        if deb and fin and deb > fin and not m.group(3):
            deb = D(j1, m1, int(a2) - 1)
        out.append((deb, fin))
    for m in R_ISO.finditer(t):
        g = m.groups(); out.append((D(g[0], g[1], g[2]), D(g[3], g[4], g[5])))
    for m in R_NL.finditer(t):
        j1, n1, j2, n2 = m.groups()
        m1, m2 = MOIS.get(n1[:3].lower()), MOIS.get(n2[:3].lower())
        if m1 and m2:
            # année : 2027 si le texte voisin la porte, sinon on s'abstient
            ctx = t[max(0, m.start() - 40):m.end() + 5]
            a = re.search(r'\b(202[67])\b', ctx)
            if a:
                out.append((D(j1, m1, a.group(1)), D(j2, m2, a.group(1))))
    ok = set()
    for a, b in out:
        if a and b and a >= AUJ and 0 <= (b - a).days <= 30:
            ok.add((a, b))
    return sorted(ok)

def texte(url):
    r = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    t = urllib.request.urlopen(r, timeout=15).read().decode('utf8', 'ignore')
    t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))

offres = d['offres']
liens = collections.Counter(e['lien'] for e in offres)
EXCLUS = {'seafarer', 'ueberlingen', 'ezs'}
cand = [e for e in offres if not e.get('debut') and not e.get('hors_offre') and e['ecole_slug'] not in EXCLUS]
cache = {}
def page(u):
    if u not in cache:
        try:
            cache[u] = periodes(texte(u))
        except Exception:
            cache[u] = None
    return cache[u]
def trav(e):
    if liens[e['lien']] > 1:
        return e, None, 'lien partagé'
    p = page(e['lien'])
    if p is None:
        return e, None, 'erreur'
    if not p or len(p) > MAXP:
        return e, None, 'aucune/trop'
    return e, p[0], 'page'
with cf.ThreadPoolExecutor(8) as ex:
    res = list(ex.map(trav, cand))
n = 0
src = collections.Counter()
par = collections.Counter()
for e, p, s in res:
    src[s] += 1
    if p:
        n += 1
        par[e['ecole_slug']] += 1
        if '--ecrit' in sys.argv:
            e['debut'], e['fin'] = p[0].isoformat(), p[1].isoformat()
            e['duree_jours'] = (p[1] - p[0]).days + 1
        else:
            print(e['ecole_slug'], e['titre'][:40], p[0], p[1])
print(n, 'offres datées', dict(src), dict(par))
if '--ecrit' in sys.argv:
    json.dump(d, open(F, 'w'), ensure_ascii=False, indent=1)
