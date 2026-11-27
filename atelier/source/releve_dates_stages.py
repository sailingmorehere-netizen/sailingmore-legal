#!/usr/bin/env python3
"""Tâche 44 : renseigne debut/fin/duree_jours ensemble pour les offres de stages.json
dont la page publie une période datée. Règles strictes :
 - uniquement des PÉRIODES (début + fin), jamais une date seule (avis, 'Stand', promos) ;
 - début >= aujourd'hui, fin entre 0 et 30 jours après le début ;
 - lien propre à l'offre (partagé par plusieurs offres = on ne devine pas) ;
 - la page ne doit pas dépasser 6 périodes futures distinctes (sinon : calendrier multi-cours) ;
 - sinon rien : champs laissés vides. Usage : releve_dates_stages.py [--ecrit]"""
import json, re, sys, html, datetime as dt, urllib.request, concurrent.futures as cf, collections
F = 'projets/sailingmore/stages.json'
AUJ = dt.date(2026, 11, 27)
d = json.load(open(F))
MOIS = {}
for i, ns in enumerate([
    'jan january janv januari januar', 'feb february févr februari februar', 'mar march mars märz maart',
    'apr april avr', 'may mai mei', 'jun june juin juni', 'jul july juil juli', 'aug august août',
    'sep sept september', 'oct october okt oktober', 'nov november', 'dec december dez']):
    for n in ns.split():
        MOIS[n] = i + 1
def D(j, m, a):
    try:
        return dt.date(int(a), int(m), int(j))
    except ValueError:
        return None
N = r'(\d{1,2})\.(\d{1,2})\.(202[67])'
R_NUM = [
    re.compile(N + r'\.?\s*(?:-|–|—|until|to|bis|↔)\s*' + N),
    re.compile(r'From\s+' + N + r'\.?\s*until\s+' + N, re.I),
]
R_NUM_COURT = re.compile(r'(\d{1,2})\.?\s*(?:-|–)\s*(\d{1,2})\.(\d{1,2})\.(202[67])')   # 10.–11.5.2027
R_NUM_COURT2 = re.compile(r'(\d{1,2})\.(\d{1,2})\.\s*(?:-|–)\s*(\d{1,2})\.(\d{1,2})\.(202[67])')  # 1.6.–5.6.2027
R_EN = re.compile(r'(\d{1,2})(?:st|nd|rd|th)?\s*(?:-|–|to)\s*(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\s+(202[67])')
R_EN2 = re.compile(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\s*(?:-|–|to)\s*(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\s+(202[67])')

def periodes(t):
    out = []
    for rx in R_NUM:
        for m in rx.finditer(t):
            g = m.groups(); out.append((D(g[0], g[1], g[2]), D(g[3], g[4], g[5])))
    for m in R_NUM_COURT2.finditer(t):
        g = m.groups(); out.append((D(g[0], g[1], g[4]), D(g[2], g[3], g[4])))
    for m in R_NUM_COURT.finditer(t):
        g = m.groups(); out.append((D(g[0], g[2], g[3]), D(g[1], g[2], g[3])))
    for m in R_EN.finditer(t):
        g = m.groups(); mo = MOIS.get(g[2].lower())
        if mo: out.append((D(g[0], mo, g[3]), D(g[1], mo, g[3])))
    for m in R_EN2.finditer(t):
        g = m.groups(); m1, m2 = MOIS.get(g[1].lower()), MOIS.get(g[3].lower())
        if m1 and m2: out.append((D(g[0], m1, g[4]), D(g[2], m2, g[4])))
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
# exclus après lecture : seafarer (période promo, pas un stage), ueberlingen (tarif de saison),
# ezs (page multi-cours, la 1re période n'est pas celle de l'offre)
EXCLUS = {'seafarer', 'ueberlingen', 'ezs'}
cand = [e for e in offres if not e.get('debut') and not e.get('hors_offre') and e['ecole_slug'] not in EXCLUS]
def trav(e):
    p = periodes(e['titre'])
    if p:
        return e, p[0], 'titre'
    if liens[e['lien']] > 1:
        return e, None, 'lien partagé'
    try:
        p = periodes(texte(e['lien']))
    except Exception as x:
        return e, None, 'erreur'
    if not p or len(p) > 6:
        return e, None, 'aucune/trop'
    return e, p[0], 'page'
with cf.ThreadPoolExecutor(8) as ex:
    res = list(ex.map(trav, cand))
n = 0
src = collections.Counter()
for e, p, s in res:
    src[s] += 1
    if p:
        n += 1
        if '--ecrit' in sys.argv:
            e['debut'], e['fin'] = p[0].isoformat(), p[1].isoformat()
            e['duree_jours'] = (p[1] - p[0]).days + 1
        else:
            print(e['ecole_slug'], e['titre'][:40], p[0], p[1], s)
print(n, 'offres datées', dict(src))
if '--ecrit' in sys.argv:
    json.dump(d, open(F, 'w'), ensure_ascii=False, indent=1)
