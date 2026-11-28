# © 2026 Sailing More — tous droits réservés. All rights reserved.
"""Tâche 60 : lit la page `lien` des offres sans prix_eur (lecture seule) et écrit
les extraits contenant un montant en euros dans releve_prix60.json. Ne modifie pas stages.json."""
import json, re, html, urllib.request, concurrent.futures as cf
F = 'projets/sailingmore/stages.json'
d = json.load(open(F, encoding='utf-8'))
cand = [(i, e) for i, e in enumerate(d['offres'])
        if e.get('prix_eur') in (None, '', 0) and not e.get('hors_offre') and e.get('devise') == 'EUR' and e.get('lien')]
PAT = re.compile(r'(?:€\s?\d[\d.,  ]{0,8}\d|\d[\d.,  ]{0,8}\d\s?(?:€|EUR|euro))', re.I)

def lire(x):
    i, e = x
    try:
        r = urllib.request.Request(e['lien'], headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
        t = urllib.request.urlopen(r, timeout=20).read(600000).decode('utf-8', 'replace')
    except Exception as ex:
        return i, {'err': str(ex)[:80]}
    t = re.sub(r'(?is)<(script|style|noscript).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    t = re.sub(r'\s+', ' ', t)
    out = []
    for m in PAT.finditer(t):
        out.append(t[max(0, m.start() - 70):m.end() + 30])
        if len(out) >= 5:
            break
    return i, {'ex': out}

with cf.ThreadPoolExecutor(12) as ex:
    R = dict(ex.map(lire, cand))
res = {str(i): {'ecole': d['offres'][i]['ecole'], 'titre': d['offres'][i]['titre'], 'lien': d['offres'][i]['lien'], **v}
       for i, v in R.items()}
json.dump(res, open('releve_prix60.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(res), sum(1 for v in res.values() if v.get('ex')), sum(1 for v in res.values() if v.get('err')))
