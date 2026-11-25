import json, os, re, html, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))['o']
IDX = [113, 114, 115, 116, 118, 119, 120, 121, 122, 164, 167, 170, 172, 173, 211, 212, 214, 215, 216, 227, 229, 272, 313, 375, 401, 228]
K = re.compile(r'(preis|kosten|prezzo|prezzi|tarif|prix|precio|cuota|euro|eur\b|€|£|\bab \d|\d\s?,-)', re.I)
for i in IDX:
    o = L[i]
    try:
        r = urllib.request.Request(o[10], headers={'User-Agent': 'Mozilla/5.0'})
        b = urllib.request.urlopen(r, timeout=20).read().decode('utf-8', 'ignore')
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<(script|style)[\s\S]*?</\1>|<[^>]+>', ' ', b)))
        out = []
        for m in K.finditer(t):
            s = t[max(0, m.start() - 45):m.end() + 40]
            if re.search(r'\d', s):
                out.append(s)
            if len(out) >= 4:
                break
        print(i, o[4][:16], '|', out, flush=True)
    except Exception as e:
        print(i, 'ERR', str(e)[:50], flush=True)
