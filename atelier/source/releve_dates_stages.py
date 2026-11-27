#!/usr/bin/env python3
"""Relève debut/fin/duree_jours sur la page de l'école pour les offres sans debut.
Lecture seule sur le réseau (GET). Ne renseigne les trois champs ensemble que si la page
publie une plage de dates explicite à venir ; sinon laisse vide.
Usage: releve_dates_stages.py [--ecrire]"""
import json, os, re, sys, hashlib, datetime, urllib.request
from concurrent.futures import ThreadPoolExecutor
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, 'projets/sailingmore/stages.json')
CACHE = '/tmp/stages_pages'
os.makedirs(CACHE, exist_ok=True)
AUJ = datetime.date(2026, 11, 27)
MOIS = {}
for i, noms in enumerate([
    'jan january janvier januar januari gennaio enero janeiro', 'feb february février fevrier februar februari febbraio febrero fevereiro',
    'mar march mars märz maart marzo marzo março', 'apr april avril aprile abril',
    'may mai mei maggio mayo maio', 'jun june juin juni giugno junio junho',
    'jul july juillet juli luglio julio julho', 'aug august août aout agosto',
    'sep sept september septembre settembre septiembre setembro', 'oct october octobre oktober ottobre octubre outubro',
    'nov november novembre novembro noviembre', 'dec december décembre decembre dezember dicembre diciembre dezembro'], 1):
    for n in noms.split():
        MOIS[n] = i
M = '|'.join(sorted(MOIS, key=len, reverse=True))
ORD = r'(?:st|nd|rd|th|er|\.)?'
SEP = r'\s*(?:-|–|—|to|au|bis|tot|al|a|até|–)\s*'


VALIDES = {('bhmarine', 'RYA Competent Crew'), ('ezs', 'STCW-cursussen'),
           ('soleil', 'Corso di Navigazione Costiera'), ('virgins', 'Greece Flotilla Week')}


def page(url):
    f = os.path.join(CACHE, hashlib.md5(url.encode()).hexdigest())
    if os.path.exists(f):
        return open(f, encoding='utf-8', errors='replace').read()
    try:
        rq = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
        t = urllib.request.urlopen(rq, timeout=25).read().decode('utf-8', 'replace')
    except Exception:
        t = ''
    open(f, 'w', encoding='utf-8').write(t)
    return t


def texte(h):
    h = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', h)
    h = re.sub(r'<[^>]+>', ' ', h)
    h = h.replace('&nbsp;', ' ').replace('&#8211;', '–').replace('&ndash;', '–')
    return re.sub(r'\s+', ' ', h)


def d(y, m, j):
    try:
        return datetime.date(int(y), int(m), int(j))
    except ValueError:
        return None


def plages(t):
    out = []
    # ISO : 2026-12-05 ... 2026-12-12
    for a in re.finditer(r'(20\d\d)-(\d\d)-(\d\d)\s*(?:-|–|to|/)\s*(20\d\d)-(\d\d)-(\d\d)', t):
        out.append((d(*a.group(1, 2, 3)), d(*a.group(4, 5, 6))))
    # 5 - 12 December 2026 / 5th to 12th Dec 2026
    for a in re.finditer(rf'\b(\d{{1,2}}){ORD}{SEP}(\d{{1,2}}){ORD}\s+(?:de\s+|of\s+)?({M})\w*\.?,?\s+(?:de\s+)?(20\d\d)', t, re.I):
        j1, j2, mo, y = a.groups()
        mo = MOIS.get(mo.lower())
        if mo:
            out.append((d(y, mo, j1), d(y, mo, j2)))
    # 28 Nov - 5 Dec 2026
    for a in re.finditer(rf'\b(\d{{1,2}}){ORD}\s+({M})\w*\.?{SEP}(\d{{1,2}}){ORD}\s+({M})\w*\.?,?\s+(20\d\d)', t, re.I):
        j1, m1, j2, m2, y = a.groups()
        m1, m2 = MOIS.get(m1.lower()), MOIS.get(m2.lower())
        if m1 and m2:
            y2 = int(y)
            y1 = y2 - 1 if m1 > m2 else y2
            out.append((d(y1, m1, j1), d(y2, m2, j2)))
    # 5.12.2026 - 12.12.2026 ou 05/12/2026 - 12/12/2026
    for a in re.finditer(r'\b(\d{1,2})[./](\d{1,2})[./](20\d\d)\s*(?:-|–|bis|au|to)\s*(\d{1,2})[./](\d{1,2})[./](20\d\d)', t):
        j1, m1, y1, j2, m2, y2 = a.groups()
        out.append((d(y1, m1, j1), d(y2, m2, j2)))
    return [(a, b) for a, b in out if a and b and a >= AUJ and a <= b and (b - a).days <= 60]


def main():
    ecrire = '--ecrire' in sys.argv
    data = json.load(open(P))
    offres = data['offres']
    cibles = [e for e in offres if not e.get('debut') and e.get('lien')]
    with ThreadPoolExecutor(12) as ex:
        pages = dict(zip([e['lien'] for e in cibles], ex.map(page, [e['lien'] for e in cibles])))
    n = 0
    trouve = {}
    for e in cibles:
        t = texte(pages[e['lien']])
        pl = sorted(set(plages(t)))
        if pl:
            trouve[id(e)] = (pl[0], t)
    # une même plage sur 3 offres ou plus d'une école = bandeau commun, pas une session de l'offre
    freq = {}
    for e in cibles:
        if id(e) in trouve:
            k = (e['ecole_slug'], trouve[id(e)][0])
            freq[k] = freq.get(k, 0) + 1
    for e in cibles:
        if id(e) not in trouve:
            continue
        (a, b), t = trouve[id(e)]
        if freq[(e['ecole_slug'], (a, b))] >= 3:
            continue
        # contrôlé à la main sur le contexte de la page : les autres plages trouvées étaient fausses
        if (e['ecole_slug'], e['titre']) not in VALIDES:
            continue
        i = t.find(str(a.day))
        print('   ctx:', t[max(0, i - 60):i + 80])
        e['debut'], e['fin'] = a.isoformat(), b.isoformat()
        e['duree_jours'] = (b - a).days + 1
        e['verifie'] = AUJ.isoformat()
        n += 1
        print(e['ecole_slug'], e['titre'][:40], e['debut'], e['fin'], e['duree_jours'])
    print(f'{n} offres datées sur {len(cibles)} sans debut')
    if ecrire:
        json.dump(data, open(P, 'w'), ensure_ascii=False, indent=1)
        print('écrit')


main()
