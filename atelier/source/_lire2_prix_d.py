import json, os, re, sys, urllib.request, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
g = json.load(open(os.path.join(R, 'projets/sailingmore/site/go-liens.json')))
ids = sys.argv[1:]
RE = re.compile(r'(prix|tarif|preis|euro|precio|prezzo|costo|kosten|price|cost|€|\bab\s\d)', re.I)
for i in ids:
    u = g[i]
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15).read().decode('utf-8', 'ignore')
        t = re.sub(r'<(script|style).*?</\1>', ' ', t, flags=re.S)
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
        m = [t[max(0, x.start() - 40):x.end() + 60] for x in RE.finditer(t) if re.search(r'\d{2,}', t[x.start():x.end() + 60])][:4]
    except Exception as e:
        m = ['ERREUR ' + str(e)[:50]]
    print(i, u)
    for s in m:
        print('   ', s)
