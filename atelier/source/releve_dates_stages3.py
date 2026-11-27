#!/usr/bin/env python3
"""Tâche 41 : complète releve_dates_stages.py / 2 pour les pages-CALENDRIER (plus de 6 périodes).
Décision prise : pour une offre dont la page publie un calendrier de sessions, debut/fin = la PROCHAINE
session (la première période à venir), avec debut, fin, duree_jours écrits ensemble. Année absente :
première année qui met le début à partir d'aujourd'hui (<= 12 mois). Durée 0..30 j. Lien propre à l'offre.
Usage : releve_dates_stages3.py [--ecrit]"""
import json, re, sys, html, datetime as dt, urllib.request, concurrent.futures as cf, collections
F = 'projets/sailingmore/stages.json'
AUJ = dt.date(2026, 11, 27)
LIM = dt.date(2027, 11, 27)
d = json.load(open(F))
SEP = r'\s*(?:-|–|—|bis|until|au)\s*'
R_A = re.compile(r'(?<![\d./])(\d{1,2})\.(?:(\d{1,2})\.)?' + SEP + r'(\d{1,2})\.(\d{1,2})\.(?:\s?(20\d\d))?')
R_B = re.compile(r'(?<![\d/])(\d{2})/(\d{2})\s+(\d{2})/(\d{2})(?![\d/])')

def D(j, m, a):
    try:
        return dt.date(int(a), int(m), int(j))
    except (ValueError, TypeError):
        return None

def annee(j1, m1, j2, m2, a):
    for y in ([int(a)] if a else [2026, 2027]):
        deb = D(j1, m1, y)
        fin = D(j2, m2, y + (1 if (m2, j2) < (m1, j1) else 0)) if deb else None
        if deb and fin and deb >= AUJ and (a or deb < LIM) and 0 <= (fin - deb).days <= 30:
            return deb, fin
    return None

def periodes(t):
    out = set()
    for m in R_A.finditer(t):
        j1, m1, j2, m2, a = m.groups()
        r = annee(j1, m1 or m2, j2, m2, a)
        if r: out.add(r)
    for m in R_B.finditer(t):
        j1, m1, j2, m2 = m.groups()
        if 1 <= int(m1) <= 12 and 1 <= int(m2) <= 12:
            r = annee(j1, m1, j2, m2, None)
            if r: out.add(r)
    return sorted(out)

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
def trav(e):
    if liens[e['lien']] > 1:
        return e, None, 'lien partagé'
    u = e['lien']
    if u not in cache:
        try: cache[u] = periodes(texte(u))
        except Exception: cache[u] = None
    p = cache[u]
    if p is None: return e, None, 'erreur'
    if not p: return e, None, 'aucune'
    return e, p[0], 'page'
with cf.ThreadPoolExecutor(8) as ex:
    res = list(ex.map(trav, cand))
src = collections.Counter(); par = collections.Counter(); n = 0
for e, p, s in res:
    src[s] += 1
    if p:
        n += 1; par[e['ecole_slug']] += 1
        if '--ecrit' in sys.argv:
            e['debut'], e['fin'] = p[0].isoformat(), p[1].isoformat()
            e['duree_jours'] = (p[1] - p[0]).days + 1
        else:
            print(e['ecole_slug'], e['titre'][:40], p[0], p[1])
print(n, 'offres datées', dict(src), dict(par))
if '--ecrit' in sys.argv:
    json.dump(d, open(F, 'w'), ensure_ascii=False, indent=1)
