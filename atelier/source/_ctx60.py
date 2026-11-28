"""Vérifie sur la page de l'offre la présence de montants précis, et montre le contexte de quelques autres."""
import json, re, html, urllib.request
d = json.load(open('projets/sailingmore/stages.json', encoding='utf-8'))

def page(i):
    rq = urllib.request.Request(d['offres'][i]['lien'], headers={'User-Agent': 'Mozilla/5.0 (lecture)'})
    t = urllib.request.urlopen(rq, timeout=25).read(900000).decode('utf-8', 'replace')
    t = re.sub(r'(?is)<(script|style|noscript).*?</\1>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))

VERIF = {817: '122', 820: '154', 826: '230', 827: '200', 840: '490', 841: '276', 881: '230', 883: '165', 812: '250', 813: '250'}
for i, k in VERIF.items():
    t = page(i)
    ms = [m.start() for m in re.finditer(re.escape(k), t)][:2]
    print('#', i, d['offres'][i]['titre'][:50], '| trouvé' if ms else '| ABSENT')
    for s in ms:
        print('     ', t[max(0, s - 90):s + 50])
CTX = {804: r'Zoom8', 867: r'EXTRA', 877: r'tandíj|Ft', 882: r'kombin', 883: r'gyakorló hétvége', 838: r'2 dni|dvodnevni', 892: r'Sailcamp'}
for i, k in CTX.items():
    t = page(i)
    print('##', i, d['offres'][i]['titre'][:50])
    for m in list(re.finditer(k, t, re.I))[:3]:
        print('     ', t[max(0, m.start() - 60):m.end() + 110])
