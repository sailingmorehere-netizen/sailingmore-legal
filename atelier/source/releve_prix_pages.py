# © 2026 Sailing More — tous droits réservés. All rights reserved.
import json, re, sys, urllib.request
d = json.load(open('/opt/data/cache/claude-nuit/travail/projets/sailingmore/stages.json', encoding='utf-8'))
ecoles = sys.argv[1:]
for e in d['offres']:
    if e.get('prix_eur') in (None, '', []) and e['ecole'] in ecoles and not e.get('hors_offre'):
        try:
            r = urllib.request.Request(e['lien'], headers={'User-Agent': 'Mozilla/5.0'})
            h = urllib.request.urlopen(r, timeout=15).read().decode('utf-8', 'ignore')
        except Exception as x:
            print('ERR', e['lien'], x); continue
        t = re.sub(r'<(script|style).*?</\1>', ' ', h, flags=re.S)
        t = re.sub(r'<[^>]+>', ' ', t)
        t = re.sub(r'\s+', ' ', t)
        ms = [t[max(0, m.start() - 50):m.end() + 20] for m in re.finditer(r'(£|€|EUR|GBP)\s?\d[\d.,]*|\d[\d.,]*\s?(€|£|euro)', t)]
        print('##', e['ecole'][:6], e['titre'][:40], e['lien'], len(h))
        for s in ms[:3]:
            print('   ', s)
