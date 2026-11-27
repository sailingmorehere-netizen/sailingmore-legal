#!/usr/bin/env python3
"""Tâche 59 : niveau des offres CNV Versoix, lu sur la page de l'école (étiquette de chaque session :
Beginner / All levels / Advanced / Advanced). Appariement session <-> offre par (date de début, heure, prix).
  Beginner -> debutant ; Advanced -> confirme ; « All levels / Advanced » = pas un niveau unique -> laissé vide.
    python3 scripts/niveaux_cnv59.py            # simulation
    python3 scripts/niveaux_cnv59.py --ecrire   # écrit stages.json (sauvegarde .bak-avant-59b)
"""
import json, os, re, sys, html, shutil, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/stages.json')
MOIS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
        'november', 'december']
MA = '|'.join(m.capitalize() for m in MOIS)
LV = r'(All levels / Advanced|Beginner|Advanced|Intermediate|All levels)'
ROW = re.compile(LV + r' (' + MA + r') (\d{4}) (.+?) · (\d\d):(\d\d)[–-]\d\d:\d\d CHF (\d+)')
MAP = {'Beginner': 'debutant', 'Advanced': 'confirme', 'Intermediate': 'intermediaire',
       'All levels / Advanced': 'tous_niveaux', 'All levels': 'tous_niveaux'}  # précédent tâche 52

d = json.load(open(F))
offres = d['offres']
pages = sorted({e['lien'] for e in offres if e['ecole_slug'] == 'cnv-versoix'})
sessions = {}
for u in pages:
    t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf8', 'ignore')
    t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    for m in ROW.finditer(t):
        niv, mois, an, seg, hh, mm, prix = m.groups()
        seg = seg.split(',')[-1] if ',' in seg else seg
        mm_ = re.search(r'(\d{1,2})', seg)
        nom = re.search('(' + MA + ')', seg)
        if not mm_:
            continue
        mo = MOIS.index((nom.group(1) if nom else mois).lower()) + 1
        an_ = int(an)
        cle = (u, '%d-%02d-%02d' % (an_, mo, int(mm_.group(1))), '%s:%s' % (hh, mm))
        sessions.setdefault(cle, set()).add(niv)
print(len(sessions), 'sessions lues sur', len(pages), 'pages')
ok = amb = sans = 0
ecrits = 0
for e in offres:
    if e['ecole_slug'] != 'cnv-versoix' or e.get('niveau'):
        continue
    h = re.search(r'(\d\d:\d\d)-\d\d:\d\d', e['titre'])
    cle = (e['lien'], e['debut'], h.group(1) if h else '')
    niv = sessions.get(cle)
    if not niv:
        sans += 1
        if sans < 6:
            print('  introuvable', cle, e['titre'])
            print('   sessions voisines', [k[1:] for k in sessions if k[0] == e['lien']][:5])
        continue
    if len(niv) != 1 or list(niv)[0] not in MAP:
        amb += 1
        continue
    ok += 1
    e['niveau'] = MAP[list(niv)[0]]
print('apparié et niveau unique:', ok, '| tous niveaux / ambigu:', amb, '| session introuvable:', sans)
if '--ecrire' in sys.argv:
    shutil.copy(F, F + '.bak-avant-59b')
    json.dump(d, open(F, 'w'), ensure_ascii=False, indent=1)
    print('écrit')
