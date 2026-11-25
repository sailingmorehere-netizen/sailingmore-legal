import json, os, re, html, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))['o']
for i, pat in [(173, r'240,-'), (170, r'Preis|,-'), (172, r',-'), (213, r'Tariffe|€')]:
    o = L[i]
    r = urllib.request.Request(o[10], headers={'User-Agent': 'Mozilla/5.0'})
    b = urllib.request.urlopen(r, timeout=20).read().decode('utf-8', 'ignore')
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<(script|style)[\s\S]*?</\1>|<[^>]+>', ' ', b)))
    print('==', i, o[3])
    for m in list(re.finditer(pat, t))[:3]:
        print('  ', t[max(0, m.start() - 250):m.end() + 250])
