import json, re, html, urllib.request
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
def page(i):
    rq = urllib.request.Request(d['offres'][i]['lien'], headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
    t = urllib.request.urlopen(rq, timeout=25).read(900000).decode('utf-8', 'replace')
    t = re.sub(r'(?is)<(script|style|noscript).*?</\1>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
for i in (893, 894, 887):
    t = page(i)
    print('##', i, d['offres'][i]['titre'], d['offres'][i]['lien'][-40:])
    for m in list(re.finditer(r'(?:RON|LEI|lei)\b', t))[:7]:
        print('     ', t[max(0, m.start() - 100):m.end() + 3])
