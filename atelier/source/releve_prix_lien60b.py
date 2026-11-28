"""Tâche 60, passe 2 : offres sans prix_eur dont la passe 1 n'a rien trouvé (ou en HUF/RON).
Motifs élargis : EUR 250, 250,-, Ft, lei/RON, 'euro'. Écrit releve_prix60b.json (lecture seule du site)."""
import json, re, html, urllib.request, concurrent.futures as cf
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
r1 = json.load(open('releve_prix60.json', encoding='utf-8'))
cand = [(i, e) for i, e in enumerate(d['offres'])
        if e.get('prix_eur') in (None, '', 0) and not e.get('hors_offre') and e.get('lien')
        and not r1.get(str(i), {}).get('ex')]
PAT = re.compile(r'(?:\bEUR\s?\d[\d.,]*|\d[\d.,  ]{0,8}\d\s?(?:,-|Ft|HUF|lei|RON|Euro|eur\b)|\b(?:Ft|lei|RON)\s?\d[\d.,]*|\d{2,3}\s?(?:Ft|lei|RON|Euro)\b)', re.I)

def lire(x):
    i, e = x
    try:
        rq = urllib.request.Request(e['lien'], headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
        t = urllib.request.urlopen(rq, timeout=20).read(700000).decode('utf-8', 'replace')
    except Exception as ex:
        return i, {'err': str(ex)[:80]}
    t = re.sub(r'(?is)<(script|style|noscript).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    t = re.sub(r'\s+', ' ', t)
    out = []
    for m in PAT.finditer(t):
        out.append(t[max(0, m.start() - 70):m.end() + 30])
        if len(out) >= 4:
            break
    return i, {'ex': out, 'n': len(t)}

with cf.ThreadPoolExecutor(12) as ex:
    R = dict(ex.map(lire, cand))
res = {str(i): {'ecole': d['offres'][i]['ecole'], 'titre': d['offres'][i]['titre'], 'dev': d['offres'][i].get('devise'), **v}
       for i, v in R.items()}
json.dump(res, open('releve_prix60b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for i, v in res.items():
    if v.get('ex'):
        print(f"#{i} {v['ecole']} | {v['titre'][:55]} [{v['dev']}]")
        for x in v['ex'][:2]:
            print('    ', x[:130])
print(len(res), sum(1 for v in res.values() if v.get('ex')), sum(1 for v in res.values() if v.get('err')))
