import json, re, sys
p = 'projets/sailingmore/stages.json'
raw = json.load(open(p, encoding='utf-8'))
L = raw if isinstance(raw, list) else max((v for v in raw.values() if isinstance(v, list)), key=len)
vide = lambda e, k: e.get(k) in (None, '', [])
if len(sys.argv) > 1 and sys.argv[1] == 'cles':
    print(sorted(L[0].keys()))
    for e in [x for x in L if vide(x, 'duree_jours')][:8]:
        print({k: e.get(k) for k in e if k in ('titre', 'nom', 'title', 'prix_eur', 'type')})
    sys.exit()
MOTS = {'un': 1, 'une': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5, 'six': 6, 'sept': 7, 'huit': 8,
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six ': 6, 'seven': 7, 'eight': 8}
RE_N = re.compile(r'\b(\d{1,2})\s*(?:-|à|to)?\s*(?:\d{1,2})?\s*(jours?|days?|tage?|giorni|d[ií]as|dias|journées?)\b', re.I)
RE_M = re.compile(r'\b(un|une|deux|trois|quatre|cinq|six|sept|huit|one|two|three|four|five|seven|eight)\s+(jours?|days?)\b', re.I)
RE_WE = re.compile(r'week[- ]?end|weekend|wochenende|fin de semaine', re.I)
RE_SEM = re.compile(r'\b(1|une|one)\s+(semaine|week)\b', re.I)
def duree(t):
    t = t or ''
    m = RE_N.search(t)
    if m:
        # plage "2-3 jours" : on ne tranche pas
        if re.search(r'\d\s*(?:-|à|to)\s*\d', m.group(0)):
            return None
        return int(m.group(1))
    m = RE_M.search(t)
    if m:
        return MOTS[m.group(1).lower()]
    if RE_WE.search(t):
        return 2
    if RE_SEM.search(t):
        return 7
    return None
import shutil
shutil.copyfile(p, p + '.bak-avant-66')
n = 0
for e in L:
    if not vide(e, 'duree_jours'):
        continue
    d = duree(e.get('titre') or e.get('nom') or e.get('title'))
    if d and 1 <= d <= 14:
        e['duree_jours'] = d
        n += 1
json.dump(raw, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('remplis', n)
