#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Tâche 61 : relève debut/fin ÉCRITS avec année complète sur la page de l'offre (jamais déduits).
Formes : JJ.MM.AAAA[.] (until|bis|au|-|–) JJ.MM.AAAA[.] ; AAAA-MM-JJ (to|-|–) AAAA-MM-JJ ;
JJ/MM/AAAA - JJ/MM/AAAA. Décision : première période À VENIR (>= aujourd'hui), durée 0..60 j,
lien propre à l'offre. Usage : releve_dates_stages4.py [--ecrit]"""
import json, re, sys, html, datetime as dt, urllib.request, concurrent.futures as cf, collections
F = 'projets/sailingmore/stages.json'
AUJ = dt.date(2026, 11, 28)
d = json.load(open(F))
SEP = r'\s*(?:-|–|—|bis|until|au|to|à|al|a)\s*'
R1 = re.compile(r'(?<![\d./])(\d{1,2})[./](\d{1,2})[./](20\d\d)\.?' + SEP + r'(\d{1,2})[./](\d{1,2})[./](20\d\d)(?!\d)')
R2 = re.compile(r'(?<!\d)(20\d\d)-(\d\d)-(\d\d)' + SEP + r'(20\d\d)-(\d\d)-(\d\d)(?!\d)')

MOIS = {}
for i, ns in enumerate([
    'januari january janvier januar', 'februari february février fevrier februar', 'maart march mars märz',
    'april avril', 'mei may mai', 'juni june juin', 'juli july juillet', 'augustus august août aout',
    'september septembre', 'oktober october octobre', 'november novembre', 'december décembre decembre dezember'], 1):
    for n in ns.split(): MOIS[n] = i
_M = '|'.join(sorted(MOIS, key=len, reverse=True))
# « 23-25 februari 2027 », « 14 t/m 17 mei 2026 », « 28 June - 2 July 2027 » (année obligatoire, écrite)
R3 = re.compile(r'(?<![\d./])(\d{1,2})(?:\.|st|nd|rd|th|er)?\s*(?:(' + _M + r')\s*(20\d\d)?)?\s*(?:-|–|—|t/m|to|au|bis|until)\s*(\d{1,2})(?:\.|st|nd|rd|th)?\s*(' + _M + r')\s*(20\d\d)(?!\d)', re.I)

def D(a, m, j):
    try: return dt.date(int(a), int(m), int(j))
    except ValueError: return None

def periodes(t):
    out = set()
    for m in R1.finditer(t):
        j1, m1, a1, j2, m2, a2 = m.groups()
        out.add((D(a1, m1, j1), D(a2, m2, j2)))
    for m in R2.finditer(t):
        a1, m1, j1, a2, m2, j2 = m.groups()
        out.add((D(a1, m1, j1), D(a2, m2, j2)))
    txt = set()
    for m in R3.finditer(t):
        j1, m1, a1, j2, m2, a2 = m.groups()
        mo1 = MOIS.get((m1 or m2).lower()); mo2 = MOIS.get(m2.lower())
        if not (mo1 and mo2): continue
        y2 = a2; y1 = a1 or a2
        txt.add((D(y1, mo1, j1), D(y2, mo2, j2)))
    if len(txt) <= 4: out |= txt   # page-calendrier trop riche : on ne devine pas
    ok = [p for p in out if p[0] and p[1] and 0 <= (p[1] - p[0]).days <= 60]
    fut = sorted(p for p in ok if p[0] >= AUJ)
    # --passe : à défaut de session à venir, la dernière session écrite sur la page
    return fut or (sorted(ok)[-1:] if '--passe' in sys.argv else [])

def texte(url):
    r = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    t = urllib.request.urlopen(r, timeout=15).read().decode('utf8', 'ignore')
    t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))

offres = d['offres']
liens = collections.Counter(e['lien'] for e in offres)
cand = [e for e in offres if not e.get('debut') and not e.get('hors_offre')]
cache = {}
def trav(e):
    if liens[e['lien']] > 1: return e, None, 'lien partagé'
    u = e['lien']
    if u not in cache:
        try: cache[u] = periodes(texte(u))
        except Exception: cache[u] = None
    p = cache[u]
    if p is None: return e, None, 'erreur'
    return (e, p[0], 'page') if p else (e, None, 'aucune')
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
