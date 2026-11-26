import json, re, urllib.request, html, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(R + '/projets/sailingmore/site/stages-proches.json'))['o']
lot = ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife',
       'Urban Truant', 'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica',
       'Segelschule Überlingen', 'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail',
       'Vent du Large', 'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']
pat = re.compile(r'(?:€|£|\$|EUR|CHF|GBP)\s?\d[\d.,\']*|\d[\d.,\']*\s?(?:€|£|\$|EUR|euro|CHF|GBP|Euro)', re.I)
out = []
for i, o in enumerate(L):
    if o[4] in lot and o[8] in (None, '', 0):
        u = o[10]
        try:
            req = urllib.request.Request(u if u.startswith('http') else 'https://sailingmore.fr/' + u,
                                         headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=20)
            final = resp.geturl()
            t = resp.read().decode('utf-8', 'ignore')
            t = re.sub(r'(?s)<(script|style).*?</\1>', ' ', t)
            t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
            t = re.sub(r'\s+', ' ', t)
            hits = [t[max(0, m.start() - 60):m.end() + 30] for m in pat.finditer(t)][:6]
        except Exception as e:
            final, hits = u, ['ERR ' + str(e)[:60]]
        out.append(f'{i} | {o[4]} | {o[3][:50]} | {final}\n   ' + '\n   '.join(hits))
open(R + '/sonde_prix_d.txt', 'w').write('\n'.join(out))
print(len(out))
