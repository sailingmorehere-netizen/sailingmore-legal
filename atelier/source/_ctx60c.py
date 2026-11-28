import json, re, html, urllib.request
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))
def page(i):
    rq = urllib.request.Request(d['offres'][i]['lien'], headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
    t = urllib.request.urlopen(rq, timeout=25).read(900000).decode('utf-8', 'replace')
    t = re.sub(r'(?is)<(script|style|noscript).*?</\1>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
t = page(838)
for m in re.finditer(r'Tečaj jadranja – 2 dni', t):
    print('838 >', t[m.start():m.start() + 330]); break
for i in (888, 890, 878, 879):
    t = page(i)
    print('##', i, d['offres'][i]['titre'])
    for m in list(re.finditer(r'(?:lei|Ft)\b', t))[:5]:
        print('     ', t[max(0, m.start() - 110):m.end() + 5])
