import json, os, re, sys, urllib.request, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
g = json.load(open(os.path.join(R, 'projets/sailingmore/site/go-liens.json')))
d = json.load(open(os.path.join(R, 'projets/sailingmore/site/stages-proches.json')))
sys.path.insert(0, os.path.join(R, 'scripts'))
lot = ['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife', 'Urban Truant',
       'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica', 'Segelschule Überlingen',
       'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail', 'Vent du Large',
       'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone']
RE = re.compile(r'(?:€|EUR|CHF|£|Fr\.?)\s?\d[\d.,\']*|\d[\d.,\']*\s?(?:€|EUR|CHF|£|Euro)', re.I)
for i, o in enumerate(d['o']):
    if o[4] in lot and o[8] in (None, '', 0):
        idd = re.search(r'id=(\w+)', o[10]).group(1)
        u = g.get(idd)
        u = u if isinstance(u, str) else json.dumps(u)
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            t = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', 'ignore')
            t = re.sub(r'<(script|style).*?</\1>', ' ', t, flags=re.S)
            t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
            t = re.sub(r'\s+', ' ', t)
            m = [t[max(0, x.start() - 50):x.end() + 20] for x in RE.finditer(t)][:5]
        except Exception as e:
            m = ['ERREUR ' + str(e)[:60]]
        print(i, o[3][:40], '|', u)
        for s in m:
            print('    ', s)
