#!/usr/bin/env python3
# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Relève debut/fin/duree_jours sur la page de l'école (champ 'lien') pour les offres sans date.
Ne retient que des plages explicites début–fin, à venir (>= aujourd'hui), de 1 à 60 jours.
Source muette => offre laissée vide. Usage : releve_dates_stages.py [--ecrire]"""
import json, re, sys, html, datetime as dt, concurrent.futures as cf, urllib.request
P = 'projets/sailingmore/stages.json'
AUJ = dt.date(2026, 11, 28)
M = {}
for i, ns in enumerate([
    'jan janu janv ene gen januar', 'feb febr févr fév febbraio februar febrero', 'mar mär mars märz marz marzo maart march',
    'apr avr abr april avril aprile abril', 'may mai mag mayo mei maggio', 'jun juin giu junio juni june giugno',
    'jul juil lug julio juli july luglio', 'aug août ago augustus august agosto', 'sep sept set septiembre september settembre',
    'oct okt ott octubre october oktober ottobre', 'nov noviembre november novembre', 'dec dez dic déc diciembre december dezember dicembre'], 1):
    for n in ns.split():
        M[n] = i
MOIS = '|'.join(sorted(M, key=len, reverse=True))
SEP = r'\s*(?:–|—|-|→|↔|to|until|bis|t/m|au|al|a|do)\s*'
RX = [
    # 04.04.2026 – 09.04.2026 / From 12.04.2026. until 14.04.2026.
    (re.compile(r'(\d{1,2})[./](\d{1,2})[./](20\d\d)\.?' + SEP + r'(\d{1,2})[./](\d{1,2})[./](20\d\d)'), 'dmy_dmy'),
    # 1.–5.6.2026
    (re.compile(r'(\d{1,2})\.\s*[–-]\s*(\d{1,2})\.(\d{1,2})\.(20\d\d)'), 'd_dmy'),
    # 08 Dec 2026 → 10 Dec 2026 / 5 June 2027 - 12 June 2027
    (re.compile(r'(\d{1,2})(?:st|nd|rd|th)?\.?\s+(' + MOIS + r')[a-zéû]*\.?\s+(20\d\d)' + SEP + r'(\d{1,2})(?:st|nd|rd|th)?\.?\s+(' + MOIS + r')[a-zéû]*\.?\s+(20\d\d)', re.I), 'dMy_dMy'),
    # 27 - 28 March 2027 / 26. - 29. März 2027
    (re.compile(r'(\d{1,2})(?:st|nd|rd|th)?\.?' + SEP + r'(\d{1,2})(?:st|nd|rd|th)?\.?\s+(' + MOIS + r')[a-zéû]*\.?,?\s+(20\d\d)', re.I), 'd_dMy'),
    # 2027 März: 26. - 29. März
    (re.compile(r'(20\d\d)\s+[A-Za-zä]+:?\s*(\d{1,2})\.?' + SEP + r'(\d{1,2})\.?\s+(' + MOIS + r')[a-zä]*', re.I), 'y_d_dM'),
]
def D(y, m, d):
    try:
        return dt.date(int(y), int(m), int(d))
    except ValueError:
        return None
def plages(t):
    out = []
    for rx, k in RX:
        for g in rx.finditer(t):
            x = g.groups()
            if k == 'dmy_dmy': a, b = D(x[2], x[1], x[0]), D(x[5], x[4], x[3])
            elif k == 'd_dmy': a, b = D(x[3], x[2], x[0]), D(x[3], x[2], x[1])
            elif k == 'dMy_dMy': a, b = D(x[2], M[x[1].lower()], x[0]), D(x[5], M[x[4].lower()], x[3])
            elif k == 'd_dMy': a, b = D(x[3], M[x[2].lower()], x[0]), D(x[3], M[x[2].lower()], x[1])
            else: a, b = D(x[0], M[x[3].lower()], x[1]), D(x[0], M[x[3].lower()], x[2])
            if a and b and a >= AUJ and 0 <= (b - a).days <= 59:
                out.append((a, b))
    return sorted(set(out))
def get(u):
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (lecture seule)'})
        t = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', 'replace')
    except Exception:
        return u, []
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    return u, plages(re.sub(r'\s+', ' ', t))
if __name__ == '__main__':
    d = json.load(open(P, encoding='utf-8'))
    w = [e for e in d['offres'] if not e.get('debut')]
    urls = sorted({e['lien'] for e in w})
    with cf.ThreadPoolExecutor(16) as ex:
        res = dict(ex.map(get, urls))
    # une plage retrouvée sur >= 3 pages du même site est un bandeau, pas une date d'offre
    from collections import Counter
    from urllib.parse import urlparse
    cnt = Counter((urlparse(u).netloc, p) for u, r in res.items() for p in set(r))
    n = 0
    for e in w:
        r = [p for p in res.get(e['lien'], []) if cnt[(urlparse(e['lien']).netloc, p)] < 3]
        # page d'accueil / agrégat : on ne retient rien (dates de plusieurs offres mélangées)
        if urlparse(e['lien']).path.strip('/') == '':
            r = []
        if r:
            a, b = r[0]
            e['debut'], e['fin'], e['duree_jours'] = a.isoformat(), b.isoformat(), (b - a).days + 1
            n += 1
            print(e['ecole_slug'], '|', e['titre'][:40], '|', e['debut'], e['fin'], e['duree_jours'], '|', e['lien'][:70])
    # date dans le titre d'une offre d'une demi-journée (« 4 h (19.5.2027) ») : un seul jour
    for e in w:
        g = re.search(r'\b(\d{1,2}) ?h \((\d{1,2})\.(\d{1,2})\.(20\d\d)\)', e['titre'])
        if g and not e.get('debut') and int(g.group(1)) <= 8:
            a = D(g.group(4), g.group(3), g.group(2))
            if a and a >= AUJ:
                e['debut'] = e['fin'] = a.isoformat(); e['duree_jours'] = 1; n += 1
                print(e['ecole_slug'], '|', e['titre'][:40], '| titre', e['debut'])
    print(n, 'offres renseignées')
    if '--ecrire' in sys.argv:
        json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('écrit')
