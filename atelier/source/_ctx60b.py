import json, re, html, urllib.request
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
for i in (169, 170, 172, 173, 399, 814, 827):
    rq = urllib.request.Request(d['offres'][i]['lien'], headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
    t = urllib.request.urlopen(rq, timeout=25).read(900000).decode('utf-8', 'replace')
    t = re.sub(r'(?is)<(script|style|noscript).*?</\1>', ' ', t)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    print('##', i, d['offres'][i]['titre'][:60], d['offres'][i]['lien'][-40:])
    for m in list(re.finditer(r'\d[\d.]*,-|\d+\s?(?:Euro|€)', t))[:6]:
        print('     ', t[max(0, m.start() - 75):m.end() + 15])
