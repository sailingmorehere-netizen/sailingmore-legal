import json, os, re, html, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))['o']
src = open(os.path.join(R, 'scripts/applique_prix_d.py')).read()
P = eval(src[src.index('P = {') + 4:src.index('\n}\n') + 2], {'E': 'EUR', 'G': 'GBP', 'C': 'CHF'})
for i, (p, c) in P.items():
    o = L[i]
    try:
        r = urllib.request.Request(o[10], headers={'User-Agent': 'Mozilla/5.0'})
        b = urllib.request.urlopen(r, timeout=20).read().decode('utf-8', 'ignore')
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<(script|style)[\s\S]*?</\1>|<[^>]+>', ' ', b)))
        n = str(p)
        hit = re.search(r'(?<![\d.,])' + n + r'(?:[.,]\d+)?(?![\d])', t)
        print(i, o[4][:18], p, c, 'OK' if hit else 'ABSENT', '|', t[max(0, hit.start() - 40):hit.end() + 15] if hit else '', flush=True)
    except Exception as e:
        print(i, o[4][:18], p, 'ERR', str(e)[:50], flush=True)
