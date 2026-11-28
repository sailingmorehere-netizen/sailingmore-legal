# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Tâche 51 : marque hors_offre les pages d'info (sans prix, sans date, sans inscription).
Vérifie chaque lien (statut HTTP + signaux d'inscription) avant de marquer. Ne supprime rien."""
import json, re, sys, urllib.request

F = 'projets/sailingmore/stages.json'
IDX = [76, 82, 90, 95, 96, 98, 100, 103, 106, 108, 120, 123, 205 - 0 if False else 207, 208, 210,
       226, 234, 240, 243, 246, 248, 253, 254, 263, 264, 265, 266, 267, 270, 271,
       341, 360, 361, 362, 363, 364, 365, 366, 367, 368, 374, 376, 386, 387, 308, 337]
SIGNAUX = re.compile(r'add to cart|in winkelwagen|inschrijven|book now|reserveer|boek nu|buchen|anmelden|jetzt buchen|checkout', re.I)

txt = open(F, encoding='utf-8').read()
d = json.loads(txt)
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
indent = None
for ind in (None, 1, 2, 4):
    for ea in (False, True):
        if json.dumps(d, indent=ind, ensure_ascii=ea) == txt.rstrip('\n'):
            indent, EA, ok = ind, ea, True
            break
    else:
        continue
    break
else:
    print('format JSON non reproductible, abandon'); sys.exit(1)

n = 0
for i in IDX:
    x = L[i]
    if x.get('prix_eur') not in (None, '', []) or x.get('debut') or x.get('hors_offre'):
        print('SKIP', i, x.get('titre')); continue
    try:
        r = urllib.request.urlopen(urllib.request.Request(x['lien'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=15)
        st = r.status; body = r.read(400000).decode('utf-8', 'ignore')
        sig = len(SIGNAUX.findall(body))
    except Exception as e:
        st, sig = str(e)[:40], -1
    print(i, x['ecole'], '|', x['titre'][:50], '|', st, '| signaux', sig)
    if sig > 3:
        print('   -> signaux d\'inscription, NON marqué'); continue
    x['hors_offre'] = True
    n += 1
open(F, 'w', encoding='utf-8').write(json.dumps(d, indent=indent, ensure_ascii=EA) + ('\n' if txt.endswith('\n') else ''))
print('marqués', n)
