"""Tâche 58, complément : dates publiées dans le TITRE même de l'offre (format finlandais D.–D.M.YYYY ou D.M.YYYY), futures seulement.
Écrit debut, fin, duree_jours ensemble. Lancé après _dates58.py applique."""
import json, os, re, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(R, 'projets/sailingmore/stages.json')
AUJ = datetime.date(2026, 11, 27)
d = json.load(open(F, encoding='utf-8'))
n = 0
for e in d['offres']:
    if e.get('debut') or e.get('hors_offre'):
        continue
    t = e['titre']
    m = re.search(r'(\d{1,2})\.?\s*[–-]\s*(\d{1,2})\.(\d{1,2})\.(20\d\d)', t)
    try:
        if m:
            a = datetime.date(int(m[4]), int(m[3]), int(m[1])); b = datetime.date(int(m[4]), int(m[3]), int(m[2]))
        else:
            m = re.search(r'(\d{1,2})\.(\d{1,2})\.(20\d\d)', t)
            if not m: continue
            a = b = datetime.date(int(m[3]), int(m[2]), int(m[1]))
    except ValueError:
        continue
    if a < AUJ or b < a:
        continue
    e['debut'], e['fin'], e['duree_jours'] = a.isoformat(), b.isoformat(), (b - a).days + 1
    e['verifie'] = AUJ.isoformat()
    n += 1
json.dump(d, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('datées par le titre', n)
