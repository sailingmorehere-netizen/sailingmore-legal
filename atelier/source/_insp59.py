import json, re, html, os, urllib.request, collections
from concurrent.futures import ThreadPoolExecutor
R = '.'
o = json.load(open('projets/sailingmore/stages.json'))['offres']
liens = sorted({e['lien'] for e in o if not e.get('niveau') and e['ecole_slug'] != 'cnv-versoix'})
os.makedirs('tmp_n59', exist_ok=True)
def get(u):
    p = 'tmp_n59/' + re.sub(r'\W+', '_', u)[:150] + '.txt'
    if os.path.exists(p):
        return u, open(p).read()
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20).read().decode('utf8', 'ignore')
        t = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', t)
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    except Exception as ex:
        t = ''
    open(p, 'w').write(t)
    return u, t
with ThreadPoolExecutor(12) as ex:
    res = dict(ex.map(get, liens))
pat = re.compile(r'(?i)\b(?:skill level|level|niveau|livello|nivel|stufe|niveaus?|niveau)\s*[:\-–]\s*([A-Za-zéèàäöüß/ ]{3,30})')
c = collections.Counter()
par = collections.defaultdict(collections.Counter)
for u, t in res.items():
    sl = [e['ecole_slug'] for e in o if e['lien'] == u][0]
    for m in pat.finditer(t):
        par[sl][m.group(1).strip().lower()[:25]] += 1
print(len(res), 'pages,', sum(1 for t in res.values() if t), 'lues')
for sl, cc in par.items():
    print(sl, cc.most_common(6))
