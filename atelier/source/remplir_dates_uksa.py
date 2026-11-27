"""Tâche 53 : dates début/fin des stages UKSA, relevées sur uksa.org (lecture seule).

Pour chaque fiche UKSA, lit la page du cours, prend la plus proche date publiée du tableau
« Upcoming dates » (Start date → End date), écrit debut, fin, duree_jours = fin - debut + 1 et verifie.
Pages sans dates (formations à la demande) : fiche laissée vide. prix_eur n'est pas écrit : la page
donne des livres sterling, pas des euros.
"""
import datetime
import json
import re
import subprocess

F = '/opt/data/cache/claude-nuit/travail/projets/sailingmore/stages.json'
AUJ = '2026-11-27'
MOIS = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
RE = re.compile(r'(\d{1,2}) ([A-Z][a-z]{2}) (20\d\d)\s*(?:→|&rarr;|&#8594;|-&gt;)\s*(\d{1,2}) ([A-Z][a-z]{2}) (20\d\d)')

d = json.load(open(F, encoding='utf-8'))
L = d if isinstance(d, list) else max([v for v in d.values() if isinstance(v, list)], key=len)
cache = {}


def dates(url):
    if url in cache:
        return cache[url]
    h = subprocess.run(['curl', '-sL', '-m', '30', url], capture_output=True, text=True).stdout
    h = re.sub(r'<(script|style)\b.*?</\1>', ' ', h, flags=re.S)
    t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h))
    i = t.find('Upcoming dates')
    res = []
    if i >= 0:
        for m in RE.finditer(t[i:i + 6000]):
            a = datetime.date(int(m[3]), MOIS[m[2]], int(m[1]))
            b = datetime.date(int(m[6]), MOIS[m[5]], int(m[4]))
            if b >= a:
                res.append((a, b))
    cache[url] = min(res) if res else None
    return cache[url]


n = 0
for x in L:
    if x.get('ecole') != 'UKSA' or x.get('hors_offre') or x.get('debut'):
        continue
    r = dates(x['lien'])
    print('OK ' if r else 'vide', x['titre'][:60], r[0] if r else '')
    if not r:
        continue
    a, b = r
    x['debut'], x['fin'] = a.isoformat(), b.isoformat()
    x['duree_jours'] = (b - a).days + 1
    x['verifie'] = AUJ
    n += 1
json.dump(d, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(n, 'fiches datées')
