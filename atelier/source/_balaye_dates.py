import json, re, urllib.request, html, concurrent.futures as cf
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
w = [e for e in d['offres'] if not e.get('debut')]
urls = sorted({e['lien'] for e in w})
pat = re.compile(r'(20(?:26|27)-\d\d-\d\d|\d{1,2}[./]\d{1,2}[./]20(?:26|27)|\d{1,2}(?:st|nd|rd|th)?\.? (?:of )?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Janv|Févr|Mars|Avr|Mai|Juin|Juil|Août|Sept|Okt|Dez|Mär|Gen|Mag|Giu|Lug|Ago|Set|Ott|Ene|Abr|Mrt|Mei)[a-zéû]*\.?(?: 20(?:26|27))?)')
def get(u):
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
        t = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', 'replace')
    except Exception as e:
        return u, None, str(e)[:40]
    t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    t = re.sub(r'\s+', ' ', t)
    out = []
    for m in pat.finditer(t):
        s = max(0, m.start() - 50)
        out.append(t[s:m.end() + 50])
        if len(out) >= 6: break
    return u, out, ''
res = {}
with cf.ThreadPoolExecutor(16) as ex:
    for u, o, err in ex.map(get, urls):
        res[u] = o
json.dump(res, open('scripts/_balayage.json', 'w'), ensure_ascii=False, indent=1)
print(len(urls), 'urls;', sum(1 for v in res.values() if v is None), 'erreurs;', sum(1 for v in res.values() if v), 'avec dates')
