"""Tâche 60, passe 3 : devises £ / $ / CHF / PLN etc. sur les offres encore sans prix. Écrit releve_prix60c.json."""
import json, re, html, urllib.request, concurrent.futures as cf
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
print('taux', d['taux'])
r1 = json.load(open('releve_prix60.json', encoding='utf-8'))
r2 = json.load(open('releve_prix60b.json', encoding='utf-8'))
cand = [(i, e) for i, e in enumerate(d['offres'])
        if e.get('prix_eur') in (None, '', 0) and not e.get('hors_offre') and e.get('lien')
        and not r1.get(str(i), {}).get('ex') and not r2.get(str(i), {}).get('ex')]
PAT = re.compile(r'(?:[£$]\s?\d[\d.,]*|\d[\d.,]*\s?(?:GBP|USD|CHF|£|\$)|\b(?:GBP|USD|CHF)\s?\d[\d.,]*|\bFr\.?\s?\d{2,4})', re.I)

def lire(x):
    i, e = x
    try:
        rq = urllib.request.Request(e['lien'], headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
        t = urllib.request.urlopen(rq, timeout=20).read(700000).decode('utf-8', 'replace')
    except Exception as ex:
        return i, {'err': str(ex)[:60]}
    t = re.sub(r'(?is)<(script|style|noscript).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    t = re.sub(r'\s+', ' ', t)
    out = [t[max(0, m.start() - 60):m.end() + 25] for m in list(PAT.finditer(t))[:3]]
    return i, {'ex': out, 'n': len(t)}

with cf.ThreadPoolExecutor(12) as ex:
    R = dict(ex.map(lire, cand))
res = {str(i): {'ecole': d['offres'][i]['ecole'], 'titre': d['offres'][i]['titre'], **v} for i, v in R.items()}
json.dump(res, open('releve_prix60c.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for i, v in res.items():
    if v.get('ex'):
        print(f"#{i} {v['ecole']} | {v['titre'][:50]}")
        for x in v['ex'][:2]:
            print('    ', x[:110])
print(len(res), sum(1 for v in res.values() if v.get('ex')))
