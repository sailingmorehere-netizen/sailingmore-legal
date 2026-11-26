import json, os, re, urllib.request, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = R + '/projets/sailingmore/site/'
L = json.load(open(S + 'stages-proches.json'))['o']
NOMS = set(['Segelschule Insel Reichenau', 'Compagnia della Vela', 'École de croisière Slowlife', 'Urban Truant',
            'Segelschule Grosse Freiheit', 'La Scuola della Vela', 'Soleil Scuola Nautica', 'Segelschule Überlingen',
            'EZS Zeilschool', 'Real Club de Mar', 'Blue Spirit', 'Solent Sail', 'Vent du Large',
            'Lagoo Segelschule Zürich', 'Segelschule Rehbach', 'Segelschule Schluchsee', 'Windzone'])
G = json.load(open(S + 'go-liens.json'))
G = G.get('o', G) if isinstance(G, dict) else G
for i, o in enumerate(L):
    if o[4] in NOMS and o[8] in (None, '', 0) and not o[16]:
        u = G.get(o[10].split('id=')[1].split('&')[0])
        print('==', i, o[3][:40], u)
        try:
            h = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20).read().decode('utf8', 'replace')
        except Exception as e:
            print('  ERR', e); continue
        t = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<(script|style)[^>]*>.*?</\1>|<[^>]+>', ' ', h, flags=re.S)))
        m = re.findall(r'.{60}(?:\d[\d.,]*\s?(?:€|EUR|Euro|CHF|Fr\.)|(?:€|EUR|CHF)\s?\d[\d.,]*).{25}', t)
        for x in m[:6]:
            print('  ', x)
        if not m:
            print('  (aucun montant) len', len(t))
